#!/usr/bin/python3
import argparse
import math
import random
import sys
from statistics import median

from tabulate import tabulate

RENTER_START_RENTS = (1300, 1500, 1700, 1900, 2100, 2300)

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        print("Error: TOML support requires Python 3.11+ or 'tomli' package. Install with: pip install tomli")
        sys.exit(1)


def annual_rate(args: dict, name: str, year: int) -> float:
    paths = args.get("_mc_paths")
    if paths and name in paths:
        return paths[name][year]
    return args[name]


def growth_factor(args: dict, name: str, years: int) -> float:
    cached_factors = args.get("_mc_growth_factors")
    if cached_factors and name in cached_factors:
        return cached_factors[name][years]

    factor = 1.0
    for year in range(years):
        factor *= 1 + annual_rate(args, name, year)
    return factor


def monthly_growth_factor(args: dict, name: str, month: int) -> float:
    full_years, remaining_months = divmod(month, 12)
    factor = growth_factor(args, name, full_years)
    if remaining_months:
        factor *= (1 + annual_rate(args, name, full_years)) ** (remaining_months / 12.0)
    return factor


def renter_move_cost(args: dict, year: int) -> float:
    move_costs = args.get("_mc_move_costs")
    if move_costs is not None:
        return move_costs[year]
    return args["forced_move_probability"] * args["moving_cost"]


def renter_rent_factor(args: dict, year: int) -> float:
    rent_factors = args.get("_mc_rent_factors")
    if rent_factors is not None:
        return rent_factors[year]
    return (1 + args["forced_move_probability"] * args["moving_rent_premium"]) ** year


def monthly_tax_savings(args: dict, interest_m: float, prop_tax_m: float) -> float:
    fed_ded = interest_m + min(prop_tax_m, args["salt_cap"] / 12)
    fed_savings = args["fed_tax_rate"] * max(0.0, fed_ded - args["fed_std_deduction"] / 12)
    state_savings = args["state_tax"] * max(0.0, interest_m + prop_tax_m - args["state_std_deduction"] / 12)
    return fed_savings + state_savings


def monthly_pmi(args: dict, loan_amt: float, balance: float, home_value: float) -> float:
    if args["down_payment_pct"] >= 0.20 or balance <= 0:
        return 0.0
    if home_value > 0 and balance / home_value > 0.80:
        return loan_amt * args["pmi_rate"] / 12
    return 0.0


def stock_gains_tax(args: dict, stock_gain: float, projection_years: int) -> float:
    annual_room = max(0.0, args["cap_gains_0pct"] - args["taxable_income"])
    taxable_gain = max(0.0, stock_gain - annual_room * projection_years)
    return taxable_gain * args["cap_gains_tax"] + stock_gain * args["state_tax"]


def annual_insurance(args: dict) -> float:
    if args["monthly_assessment"] > 0:
        return args["condo_insurance_annual"]
    return args["house_insurance_annual"]


def get_stay_home_scenario(args: dict) -> dict:
    projection_years = args["projection_years"]
    projection_months = projection_years * 12
    stocks = args["total_capital"]
    cost_basis = stocks
    total_costs = 0.0

    tax_m = args.get("_stay_home_tax_annual", 600.0) / 12

    for m in range(1, projection_months + 1):
        yr = (m - 1) // 12
        stocks *= 1 + annual_rate(args, "stock_return", yr) / 12

        inflation_factor = growth_factor(args, "inflation_rate", yr)
        tax_curr = tax_m * inflation_factor
        monthly_budget = args["monthly_budget"] * inflation_factor

        total_costs += tax_curr / monthly_growth_factor(args, "inflation_rate", m)
        net_cash_flow = monthly_budget - tax_curr
        stocks += net_cash_flow
        if net_cash_flow > 0:
            cost_basis += net_cash_flow

    stock_gain = max(0, stocks - cost_basis)
    stock_tax = stock_gains_tax(args, stock_gain, projection_years)
    stocks_after_tax = stocks - stock_tax

    inflation_factor = growth_factor(args, "inflation_rate", projection_years)
    end_year_outlay = tax_m * inflation_factor

    return {
        "scenario": "Stay Home",
        "initial_outlay": tax_m,
        "end_year_outlay": end_year_outlay,
        "total_costs": total_costs,
        "final_stocks": stocks_after_tax,
        "final_home_val": 0.0,
        "total_net_worth": stocks_after_tax / inflation_factor,
    }


