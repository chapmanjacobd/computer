#!/usr/bin/env pytest
# SPDX-License-Identifier: WTFPL

import math
import os
import random

import pytest

import condo

os.chdir(os.path.dirname(__file__))


def make_args(**overrides):
    args = {
        "total_capital": 130000,
        "monthly_budget": 2162,
        "projection_years": 10,
        "mortgage_rate": 0.06,
        "mortgage_term": 15,
        "down_payment_pct": 0.20,
        "price": 275000,
        "stock_return": 0.07,
        "inflation_rate": 0.03,
        "appreciation_rate": 0.035,
        "rent_growth_rate": 0.04,
        "hoa_growth_rate": 0.06,
        "cap_gains_tax": 0.15,
        "selling_cost_pct": 0.05,
        "maintenance_pct": 0.003,
        "state_tax": 0.0495,
        "standard_deduction": 31500,
        "state_std_deduction": 10400,
        "fed_tax_rate": 0.22,
        "salt_cap": 10000,
        "home_gain_exclusion": 500000,
        "pmi_rate": 0.0075,
        "cap_gains_0pct": 98900,
        "taxable_income": 2507,
        "effective_tax_rate": 0.019,
        "annual_taxes": 275000 * 0.019,
        "monthly_assessment": 223,
        "condo_insurance_annual": 600,
        "house_insurance_annual": 1800,
        "renters_insurance_annual": 240,
        "forced_move_probability": 0.08,
        "moving_cost": 2500,
        "moving_rent_premium": -0.02,
        "inflation_volatility": 0.015,
        "appreciation_volatility": 0.10,
        "rent_growth_volatility": 0.02,
        "hoa_growth_volatility": 0.03,
        "stock_volatility": 0.18,
        "mortgage_rate_volatility": 0.01,
        "tax_volatility": 0.10,
        "maintenance_volatility": 0.35,
        "moving_cost_volatility": 0.25,
        "appreciation_inflation_beta": 0.9,
        "rent_growth_inflation_beta": 0.75,
        "hoa_growth_inflation_beta": 0.35,
        "stock_inflation_beta": 0.15,
        "mortgage_inflation_beta": 0.7,
        "macro_shock_beta": 0.3,
        "appreciation_rate_sensitivity": -1.5,
        "inflation_ar_coeffs": [0.85],
        "appreciation_ar_coeffs": [0.70],
        "rent_growth_ar_coeffs": [0.60],
        "hoa_growth_ar_coeffs": [0.60],
        "stock_ar_coeffs": [],
    }
    args.update(overrides)
    return args


def zero_volatility_args(**overrides):
    args = make_args(**overrides)
    args.update(
        {
            "inflation_volatility": 0.0,
            "appreciation_volatility": 0.0,
            "rent_growth_volatility": 0.0,
            "hoa_growth_volatility": 0.0,
            "stock_volatility": 0.0,
            "mortgage_rate_volatility": 0.0,
            "tax_volatility": 0.0,
            "maintenance_volatility": 0.0,
            "moving_cost_volatility": 0.0,
        }
    )
    return args


def test_monthly_tax_savings_no_deduction():
    args = make_args()
    assert condo.monthly_tax_savings(args, 0, 0) == 0.0


def test_monthly_tax_savings_below_standard_deduction_fed_side_zero():
    args = make_args(standard_deduction=31500)
    interest_m, prop_tax_m = 1000.0, 400.0
    fed_ded = interest_m + min(prop_tax_m, args["salt_cap"] / 12)
    assert fed_ded - args["standard_deduction"] / 12 <= 0
    state_savings = args["state_tax"] * max(
        0.0, interest_m + prop_tax_m - args["state_std_deduction"] / 12
    )
    assert condo.monthly_tax_savings(args, interest_m, prop_tax_m) == pytest.approx(state_savings)


def test_monthly_tax_savings_salt_cap():
    args = make_args(standard_deduction=0)
    interest_m, prop_tax_m = 1000.0, 5000.0
    fed_ded = interest_m + args["salt_cap"] / 12
    state_ded = interest_m + prop_tax_m - args["state_std_deduction"] / 12
    expected = (
        args["fed_tax_rate"] * max(0.0, fed_ded - args["standard_deduction"] / 12)
        + args["state_tax"] * max(0.0, state_ded)
    )
    assert condo.monthly_tax_savings(args, interest_m, prop_tax_m) == pytest.approx(expected)


