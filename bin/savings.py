#!/usr/bin/python3
"""Compare where recurring savings should be invested.

The simulator compares priority orders for five destinations:
emergency fund, Roth IRA, solo 401(k), Roth 401(k), and taxable brokerage.
Each order receives the same annual after-tax savings budget.  The budget is
filled in priority order, subject to account limits; any remainder goes to the
next account.  Traditional solo 401(k) contributions are grossed up for their
current-year tax deduction, while terminal values are reported after estimated
withdrawal taxes.

This is an educational planning model, not tax advice.  Tax brackets,
contribution limits, and account rules are configurable in TOML. Employer
contributions, employer matches, RMDs, and early-withdrawal penalties are not
modeled.
"""

import argparse
import itertools
import math
import random
import sys
from concurrent.futures import ProcessPoolExecutor
from statistics import mean

from tabulate import tabulate

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        print("Error: TOML support requires Python 3.11+ or 'tomli' package. Install with: pip install tomli")
        sys.exit(1)


ACCOUNT_NAMES = (
    "emergency_fund",
    "roth_ira",
    "solo_401k",
    "roth_401k",
    "brokerage",
)
ACCOUNT_LABELS = {
    "emergency_fund": "Emergency fund",
    "roth_ira": "Roth IRA",
    "solo_401k": "Solo 401k",
    "roth_401k": "Roth 401k",
    "brokerage": "Brokerage",
}

FEDERAL_BRACKETS_MFJ = [
    (24800, 0.10),
    (100800, 0.12),
    (211400, 0.22),
    (403550, 0.24),
    (512450, 0.32),
    (768700, 0.35),
]
FEDERAL_BRACKETS_SINGLE = [
    (12400, 0.10),
    (50400, 0.12),
    (105700, 0.22),
    (201775, 0.24),
    (256225, 0.32),
    (384350, 0.35),
]


def _normalize_brackets(value) -> list[tuple[float, float]]:
    brackets = []
    for item in value:
        if isinstance(item, dict):
            limit = item.get("up_to", item.get("limit"))
            rate = item["rate"]
        else:
            limit, rate = item
        if limit is None or str(limit).lower() in {"inf", "infinity"}:
            limit = float("inf")
        brackets.append((float(limit), float(rate)))
    if not brackets or any(rate < 0 or rate >= 1 for _, rate in brackets):
        raise ValueError("federal tax brackets must contain non-negative rates below 100%")
    return sorted(brackets)


def ordinary_income_tax(taxable_income: float, brackets: list[tuple[float, float]]) -> float:
    """Return tax on ordinary taxable income using progressive brackets."""
    remaining = max(0.0, taxable_income)
    lower = 0.0
    tax = 0.0
    last_rate = brackets[-1][1]
    for upper, rate in brackets:
        if remaining <= lower:
            break
        amount = min(remaining, upper) - lower
        tax += max(0.0, amount) * rate
        lower = upper
        last_rate = rate
    if remaining > lower:
        tax += (remaining - lower) * last_rate
    return tax


def marginal_ordinary_rate(taxable_income: float, brackets: list[tuple[float, float]]) -> float:
    income = max(0.0, taxable_income)
    for upper, rate in brackets:
        if income <= upper:
            return rate
    return brackets[-1][1]


def _status_value(args: dict, name: str, status: str) -> float:
    if name in args:
        return float(args[name])
    return float(args[f"{name}_{status}"])


def federal_brackets(args: dict) -> list[tuple[float, float]]:
    configured = args.get("federal_brackets")
    if configured is not None:
        return _normalize_brackets(configured)
    status = str(args.get("filing_status", "mfj")).lower()
    return _normalize_brackets(
        args.get(
            "federal_brackets_single" if status in {"single", "s"} else "federal_brackets_mfj",
            FEDERAL_BRACKETS_SINGLE if status in {"single", "s"} else FEDERAL_BRACKETS_MFJ,
        )
    )


def _state_tax(args: dict, gross_income: float, pretax_contribution: float = 0.0) -> float:
    taxable = max(
        0.0,
        gross_income
        - pretax_contribution
        - float(args.get("state_standard_deduction", 0.0)),
    )
    return taxable * float(args.get("state_tax_rate", 0.0))


