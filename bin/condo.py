#!/usr/bin/python3
import argparse

from tabulate import tabulate


def calculate_buyer_net_worth(args: dict, term_years: int = 15, mortgage_rate: float = None) -> dict:
    if mortgage_rate is None:
        mortgage_rate = args["mortgage_rate"]
    stock_return_m = args["stock_return"] / 12
    r = mortgage_rate / 12

    dp_amt = args["price"] * args["down_payment_pct"]
    loan_amt = args["price"] - dp_amt

    term_months = term_years * 12
    pmt = loan_amt * (r * (1 + r) ** term_months) / ((1 + r) ** term_months - 1)

    buyer_stocks = args["total_capital"] - dp_amt
    tax_m = args["annual_taxes"] / 12
    hoa_m = args["monthly_assessment"]

    base_outlay_y1 = pmt + tax_m + hoa_m
    total_costs = dp_amt

    for m in range(1, 361):
        buyer_stocks *= 1 + stock_return_m
        yr = (m - 1) // 12

        tax_curr = tax_m * ((1 + args["inflation_rate"]) ** yr)
        hoa_curr = hoa_m * ((1 + args["inflation_rate"]) ** yr)
        pmt_curr = pmt if m <= term_months else 0.0

        buyer_outlay = pmt_curr + tax_curr + hoa_curr
        monthly_budget = args["monthly_budget"] * ((1 + args["inflation_rate"]) ** yr)

        total_costs += buyer_outlay / ((1 + args["inflation_rate"]) ** (m / 12.0))
        buyer_stocks += monthly_budget - buyer_outlay

    final_home_val = (args["price"] * ((1 + args["appreciation_rate"]) ** 30)) / ((1 + args["inflation_rate"]) ** 30)
    final_net_worth = (buyer_stocks / ((1 + args["inflation_rate"]) ** 30)) + final_home_val

    y16_outlay = (pmt if term_months > 180 else 0.0) + (tax_m + hoa_m) * ((1 + args["inflation_rate"]) ** 15)
    y31_outlay = (pmt if term_months > 360 else 0.0) + (tax_m + hoa_m) * ((1 + args["inflation_rate"]) ** 30)

    scenario_name = f"Condo {term_years}-yr (${args['price']:,.0f} | Tax: ${args['annual_taxes']:,.0f} | HOA: ${args['monthly_assessment']:.0f})"
    if buyer_stocks < 0:
        scenario_name += " !!UNDERWATER"

    return {
        "scenario": scenario_name,
        "initial_outlay": base_outlay_y1,
        "y16_outlay": y16_outlay,
        "y31_outlay": y31_outlay,
        "total_costs": total_costs,
        "final_stocks": buyer_stocks,
        "final_home_val": final_home_val,
        "total_net_worth": final_net_worth,
    }


def get_base_renter_scenarios(args: dict) -> list[dict]:
    stock_return_m = args["stock_return"] / 12
    renter_results = []

    for start_rent in [1300, 1500, 1700, 1900, 2100, 2300, 2500, 2700, 2900]:
        renter_stocks = args["total_capital"]
        total_costs = 0.0

        for m in range(1, 361):
            renter_stocks *= 1 + stock_return_m
            yr = (m - 1) // 12

            rent_curr = start_rent * ((1 + args["inflation_rate"]) ** yr)
            monthly_budget = args["monthly_budget"] * ((1 + args["inflation_rate"]) ** yr)

            total_costs += rent_curr / ((1 + args["inflation_rate"]) ** (m / 12.0))
            renter_stocks += monthly_budget - rent_curr

        y16_outlay = start_rent * ((1 + args["inflation_rate"]) ** 15)
        y31_outlay = start_rent * ((1 + args["inflation_rate"]) ** 30)

        scenario_name = f"Rent at ${start_rent}/mo"
        if renter_stocks < 0:
            scenario_name += " !!UNDERWATER"

        renter_results.append(
            {
                "scenario": scenario_name,
                "initial_outlay": float(start_rent),
                "y16_outlay": y16_outlay,
                "y31_outlay": y31_outlay,
                "total_costs": total_costs,
                "final_stocks": renter_stocks,
                "final_home_val": 0.0,
                "total_net_worth": renter_stocks / ((1 + args["inflation_rate"]) ** 30),
            }
        )

    return renter_results


def print_decision_table(scenarios: list[dict]):
    scenarios.sort(key=lambda x: x["total_net_worth"], reverse=True)

    headers = ["Scenario", "Init Outlay", "Yr 31 Outlay", "NPV Total Costs", "NPV Net Worth"]
    table = []

    for s in scenarios:
        row = [
            s['scenario'],
            f"${s['initial_outlay']:,.2f}",
            f"${s['y31_outlay']:,.2f}",
            f"${s['total_costs']:,.0f}",
            f"${s['total_net_worth']:,.0f}",
        ]
        table.append(row)

    print(tabulate(table, headers=headers, tablefmt="simple") + "\n")


def parse_float_with_commas(s: str) -> float:
    return float(str(s).replace(',', ''))


def main():
    parser = argparse.ArgumentParser(description="30-Year Real Estate vs Renting Decision Table Evaluator")

    parser.add_argument("--price", type=parse_float_with_commas, default=230000, help="Sale price of the target condo alternative")
    parser.add_argument("--annual-taxes", type=parse_float_with_commas, default=3152, help="Annual property taxes")
    parser.add_argument("--monthly-assessment", type=parse_float_with_commas, default=320, help="Monthly HOA assessment")

    parser.add_argument("--total-capital", type=parse_float_with_commas, default=130000, help="Total liquid cash available upfront")
    parser.add_argument("--monthly-budget", type=parse_float_with_commas, default=2100, help="Baseline monthly cash outlays")
    parser.add_argument(
        "--mortgage-rate", type=parse_float_with_commas, default=0.061, help="Annual mortgage interest rate (15-yr fixed)"
    )
    parser.add_argument(
        "--mortgage-rate-30", type=parse_float_with_commas, default=0.069, help="Annual mortgage interest rate (30-yr fixed)"
    )
    parser.add_argument("--down-payment-pct", type=parse_float_with_commas, default=0.20, help="Down payment fraction (e.g. 0.20)")
    parser.add_argument("--stock-return", type=parse_float_with_commas, default=0.07, help="Nominal annual stock market return")
    parser.add_argument("--inflation-rate", type=parse_float_with_commas, default=0.03, help="Annual inflation for rent/HOA/taxes")
    parser.add_argument("--appreciation-rate", type=parse_float_with_commas, default=0.03, help="Annual real estate appreciation rate")

    args = parser.parse_args()
    args_dict = vars(args)

    all_scenarios = get_base_renter_scenarios(args_dict)

    scenario_15_yr = calculate_buyer_net_worth(args_dict, term_years=15, mortgage_rate=args_dict["mortgage_rate"])
    all_scenarios.append(scenario_15_yr)

    scenario_30_yr = calculate_buyer_net_worth(args_dict, term_years=30, mortgage_rate=args_dict["mortgage_rate_30"])
    all_scenarios.append(scenario_30_yr)

    print_decision_table(all_scenarios)


if __name__ == "__main__":
    main()
