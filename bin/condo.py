#!/usr/bin/python3
import argparse

from tabulate import tabulate


def calculate_buyer_net_worth(args: dict) -> dict:
    stock_return_m = args["stock_return"] / 12
    r_15 = args["mortgage_rate"] / 12

    dp_amt = args["price"] * args["down_payment_pct"]
    loan_amt = args["price"] - dp_amt

    pmt_15 = loan_amt * (r_15 * (1 + r_15) ** 180) / ((1 + r_15) ** 180 - 1)

    buyer_stocks = args["total_capital"] - dp_amt
    tax_m = args["annual_taxes"] / 12
    hoa_m = args["monthly_assessment"]

    base_outlay_y1 = pmt_15 + tax_m + hoa_m

    for m in range(1, 361):
        buyer_stocks *= 1 + stock_return_m
        yr = (m - 1) // 12

        tax_curr = tax_m * ((1 + args["inflation_rate"]) ** yr)
        hoa_curr = hoa_m * ((1 + args["inflation_rate"]) ** yr)
        pmt_curr = pmt_15 if m <= 180 else 0.0

        buyer_outlay = pmt_curr + tax_curr + hoa_curr
        monthly_budget = args["base_monthly_budget"] * ((1 + args["inflation_rate"]) ** yr)

        buyer_stocks += monthly_budget - buyer_outlay

    final_home_val = args["price"] * ((1 + args["appreciation_rate"]) ** 30)
    final_net_worth = buyer_stocks + final_home_val

    y30_outlay = (tax_m + hoa_m) * ((1 + args["inflation_rate"]) ** 29)

    return {
        "scenario": f"Condo (${args['price']:,.0f} | Tax: ${args['annual_taxes']:,.0f} | HOA: ${args['monthly_assessment']:.0f})",
        "initial_outlay": base_outlay_y1,
        "y30_outlay": y30_outlay,
        "final_stocks": buyer_stocks,
        "final_home_val": final_home_val,
        "total_net_worth": final_net_worth,
    }


def get_base_renter_scenarios(args: dict) -> list[dict]:
    stock_return_m = args["stock_return"] / 12
    renter_results = []

    for start_rent in [1300, 1600, 1700, 1800, 2200]:
        renter_stocks = args["total_capital"]

        for m in range(1, 361):
            renter_stocks *= 1 + stock_return_m
            yr = (m - 1) // 12

            rent_curr = start_rent * ((1 + args["inflation_rate"]) ** yr)
            monthly_budget = args["base_monthly_budget"] * ((1 + args["inflation_rate"]) ** yr)

            renter_stocks += monthly_budget - rent_curr

        y30_outlay = start_rent * ((1 + args["inflation_rate"]) ** 29)

        renter_results.append(
            {
                "scenario": f"Renter (${start_rent}/mo starting rent)",
                "initial_outlay": float(start_rent),
                "y30_outlay": y30_outlay,
                "final_stocks": renter_stocks,
                "final_home_val": 0.0,
                "total_net_worth": renter_stocks,
            }
        )

    return renter_results


def print_decision_table(scenarios: list[dict]):
    scenarios.sort(key=lambda x: x["total_net_worth"], reverse=True)

    headers = ["Scenario", "Init Outlay", "Yr 30 Outlay", "Stocks", "Home Equity", "Net Worth"]
    table = []

    for s in scenarios:
        row = [
            s['scenario'],
            f"${s['initial_outlay']:,.2f}",
            f"${s['y30_outlay']:,.2f}",
            f"${s['final_stocks']:,.0f}",
            f"${s['home_val_30'] if 'home_val_30' in s else s['final_home_val']:,.0f}",
            f"${s['total_net_worth']:,.0f}",
        ]
        table.append(row)

    print(tabulate(table, headers=headers, tablefmt="simple") + "\n")


def main():
    parser = argparse.ArgumentParser(description="30-Year Real Estate vs Renting Decision Table Evaluator")

    parser.add_argument("--price", type=float, default=230000, help="Sale price of the target condo alternative")
    parser.add_argument("--annual-taxes", type=float, default=3152, help="Annual property taxes")
    parser.add_argument("--monthly-assessment", type=float, default=320, help="Monthly HOA assessment")

    parser.add_argument("--total-capital", type=float, default=132940, help="Total liquid cash available upfront")
    parser.add_argument("--base-monthly-budget", type=float, default=2145.32, help="Baseline monthly cash outlays")
    parser.add_argument(
        "--mortgage-rate", type=float, default=0.061, help="Annual mortgage interest rate (15-yr fixed)"
    )
    parser.add_argument("--down-payment-pct", type=float, default=0.20, help="Down payment fraction (e.g. 0.20)")
    parser.add_argument("--stock-return", type=float, default=0.07, help="Nominal annual stock market return")
    parser.add_argument("--inflation-rate", type=float, default=0.03, help="Annual inflation for rent/HOA/taxes")
    parser.add_argument("--appreciation-rate", type=float, default=0.03, help="Annual real estate appreciation rate")

    args = parser.parse_args()
    args_dict = vars(args)

    all_scenarios = get_base_renter_scenarios(args_dict)

    new_buyer_scenario = calculate_buyer_net_worth(args_dict)
    all_scenarios.append(new_buyer_scenario)

    print_decision_table(all_scenarios)


if __name__ == "__main__":
    main()