def current_taxable_income(args: dict, pretax_contribution: float = 0.0) -> float:
    return max(
        0.0,
        float(args["annual_income"])
        - float(args.get("standard_deduction", 0.0))
        - pretax_contribution,
    )


def current_income_tax(args: dict, pretax_contribution: float = 0.0) -> float:
    taxable = current_taxable_income(args, pretax_contribution)
    federal = ordinary_income_tax(taxable, federal_brackets(args))
    return federal + _state_tax(args, args["annual_income"], pretax_contribution)


def long_term_capital_gains_tax(
    args: dict, gain: float, ordinary_taxable_income: float = 0.0
) -> float:
    """Return federal and state tax on qualified dividends or LTCG.

    The federal calculation stacks gains above ordinary taxable income, so
    ordinary income consumes the 0% capital-gains band before gains do.
    """
    gain = max(0.0, gain)
    ordinary = max(0.0, ordinary_taxable_income)
    status = "single" if str(args.get("filing_status", "mfj")).lower() in {"single", "s"} else "mfj"
    zero_limit = _status_value(args, "ltcg_0pct_limit", status)
    fifteen_limit = _status_value(args, "ltcg_15pct_limit", status)
    zero_amount = min(gain, max(0.0, zero_limit - ordinary))
    remaining = gain - zero_amount
    fifteen_room = max(0.0, fifteen_limit - max(ordinary, zero_limit))
    fifteen_amount = min(remaining, fifteen_room)
    twenty_amount = remaining - fifteen_amount
    federal = fifteen_amount * float(args["ltcg_15pct_rate"]) + twenty_amount * float(
        args["ltcg_20pct_rate"]
    )
    state = gain * float(args.get("state_tax_rate", 0.0))
    return federal + state


def pretax_cash_cost(args: dict, contribution: float, other_pretax: float = 0.0) -> float:
    """Cash cost of a traditional contribution after its current tax savings."""
    contribution = max(0.0, contribution)
    before = current_income_tax(args, other_pretax)
    after = current_income_tax(args, other_pretax + contribution)
    return contribution - max(0.0, before - after)


def gross_contribution_for_cash(
    args: dict,
    cash: float,
    maximum: float,
    other_pretax: float = 0.0,
) -> float:
    """Solve for the largest traditional contribution affordable with cash."""
    cash = max(0.0, cash)
    maximum = max(0.0, maximum)
    if cash == 0.0 or maximum == 0.0:
        return 0.0
    if pretax_cash_cost(args, maximum, other_pretax) <= cash:
        return maximum
    low, high = 0.0, maximum
    for _ in range(48):
        middle = (low + high) / 2.0
        if pretax_cash_cost(args, middle, other_pretax) <= cash:
            low = middle
        else:
            high = middle
    return low


def roth_ira_limit(args: dict) -> float:
    if not args.get("roth_ira_eligible", True):
        return 0.0
    income = float(args["annual_income"])
    status = "single" if str(args.get("filing_status", "mfj")).lower() in {"single", "s"} else "mfj"
    start = _status_value(args, "roth_ira_phaseout_start", status)
    end = _status_value(args, "roth_ira_phaseout_end", status)
    limit = float(args["roth_ira_limit"])
    if income <= start:
        return limit
    if income >= end:
        return 0.0
    return limit * (end - income) / (end - start)