def test_monthly_tax_savings_over_standard_deduction():
    args = make_args(standard_deduction=15750)
    got = condo.monthly_tax_savings(args, 4000, 5000)
    expected = 0.22 * (4000 + 10000 / 12 - 15750 / 12) + 0.0495 * (
        4000 + 5000 - args["state_std_deduction"] / 12
    )
    assert got == pytest.approx(expected)


def test_monthly_pmi_exempt_with_20_down():
    args = make_args()
    assert condo.monthly_pmi(args, 220000, 210000, 250000) == 0.0


def test_monthly_pmi_over_80_ltv():
    args = make_args(down_payment_pct=0.05)
    got = condo.monthly_pmi(args, 220000, 200000, 230000)
    assert got == pytest.approx(220000 * args["pmi_rate"] / 12)


def test_monthly_pmi_at_exactly_80_ltv():
    args = make_args(down_payment_pct=0.05)
    assert condo.monthly_pmi(args, 200000, 160000, 200000) == 0.0


def test_monthly_pmi_zero_balance_or_zero_value():
    args = make_args(down_payment_pct=0.05)
    assert condo.monthly_pmi(args, 200000, 0, 220000) == 0.0
    assert condo.monthly_pmi(args, 200000, 190000, 0) == 0.0


def test_stock_gains_tax_uses_single_year_zero_room():
    args = make_args(cap_gains_0pct=100, taxable_income=60)
    gain = 1000.0
    room = 100 - 60
    taxable = max(0.0, gain - room)
    expected = taxable * args["cap_gains_tax"] + gain * args["state_tax"]
    assert condo.stock_gains_tax(args, gain) == pytest.approx(expected)


def test_stock_gains_tax_within_zero_bracket():
    args = make_args(cap_gains_0pct=100, taxable_income=60)
    assert condo.stock_gains_tax(args, 40) == pytest.approx(40 * args["state_tax"])


def test_harvest_gains_realizes_up_to_room():
    args = make_args(cap_gains_0pct=100, taxable_income=60)
    stocks, basis = 150.0, 100.0
    stocks, basis = condo.harvest_gains(args, stocks, basis)
    assert basis == pytest.approx(140.0)
    assert stocks == pytest.approx(150 - 40 * args["state_tax"])


def test_harvest_gains_within_room_realizes_all():
    args = make_args(cap_gains_0pct=100, taxable_income=60)
    stocks, basis = 130.0, 100.0
    stocks, basis = condo.harvest_gains(args, stocks, basis)
    assert basis == pytest.approx(130.0)
    assert stocks == pytest.approx(130 - 30 * args["state_tax"])


def test_harvest_gains_no_gain_noop():
    args = make_args(cap_gains_0pct=100, taxable_income=60)
    assert condo.harvest_gains(args, 100.0, 100.0) == (100.0, 100.0)


def test_stay_home_harvests_eliminate_federal_tax_with_large_room():
    args = make_args(
        projection_years=2,
        total_capital=10000,
        monthly_budget=0,
        stock_return=0.10,
        inflation_rate=0.0,
        cap_gains_tax=0.5,
        state_tax=0.0,
        annual_taxes=0,
        cap_gains_0pct=1000000,
        taxable_income=0,
    )
    res = condo.get_stay_home_scenario(args)
    assert res["final_stocks"] == pytest.approx(10000 * 1.1**2)


def test_annual_insurance_condo_vs_house():
    args = make_args()
    assert condo.annual_insurance(args) == args["condo_insurance_annual"]
    assert condo.annual_insurance(make_args(monthly_assessment=0)) == args["house_insurance_annual"]


def test_mortgage_payment_amortizes_to_zero():
    loan = 220000
    r = 0.059 / 12
    n = 180
    pmt = loan * (r * (1 + r) ** n) / ((1 + r) ** n - 1)
    bal = loan
    for _ in range(n):
        bal -= pmt - bal * r
    assert bal == pytest.approx(0.0, abs=1e-6)


def test_remaining_loan_matches_schedule():
    loan = 220000
    r = 0.059 / 12
    n = 360
    pmt = loan * (r * (1 + r) ** n) / ((1 + r) ** n - 1)
    for months in (12, 120, 359):
        bal = loan
        for _ in range(months):
            bal -= pmt - bal * r
        rem = loan * (1 + r) ** months - pmt * (((1 + r) ** months - 1) / r)
        assert bal == pytest.approx(rem, abs=1e-6)


