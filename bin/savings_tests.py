#!/usr/bin/env pytest

import os

import pytest

import savings

os.chdir(os.path.dirname(__file__))


def make_args(**overrides):
    args = savings.load_toml_config("savings.toml")
    args.update(
        {
            "annual_savings": 1000.0,
            "annual_income": 100000.0,
            "projection_years": 1,
            "emergency_fund_target": 0.0,
            "stock_return": 0.0,
            "stock_volatility": 0.0,
            "inflation_rate": 0.0,
            "inflation_volatility": 0.0,
            "brokerage_dividend_yield": 0.0,
            "state_tax_rate": 0.0,
            "ltcg_0pct_limit": 1000000.0,
            "retirement_taxable_income": 0.0,
        }
    )
    args.update(overrides)
    return args


def test_ltcg_tax_stacks_after_ordinary_income():
    args = make_args(
        ltcg_0pct_limit=100.0,
        ltcg_15pct_limit=200.0,
        ltcg_15pct_rate=0.15,
        ltcg_20pct_rate=0.20,
    )
    assert savings.long_term_capital_gains_tax(args, 100.0, 60.0) == pytest.approx(9.0)


def test_pretax_contribution_uses_current_tax_savings():
    args = make_args(
        annual_income=100000.0,
        standard_deduction=0.0,
        state_standard_deduction=0.0,
        federal_brackets=[[1000000.0, 0.20]],
    )
    assert savings.pretax_cash_cost(args, 1000.0) == pytest.approx(800.0)
    assert savings.gross_contribution_for_cash(args, 800.0, 10000.0) == pytest.approx(
        1000.0, abs=1e-8
    )


def test_allocation_honors_shared_401k_limit():
    args = make_args(
        annual_savings=30000.0,
        employee_401k_limit=10000.0,
        solo_401k_limit=10000.0,
        roth_401k_limit=10000.0,
    )
    balances = {account: 0.0 for account in savings.ACCOUNT_NAMES}
    allocated = savings.allocate_savings(
        args,
        ("solo_401k", "roth_401k", "roth_ira", "emergency_fund", "brokerage"),
        balances,
    )
    assert allocated["solo_401k"] == pytest.approx(10000.0)
    assert allocated["roth_401k"] == pytest.approx(0.0)
    assert allocated["roth_ira"] == pytest.approx(7000.0)
    assert allocated["_cash_remaining"] == pytest.approx(0.0)


def test_roth_beats_taxable_when_capital_gains_are_taxed():
    args = make_args(
        ltcg_0pct_limit=0.0,
        ltcg_15pct_limit=0.0,
        ltcg_15pct_rate=0.15,
    )
    roth = savings.simulate_strategy(
        args,
        ("roth_ira", "emergency_fund", "solo_401k", "roth_401k", "brokerage"),
        stock_returns=[0.10],
        inflation_rates=[0.0],
    )
    brokerage = savings.simulate_strategy(
        args,
        ("brokerage", "emergency_fund", "roth_ira", "solo_401k", "roth_401k"),
        stock_returns=[0.10],
        inflation_rates=[0.0],
    )
    assert roth["final_value"] > brokerage["final_value"]


def test_monte_carlo_is_reproducible():
    args = make_args(projection_years=2, annual_savings=5000.0)
    first, raw_first = savings.run_monte_carlo(args, simulations=3, seed=7)
    second, raw_second = savings.run_monte_carlo(args, simulations=3, seed=7)
    assert [row["median"] for row in first] == [row["median"] for row in second]
    assert raw_first == raw_second
