#!/usr/bin/python3
"""Tax lot harvesting advisor for brokerage accounts.

Reads brokerage tax lots from a CSV (Schwab, Fidelity, or Vanguard export) and
tax context from a savings.py TOML config, then recommends which lots to sell
for tax-gain harvesting (filling the remaining federal 0% long-term capital
gains bracket) and which lots show tax-loss harvesting opportunities with
suggested swap partners.

Educational planning tool, not tax advice. Wash-sale rules, specific-lot
selection, and foreign tax credits are not modeled.
"""

import argparse
import csv
import datetime as _dt
import os
import re
import sys

from tabulate import tabulate

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from savings import (
    load_toml_config,
    _single_or_mfj_status,
    _status_value,
    _state_capital_gains_rate,
    long_term_capital_gains_tax,
)

CASH_SYMBOL_RE = re.compile(
    r"cash|money|mkt|sweep|fdr|fcash|paid in lieu", re.IGNORECASE
)

SWAP_MAP = {
    "VEA": "IEFA",
    "IEFA": "VEA",
    "VXUS": "IXUS",
    "IXUS": "VXUS",
    "BND": "SCHZ",
    "SCHZ": "BND",
    "BNDX": "IAGG",
    "IAGG": "BNDX",
    "VTI": "ITOT",
    "ITOT": "VTI",
    "VUG": "IWF",
    "IWF": "VUG",
    "VTV": "IWD",
    "IWD": "VTV",
    "VO": "ITOT",
    "VV": "SPY",
    "SPY": "ITOT",
    "SCHB": "VTI",
    "SPY": "VOO",
    "VOO": "VTI",
}

SWAP_GROUPS = (
    ("DFUS", "AVUS", "SCHB", "VTI", "ITOT"),
    ("SCHF", "AVIV", "DFAI", "VEA", "IEFA"),
    ("AVUV", "DFSV", "FNDA", "VIOV", "IJS"),
    ("AVDV", "DISV", "FNDC", "VSS"),
    ("SCHE", "AVES", "DFEM", "VWO", "IEMG"),
    ("SWNTX", "AVBD", "DFBIX", "BNDX"),
    ("SCHP", "AVIP", "DFAIP", "SWRSX", "VVAX", "DFIP", "VTIP"),
    ("AVHY", "DFHIX", "SCYB", "JNK", "VWEHX"),
)


def _build_swap_map() -> dict[str, str]:
    """Return the symbol -> swap-partner map, merging group rings over base pairs."""
    merged = dict(SWAP_MAP)
    for group in SWAP_GROUPS:
        symbols = tuple(dict.fromkeys(group))
        for index, symbol in enumerate(symbols):
            merged[symbol] = symbols[(index + 1) % len(symbols)]
    return merged


def swap_partner(symbol: str) -> str | None:
    """Return a valid swap partner for a symbol, or None."""
    return _build_swap_map().get(symbol)

MONTH_ABBREV = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}


def _parse_date(value: str) -> _dt.date | None:
    """Parse a date from the various brokerage CSV formats."""
    value = (value or "").strip()
    if not value or value in {"-", "--", ""}:
        return None
    for fmt in ("%m/%d/%Y", "%m/%d/%y", "%Y-%m-%d"):
        try:
            return _dt.datetime.strptime(value, fmt).date()
        except ValueError:
            pass
    parts = re.split(r"[-/ ]+", value.strip())
    if len(parts) == 3 and parts[0].lower() in MONTH_ABBREV:
        try:
            year = int(parts[-1])
            if year < 100:
                year += 2000
            return _dt.date(year, MONTH_ABBREV[parts[0].lower()], int(parts[1]))
        except ValueError:
            return None
    return None


def _parse_money(value: str) -> float:
    value = (value or "").strip().replace(",", "").replace("$", "").replace("%", "")
    if not value or value in {"-", "--", ""}:
        return 0.0
    try:
        return float(value)
    except ValueError:
        return 0.0