def allocate_savings(
    args: dict, order: tuple[str, ...], balances: dict[str, float], year: int = 0
) -> dict[str, float]:
    """Allocate one year's after-tax cash budget according to an account order."""
    if set(order) != set(ACCOUNT_NAMES) or len(order) != len(ACCOUNT_NAMES):
        raise ValueError(f"order must contain each account exactly once: {ACCOUNT_NAMES}")

    cash = float(args["annual_savings"]) * (
        1.0 + float(args.get("savings_growth_rate", 0.0))
    ) ** year
    contributions = {name: 0.0 for name in ACCOUNT_NAMES}
    annual_401k = 0.0
    annual_roth_ira = 0.0
    annual_solo = 0.0

    for account in order:
        if cash <= 1e-9:
            break
        if account == "emergency_fund":
            room = max(0.0, float(args["emergency_fund_target"]) - balances["emergency_fund"])
            amount = min(cash, room)
            contributions[account] = amount
            cash -= amount
        elif account == "roth_ira":
            amount = min(cash, max(0.0, roth_ira_limit(args) - annual_roth_ira))
            contributions[account] = amount
            annual_roth_ira += amount
            cash -= amount
        elif account == "solo_401k":
            employee_room = max(0.0, float(args["employee_401k_limit"]) - annual_401k)
            earned_income_room = max(0.0, float(args["annual_income"]))
            maximum = min(
                employee_room,
                max(0.0, float(args["solo_401k_limit"]) - annual_solo),
                earned_income_room,
            )
            amount = gross_contribution_for_cash(args, cash, maximum)
            cost = pretax_cash_cost(args, amount)
            contributions[account] = amount
            annual_solo += amount
            annual_401k += amount
            cash -= cost
        elif account == "roth_401k":
            employee_room = max(0.0, float(args["employee_401k_limit"]) - annual_401k)
            amount = min(
                cash,
                employee_room,
                max(0.0, float(args["roth_401k_limit"])),
            )
            contributions[account] = amount
            annual_401k += amount
            cash -= amount
        else:
            contributions[account] = cash
            cash = 0.0

    contributions["_cash_remaining"] = max(0.0, cash)
    return contributions


def _sample_return(rng: random.Random, mean_return: float, volatility: float) -> float:
    if volatility <= 0.0:
        return mean_return
    if mean_return <= -1.0:
        raise ValueError("mean returns must be greater than -100%")
    gross = math.exp(
        math.log(1.0 + mean_return) - 0.5 * volatility**2 + rng.gauss(0.0, volatility)
    )
    return max(-0.95, gross - 1.0)


def make_market_paths(args: dict, rng: random.Random) -> tuple[list[float], list[float]]:
    years = int(args["projection_years"])
    stock = [
        _sample_return(rng, float(args["stock_return"]), float(args["stock_volatility"]))
        for _ in range(years)
    ]
    inflation = [
        _sample_return(rng, float(args["inflation_rate"]), float(args["inflation_volatility"]))
        for _ in range(years)
    ]
    return stock, inflation


def _starting_balances(args: dict) -> tuple[dict[str, float], float]:
    balances = {
        account: float(args.get(f"starting_{account}", 0.0)) for account in ACCOUNT_NAMES
    }
    basis = float(args.get("starting_brokerage_basis", balances["brokerage"]))
    return balances, basis


def _terminal_after_tax_value(args: dict, balances: dict[str, float], basis: float) -> dict:
    retirement_income = float(args.get("retirement_taxable_income", 0.0))
    brackets = federal_brackets(args)
    brokerage_gain = max(0.0, balances["brokerage"] - basis)
    brokerage_tax = long_term_capital_gains_tax(args, brokerage_gain, retirement_income)
    brokerage = max(0.0, balances["brokerage"] - brokerage_tax)

    solo_tax = (
        ordinary_income_tax(retirement_income + balances["solo_401k"], brackets)
        - ordinary_income_tax(retirement_income, brackets)
        + balances["solo_401k"] * float(args.get("state_tax_rate", 0.0))
    )
    solo = max(0.0, balances["solo_401k"] - solo_tax)
    after_tax = (
        balances["emergency_fund"]
        + balances["roth_ira"]
        + balances["roth_401k"]
        + brokerage
        + solo
    )
    return {
        "final_value": after_tax,
        "final_brokerage": brokerage,
        "final_solo_401k": solo,
        "terminal_tax": brokerage_tax + solo_tax,
    }