def test_buyer_minimal_case():
    loan = 80000
    r = 0.06 / 12
    n = 180
    pmt = loan * (r * (1 + r) ** n) / ((1 + r) ** n - 1)
    bal = loan
    for _ in range(12):
        bal -= pmt - bal * r
    res = condo.calculate_buyer_net_worth(
        make_args(
            projection_years=1,
            price=100000,
            total_capital=20000,
            monthly_budget=0,
            mortgage_rate=0.06,
            mortgage_term=15,
            stock_return=0.0,
            inflation_rate=0.0,
            appreciation_rate=0.0,
            rent_growth_rate=0.0,
            hoa_growth_rate=0.0,
            selling_cost_pct=0.0,
            maintenance_pct=0.0,
            state_tax=0.0,
            state_std_deduction=0,
            fed_tax_rate=0.0,
            home_gain_exclusion=0,
            effective_tax_rate=0.0,
            annual_taxes=0,
            monthly_assessment=0,
            condo_insurance_annual=0,
            house_insurance_annual=0,
            cap_gains_0pct=0,
            taxable_income=0,
        ),
        term_years=15,
    )
    assert res["total_costs"] == pytest.approx(20000 + 12 * pmt)
    assert res["final_stocks"] == pytest.approx(-12 * pmt)
    assert res["final_home_val"] == pytest.approx(100000 - bal)
    assert res["total_net_worth"] == pytest.approx(100000 - bal - 12 * pmt)


def test_stay_home_minimal_case():
    args = make_args(
        projection_years=1,
        total_capital=0,
        monthly_budget=0,
        stock_return=0.0,
        inflation_rate=0.0,
        cap_gains_0pct=0,
        taxable_income=0,
    )
    del args["annual_taxes"]
    res = condo.get_stay_home_scenario(args)
    assert res["total_costs"] == pytest.approx(600.0)
    assert res["initial_outlay"] == pytest.approx(50.0)
    assert res["end_year_outlay"] == pytest.approx(50.0)
    assert res["final_home_val"] == 0.0
    assert res["total_net_worth"] == pytest.approx(-600.0)


def test_renter_minimal_case():
    res = condo.get_base_renter_scenarios(
        make_args(
            projection_years=1,
            total_capital=0,
            monthly_budget=0,
            stock_return=0.0,
            inflation_rate=0.0,
            rent_growth_rate=0.0,
            renters_insurance_annual=0,
            forced_move_probability=0.0,
            moving_cost=0,
            moving_rent_premium=0.0,
            cap_gains_0pct=0,
            taxable_income=0,
        )
    )[0]
    assert res["total_costs"] == pytest.approx(12 * condo.RENTER_START_RENTS[0])
    assert res["initial_outlay"] == pytest.approx(condo.RENTER_START_RENTS[0])
    assert res["end_year_outlay"] == pytest.approx(condo.RENTER_START_RENTS[0])
    assert res["total_net_worth"] == pytest.approx(-12 * condo.RENTER_START_RENTS[0])


def test_growth_factor_matches_annual_compounding():
    args = make_args()
    for name, rate in (
        ("stock_return", 0.07),
        ("inflation_rate", 0.03),
        ("appreciation_rate", 0.035),
        ("rent_growth_rate", 0.04),
        ("hoa_growth_rate", 0.06),
    ):
        assert condo.growth_factor(args, name, 1) == pytest.approx(1 + rate)
        assert condo.growth_factor(args, name, 2) == pytest.approx((1 + rate) ** 2)


def test_monthly_growth_factor_matches_annual_rate():
    args = make_args()
    r = args["inflation_rate"]
    for m in (1, 5, 12, 13, 120):
        assert condo.monthly_growth_factor(args, "inflation_rate", m) == pytest.approx(
            (1 + r) ** (m / 12)
        )
    assert condo.monthly_growth_factor(args, "inflation_rate", 12) == pytest.approx(1 + r)


def test_monthly_stock_return():
    args = make_args()
    r = args["stock_return"]
    assert condo.monthly_stock_return(args, "stock_return", 0) == pytest.approx(
        (1 + r) ** (1 / 12) - 1
    )


def test_ar_autocorrelations_ar1():
    assert condo._ar_autocorrelations([0.85]) == pytest.approx([0.85])
    assert condo._ar_autocorrelations([-0.3]) == pytest.approx([-0.3])