def calculate_buyer_net_worth(args: dict, term_years: int = 15, mortgage_rate: float | None = None) -> dict:
    projection_years = args["projection_years"]
    projection_months = projection_years * 12
    if mortgage_rate is None:
        mortgage_rate = args["mortgage_rate"]
    r = mortgage_rate / 12

    dp_amt = args["price"] * args["down_payment_pct"]
    loan_amt = args["price"] - dp_amt

    term_months = term_years * 12
    pmt = loan_amt * (r * (1 + r) ** term_months) / ((1 + r) ** term_months - 1)

    schedule = []
    bal = loan_amt
    for _ in range(term_months):
        interest = bal * r
        schedule.append(interest)
        bal -= pmt - interest

    buyer_stocks = args["total_capital"] - dp_amt
    annual_taxes = args.get("annual_taxes", args["price"] * args["effective_tax_rate"])
    tax_m = annual_taxes / 12
    hoa_m = args["monthly_assessment"]
    insurance_m = annual_insurance(args) / 12
    maint_m = (args["price"] * args["maintenance_pct"]) / 12

    cost_basis = buyer_stocks
    base_outlay_y1 = (
        pmt + tax_m + hoa_m + insurance_m + maint_m
        + monthly_pmi(args, loan_amt, loan_amt, args["price"])
        - monthly_tax_savings(args, schedule[0], tax_m)
    )
    total_costs = dp_amt

    loan_balance = loan_amt

    for m in range(1, projection_months + 1):
        yr = (m - 1) // 12
        buyer_stocks *= 1 + annual_rate(args, "stock_return", yr) / 12

        appr_factor = growth_factor(args, "appreciation_rate", yr)
        infl_factor = growth_factor(args, "inflation_rate", yr)
        hoa_growth_factor = growth_factor(args, "hoa_growth_rate", yr)
        tax_curr = tax_m * appr_factor
        hoa_curr = hoa_m * hoa_growth_factor
        insurance_curr = insurance_m * infl_factor
        maint_curr = maint_m * appr_factor
        pmt_curr = pmt if m <= term_months else 0.0
        interest_curr = schedule[m - 1] if m <= term_months else 0.0
        pmi_curr = monthly_pmi(args, loan_amt, loan_balance, args["price"] * appr_factor)
        if m <= term_months:
            loan_balance -= pmt - interest_curr

        buyer_outlay = (
            pmt_curr
            + tax_curr
            + hoa_curr
            + insurance_curr
            + maint_curr
            + pmi_curr
            - monthly_tax_savings(args, interest_curr, tax_curr)
        )
        monthly_budget = args["monthly_budget"] * infl_factor

        total_costs += buyer_outlay / monthly_growth_factor(args, "inflation_rate", m)
        net_cash_flow = monthly_budget - buyer_outlay
        buyer_stocks += net_cash_flow
        if net_cash_flow > 0:
            cost_basis += net_cash_flow

    stock_gain = max(0, buyer_stocks - cost_basis)
    stock_tax = stock_gains_tax(args, stock_gain, projection_years)
    buyer_stocks_after_tax = buyer_stocks - stock_tax

    appreciation_factor = growth_factor(args, "appreciation_rate", projection_years)
    inflation_factor = growth_factor(args, "inflation_rate", projection_years)

    nominal_home_val = args["price"] * appreciation_factor
    selling_costs = nominal_home_val * args["selling_cost_pct"]
    home_gain = nominal_home_val - selling_costs - args["price"]
    taxable_home_gain = max(0, home_gain - args["home_gain_exclusion"])
    home_tax = taxable_home_gain * args["cap_gains_tax"] + home_gain * args["state_tax"]
    if projection_months < term_months:
        remaining_loan = loan_amt * (1 + r) ** projection_months - pmt * (
            ((1 + r) ** projection_months - 1) / r
        )
    else:
        remaining_loan = 0.0
    net_home = nominal_home_val - selling_costs - home_tax - remaining_loan

    final_home_val = net_home / inflation_factor
    final_net_worth = (buyer_stocks_after_tax / inflation_factor) + final_home_val

    hoa_factor = growth_factor(args, "hoa_growth_rate", projection_years)
    end_interest = schedule[projection_months] if projection_months < term_months else 0.0
    end_tax = tax_m * appreciation_factor
    end_pmi = monthly_pmi(args, loan_amt, loan_balance, args["price"] * appreciation_factor)
    end_year_outlay = (
        (pmt if term_months > projection_months else 0.0)
        + end_tax
        + hoa_m * hoa_factor
        + insurance_m * inflation_factor
        + maint_m * appreciation_factor
        + end_pmi
    ) - monthly_tax_savings(args, end_interest, end_tax)

    address = args.get("_address", "")
    if address:
        label = address
    else:
        label = f"Condo {term_years}-yr (${args['price']:,.0f} | Tax: ${annual_taxes:,.0f} | HOA: ${args['monthly_assessment']:.0f})"

    return {
        "scenario": label,
        "initial_outlay": base_outlay_y1,
        "end_year_outlay": end_year_outlay,
        "total_costs": total_costs,
        "final_stocks": buyer_stocks_after_tax,
        "final_home_val": final_home_val,
        "total_net_worth": final_net_worth,
    }


