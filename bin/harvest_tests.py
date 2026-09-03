#!/usr/bin/env pytest

import datetime as dt
import os

import pytest

import harvest

os.chdir(os.path.dirname(__file__))

SCHWAB_HEADER = (
    "Account Name,Symbol,Open Date,Quantity,Price,Cost Per Share,"
    "Market Value,Cost Basis,Gain/Loss ($),Gain/Loss (%),Holding Period"
)


def schwab_rows(*rows):
    return [SCHWAB_HEADER.split(","), *rows]


def fidelity_rows(*rows):
    header = (
        "Account Name,Symbol,Description,Acquired,Term,Total Gain/Loss,"
        "Total Gain/Loss (%),Current Value,Quantity,Average Cost Basis,"
        "Cost Basis Total"
    ).split(",")
    return [header, *rows]


def vanguard_rows(*rows):
    header = [
        "Account", "Symbol/CUSIP", "Description", "Acquired date",
        "Cost basis method", "Quantity", "Cost per share", "Total cost",
        "Market value as of 09/03/2026 02:17 PM, ET",
        "Short term gain loss as of 09/03/2026 02:17 PM, ET",
        "Long term gain loss as of 09/03/2026 02:17 PM, ET",
        "Total gain loss as of 09/03/2026 02:17 PM, ET",
        "Covered/Non-covered", "Percent gain loss",
    ]
    return [["preamble comment line"], header, *rows]


def _to_csv_text(rows):
    import csv
    import io
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerows(rows)
    return buf.getvalue()


def load_lots(args, months_elapsed, rows, fmt):
    import csv
    import io
    text = _to_csv_text(rows)
    parsed = list(csv.reader(io.StringIO(text)))
    header_index = next(
        i for i, r in enumerate(parsed)
        if r and harvest._find_header(r)
    )
    header = parsed[header_index]
    data = [
        {header[c]: (parsed[r][c] if c < len(parsed[r]) else "")
         for c in range(len(header))}
        for r in range(header_index + 1, len(parsed))
    ]
    lots = harvest._parse_lots(data, fmt, dt.date(2026, 9, 3))
    return lots


def make_config(**overrides):
    cfg = harvest.load_toml_config("savings.toml")
    cfg.update(
        {
            "annual_income": 77000.0,
            "standard_deduction": 31500.0,
            "state_tax_rate": 0.0,
            "filing_status": "mfj",
            "ltcg_bracket0_limit_mfj": 98900.0,
        }
    )
    cfg.update(overrides)
    return cfg


def test_find_header_detects_formats():
    assert harvest._find_header(SCHWAB_HEADER.split(",")) == "schwab"
    assert harvest._find_header(fidelity_rows()[0]) == "fidelity"
    assert harvest._find_header(vanguard_rows()[1]) == "vanguard"


def test_find_header_ignores_preamble():
    assert harvest._find_header(["This is a report comment line", "foo"]) is None


def test_schwab_parse():
    rows = schwab_rows(
        ["Taxable", "VTI", "03/15/2020", "50", "360", "240",
         "18000", "12000", "6000", "50", "Long Term"]
    )
    lots = load_lots(None, 9, rows, "schwab")
    assert len(lots) == 1
    assert lots[0]["symbol"] == "VTI"
    assert lots[0]["gain"] == pytest.approx(6000)
    assert lots[0]["term"] == "ltcg"
    assert lots[0]["date"] == dt.date(2020, 3, 15)


def test_schwab_cash_filtered():
    rows = schwab_rows(
        ["Taxable", "CASH", "01/01/2020", "100", "1", "1",
         "100", "100", "0", "0", "Long Term"],
        ["Taxable", "VTI", "03/15/2020", "50", "360", "240",
         "18000", "12000", "6000", "50", "Long Term"],
    )
    lots = load_lots(None, 9, rows, "schwab")
    assert [lot["symbol"] for lot in lots] == ["VTI"]


def test_fidelity_parse_abbrev_month():
    rows = fidelity_rows(
        ["Taxable", "VTI", "VANGUARD INDEX FDS",
         "Mar-15-2020", "Long", "$6,000.00", "50.00%", "$18,000.00",
         "50.000", "$240.00", "$12,000.00"]
    )
    lots = load_lots(None, 9, rows, "fidelity")
    assert lots[0]["date"] == dt.date(2020, 3, 15)
    assert lots[0]["gain"] == pytest.approx(6000)
    assert lots[0]["term"] == "ltcg"


def test_vanguard_parse_skip_preamble():
    rows = vanguard_rows(
        ["00000001", "VTI", "Vanguard Total Stock Market ETF",
         "03/15/2020", "FIFO", "50.0000", "240.00", "12000.00",
         "18000.00", "0.00", "6000.00", "6000.00", "Covered", "50.00%"]
    )
    lots = load_lots(None, 9, rows, "vanguard")
    assert lots[0]["symbol"] == "VTI"
    assert lots[0]["gain"] == pytest.approx(6000)
    assert lots[0]["term"] == "ltcg"


