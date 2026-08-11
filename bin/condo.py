#!/usr/bin/python3
import argparse
import sys

from tabulate import tabulate

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        print("Error: TOML support requires Python 3.11+ or 'tomli' package. Install with: pip install tomli")
        sys.exit(1)


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
    stock_return_m = args["stock_return"] / 12
    stocks = args["total_capital"]
    cost_basis = stocks
    total_costs = 0.0

    tax_m = 600.0 / 12

    for m in range(1, projection_months + 1):
        stocks *= 1 + stock_return_m
        yr = (m - 1) // 12

        tax_curr = tax_m * ((1 + args["inflation_rate"]) ** yr)
        monthly_budget = args["monthly_budget"] * ((1 + args["inflation_rate"]) ** yr)

        total_costs += tax_curr / ((1 + args["inflation_rate"]) ** (m / 12.0))
        net_cash_flow = monthly_budget - tax_curr
        stocks += net_cash_flow
        if net_cash_flow > 0:
            cost_basis += net_cash_flow

    stock_gain = max(0, stocks - cost_basis)
    stock_tax = stock_gains_tax(args, stock_gain, projection_years)
    stocks_after_tax = stocks - stock_tax

    inflation_factor = (1 + args["inflation_rate"]) ** projection_years
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
    stock_return_m = args["stock_return"] / 12
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
        buyer_stocks *= 1 + stock_return_m
        yr = (m - 1) // 12

        appr_factor = (1 + args["appreciation_rate"]) ** yr
        infl_factor = (1 + args["inflation_rate"]) ** yr
        hoa_growth_factor = (1 + args["hoa_growth_rate"]) ** yr
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

        total_costs += buyer_outlay / ((1 + args["inflation_rate"]) ** (m / 12.0))
        net_cash_flow = monthly_budget - buyer_outlay
        buyer_stocks += net_cash_flow
        if net_cash_flow > 0:
            cost_basis += net_cash_flow

    stock_gain = max(0, buyer_stocks - cost_basis)
    stock_tax = stock_gains_tax(args, stock_gain, projection_years)
    buyer_stocks_after_tax = buyer_stocks - stock_tax

    appreciation_factor = (1 + args["appreciation_rate"]) ** projection_years
    inflation_factor = (1 + args["inflation_rate"]) ** projection_years

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

    hoa_factor = (1 + args["hoa_growth_rate"]) ** projection_years
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
    stock_return_m = args["stock_return"] / 12
    renter_results = []

    for start_rent in [1300, 1500, 1700, 1900, 2100, 2300]:
        renter_stocks = args["total_capital"]
        cost_basis = renter_stocks
        total_costs = 0.0

        for m in range(1, projection_months + 1):
            renter_stocks *= 1 + stock_return_m
            yr = (m - 1) // 12

            rent_curr = start_rent * ((1 + args["rent_growth_rate"]) ** yr)
            monthly_budget = args["monthly_budget"] * ((1 + args["inflation_rate"]) ** yr)

            total_costs += rent_curr / ((1 + args["inflation_rate"]) ** (m / 12.0))
            net_cash_flow = monthly_budget - rent_curr
            renter_stocks += net_cash_flow
            if net_cash_flow > 0:
                cost_basis += net_cash_flow

        stock_gain = max(0, renter_stocks - cost_basis)
        stock_tax = stock_gains_tax(args, stock_gain, projection_years)
        renter_stocks_after_tax = renter_stocks - stock_tax

        end_year_outlay = start_rent * ((1 + args["rent_growth_rate"]) ** projection_years)

        scenario_name = f"Rent at ${start_rent}/mo"

        renter_results.append(
            {
                "scenario": scenario_name,
                "initial_outlay": float(start_rent),
                "end_year_outlay": end_year_outlay,
                "total_costs": total_costs,
                "final_stocks": renter_stocks_after_tax,
                "final_home_val": 0.0,
                "total_net_worth": renter_stocks_after_tax / ((1 + args["inflation_rate"]) ** projection_years),
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

    args = parser.parse_args()

    defaults, scenarios_config = load_toml_config(args.config)

    if args.total_capital is not None:
        defaults["total_capital"] = args.total_capital
    if args.monthly_budget is not None:
        defaults["monthly_budget"] = args.monthly_budget

    for sc in scenarios_config:
        for key in ("total_capital", "monthly_budget"):
            if key not in sc:
                sc[key] = defaults[key]

    all_scenarios = []

    all_scenarios.append(get_stay_home_scenario(defaults))
    all_scenarios.extend(get_base_renter_scenarios(defaults))

    for sc_config in scenarios_config:
        sc = calculate_buyer_net_worth(sc_config, term_years=sc_config["mortgage_term"])
        all_scenarios.append(sc)

    print_decision_table(all_scenarios, defaults["projection_years"])


if __name__ == "__main__":
    main()