def _find_header(row):
    """Return the brokerage format name for a header row, or None if unknown."""
    joined = " ".join(row).lower()
    scored = {
        "schwab": sum(1 for token in (
            "open date", "cost per share", "holding period", "gain/loss ($)"
        ) if token in joined),
        "fidelity": sum(1 for token in (
            "acquired", "term", "current value", "average cost basis"
        ) if token in joined),
        "vanguard": sum(1 for token in (
            "acquired date", "symbol/cusip", "cost basis method", "total cost"
        ) if token in joined),
    }
    best = max(scored, key=scored.get)
    return best if scored[best] > 0 else None


def _row_map(row) -> dict:
    return {key.strip().lower(): value for key, value in row.items() if key}


def _get(row: dict, *names: str) -> str:
    for name in names:
        if name in row:
            return row[name]
    return ""


def _get_prefix(row: dict, prefix: str) -> str:
    """Return the value of the first column whose lowercase key starts with prefix."""
    prefix = prefix.lower()
    for key, value in row.items():
        if key and key.startswith(prefix):
            return value
    return ""


def _parse_lots(data, fmt: str, today: _dt.date) -> list[dict]:
    """Convert a brokerage CSV into normalized lot dicts."""
    lots = []
    for raw in data:
        row = _row_map(raw)
        symbol = _get(row, "symbol", "symbol/cusip").split(" ")[0].strip()
        if not symbol or CASH_SYMBOL_RE.search(symbol):
            continue

        if fmt == "schwab":
            date = _parse_date(_get(row, "open date"))
            quantity = _parse_money(_get(row, "quantity"))
            market_value = _parse_money(_get(row, "market value"))
            basis = _parse_money(_get(row, "cost basis"))
            gain = _parse_money(_get(row, "gain/loss ($)"))
            if market_value == 0 and gain != 0:
                market_value = basis + gain
            period = _get(row, "holding period").lower()
            term = "ltcg" if "long" in period else (
                "stcg" if "short" in period else "unknown"
            )
        elif fmt == "fidelity":
            date = _parse_date(_get(row, "acquired"))
            quantity = _parse_money(_get(row, "quantity"))
            market_value = _parse_money(_get(row, "current value"))
            basis = _parse_money(_get(row, "cost basis total"))
            gain = _parse_money(_get(row, "total gain/loss"))
            if market_value == 0 and gain != 0:
                market_value = basis + gain
            term = _get(row, "term").lower()
            term = "ltcg" if "long" in term else (
                "stcg" if "short" in term else "unknown"
            )
        elif fmt == "vanguard":
            date = _parse_date(_get(row, "acquired date"))
            quantity = _parse_money(_get(row, "quantity"))
            market_value = _parse_money(_get_prefix(row, "market value"))
            basis = _parse_money(_get(row, "total cost"))
            gain = _parse_money(_get_prefix(row, "total gain loss"))
            ltcg = _parse_money(_get_prefix(row, "long term gain loss"))
            stcg = _parse_money(_get_prefix(row, "short term gain loss"))
            if gain == 0:
                gain = ltcg + stcg
            if market_value == 0 and gain != 0:
                market_value = basis + gain
            if stcg != 0 and abs(stcg) > 1e-9:
                term = "stcg"
            else:
                term = "ltcg"
        else:
            raise ValueError(f"unknown format: {fmt}")

        gain_pct = (
            gain / basis * 100.0 if basis and abs(gain) > 1e-9 else 0.0
        )
        long_term = (
            term == "ltcg"
            or (date is not None and (today - date).days > 365)
        )
        lots.append(
            {
                "symbol": symbol,
                "date": date,
                "quantity": quantity,
                "cost_basis": basis,
                "market_value": market_value,
                "gain": gain,
                "gain_pct": gain_pct,
                "term": "ltcg" if long_term else "stcg",
            }
        )
    return lots


def _headroom(args: dict, months_elapsed: int) -> dict:
    status = _single_or_mfj_status(args)
    annual_income = float(args.get("annual_income", 0.0))
    standard_deduction = float(args.get("standard_deduction", 0.0))
    ytd_gross = annual_income * months_elapsed / 12.0
    ordinary_taxable = max(0.0, ytd_gross - standard_deduction)
    zero_limit = _status_value(args, "ltcg_bracket0_limit", status, 1.0)
    room = max(0.0, zero_limit - ordinary_taxable)
    return {
        "status": status,
        "annual_income": annual_income,
        "ytd_gross_income": ytd_gross,
        "standard_deduction": standard_deduction,
        "ordinary_taxable": ordinary_taxable,
        "zero_limit": zero_limit,
        "room": room,
    }