def test_ar_autocorrelations_ar2_closed_form():
    phi1, phi2 = 0.5, -0.3
    rho = condo._ar_autocorrelations([phi1, phi2])
    rho1 = phi1 / (1 - phi2)
    rho2 = phi1 * rho1 + phi2
    assert rho == pytest.approx([rho1, rho2])


def test_ar_innov_sigma():
    assert condo._ar_innov_sigma([], 0.18) == pytest.approx(0.18)
    vol = 0.015
    assert condo._ar_innov_sigma([0.85], vol) == pytest.approx(vol * math.sqrt(1 - 0.85**2))


def test_ar_innov_sigma_rejects_non_stationary():
    with pytest.raises(ValueError):
        condo._ar_innov_sigma([1.0], 0.015)
    with pytest.raises(ValueError):
        condo._ar_innov_sigma([0.8, 0.5], 0.015)


def test_ar_log_returns_preserves_mean():
    rng = random.Random(1)
    path = condo.ar_log_returns(rng, [0.07] * 2000, 0.06, [], -0.5, 0.5)
    assert sum(1 + x for x in path) / len(path) == pytest.approx(1.07, abs=1e-2)


def test_ar_log_returns_reproduces_autocorrelation():
    rng = random.Random(0)
    path = condo.ar_log_returns(rng, [0.03] * 3000, 0.05, [0.6], -0.3, 0.3)
    mean = sum(path) / len(path)
    num = sum((path[i] - mean) * (path[i - 1] - mean) for i in range(1, len(path)))
    den = sum((x - mean) ** 2 for x in path)
    assert num / den == pytest.approx(0.6, abs=0.15)


def test_ar_log_returns_deterministic_and_clamped():
    rng = random.Random(5)
    a = condo.ar_log_returns(rng, [0.03] * 10, 0.05, [0.6], -0.3, 0.3)
    rng = random.Random(5)
    b = condo.ar_log_returns(rng, [0.03] * 10, 0.05, [0.6], -0.3, 0.3)
    assert a == b
    assert all(-0.3 <= x <= 0.3 for x in a)


def test_make_market_paths_shape_and_bounds():
    args = make_args(projection_years=20)
    rng = random.Random(7)
    market = condo.make_market_paths(args, rng)
    assert set(market) == {
        "stock_return",
        "inflation_rate",
        "appreciation_rate",
        "rent_growth_rate",
        "hoa_growth_rate",
        "mortgage_rate",
        "mortgage_rate_path",
    }
    for name in (
        "stock_return",
        "inflation_rate",
        "appreciation_rate",
        "rent_growth_rate",
        "hoa_growth_rate",
    ):
        assert len(market[name]) == 20
    assert all(-0.80 <= x <= 1.00 for x in market["stock_return"])
    assert all(-0.30 <= x <= 0.30 for x in market["appreciation_rate"])
    assert all(-0.01 <= x <= 0.12 for x in market["inflation_rate"])
    assert all(-0.05 <= x <= 0.12 for x in market["rent_growth_rate"])
    assert all(-0.05 <= x <= 0.20 for x in market["hoa_growth_rate"])
    assert 0.03 <= market["mortgage_rate"] <= 0.10


def test_make_trial_args_factors_consistent():
    args = make_args(projection_years=10)
    market = condo.make_market_paths(args, random.Random(7))
    trial = condo.make_trial_args(args, market, random.Random(8))
    for name, rates in trial["_mc_paths"].items():
        for year, rate in enumerate(rates):
            monthly = (1 + rate) ** (1 / 12) - 1
            assert trial["_mc_monthly_returns"][name][year] == pytest.approx(monthly)
            expected = 1.0
            for r in rates[: year + 1]:
                expected *= 1 + r
            assert trial["_mc_monthly_factors"][name][12 * (year + 1)] == pytest.approx(
                expected, abs=1e-9
            )


def test_mc_growth_factor_matches_monthly_growth_factor():
    args = make_args(projection_years=10)
    market = condo.make_market_paths(args, random.Random(7))
    trial = condo.make_trial_args(args, market, random.Random(8))
    for name in ("inflation_rate", "appreciation_rate", "rent_growth_rate", "hoa_growth_rate"):
        for yr in (0, 1, 5, 10):
            assert condo.growth_factor(trial, name, yr) == pytest.approx(
                condo.monthly_growth_factor(trial, name, 12 * yr), abs=1e-9
            )