def simulate_strategy(
    args: dict,
    order: tuple[str, ...],
    stock_returns: list[float] | None = None,
    inflation_rates: list[float] | None = None,
    rng: random.Random | None = None,
) -> dict:
    """Simulate one priority order and return nominal and real terminal values."""
    years = int(args["projection_years"])
    if stock_returns is None or inflation_rates is None:
        if rng is None:
            rng = random.Random()
        stock_returns, inflation_rates = make_market_paths(args, rng)
    if len(stock_returns) != years or len(inflation_rates) != years:
        raise ValueError("market paths must contain projection_years values")

    balances, basis = _starting_balances(args)
    annual_contributions = []
    inflation_factor = 1.0
    brackets = federal_brackets(args)

    for year, (stock_return, inflation_rate) in enumerate(zip(stock_returns, inflation_rates)):
        contributions = allocate_savings(args, order, balances, year)
        annual_contributions.append(
            {name: contributions[name] for name in ACCOUNT_NAMES}
        )
        solo_contribution = contributions["solo_401k"]
        taxable_income = current_taxable_income(args, solo_contribution)

        for account in ACCOUNT_NAMES:
            contribution = contributions[account]
            before_return = balances[account] + contribution
            if account == "emergency_fund":
                interest = before_return * float(args["emergency_fund_return"])
                tax_rate = marginal_ordinary_rate(taxable_income, brackets) + float(
                    args.get("state_tax_rate", 0.0)
                )
                balances[account] = max(0.0, before_return + interest * (1.0 - tax_rate))
            elif account == "brokerage":
                dividend = max(0.0, before_return * float(args["brokerage_dividend_yield"]))
                dividend_tax = long_term_capital_gains_tax(
                    args, dividend, taxable_income
                )
                balances[account] = max(
                    0.0, before_return * (1.0 + stock_return) - dividend_tax
                )
                basis += contribution + max(0.0, dividend - dividend_tax)
            else:
                balances[account] = max(0.0, before_return * (1.0 + stock_return))
        inflation_factor *= max(0.01, 1.0 + inflation_rate)

    terminal = _terminal_after_tax_value(args, balances, basis)
    terminal["strategy"] = " -> ".join(ACCOUNT_LABELS[name] for name in order)
    terminal["order"] = order
    terminal["balances"] = balances
    terminal["basis"] = basis
    terminal["annual_contributions"] = annual_contributions
    terminal["real_value"] = terminal["final_value"] / inflation_factor
    return terminal


def _derive_seed(seed: int, simulation: int) -> int:
    return (seed + simulation * 1000003) & ((1 << 64) - 1)


def _run_trial(payload: tuple[dict, int, list[tuple[str, ...]]]) -> list[float]:
    args, seed, orders = payload
    stock, inflation = make_market_paths(args, random.Random(seed))
    return [
        simulate_strategy(
            args,
            order,
            stock_returns=stock,
            inflation_rates=inflation,
        )["real_value"]
        for order in orders
    ]


def _percentile(values: list[float], fraction: float) -> float:
    if not values:
        return 0.0
    index = int(fraction * (len(values) - 1))
    return sorted(values)[index]


def run_monte_carlo(
    args: dict,
    simulations: int | None = None,
    seed: int | None = None,
    workers: int = 1,
) -> tuple[list[dict], list[list[float]]]:
    simulations = int(
        simulations if simulations is not None else args["monte_carlo_simulations"]
    )
    seed = int(seed if seed is not None else args["monte_carlo_seed"])
    if simulations < 1:
        raise ValueError("simulations must be at least 1")
    orders = list(itertools.permutations(ACCOUNT_NAMES))
    payloads = ((args, _derive_seed(seed, index), orders) for index in range(simulations))

    if workers > 1:
        with ProcessPoolExecutor(max_workers=workers) as executor:
            trials = list(executor.map(_run_trial, payloads))
    else:
        trials = [_run_trial(payload) for payload in payloads]

    raw = [[trial[index] for trial in trials] for index in range(len(orders))]
    best_counts = [0] * len(orders)
    for trial in trials:
        best = max(trial)
        for index, value in enumerate(trial):
            if value == best:
                best_counts[index] += 1

    summaries = []
    for index, (order, values) in enumerate(zip(orders, raw)):
        summaries.append(
            {
                "strategy": " -> ".join(ACCOUNT_LABELS[name] for name in order),
                "order": order,
                "median": _percentile(values, 0.50),
                "p25": _percentile(values, 0.25),
                "p75": _percentile(values, 0.75),
                "mean": mean(values),
                "probability_best": best_counts[index] / simulations,
            }
        )
    summaries.sort(key=lambda row: row["median"], reverse=True)
    return summaries, raw


