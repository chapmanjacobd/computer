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


def test_early_withdrawal_penalty_applies_to_traditional_balance():
    args = make_args(
        annual_savings=0.0,
        starting_brokerage=0.0,
        starting_solo_401k=1000.0,
        starting_age=30,
        federal_brackets=[[1000000.0, 0.0]],
        early_withdrawal_penalty_rate=0.10,
    )
    result = savings.simulate_strategy(
        args,
        ("solo_401k", "roth_ira", "roth_401k", "emergency_fund", "brokerage"),
        stock_returns=[0.0],
        inflation_rates=[0.0],
    )
    assert result["early_withdrawal_penalty"] == pytest.approx(100.0)
    assert result["final_value"] == pytest.approx(900.0)


def test_early_withdrawal_penalty_excludes_roth_basis():
    args = make_args(
        annual_savings=0.0,
        starting_brokerage=0.0,
        starting_roth_ira=1500.0,
        starting_roth_ira_basis=1000.0,
        starting_age=30,
        early_withdrawal_penalty_rate=0.10,
    )
    result = savings.simulate_strategy(
        args,
        ("roth_ira", "solo_401k", "roth_401k", "emergency_fund", "brokerage"),
        stock_returns=[0.0],
        inflation_rates=[0.0],
    )
    assert result["early_withdrawal_penalty"] == pytest.approx(50.0)
    assert result["final_value"] == pytest.approx(1450.0)


def test_roth_contributions_are_added_to_penalty_basis():
    args = make_args(
        annual_savings=1000.0,
        starting_brokerage=0.0,
        starting_age=30,
        early_withdrawal_penalty_rate=0.10,
    )
    result = savings.simulate_strategy(
        args,
        ("roth_ira", "solo_401k", "roth_401k", "emergency_fund", "brokerage"),
        stock_returns=[0.0],
        inflation_rates=[0.0],
    )
    assert result["early_withdrawal_penalty"] == pytest.approx(0.0)
    assert result["final_value"] == pytest.approx(1000.0)


def test_no_early_withdrawal_penalty_at_penalty_free_age():
    args = make_args(
        annual_savings=0.0,
        starting_brokerage=0.0,
        starting_solo_401k=1000.0,
        starting_age=59,
        projection_years=1,
        federal_brackets=[[1000000.0, 0.0]],
        early_withdrawal_penalty_rate=0.10,
    )
    result = savings.simulate_strategy(
        args,
        ("solo_401k", "roth_ira", "roth_401k", "emergency_fund", "brokerage"),
        stock_returns=[0.0],
        inflation_rates=[0.0],
    )
    assert result["terminal_withdrawal_age"] == pytest.approx(60.0)
    assert result["early_withdrawal_penalty"] == pytest.approx(0.0)
    assert result["final_value"] == pytest.approx(1000.0)


def test_monte_carlo_is_reproducible():
    args = make_args(projection_years=2, annual_savings=5000.0)
    first, raw_first = savings.run_monte_carlo(args, simulations=3, seed=7)
    second, raw_second = savings.run_monte_carlo(args, simulations=3, seed=7)
    assert [row["median"] for row in first] == [row["median"] for row in second]
    assert raw_first == raw_second


def test_loads_all_starting_balances(tmp_path):
    config = tmp_path / "balances.toml"
    config.write_text(
        """
        starting_emergency_fund = 1000
        starting_roth_ira = 2000
        starting_roth_ira_basis = 1500
        starting_solo_401k = 3000
        starting_roth_401k = 4000
        starting_roth_401k_basis = 3500
        starting_brokerage = 5000
        starting_brokerage_basis = 4500
        """
    )
    args = savings.load_toml_config(str(config))
    assert args["starting_emergency_fund"] == 1000
    assert args["starting_roth_ira"] == 2000
    assert args["starting_roth_ira_basis"] == 1500
    assert args["starting_solo_401k"] == 3000
    assert args["starting_roth_401k"] == 4000
    assert args["starting_roth_401k_basis"] == 3500
    assert args["starting_brokerage"] == 5000
    assert args["starting_brokerage_basis"] == 4500


def test_solo_401k_supports_employer_contributions_and_catchup():
    args = make_args(
        starting_age=50,
        annual_income=100000.0,
        annual_savings=30000.0,
        solo_401k_employer_rate=0.25,
        solo_401k_limit=70000.0,
        employee_401k_limit=23500.0,
        employee_401k_catchup=7500.0,
    )
    balances = {account: 0.0 for account in savings.ACCOUNT_NAMES}
    allocated = savings.allocate_savings(
        args,
        ("solo_401k", "roth_401k", "roth_ira", "emergency_fund", "brokerage"),
        balances,
    )
    assert allocated["_employer_contribution"] == pytest.approx(25000.0)
    assert allocated["solo_401k"] + allocated["_employer_contribution"] <= 77500.0 + 1e-9


def test_market_paths_are_monthly():
    args = make_args(projection_years=2)
    stock, inflation = savings.make_market_paths(args, savings.random.Random(3))
    assert len(stock) == 24
    assert len(inflation) == 24


def test_optimizer_returns_a_dollar_split():
    args = make_args(
        annual_savings=2000.0,
        projection_years=1,
        optimization_step=1000.0,
        optimization_passes=1,
    )
    allocation, summary = savings.optimize_allocation(
        args, simulations=2, seed=5, objective="median"
    )
    assert set(allocation) == set(savings.ACCOUNT_NAMES)
    assert sum(allocation.values()) == pytest.approx(1.0)
    assert summary["allocation"] == allocation


def test_limits_and_brackets_are_inflation_indexed_by_projection_year():
    args = make_args(
        annual_savings=10000.0,
        inflation_rate=0.10,
        projection_years=2,
        employee_401k_limit=0.0,
        solo_401k_limit=0.0,
        roth_401k_limit=0.0,
    )
    balances = {account: 0.0 for account in savings.ACCOUNT_NAMES}
    allocated = savings.allocate_savings(
        args,
        ("roth_ira", "emergency_fund", "solo_401k", "roth_401k", "brokerage"),
        balances,
        year=1,
    )
    assert allocated["roth_ira"] == pytest.approx(7700.0)
    assert allocated["brokerage"] == pytest.approx(2300.0)
    assert savings.federal_brackets(args, 1.10)[0][0] == pytest.approx(
        args["federal_brackets_mfj"][0][0] * 1.10
    )


def test_rmd_is_taxed_and_reinvested_after_tax():
    args = make_args(
        annual_savings=0.0,
        starting_age=73,
        starting_solo_401k=26500.0,
        starting_brokerage=0.0,
        starting_brokerage_basis=0.0,
        federal_brackets=[[1000000.0, 0.20]],
        standard_deduction=0.0,
        state_standard_deduction=0.0,
        rmd_reinvest_after_tax=True,
    )
    result = savings.simulate_strategy(
        args,
        ("solo_401k", "roth_ira", "roth_401k", "emergency_fund", "brokerage"),
        stock_returns=[0.0],
        inflation_rates=[0.0],
    )
    assert result["rmd_total"] == pytest.approx(1000.0)
    assert result["rmd_tax"] == pytest.approx(200.0)
    assert result["rmd_reinvested"] == pytest.approx(800.0)
    assert result["total_tax_cost"] == pytest.approx(5300.0)
    assert result["balances"]["solo_401k"] == pytest.approx(25500.0)
    assert result["balances"]["brokerage"] == pytest.approx(800.0)
    assert result["final_value"] == pytest.approx(21200.0)