def test_mc_zero_volatility_matches_deterministic_buyer():
    args = zero_volatility_args(projection_years=10)
    det = condo.calculate_buyer_net_worth(args, term_years=15)
    market = condo.make_market_paths(args, random.Random(1))
    trial = condo.make_trial_args(args, market, random.Random(1))
    mc = condo.calculate_buyer_net_worth(trial, term_years=15)
    assert det["total_costs"] == pytest.approx(mc["total_costs"], rel=1e-9)
    assert det["total_net_worth"] == pytest.approx(mc["total_net_worth"], rel=1e-9)


def test_mc_zero_volatility_matches_deterministic_renter():
    args = zero_volatility_args(projection_years=10, forced_move_probability=0.0)
    det = condo.get_base_renter_scenarios(args)
    market = condo.make_market_paths(args, random.Random(1))
    trial = condo.make_trial_args(args, market, random.Random(1), include_renter_risk=True)
    mc = condo.get_base_renter_scenarios(trial)
    for d, m in zip(det, mc):
        assert d["total_costs"] == pytest.approx(m["total_costs"], rel=1e-9)
        assert d["total_net_worth"] == pytest.approx(m["total_net_worth"], rel=1e-9)


def test_mc_zero_volatility_matches_deterministic_stay_home():
    args = zero_volatility_args(projection_years=10)
    det = condo.get_stay_home_scenario(args)
    market = condo.make_market_paths(args, random.Random(1))
    trial = condo.make_trial_args(args, market, random.Random(1))
    mc = condo.get_stay_home_scenario(trial)
    assert det["total_costs"] == pytest.approx(mc["total_costs"], rel=1e-9)
    assert det["total_net_worth"] == pytest.approx(mc["total_net_worth"], rel=1e-9)


def test_renter_rent_factor_deterministic():
    args = make_args()
    for year in (0, 1, 10):
        expected = (1 + args["forced_move_probability"] * args["moving_rent_premium"]) ** year
        assert condo.renter_rent_factor(args, year) == pytest.approx(expected)


def test_renter_move_cost_deterministic():
    args = make_args()
    assert condo.renter_move_cost(args, 3) == pytest.approx(
        args["forced_move_probability"] * args["moving_cost"]
    )


def test_derive_seed_deterministic_and_distinct():
    assert condo.derive_seed(42, 1, 2, 3) == condo.derive_seed(42, 1, 2, 3)
    seeds = {condo.derive_seed(42, i) for i in range(20)}
    assert len(seeds) == 20


def test_bootstrap_median_se():
    assert condo.bootstrap_median_se([5.0] * 10) == 0.0
    assert condo.bootstrap_median_se([]) == 0.0
    assert condo.bootstrap_median_se([3.0]) == 0.0
    samples = [random.random() * 1000 for _ in range(50)]
    assert condo.bootstrap_median_se(samples) == condo.bootstrap_median_se(samples)


def test_aggregate_scenario():
    results = [
        {"scenario": "X", "total_net_worth": 1.0, "initial_outlay": 10.0, "end_year_outlay": 20.0, "final_stocks": 111.0, "final_home_val": 1.0, "total_costs": 1.0},
        {"scenario": "X", "total_net_worth": 3.0, "initial_outlay": 30.0, "end_year_outlay": 60.0, "final_stocks": 333.0, "final_home_val": 3.0, "total_costs": 3.0},
        {"scenario": "X", "total_net_worth": 2.0, "initial_outlay": 20.0, "end_year_outlay": 40.0, "final_stocks": 222.0, "final_home_val": 2.0, "total_costs": 2.0},
    ]
    row = condo.aggregate_scenario(results)
    assert row["total_net_worth"] == 2.0
    assert row["total_costs"] == 2.0
    assert row["initial_outlay"] == pytest.approx(20.0)
    assert row["end_year_outlay"] == pytest.approx(40.0)