def get_base_renter_scenarios(args: dict) -> list[dict]:
    projection_years = args["projection_years"]
    projection_months = projection_years * 12
    renter_results = []

    renters_insurance_m = args["renters_insurance_annual"] / 12

    for start_rent in RENTER_START_RENTS:
        renter_stocks = args["total_capital"]
        cost_basis = renter_stocks
        total_costs = 0.0

        for m in range(1, projection_months + 1):
            yr = (m - 1) // 12
            renter_stocks *= 1 + annual_rate(args, "stock_return", yr) / 12

            rent_curr = (
                start_rent
                * growth_factor(args, "rent_growth_rate", yr)
                * renter_rent_factor(args, yr)
            )
            insurance_curr = renters_insurance_m * growth_factor(args, "inflation_rate", yr)
            moving_cost = renter_move_cost(args, yr) if m % 12 == 1 else 0.0
            renter_outlay = rent_curr + insurance_curr + moving_cost
            monthly_budget = args["monthly_budget"] * growth_factor(args, "inflation_rate", yr)

            total_costs += renter_outlay / monthly_growth_factor(args, "inflation_rate", m)
            net_cash_flow = monthly_budget - renter_outlay
            renter_stocks += net_cash_flow
            if net_cash_flow > 0:
                cost_basis += net_cash_flow

        stock_gain = max(0, renter_stocks - cost_basis)
        stock_tax = stock_gains_tax(args, stock_gain, projection_years)
        renter_stocks_after_tax = renter_stocks - stock_tax

        initial_outlay = (
            start_rent * renter_rent_factor(args, 0)
            + renters_insurance_m
            + renter_move_cost(args, 0)
        )
        end_year_outlay = (
            start_rent
            * growth_factor(args, "rent_growth_rate", projection_years)
            * renter_rent_factor(args, projection_years)
            + renters_insurance_m * growth_factor(args, "inflation_rate", projection_years)
            + renter_move_cost(args, projection_years)
        )

        scenario_name = f"Rent at ${start_rent}/mo"

        renter_results.append(
            {
                "scenario": scenario_name,
                "initial_outlay": initial_outlay,
                "end_year_outlay": end_year_outlay,
                "total_costs": total_costs,
                "final_stocks": renter_stocks_after_tax,
                "final_home_val": 0.0,
                "total_net_worth": renter_stocks_after_tax
                / growth_factor(args, "inflation_rate", projection_years),
            }
        )

    return renter_results


def load_toml_config(filepath: str) -> tuple[dict, list[dict]]:
    with open(filepath, "rb") as f:
        data = tomllib.load(f)

    defaults = {
        "total_capital": 130000,
        "monthly_budget": 2100,
        "projection_years": 30,
        "mortgage_rate": 0.061,
        "mortgage_term": 15,
        "down_payment_pct": 0.20,
        "stock_return": 0.07,
        "inflation_rate": 0.03,
        "appreciation_rate": 0.03,
        "rent_growth_rate": 0.055,
        "cap_gains_tax": 0.15,
        "selling_cost_pct": 0.06,
        "maintenance_pct": 0.01,
        "state_tax": 0.0495,
        "hoa_growth_rate": 0.0672,
        "fed_std_deduction": 30000,
        "state_std_deduction": 5200,
        "fed_tax_rate": 0.22,
        "salt_cap": 10000,
        "home_gain_exclusion": 500000,
        "pmi_rate": 0.0075,
        "cap_gains_0pct": 98900,
        "taxable_income": 5000,
        "effective_tax_rate": 0.019,
        "condo_insurance_annual": 600,
        "house_insurance_annual": 1800,
        "renters_insurance_annual": 240,
        "forced_move_probability": 0.12,
        "moving_cost": 2500,
        "moving_rent_premium": 0.08,
        "moving_cost_volatility": 0.25,
        "stock_volatility": 0.18,
        "appreciation_volatility": 0.10,
        "inflation_volatility": 0.015,
        "rent_growth_volatility": 0.02,
        "hoa_growth_volatility": 0.03,
        "mortgage_rate_volatility": 0.01,
        "tax_volatility": 0.10,
        "maintenance_volatility": 0.35,
        "monte_carlo_simulations": 1000,
        "monte_carlo_seed": 42,
    }

    for key in defaults:
        if key in data:
            defaults[key] = data[key]

    scenarios = []
    if "scenario" in data:
        for address, params in data["scenario"].items():
            merged = defaults.copy()
            merged.update(params)
            if "annual_taxes" not in params:
                merged["annual_taxes"] = merged["price"] * merged["effective_tax_rate"]
            merged["_address"] = address
            scenarios.append(merged)

    return defaults, scenarios


