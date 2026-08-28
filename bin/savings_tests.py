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
            "discount_rate": 0.0,
            "brokerage_dividend_yield": 0.0,
            "state_tax_rate": 0.0,
            "ltcg_bracket0_limit": 1000000.0,
            "retirement_taxable_income": 0.0,
        }
    )
    overrides = dict(overrides)
    balance_keys = (
        "emergency_fund_balance",
        "hsa_balance",
        "roth_ira_balance",
        "roth_ira_basis",
        "solo_401k_balance",
        "roth_401k_balance",
        "roth_401k_basis",
        "brokerage_balance",
        "brokerage_basis",
    )
    for owner_cfg in args["owner"].values():
        for key in balance_keys:
            owner_cfg[key] = 0.0
    first_owner = savings._owners(args)[0]
    for key in balance_keys:
        if key in overrides:
            args["owner"][first_owner][key] = overrides.pop(key)
    args.update(overrides)
    return args


def account_names():
    return savings._account_names(make_args())


def expand_order(*bases):
    owners = savings._owners(make_args())
    return tuple(f"{base}_{owner}" for base in bases for owner in owners)


def total_for(contributions, base):
    return sum(
        amount
        for name, amount in contributions.items()
        if savings._base_account(name)[0] == base
    )


def test_ltcg_tax_stacks_after_ordinary_income():
    args = make_args(
        ltcg_bracket0_limit=100.0,
        ltcg_bracket1_limit=200.0,
        ltcg_bracket1_rate=0.15,
        ltcg_bracket2_rate=0.20,
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
    balances = {account: 0.0 for account in account_names()}
    allocated = savings.allocate_savings(
        args,
        expand_order("solo_401k", "roth_401k", "roth_ira", "emergency_fund", "brokerage", "hsa"),
        balances,
    )
    assert total_for(allocated, "solo_401k") == pytest.approx(20000.0)
    assert total_for(allocated, "roth_401k") == pytest.approx(0.0)
    assert total_for(allocated, "roth_ira") == pytest.approx(12400.0)
    assert allocated["_cash_remaining"] == pytest.approx(0.0)


def test_ineligible_hsa_is_skipped_and_cash_reaches_brokerage():
    args = make_args(annual_savings=5000.0, hsa_eligible=False)
    balances = {account: 0.0 for account in account_names()}
    allocated = savings.allocate_savings(
        args,
        expand_order("hsa", "brokerage", "roth_ira", "solo_401k", "roth_401k", "emergency_fund"),
        balances,
    )
    assert total_for(allocated, "hsa") == pytest.approx(0.0)
    assert total_for(allocated, "brokerage") == pytest.approx(5000.0)
    assert allocated["_cash_remaining"] == pytest.approx(0.0)


def test_roth_ira_phaseout_limits_contributions():
    args = make_args(
        filing_status="single",
        annual_income=150000.0,
        roth_ira_limit=7000.0,
        roth_ira_phaseout_start_single=100000.0,
        roth_ira_phaseout_end_single=200000.0,
    )
    assert savings.roth_ira_limit(args) == pytest.approx(3500.0)

    args["annual_income"] = 200000.0
    assert savings.roth_ira_limit(args) == pytest.approx(0.0)


def test_employer_contribution_cannot_exceed_total_401k_limit():
    args = make_args(
        annual_savings=100000.0,
        annual_income=100000.0,
        solo_401k_employer_rate=1.0,
        solo_401k_limit=30000.0,
        employee_401k_limit=10000.0,
        employee_401k_catchup=0.0,
    )
    balances = {account: 0.0 for account in account_names()}
    allocated = savings.allocate_savings(
        args,
        expand_order("solo_401k", "roth_401k", "roth_ira", "emergency_fund", "brokerage", "hsa"),
        balances,
    )
    assert allocated["_employer_contribution"] == pytest.approx(60000.0)
    for owner in ("jacob", "dorothy"):
        assert (
            allocated["_employer_contribution_by_owner"][owner]
            == pytest.approx(30000.0)
        )
        assert (
            allocated[f"solo_401k_{owner}"]
            + allocated["_employer_contribution_by_owner"][owner]
            <= 30000.0 + 1e-9
        )


def test_roth_beats_taxable_when_capital_gains_are_taxed():
    args = make_args(
        ltcg_bracket0_limit=0.0,
        ltcg_bracket1_limit=0.0,
        ltcg_bracket1_rate=0.15,
    )
    roth = savings.simulate_strategy(
        args,
        expand_order("roth_ira", "emergency_fund", "solo_401k", "roth_401k", "brokerage", "hsa"),
        stock_returns=[0.10],
        inflation_rates=[0.0],
    )
    brokerage = savings.simulate_strategy(
        args,
        expand_order("brokerage", "emergency_fund", "roth_ira", "solo_401k", "roth_401k", "hsa"),
        stock_returns=[0.10],
        inflation_rates=[0.0],
    )
    assert roth["final_value"] > brokerage["final_value"]


def test_early_withdrawal_penalty_applies_to_traditional_balance():
    args = make_args(
        annual_savings=0.0,
        brokerage_balance=0.0,
        solo_401k_balance=1000.0,
        starting_age=30,
        federal_brackets=[[1000000.0, 0.0]],
        early_withdrawal_penalty_rate=0.10,
    )
    result = savings.simulate_strategy(
        args,
        expand_order("solo_401k", "roth_ira", "roth_401k", "emergency_fund", "brokerage", "hsa"),
        stock_returns=[0.0],
        inflation_rates=[0.0],
    )
    assert result["early_withdrawal_penalty"] == pytest.approx(100.0)
    assert result["final_value"] == pytest.approx(900.0)


def test_early_withdrawal_penalty_excludes_roth_basis():
    args = make_args(
        annual_savings=0.0,
        brokerage_balance=0.0,
        roth_ira_balance=1500.0,
        roth_ira_basis=1000.0,
        starting_age=30,
        early_withdrawal_penalty_rate=0.10,
    )
    result = savings.simulate_strategy(
        args,
        expand_order("roth_ira", "solo_401k", "roth_401k", "emergency_fund", "brokerage", "hsa"),
        stock_returns=[0.0],
        inflation_rates=[0.0],
    )
    assert result["early_withdrawal_penalty"] == pytest.approx(50.0)
    assert result["final_value"] == pytest.approx(1450.0)


def test_npv_is_discounted_net_plan_value():
    args = make_args(
        annual_savings=0.0,
        brokerage_balance=1000.0,
        brokerage_basis=1000.0,
        discount_rate=0.10,
    )
    result = savings.simulate_strategy(
        args,
        savings._account_names(args),
        stock_returns=[0.0],
        inflation_rates=[0.0],
    )
    assert result["final_value"] == pytest.approx(1000.0)
    assert result["npv"] == pytest.approx(-1000.0 + 1000.0 / 1.10)


def test_npv_includes_present_value_of_contributions():
    args = make_args(
        annual_savings=1200.0,
        brokerage_balance=0.0,
        discount_rate=0.12,
    )
    result = savings.simulate_strategy(
        args,
        expand_order("brokerage", "roth_ira", "solo_401k", "roth_401k", "emergency_fund", "hsa"),
        stock_returns=[0.0],
        inflation_rates=[0.0],
    )
    monthly_contribution = 100.0
    expected = 1200.0 / 1.12 - sum(
        monthly_contribution / 1.12 ** (month / 12.0) for month in range(12)
    )
    assert result["npv"] == pytest.approx(expected)


def test_roth_contributions_are_added_to_penalty_basis():
    args = make_args(
        annual_savings=1000.0,
        brokerage_balance=0.0,
        starting_age=30,
        early_withdrawal_penalty_rate=0.10,
    )
    result = savings.simulate_strategy(
        args,
        expand_order("roth_ira", "solo_401k", "roth_401k", "emergency_fund", "brokerage", "hsa"),
        stock_returns=[0.0],
        inflation_rates=[0.0],
    )
    assert result["early_withdrawal_penalty"] == pytest.approx(0.0)
    assert result["final_value"] == pytest.approx(1000.0)


def test_no_early_withdrawal_penalty_at_penalty_free_age():
    args = make_args(
        annual_savings=0.0,
        brokerage_balance=0.0,
        solo_401k_balance=1000.0,
        starting_age=59,
        projection_years=1,
        federal_brackets=[[1000000.0, 0.0]],
        early_withdrawal_penalty_rate=0.10,
    )
    result = savings.simulate_strategy(
        args,
        expand_order("solo_401k", "roth_ira", "roth_401k", "emergency_fund", "brokerage", "hsa"),
        stock_returns=[0.0],
        inflation_rates=[0.0],
    )
    assert result["terminal_withdrawal_age"] == pytest.approx(60.0)
    assert result["early_withdrawal_penalty"] == pytest.approx(0.0)
    assert result["final_value"] == pytest.approx(1000.0)


def test_market_path_length_must_match_projection():
    args = make_args(projection_years=2)
    with pytest.raises(ValueError, match="stock path"):
        savings.simulate_strategy(
            args,
            savings._account_names(args),
            stock_returns=[0.0],
            inflation_rates=[0.0, 0.0],
        )


def test_loads_all_starting_balances(tmp_path):
    config = tmp_path / "balances.toml"
    config.write_text(
        """
        [owner.jacob]
        emergency_fund_balance = 1000
        roth_ira_balance = 2000
        roth_ira_basis = 1500
        solo_401k_balance = 3000
        roth_401k_balance = 4000
        roth_401k_basis = 3500
        brokerage_balance = 5000
        brokerage_basis = 4500

        [owner.dorothy]
        hsa_balance = 6000
        """
    )
    args = savings.load_toml_config(str(config))
    balances, basis = savings._starting_balances(args)
    assert balances["emergency_fund_jacob"] == 1000
    assert balances["roth_ira_jacob"] == 2000
    assert basis["roth_ira_jacob"] == 1500
    assert balances["solo_401k_jacob"] == 3000
    assert balances["roth_401k_jacob"] == 4000
    assert basis["roth_401k_jacob"] == 3500
    assert balances["brokerage_jacob"] == 5000
    assert basis["brokerage_jacob"] == 4500
    assert balances["hsa_dorothy"] == 6000


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
    balances = {account: 0.0 for account in account_names()}
    allocated = savings.allocate_savings(
        args,
        expand_order("solo_401k", "roth_401k", "roth_ira", "emergency_fund", "brokerage", "hsa"),
        balances,
    )
    assert allocated["_employer_contribution"] == pytest.approx(50000.0)
    for owner in ("jacob", "dorothy"):
        assert (
            allocated[f"solo_401k_{owner}"]
            + allocated["_employer_contribution_by_owner"][owner]
            <= 77500.0 + 1e-9
        )


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
    assert set(allocation) == set(savings._account_names(args))
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
    balances = {account: 0.0 for account in account_names()}
    allocated = savings.allocate_savings(
        args,
        expand_order("roth_ira", "emergency_fund", "solo_401k", "roth_401k", "brokerage", "hsa"),
        balances,
        year=1,
    )
    assert allocated["roth_ira_jacob"] == pytest.approx(7700.0)
    assert allocated["roth_ira_dorothy"] == pytest.approx(2300.0)
    assert savings.federal_brackets(args, 1.10)[0][0] == pytest.approx(
        args["federal_brackets_mfj"][0][0] * 1.10
    )


def test_rmd_is_taxed_and_reinvested_after_tax():
    args = make_args(
        annual_savings=0.0,
        starting_age=73,
        solo_401k_balance=26500.0,
        brokerage_balance=0.0,
        brokerage_basis=0.0,
        federal_brackets=[[1000000.0, 0.20]],
        standard_deduction=0.0,
        state_standard_deduction=0.0,
        rmd_reinvest_after_tax=True,
    )
    result = savings.simulate_strategy(
        args,
        expand_order("solo_401k", "roth_ira", "roth_401k", "emergency_fund", "brokerage", "hsa"),
        stock_returns=[0.0],
        inflation_rates=[0.0],
    )
    assert result["rmd_total"] == pytest.approx(1000.0)
    assert result["rmd_tax"] == pytest.approx(200.0)
    assert result["rmd_reinvested"] == pytest.approx(800.0)
    assert result["total_tax_cost"] == pytest.approx(5300.0)
    assert total_for(result["balances"], "solo_401k") == pytest.approx(25500.0)
    assert total_for(result["balances"], "brokerage") == pytest.approx(800.0)
    assert result["final_value"] == pytest.approx(21200.0)


def test_expense_driven_cash_flow_derives_after_tax_savings():
    args = make_args(
        annual_savings=None,
        annual_income=100000.0,
        annual_expenses=20000.0,
        standard_deduction=0.0,
        state_standard_deduction=0.0,
        federal_brackets=[[1000000.0, 0.20]],
    )
    assert savings._annual_savings(args, 0) == pytest.approx(60000.0)


def test_age_schedules_drive_income_expenses_and_contributions():
    args = make_args(
        annual_savings=None,
        annual_income=0.0,
        annual_expenses=0.0,
        standard_deduction=0.0,
        state_standard_deduction=0.0,
        federal_brackets=[[1000000.0, 0.0]],
        incomes=[{"start_age": 30, "duration": 1, "annual_amount": 50000}],
        expenses=[{"start_age": 30, "duration": 1, "annual_amount": 10000}],
        contribution_schedules=[
            {"account": "hsa", "start_age": 30, "annual_amount": 5000}
        ],
        hsa_eligible=True,
        hsa_limit=5000,
    )
    assert savings._annual_savings(args, 0) == pytest.approx(40000.0)
    balances = {account: 0.0 for account in account_names()}
    allocated = savings.allocate_savings(
        args,
        expand_order("hsa", *(b for b in savings.ACCOUNT_NAMES if b != "hsa")),
        balances,
    )
    assert sum(
        amount for name, amount in allocated.items() if name.startswith("hsa_")
    ) == pytest.approx(10000.0)


def test_hsa_limit_and_owner_specific_limit_are_supported():
    args = make_args(
        annual_savings=10000.0,
        hsa_eligible=True,
        hsa_limit=4000.0,
        owner={
            "jacob": {"hsa_limit": 3000.0},
            "dorothy": {"hsa_limit": 2000.0},
        },
    )
    balances = {account: 0.0 for account in account_names()}
    allocated = savings.allocate_savings(
        args,
        expand_order("hsa", *(b for b in savings.ACCOUNT_NAMES if b != "hsa")),
        balances,
    )
    assert allocated["hsa_jacob"] == pytest.approx(3000.0)
    assert allocated["hsa_dorothy"] == pytest.approx(2000.0)


def test_capital_gains_state_rate_is_separate():
    args = make_args(
        state_tax_rate=0.0,
        state_capital_gains_tax_rate=0.05,
        ltcg_bracket0_limit=0.0,
        ltcg_bracket1_limit=0.0,
    )
    assert savings.long_term_capital_gains_tax(args, 100.0) == pytest.approx(25.0)


def test_roth_conversion_is_taxed_and_recorded():
    args = make_args(
        annual_savings=0.0,
        solo_401k_balance=1000.0,
        brokerage_balance=0.0,
        starting_age=60,
        standard_deduction=0.0,
        state_standard_deduction=0.0,
        federal_brackets=[[1000000.0, 0.20]],
        roth_conversions=[{"start_age": 60, "duration": 1, "annual_amount": 1000}],
    )
    result = savings.simulate_strategy(
        args, savings._account_names(args), stock_returns=[0.0], inflation_rates=[0.0]
    )
    assert result["annual_roth_conversions"][0]["gross"] == pytest.approx(1000.0)
    assert result["roth_conversion_tax"] == pytest.approx(200.0)
    assert total_for(result["balances"], "solo_401k") == pytest.approx(0.0)
    assert total_for(result["balances"], "roth_ira") == pytest.approx(1000.0)


def test_retirement_histories_report_shortfall_and_warnings():
    args = make_args(
        annual_savings=0.0,
        starting_age=65,
        retirement_start_age=65,
        retirement_monthly_expenses=1000.0,
        brokerage_balance=0.0,
        solo_401k_balance=0.0,
        social_security_annual_benefit=0.0,
    )
    result = savings.simulate_strategy(
        args, savings._account_names(args), stock_returns=[0.0], inflation_rates=[0.0]
    )
    assert len(result["monthly_expenses"]) == 12
    assert result["retirement_success"] is False
    assert result["retirement_shortfall"] == pytest.approx(12000.0)
    assert result["warnings"]


def test_ltcg_harvesting_realizes_gain_and_updates_basis():
    args = make_args(
        annual_savings=0.0,
        brokerage_balance=1000.0,
        brokerage_basis=0.0,
        ltcg_harvesting=1000,
        ltcg_bracket0_limit=0.0,
        ltcg_bracket1_limit=0.0,
        state_tax_rate=0.0,
        state_capital_gains_tax_rate=0.0,
        projection_years=1,
    )
    result = savings.simulate_strategy(
        args, savings._account_names(args), stock_returns=[1.0], inflation_rates=[0.0]
    )
    assert result["ltcg_harvested"] == pytest.approx(1000.0)
    assert result["ltcg_harvesting"][0]["tax"] == pytest.approx(200.0)
    assert total_for(result["basis"], "brokerage") == pytest.approx(1000.0)
    assert total_for(result["balances"], "brokerage") == pytest.approx(1800.0)


def test_ltcg_harvesting_can_fill_remaining_zero_percent_bracket():
    args = make_args(
        annual_savings=0.0,
        annual_income=60.0,
        standard_deduction=0.0,
        brokerage_balance=1000.0,
        brokerage_basis=0.0,
        ltcg_harvesting="0%",
        ltcg_bracket0_limit=100.0,
        ltcg_bracket1_limit=1000.0,
        state_tax_rate=0.0,
        state_capital_gains_tax_rate=0.0,
        projection_years=1,
    )
    result = savings.simulate_strategy(
        args, savings._account_names(args), stock_returns=[1.0], inflation_rates=[0.0]
    )
    assert result["ltcg_harvested"] == pytest.approx(40.0)
    assert result["ltcg_harvesting"][0]["zero_percent_room"] == pytest.approx(40.0)
    assert result["ltcg_harvesting"][0]["tax"] == pytest.approx(0.0)


def test_ltcg_harvesting_can_limit_bracket_harvest_by_gain_fraction():
    args = make_args(
        annual_savings=0.0,
        annual_income=0.0,
        brokerage_balance=1000.0,
        brokerage_basis=0.0,
        ltcg_harvesting="0%70",
        ltcg_bracket0_limit=1000.0,
        state_tax_rate=0.0,
        state_capital_gains_tax_rate=0.0,
    )
    result = savings.simulate_strategy(
        args, savings._account_names(args), stock_returns=[0.0], inflation_rates=[0.0]
    )
    assert result["ltcg_harvested"] == pytest.approx(700.0)


def test_ltcg_harvesting_float_is_unbracketed_gain_fraction():
    args = make_args(
        annual_savings=0.0,
        brokerage_balance=1000.0,
        brokerage_basis=0.0,
        ltcg_harvesting=0.25,
    )
    result = savings.simulate_strategy(
        args, savings._account_names(args), stock_returns=[0.0], inflation_rates=[0.0]
    )
    assert result["ltcg_harvested"] == pytest.approx(250.0)


def test_invalid_ltcg_harvesting_configuration_is_rejected(tmp_path):
    config = tmp_path / "invalid_harvesting.toml"
    config.write_text('annual_savings = 1000\nltcg_harvesting = true\n')
    with pytest.raises(ValueError, match="ltcg_harvesting"):
        savings.load_toml_config(str(config))


def test_compact_result_keeps_harvest_details():
    args = make_args(
        annual_savings=0.0,
        brokerage_balance=1000.0,
        brokerage_basis=0.0,
        ltcg_harvesting=1000,
        ltcg_bracket0_limit=0.0,
        ltcg_bracket1_limit=0.0,
        state_tax_rate=0.0,
        state_capital_gains_tax_rate=0.0,
        projection_years=1,
    )
    result = savings.simulate_strategy(
        args, savings._account_names(args), stock_returns=[1.0], inflation_rates=[0.0]
    )
    compact = savings._compact_result(result)
    assert compact["ltcg_harvested"] == pytest.approx(1000.0)
    assert compact["ltcg_harvesting"][0]["gain"] == pytest.approx(1000.0)


def test_harvest_plan_rows_uses_mean_gain_when_harvested():
    args = make_args(ltcg_harvesting="0%")
    trials = [
        {
            "ltcg_harvesting": [
                {"age": 30, "gain": 100.0, "tax": 0.0, "zero_percent_room": 50.0}
            ]
        },
        {
            "ltcg_harvesting": [
                {"age": 30, "gain": 300.0, "tax": 0.0, "zero_percent_room": 60.0}
            ]
        },
        {
            "ltcg_harvesting": [
                {"age": 30, "gain": 200.0, "tax": 0.0, "zero_percent_room": 70.0}
            ]
        },
        {
            "ltcg_harvesting": [
                {"age": 30, "gain": 400.0, "tax": 0.0, "zero_percent_room": 80.0}
            ]
        },
    ]
    assert savings._harvest_plan_rows(args, trials) == [
        [30, "$250", "$0", "$60", "100%"]
    ]


def test_harvest_plan_is_printed_when_harvesting_enabled(capsys):
    args = make_args(ltcg_harvesting="0%")
    allocation = {
        name: float(savings._base_account(name)[0] == "brokerage")
        for name in savings._account_names(args)
    }
    summary = {
        "allocation": allocation,
        "median": 1.0,
        "p10": 1.0,
        "p75": 1.0,
        "terminal_tax": 0.0,
        "early_withdrawal_penalty": 0.0,
        "rmd_tax": 0.0,
        "max_drawdown": 0.0,
        "ltcg_harvested": 300.0,
    }
    raw = [
        [
            {
                "ltcg_harvesting": [
                    {
                        "age": 30,
                        "gain": 200.0,
                        "tax": 0.0,
                        "zero_percent_room": 60.0,
                    }
                ]
            }
        ]
    ]
    savings.print_allocation_results(args, [summary], "median", 1, raw)
    out = capsys.readouterr().out
    assert "Annual LTCG harvesting plan" in out
    assert "Mean gain if harvested" in out
    assert "$200" in out
    assert "Average lifetime LTCG harvested: $300" in out


def test_inactive_schedule_does_not_fall_back_to_scalar_income():
    args = make_args(
        annual_savings=None,
        annual_income=100000.0,
        annual_expenses=0.0,
        standard_deduction=0.0,
        state_standard_deduction=0.0,
        federal_brackets=[[1000000.0, 0.0]],
        incomes=[{"start_age": 40, "duration": 1, "annual_amount": 50000}],
    )
    assert savings._annual_income(args, 0) == pytest.approx(0.0)
    assert savings._annual_savings(args, 0) == pytest.approx(0.0)


def test_roth_conversion_tax_is_paid_from_taxable_assets():
    args = make_args(
        annual_savings=0.0,
        starting_age=60,
        solo_401k_balance=1000.0,
        brokerage_balance=1000.0,
        brokerage_basis=1000.0,
        standard_deduction=0.0,
        state_standard_deduction=0.0,
        federal_brackets=[[1000000.0, 0.20]],
        roth_conversions=[{"start_age": 60, "duration": 1, "annual_amount": 1000}],
    )
    result = savings.simulate_strategy(
        args, savings._account_names(args), stock_returns=[0.0], inflation_rates=[0.0]
    )
    assert result["roth_conversion_tax"] == pytest.approx(200.0)
    assert total_for(result["balances"], "brokerage") == pytest.approx(800.0)


def test_roth_conversion_reports_unpaid_tax_when_no_liquid_assets_exist():
    args = make_args(
        annual_savings=0.0,
        annual_income=0.0,
        starting_age=60,
        solo_401k_balance=1000.0,
        brokerage_balance=0.0,
        standard_deduction=0.0,
        state_standard_deduction=0.0,
        federal_brackets=[[1000000.0, 0.20]],
        roth_conversions=[{"start_age": 60, "duration": 1, "annual_amount": 1000}],
    )
    result = savings.simulate_strategy(
        args,
        savings._account_names(args),
        stock_returns=[0.0],
        inflation_rates=[0.0],
    )
    assert result["roth_conversion_tax"] == pytest.approx(200.0)
    assert any("unable to pay Roth conversion tax" in warning for warning in result["warnings"])


def test_custom_withdrawal_order_controls_first_distribution():
    args = make_args(
        annual_savings=0.0,
        annual_income=0.0,
        starting_age=65,
        retirement_start_age=65,
        retirement_monthly_expenses=1000.0,
        emergency_fund_balance=500.0,
        brokerage_balance=1000.0,
        brokerage_basis=1000.0,
        retirement_withdrawal_order=[
            "brokerage",
            "emergency_fund",
            "roth_ira",
            "solo_401k",
            "roth_401k",
            "hsa",
        ],
    )
    result = savings.simulate_strategy(
        args,
        savings._account_names(args),
        stock_returns=[0.0],
        inflation_rates=[0.0],
    )
    first_distribution = result["monthly_distributions"][0]
    assert sum(
        amount
        for key, amount in first_distribution.items()
        if key.startswith("brokerage_")
    ) == pytest.approx(1000.0)
    assert not any(
        key.startswith("emergency_fund_") for key in first_distribution
    )


def test_rmd_does_not_start_before_configured_age():
    args = make_args(
        annual_savings=0.0,
        annual_income=0.0,
        starting_age=72,
        solo_401k_balance=26500.0,
        rmd_start_age=73,
    )
    result = savings.simulate_strategy(
        args,
        savings._account_names(args),
        stock_returns=[0.0],
        inflation_rates=[0.0],
    )
    assert result["rmd_total"] == pytest.approx(0.0)
    assert result["annual_rmds"] == []


def test_restrict_early_withdrawals_preserves_retirement_accounts():
    args = make_args(
        annual_savings=0.0,
        starting_age=50,
        retirement_start_age=50,
        retirement_monthly_expenses=100.0,
        brokerage_balance=0.0,
        solo_401k_balance=1000.0,
        federal_brackets=[[1000000.0, 0.0]],
        restrict_early_withdrawals=True,
    )
    result = savings.simulate_strategy(
        args, savings._account_names(args), stock_returns=[0.0], inflation_rates=[0.0]
    )
    assert total_for(result["balances"], "solo_401k") == pytest.approx(1000.0)
    assert result["retirement_shortfall"] == pytest.approx(1200.0)
    assert any("restricted" in warning for warning in result["warnings"])


def test_rmd_reinvestment_can_be_disabled():
    args = make_args(
        annual_savings=0.0,
        starting_age=73,
        solo_401k_balance=26500.0,
        brokerage_balance=0.0,
        rmd_reinvest_after_tax=False,
        federal_brackets=[[1000000.0, 0.20]],
        standard_deduction=0.0,
        state_standard_deduction=0.0,
    )
    result = savings.simulate_strategy(
        args, savings._account_names(args), stock_returns=[0.0], inflation_rates=[0.0]
    )
    assert result["rmd_reinvested"] == pytest.approx(0.0)
    assert total_for(result["balances"], "brokerage") == pytest.approx(0.0)
    assert result["annual_distributions"][0]["solo_401k"] == pytest.approx(1000.0)


def test_invalid_schedule_configuration_is_rejected(tmp_path):
    config = tmp_path / "invalid.toml"
    config.write_text(
        'annual_savings = 1000\nincomes = [{ start_age = 40, end_age = 30, annual_amount = 1 }]\n'
    )
    with pytest.raises(ValueError, match="end_age"):
        savings.load_toml_config(str(config))


def test_invalid_withdrawal_order_is_rejected(tmp_path):
    config = tmp_path / "invalid_withdrawal_order.toml"
    config.write_text(
        'annual_savings = 1000\nretirement_withdrawal_order = ["brokerage", "brokerage"]\n'
    )
    with pytest.raises(ValueError, match="withdrawal_order"):
        savings.load_toml_config(str(config))


def test_reports_do_not_include_rank_column(capsys):
    report_args = {"annual_savings": 1000.0}
    allocation = {
        name: float(savings._base_account(name)[0] == "brokerage")
        for name in savings._account_names(report_args)
    }
    savings.print_allocation_results(
        report_args,
        [
            {
                "allocation": allocation,
                "median": 1.0,
                "p10": -2.0,
                "p75": 3.0,
                "terminal_tax": 0.0,
                "early_withdrawal_penalty": 0.0,
                "rmd_tax": 0.0,
                "max_drawdown": 0.0,
            }
        ],
        "median",
        1,
    )
    assert "Rank" not in capsys.readouterr().out