def load_toml_config(filepath: str) -> dict:
    with open(filepath, "rb") as file:
        data = tomllib.load(file)

    defaults = {
        "annual_savings": 40000.0,
        "annual_income": 100000.0,
        "filing_status": "mfj",
        "standard_deduction": 31500.0,
        "state_standard_deduction": 10400.0,
        "state_tax_rate": 0.0495,
        "projection_years": 30,
        "savings_growth_rate": 0.0,
        "emergency_fund_target": 30000.0,
        "emergency_fund_return": 0.03,
        "roth_ira_limit": 7000.0,
        "roth_ira_eligible": True,
        "roth_ira_phaseout_start_mfj": 242000.0,
        "roth_ira_phaseout_end_mfj": 252000.0,
        "roth_ira_phaseout_start_single": 153000.0,
        "roth_ira_phaseout_end_single": 168000.0,
        "employee_401k_limit": 23500.0,
        "solo_401k_limit": 23500.0,
        "roth_401k_limit": 23500.0,
        "stock_return": 0.07,
        "stock_volatility": 0.18,
        "inflation_rate": 0.03,
        "inflation_volatility": 0.015,
        "brokerage_dividend_yield": 0.02,
        "ltcg_0pct_limit_mfj": 98900.0,
        "ltcg_15pct_limit_mfj": 613700.0,
        "ltcg_0pct_limit_single": 49450.0,
        "ltcg_15pct_limit_single": 545500.0,
        "ltcg_15pct_rate": 0.15,
        "ltcg_20pct_rate": 0.20,
        "retirement_taxable_income": 0.0,
        "monte_carlo_simulations": 1000,
        "monte_carlo_seed": 42,
        "federal_brackets_mfj": FEDERAL_BRACKETS_MFJ,
        "federal_brackets_single": FEDERAL_BRACKETS_SINGLE,
    }
    defaults.update(data)
    defaults["projection_years"] = int(defaults["projection_years"])
    defaults["federal_brackets_mfj"] = _normalize_brackets(defaults["federal_brackets_mfj"])
    defaults["federal_brackets_single"] = _normalize_brackets(
        defaults["federal_brackets_single"]
    )
    if "federal_brackets" in defaults:
        defaults["federal_brackets"] = _normalize_brackets(defaults["federal_brackets"])
    if "starting_brokerage_basis" not in defaults:
        defaults["starting_brokerage_basis"] = defaults.get("starting_brokerage", 0.0)
    return defaults


def _currency(value: float) -> str:
    return f"${value:,.0f}"


def print_results(summaries: list[dict], top: int) -> None:
    rows = [
        [
            index + 1,
            summary["strategy"],
            _currency(summary["median"]),
            _currency(summary["p25"]),
            _currency(summary["p75"]),
            f"{summary['probability_best']:.1%}",
        ]
        for index, summary in enumerate(summaries[:top])
    ]
    print("After-tax real terminal value by priority order:")
    print(
        tabulate(
            rows,
            headers=["Rank", "Priority order", "Median", "P25", "P75", "P(best)"],
            tablefmt="simple",
        )
    )
    best = summaries[0]
    first_place = ACCOUNT_LABELS[best["order"][0]]
    print(
        f"\nRecommended priority order: {best['strategy']}"
        f"\nFirst destination for new savings: {first_place}"
    )
    print(
        "Traditional solo 401k contributions receive a current tax deduction; "
        "brokerage gains use the configured stacked LTCG brackets."
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare savings allocations across taxable and retirement accounts"
    )
    parser.add_argument("config", help="Path to TOML configuration file")
    parser.add_argument("--simulations", type=int, help="Number of Monte Carlo trials")
    parser.add_argument("--seed", type=int, help="Random seed")
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Parallel worker processes (default: 1)",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=10,
        help="Number of priority orders to print (default: 10)",
    )
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("--workers must be at least 1")
    if args.top < 1:
        parser.error("--top must be at least 1")

    config = load_toml_config(args.config)
    simulations = (
        args.simulations
        if args.simulations is not None
        else config["monte_carlo_simulations"]
    )
    summaries, _ = run_monte_carlo(
        config,
        simulations=simulations,
        seed=args.seed,
        workers=args.workers,
    )
    print_results(summaries, args.top)


if __name__ == "__main__":
    main()