def test_aggregate_net_worth_is_raw_median():
    nw = [float(i) for i in range(20)]
    results = [
        {"scenario": "X", "total_net_worth": v, "initial_outlay": 1.0, "end_year_outlay": 2.0,
         "final_stocks": 0.0, "final_home_val": 0.0, "total_costs": 0.0}
        for v in nw
    ]
    row = condo.aggregate_scenario(results)
    assert row["total_net_worth"] == sorted(nw)[len(nw) // 2]


def test_parse_float_with_commas():
    assert condo.parse_float_with_commas("1,234.5") == 1234.5
    assert condo.parse_float_with_commas("130000") == 130000.0


def test_load_toml_config(tmp_path):
    cfg = tmp_path / "test.toml"
    cfg.write_text(
        """
        total_capital = 200000
        annual_income = 100000
        standard_deduction = 31500
        mortgage_options = [
          { term = 15, rate = 0.05 },
          { term = 30, rate = 0.06 },
        ]
        [scenario."Test Home"]
        price = 400000
        effective_tax_rate = 0.02
        monthly_budget = 3000
        """
    )
    defaults, scenarios = condo.load_toml_config(str(cfg))
    assert defaults["total_capital"] == 200000
    assert defaults["monthly_budget"] == pytest.approx(100000 / 12 * 0.43)
    assert defaults["taxable_income"] == pytest.approx(100000 - 31500)
    assert defaults["mortgage_options"][0]["rate"] == 0.05
    assert defaults["mortgage_rate"] == pytest.approx(0.05)
    assert len(scenarios) == 1
    first = scenarios[0]
    assert first["_address"] == "Test Home"
    assert first["price"] == 400000
    assert first["annual_taxes"] == pytest.approx(400000 * 0.02)
    assert first["monthly_budget"] == 3000
    assert first["total_capital"] == 200000


def test_load_toml_config_monthly_budget_override_wins():
    import tempfile

    with tempfile.NamedTemporaryFile("w", suffix=".toml", delete=False) as f:
        f.write("monthly_budget = 2000\n[scenario]\n")
    try:
        defaults, scenarios = condo.load_toml_config(f.name)
        assert defaults["monthly_budget"] == 2000
        assert defaults["annual_income"] == 77000
    finally:
        os.unlink(f.name)


def test_bounded_normal_deterministic_and_clamped():
    rng = random.Random(2)
    a = condo.bounded_normal(rng, 0.5, 0.01, 0.0, 1.0)
    rng = random.Random(2)
    b = condo.bounded_normal(rng, 0.5, 0.01, 0.0, 1.0)
    assert a == b
    vals = [condo.bounded_normal(random.Random(i), 0.5, 0.01, 0.0, 1.0) for i in range(200)]
    assert all(0.0 <= v <= 1.0 for v in vals)
    out = condo.bounded_normal(random.Random(3), 5.0, 0.0, 0.0, 1.0)
    assert 0.0 <= out <= 1.0


def test_zero_mortgage_rate_principal_only():
    loan = 80000
    n = 180
    pmt = loan / n
    res = condo.calculate_buyer_net_worth(
        make_args(
            projection_years=1,
            price=100000,
            total_capital=20000,
            monthly_budget=0,
            mortgage_rate=0.0,
            mortgage_term=15,
            stock_return=0.0,
            inflation_rate=0.0,
            appreciation_rate=0.0,
            rent_growth_rate=0.0,
            hoa_growth_rate=0.0,
            selling_cost_pct=0.0,
            maintenance_pct=0.0,
            state_tax=0.0,
            state_std_deduction=0,
            fed_tax_rate=0.0,
            home_gain_exclusion=0,
            effective_tax_rate=0.0,
            annual_taxes=0,
            monthly_assessment=0,
            condo_insurance_annual=0,
            house_insurance_annual=0,
            cap_gains_0pct=0,
            taxable_income=0,
        ),
        term_years=15,
    )
    assert res["total_costs"] == pytest.approx(20000 + 12 * pmt)
    assert res["final_stocks"] == pytest.approx(-12 * pmt)
    assert res["total_net_worth"] == pytest.approx(20000)


def test_stay_home_honors_annual_taxes():
    res = condo.get_stay_home_scenario(
        make_args(
            projection_years=1,
            total_capital=0,
            monthly_budget=0,
            stock_return=0.0,
            inflation_rate=0.0,
            cap_gains_0pct=0,
            taxable_income=0,
            annual_taxes=6000,
        )
    )
    assert res["total_costs"] == pytest.approx(6000.0)
    assert res["total_net_worth"] == pytest.approx(-6000.0)


def test_aggregate_scenario_columns_are_medians():
    results = [
        {"scenario": "X", "total_net_worth": 1.0, "initial_outlay": 10.0, "end_year_outlay": 20.0, "final_stocks": 100.0, "final_home_val": 100.0, "total_costs": 100.0},
        {"scenario": "X", "total_net_worth": 2.0, "initial_outlay": 20.0, "end_year_outlay": 40.0, "final_stocks": 200.0, "final_home_val": 200.0, "total_costs": 200.0},
        {"scenario": "X", "total_net_worth": 3.0, "initial_outlay": 30.0, "end_year_outlay": 60.0, "final_stocks": 50.0, "final_home_val": 50.0, "total_costs": 50.0},
    ]
    row = condo.aggregate_scenario(results)
    assert row["total_costs"] == pytest.approx(100.0)
    assert row["final_stocks"] == pytest.approx(100.0)
    assert row["final_home_val"] == pytest.approx(100.0)


def test_run_monte_carlo_reproducible():
    defaults = zero_volatility_args(projection_years=3, forced_move_probability=0.0)
    scenarios = [
        {**make_args(projection_years=3, price=275000, _address="Unit A")},
    ]
    for sc in scenarios:
        condo.choose_mortgage_for_scenario(sc)
    a1, raw1, skip1 = condo.run_monte_carlo(defaults, scenarios, 20, seed=42)
    a2, raw2, skip2 = condo.run_monte_carlo(defaults, scenarios, 20, seed=42)
    assert [r["total_net_worth"] for r in a1] == [r["total_net_worth"] for r in a2]
    assert skip1 == skip2
    assert len(raw1) == 1 + len(condo.RENTER_START_RENTS) + len(scenarios)
    assert all(len(rows) == 20 for rows in raw1)


def test_filter_expensive_scenarios_skips_dominated():
    defaults = zero_volatility_args(projection_years=3, forced_move_probability=0.0)
    cheap = {**make_args(projection_years=3, price=150000, _address="Cheap")}
    expensive = {**make_args(projection_years=3, price=900000, _address="Mansion")}
    for sc in (cheap, expensive):
        condo.choose_mortgage_for_scenario(sc)
    kept, skipped, bar = condo.filter_expensive_scenarios(defaults, [cheap, expensive])
    assert kept == [cheap]
    assert [s["address"] for s in skipped] == ["Mansion"]
    assert skipped[0]["price"] == 900000
    assert skipped[0]["est_nw"] < bar
    assert bar == pytest.approx(
        condo.get_base_renter_scenarios(defaults)[-1]["total_net_worth"] * condo.RENTER_PRUNING_FACTOR
    )


def test_run_monte_carlo_skips_expensive_scenarios():
    defaults = zero_volatility_args(projection_years=3, forced_move_probability=0.0)
    expensive = {**make_args(projection_years=3, price=900000, _address="Mansion")}
    condo.choose_mortgage_for_scenario(expensive)
    all_scenarios, raw, skip = condo.run_monte_carlo(defaults, [expensive], 10, seed=42)
    assert len(all_scenarios) == 1 + len(condo.RENTER_START_RENTS)
    assert len(raw) == 1 + len(condo.RENTER_START_RENTS)
    assert skip["skipped"][0]["address"] == "Mansion"


def test_record_schedule_extra_fields():
    res = condo.calculate_buyer_net_worth(
        make_args(projection_years=2), term_years=15, record_schedule=True
    )
    entry = res["_schedule"][0]
    for key in ("outlay", "stocks", "home_value", "pmi"):
        assert key in entry
    assert res["_stock_gain"] >= 0.0
    assert res["_stock_tax"] >= 0.0
    assert res["_home_gain"] >= 0.0
    assert res["_net_home"] >= 0.0


def test_horizon_years_extends_schedule():
    args = make_args(projection_years=2)
    long = condo.calculate_buyer_net_worth(
        args, term_years=15, record_schedule=True, horizon_years=10
    )
    assert len(long["_schedule"]) == 120
    short = condo.calculate_buyer_net_worth(args, term_years=15, record_schedule=True)
    assert len(short["_schedule"]) == 24


def test_risk_summary_percentiles():
    results = [
        [
            {"scenario": "Home", "total_net_worth": float(i)} for i in range(20)
        ],
        [
            {"scenario": "Buyer", "total_net_worth": float(19 - i)} for i in range(20)
        ],
    ]
    import io
    from contextlib import redirect_stdout

    buf = io.StringIO()
    with redirect_stdout(buf):
        condo.print_risk_summary_table(results)
    out = buf.getvalue()
    assert "P(Beat Home)" in out
    assert "50.0%" in out