def _gain_tax(args: dict, gain: float, ordinary_taxable: float, term: str) -> float:
    if gain <= 0:
        return 0.0
    if term == "stcg":
        taxable = max(0.0, ordinary_taxable)
        brackets = args.get("federal_brackets") or args.get(
            "federal_brackets_mfj", []
        )
        from savings import marginal_ordinary_rate
        rate = marginal_ordinary_rate(taxable, brackets)
        state = _state_capital_gains_rate(args)
        return gain * (rate + state)
    return long_term_capital_gains_tax(args, gain, ordinary_taxable, 1.0)


def _select_gain_lots(lots: list[dict], short_term: bool) -> list[dict]:
    gains = [lot for lot in lots if lot["gain"] > 1e-9]
    ltcg = sorted(
        (lot for lot in gains if lot["term"] == "ltcg"),
        key=lambda lot: lot["gain"],
        reverse=True,
    )
    if short_term:
        stcg = sorted(
            (lot for lot in gains if lot["term"] == "stcg"),
            key=lambda lot: lot["gain"],
            reverse=True,
        )
        return ltcg + stcg
    return ltcg


def _recommend_sells(
    args: dict,
    lots: list[dict],
    room: float,
    ordinary_taxable: float,
) -> tuple[list[dict], float]:
    recommended = []
    remaining = room
    for lot in lots:
        if remaining <= 1e-9:
            break
        take = min(lot["gain"], remaining)
        baseline = _gain_tax(args, 0.0, ordinary_taxable, lot["term"])
        tax = _gain_tax(args, take, ordinary_taxable, lot["term"]) - baseline
        recommended.append(
            {
                **lot,
                "recommended_harvest": take,
                "tax": tax,
            }
        )
        remaining -= take
    return recommended, max(0.0, remaining)


def _dedupe_symbols(lots: list[dict]) -> list[dict]:
    """Pick the term-classified lot most suitable for loss listing per symbol."""
    seen = {}
    for lot in lots:
        symbol = lot["symbol"]
        if symbol not in seen or lot["gain"] < seen[symbol]["gain"]:
            seen[symbol] = lot
    return list(seen.values())


def _loss_lots(lots: list[dict]) -> list[dict]:
    losses = [lot for lot in lots if lot["gain"] < -1e-9]
    losses = _dedupe_symbols(losses)
    return sorted(losses, key=lambda lot: lot["gain"])


def _print_headroom(head: dict) -> None:
    print("=== Tax Headroom ===")
    rows = [
        ["Filing status", head["status"].upper()],
        ["YTD gross income", f"${head['ytd_gross_income']:,.0f}"],
        ["Standard deduction", f"${head['standard_deduction']:,.0f}"],
        ["Ordinary taxable income", f"${head['ordinary_taxable']:,.0f}"],
        ["0% LTCG bracket limit", f"${head['zero_limit']:,.0f}"],
        ["0% room remaining", f"${head['room']:,.0f}"],
    ]
    print(tabulate(rows, tablefmt="simple"))
    print()


def _print_gains(recommended: list[dict], room_remaining: float) -> None:
    print("=== Gain Harvest Recommendations (fill 0% bracket) ===")
    if not recommended:
        print("No gain lots available to harvest.")
        print()
        return
    rows = [
        [
            lot["symbol"],
            lot["date"].isoformat() if lot["date"] else "n/a",
            lot["term"].upper(),
            f"${lot['cost_basis']:,.0f}",
            f"${lot['market_value']:,.0f}",
            f"${lot['gain']:,.0f}",
            f"${lot['recommended_harvest']:,.0f}",
            f"${lot['tax']:,.0f}",
        ]
        for lot in recommended
    ]
    print(
        tabulate(
            rows,
            headers=["Symbol", "Lot date", "Holding", "Basis", "Value", "Gain", "Suggested", "Tax"],
            tablefmt="simple",
        )
    )
    total_harvest = sum(lot["recommended_harvest"] for lot in recommended)
    total_tax = sum(lot["tax"] for lot in recommended)
    print(
        f"Total harvest: {total_harvest:,.0f} | Tax: {total_tax:,.0f} | "
        f"Room remaining: {room_remaining:,.0f}"
    )
    print()