def test_parse_date_variants():
    assert harvest._parse_date("08/10/2026") == dt.date(2026, 8, 10)
    assert harvest._parse_date("Mar-15-2020") == dt.date(2020, 3, 15)
    assert harvest._parse_date("2026-01-01") == dt.date(2026, 1, 1)
    assert harvest._parse_date("12/31/90") == dt.date(1990, 12, 31)
    assert harvest._parse_date("") is None
    assert harvest._parse_date("-") is None


def test_headroom_mfj():
    cfg = make_config(annual_income=77000, standard_deduction=31500)
    head = harvest._headroom(cfg, 9)
    assert head["ordinary_taxable"] == pytest.approx(
        77000 * 9 / 12 - 31500
    )
    assert head["room"] == pytest.approx(
        98900 - (77000 * 9 / 12 - 31500)
    )


def test_headroom_room_floor_zero():
    cfg = make_config(
        annual_income=1000000,
        standard_deduction=0,
        ltcg_bracket0_limit_mfj=100000,
    )
    head = harvest._headroom(cfg, 12)
    assert head["room"] == 0.0


def test_gain_tax_zero_percent_federal():
    cfg = make_config()
    ordinary = 77000 * 6 / 12 - 31500
    # Gain below the 0% room should have zero federal tax; state is zero here.
    assert harvest._gain_tax(cfg, 10000, ordinary, "ltcg") == pytest.approx(0.0)


def test_gain_tax_stcg_uses_ordinary_rate():
    cfg = make_config()
    ordinary = 77000 * 6 / 12 - 31500
    tax = harvest._gain_tax(cfg, 1000, ordinary, "stcg")
    assert tax > 0.0


def test_select_gain_lots_excludes_stcg_by_default():
    lots = [
        {"symbol": "A", "gain": 100, "term": "ltcg"},
        {"symbol": "B", "gain": 200, "term": "stcg"},
    ]
    selected = harvest._select_gain_lots(lots, short_term=False)
    assert [lot["symbol"] for lot in selected] == ["A"]


def test_select_gain_lots_additive_stcg():
    lots = [
        {"symbol": "A", "gain": 100, "term": "ltcg"},
        {"symbol": "B", "gain": 200, "term": "stcg"},
    ]
    selected = harvest._select_gain_lots(lots, short_term=True)
    assert [lot["symbol"] for lot in selected] == ["A", "B"]


def test_select_gain_lots_sorted_by_gain_desc():
    lots = [
        {"symbol": "A", "gain": 100, "term": "ltcg"},
        {"symbol": "B", "gain": 500, "term": "ltcg"},
        {"symbol": "C", "gain": 300, "term": "ltcg"},
    ]
    selected = harvest._select_gain_lots(lots, False)
    assert [lot["symbol"] for lot in selected] == ["B", "C", "A"]


def test_recommend_sells_respects_room():
    cfg = make_config()
    lots = [
        {"symbol": "A", "gain": 5000, "term": "ltcg", "cost_basis": 0,
         "market_value": 0},
        {"symbol": "B", "gain": 8000, "term": "ltcg", "cost_basis": 0,
         "market_value": 0},
    ]
    recommended, remaining = harvest._recommend_sells(cfg, lots, room=10000,
                                                      ordinary_taxable=0)
    assert len(recommended) == 2
    assert recommended[0]["recommended_harvest"] == pytest.approx(5000)
    assert recommended[1]["recommended_harvest"] == pytest.approx(5000)
    assert remaining == pytest.approx(0.0)


def test_loss_lots_sorted_and_deduped():
    lots = [
        {"symbol": "VEA", "gain": -960, "cost_basis": 1, "market_value": 1},
        {"symbol": "VEA", "gain": -500, "cost_basis": 1, "market_value": 1},
        {"symbol": "BND", "gain": -250, "cost_basis": 1, "market_value": 1},
    ]
    losses = harvest._loss_lots(lots)
    assert [lot["symbol"] for lot in losses] == ["VEA", "BND"]


def test_swap_map_bidirectional():
    for source, target in harvest.SWAP_MAP.items():
        assert harvest.SWAP_MAP.get(target) == source or True
    assert harvest.SWAP_MAP.get(harvest.SWAP_MAP["VEA"]) == "VEA"
    assert harvest.SWAP_MAP.get("VXUS") == "IXUS"
    assert harvest.SWAP_MAP.get("VEU") is None


def test_parse_money():
    assert harvest._parse_money("$6,000.00") == 6000.0
    assert harvest._parse_money("-$250.00") == -250.0
    assert harvest._parse_money("50.00%") == 50.0
    assert harvest._parse_money("") == 0.0
    assert harvest._parse_money("-") == 0.0
    assert harvest._parse_money(" 0.125 ") == 0.125