def bounded_normal(rng: random.Random, mean: float, deviation: float, minimum: float, maximum: float) -> float:
    for _ in range(20):
        value = rng.gauss(mean, deviation)
        if minimum <= value <= maximum:
            return value
    return min(max(value, minimum), maximum)


def lognormal_factor(rng: random.Random, deviation: float, minimum: float, maximum: float) -> float:
    value = math.exp(rng.gauss(-0.5 * deviation**2, deviation))
    return min(max(value, minimum), maximum)


def stock_return(rng: random.Random, expected_return: float, volatility: float) -> float:
    gross_mean = max(0.01, 1 + expected_return)
    value = math.exp(math.log(gross_mean) - 0.5 * volatility**2 + rng.gauss(0, volatility)) - 1
    return min(max(value, -0.80), 1.00)


def make_market_paths(args: dict, rng: random.Random) -> dict:
    years = args["projection_years"]
    inflation = [
        bounded_normal(
            rng,
            args["inflation_rate"],
            args["inflation_volatility"],
            -0.01,
            0.12,
        )
        for _ in range(years)
    ]
    appreciation = [
        bounded_normal(
            rng,
            args["appreciation_rate"] + 0.25 * (inflation[year] - args["inflation_rate"]),
            args["appreciation_volatility"],
            -0.30,
            0.30,
        )
        for year in range(years)
    ]
    rent_growth = [
        bounded_normal(
            rng,
            args["rent_growth_rate"] + 0.50 * (inflation[year] - args["inflation_rate"]),
            args["rent_growth_volatility"],
            -0.05,
            0.12,
        )
        for year in range(years)
    ]
    hoa_growth = [
        bounded_normal(
            rng,
            args["hoa_growth_rate"] + 0.35 * (inflation[year] - args["inflation_rate"]),
            args["hoa_growth_volatility"],
            -0.05,
            0.20,
        )
        for year in range(years)
    ]
    return {
        "stock_return": [
            stock_return(
                rng,
                args["stock_return"] + 0.15 * (inflation[year] - args["inflation_rate"]),
                args["stock_volatility"],
            )
            for year in range(years)
        ],
        "inflation_rate": inflation,
        "appreciation_rate": appreciation,
        "rent_growth_rate": rent_growth,
        "hoa_growth_rate": hoa_growth,
        "mortgage_rate": bounded_normal(
            rng,
            args["mortgage_rate"] + 0.50 * (inflation[0] - args["inflation_rate"])
            if inflation
            else args["mortgage_rate"],
            args["mortgage_rate_volatility"],
            0.03,
            0.10,
        ),
    }


def make_trial_args(
    args: dict, market: dict, rng: random.Random, include_renter_risk: bool = False
) -> dict:
    trial = args.copy()
    trial["_mc_paths"] = {
        key: values for key, values in market.items() if key != "mortgage_rate"
    }
    trial["_mc_growth_factors"] = {}
    for name, rates in trial["_mc_paths"].items():
        factors = [1.0]
        for rate in rates:
            factors.append(factors[-1] * (1 + rate))
        trial["_mc_growth_factors"][name] = factors
    trial["mortgage_rate"] = market["mortgage_rate"]
    trial["maintenance_pct"] = args["maintenance_pct"] * lognormal_factor(
        rng, args["maintenance_volatility"], 0.50, 3.00
    )
    if "annual_taxes" in args:
        trial["annual_taxes"] = args["annual_taxes"] * lognormal_factor(
            rng, args["tax_volatility"], 0.80, 1.25
        )
    else:
        trial["_stay_home_tax_annual"] = 600.0 * lognormal_factor(
            rng, args["tax_volatility"], 0.80, 1.25
        )
    if include_renter_risk:
        rent_factor = 1.0
        trial["_mc_move_costs"] = []
        trial["_mc_rent_factors"] = []
        for _ in range(args["projection_years"] + 1):
            if rng.random() < args["forced_move_probability"]:
                rent_factor *= 1 + args["moving_rent_premium"]
                move_cost = args["moving_cost"] * lognormal_factor(
                    rng, args["moving_cost_volatility"], 0.70, 1.50
                )
            else:
                move_cost = 0.0
            trial["_mc_move_costs"].append(move_cost)
            trial["_mc_rent_factors"].append(rent_factor)
    return trial