def _print_losses(losses: list[dict]) -> None:
    print("=== Loss Harvest Opportunities ===")
    if not losses:
        print("No loss lots found.")
        print()
        return
    rows = [
        [
            lot["symbol"],
            lot["date"].isoformat() if lot["date"] else "n/a",
            f"${lot['cost_basis']:,.0f}",
            f"${lot['market_value']:,.0f}",
            f"${lot['gain']:,.0f}",
            f"${lot['gain_pct']:.1f}%",
            swap_partner(lot["symbol"]) or "no partner",
        ]
        for lot in losses
    ]
    print(
        tabulate(
            rows,
            headers=["Symbol", "Lot date", "Basis", "Value", "Loss", "Loss %", "Swap with"],
            tablefmt="simple",
        )
    )
    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Recommend tax-lot gain and loss harvesting from brokerage CSVs"
    )
    parser.add_argument(
        "config", help="Path to savings.py TOML configuration file"
    )
    parser.add_argument("lots", nargs="+", help="Path(s) to brokerage CSV tax lot files")
    parser.add_argument(
        "--format",
        choices=["schwab", "fidelity", "vanguard", "auto"],
        default="auto",
        help="CSV format (default: auto-detect from headers)",
    )
    parser.add_argument(
        "--months",
        type=int,
        default=None,
        help="Calendar months elapsed for YTD income proration (default: current month)",
    )
    parser.add_argument(
        "--min-gain",
        type=float,
        default=0.0,
        help="Ignore gain lots below this dollar gain threshold",
    )
    parser.add_argument(
        "--min-loss",
        type=float,
        default=0.0,
        help="Ignore loss lots below this dollar loss magnitude",
    )
    parser.add_argument(
        "--short-term",
        action="store_true",
        help="Include short-term capital gain lots (appended after LTCG)",
    )
    args = parser.parse_args()

    if args.months is None:
        months_elapsed = _dt.date.today().month
    else:
        months_elapsed = args.months

    config = load_toml_config(args.config)
    today = _dt.date.today()

    all_lots = []
    for path in args.lots:
        with open(path, newline="", encoding="utf-8", errors="replace") as fh:
            rows = list(csv.reader(fh))
            if not rows:
                raise ValueError(f"empty CSV: {path}")
            if args.format == "auto":
                fmt = None
                header_index = None
                for index, row in enumerate(rows):
                    if row and any(cell.strip() for cell in row):
                        detected = _find_header(row)
                        if detected is not None:
                            fmt = detected
                            header_index = index
                            break
                if fmt is None:
                    raise ValueError(
                        f"unable to detect CSV format in {path} "
                        "(expected Schwab, Fidelity, or Vanguard)"
                    )
            else:
                fmt = args.format
                header_index = None
                for index, row in enumerate(rows):
                    if row and any(cell.strip() for cell in row):
                        lowered = [c.strip().lower() for c in row]
                        header_index = index
                        break
                if header_index is None:
                    raise ValueError(f"no header row found in {path}")
            header = [cell.strip() for cell in rows[header_index]]
            if not header or any(not cell for cell in header):
                raise ValueError(f"could not parse header row in {path}")
            data = [
                {header[col]: (rows[row][col] if col < len(rows[row]) else "")
                 for col in range(len(header))}
                for row in range(header_index + 1, len(rows))
            ]
            all_lots.extend(_parse_lots(data, fmt, today))

    head = _headroom(config, months_elapsed)

    gain_lots = _select_gain_lots(all_lots, args.short_term)
    gain_lots = [lot for lot in gain_lots if lot["gain"] >= args.min_gain]
    recommended, room_remaining = _recommend_sells(
        config, gain_lots, head["room"], head["ordinary_taxable"]
    )

    losses = [
        lot for lot in _loss_lots(all_lots) if abs(lot["gain"]) >= abs(args.min_loss)
    ]

    _print_headroom(head)
    _print_gains(recommended, room_remaining)
    _print_losses(losses)


if __name__ == "__main__":
    main()