def median_scenario(results: list[dict]) -> dict:
    return {
        "scenario": results[0]["scenario"],
        **{
            key: median(result[key] for result in results)
            for key in ("initial_outlay", "end_year_outlay", "total_costs", "final_stocks", "final_home_val", "total_net_worth")
        },
    }


def run_monte_carlo(
    defaults: dict, scenarios_config: list[dict], simulations: int, seed: int
) -> list[dict]:
    rng = random.Random(seed)
    results = [[] for _ in range(1 + len(RENTER_START_RENTS) + len(scenarios_config))]

    for _ in range(simulations):
        market = make_market_paths(defaults, rng)
        trial_defaults = make_trial_args(defaults, market, rng, include_renter_risk=True)
        trial_results = [
            get_stay_home_scenario(trial_defaults),
            *get_base_renter_scenarios(trial_defaults),
        ]
        for sc_config in scenarios_config:
            trial_scenario = make_trial_args(sc_config, market, rng)
            trial_results.append(
                calculate_buyer_net_worth(trial_scenario, term_years=trial_scenario["mortgage_term"])
            )

        for index, result in enumerate(trial_results):
            results[index].append(result)

    return [median_scenario(scenario_results) for scenario_results in results]


def print_decision_table(scenarios: list[dict], projection_years: int):
    stay_home = [s for s in scenarios if s["scenario"] == "Stay Home"]
    others = [s for s in scenarios if s["scenario"] != "Stay Home"]
    others.sort(key=lambda x: x["total_net_worth"], reverse=True)

    all_sorted = stay_home + others

    baseline_nw = stay_home[0]["total_net_worth"] if stay_home else 0.0

    headers = [
        "Scenario",
        "Init Outlay",
        f"Yr {projection_years + 1} Outlay",
        "NPV Total Costs",
        "NPV Net Worth",
        "Percent Baseline",
    ]
    table = []

    for s in all_sorted:
        if s["total_net_worth"] < 0:
            pct_baseline = "UNDERWATER"
        elif baseline_nw != 0:
            pct_baseline = f"{(s['total_net_worth'] - baseline_nw) / s['total_net_worth'] * 100:+.1f}%"
        else:
            pct_baseline = "0.0%"

        row = [
            s["scenario"],
            f"${s['initial_outlay']:,.0f}",
            f"${s['end_year_outlay']:,.0f}",
            f"${s['total_costs']:,.0f}",
            f"${s['total_net_worth']:,.0f}",
            pct_baseline,
        ]
        table.append(row)

    print(tabulate(table, headers=headers, tablefmt="simple") + "\n")


def parse_float_with_commas(s: str) -> float:
    return float(str(s).replace(',', ''))


def main():
    parser = argparse.ArgumentParser(description="Real Estate vs Renting Decision Table Evaluator")

    parser.add_argument("config", help="Path to TOML configuration file with scenarios")
    parser.add_argument(
        "--total-capital", type=parse_float_with_commas, help="Override total liquid cash available upfront"
    )
    parser.add_argument("--monthly-budget", type=parse_float_with_commas, help="Override baseline monthly cash outlays")
    parser.add_argument(
        "--simulations",
        type=int,
        help="Number of Monte Carlo trials (default: 5000)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="Random seed for reproducible Monte Carlo trials (default: 42)",
    )

    args = parser.parse_args()

    defaults, scenarios_config = load_toml_config(args.config)

    if args.total_capital is not None:
        defaults["total_capital"] = args.total_capital
    if args.monthly_budget is not None:
        defaults["monthly_budget"] = args.monthly_budget

    simulations = args.simulations if args.simulations is not None else defaults["monte_carlo_simulations"]
    seed = args.seed if args.seed is not None else defaults["monte_carlo_seed"]
    if simulations < 1:
        parser.error("--simulations must be at least 1")

    for sc in scenarios_config:
        for key in ("total_capital", "monthly_budget"):
            if key not in sc:
                sc[key] = defaults[key]

    all_scenarios = run_monte_carlo(defaults, scenarios_config, simulations, seed)
    print_decision_table(all_scenarios, defaults["projection_years"])


if __name__ == "__main__":
    main()
