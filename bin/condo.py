#!/usr/bin/python3
import argparse
import math
import os
import random
import sys
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from statistics import stdev

from tabulate import tabulate

RENTER_START_RENTS = (900, 1100, 1300, 1500, 1700, 1900, 2100)
RENTER_PRUNING_FACTOR = 0.8

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
    monthly_factors = args.get("_mc_monthly_factors")
    if monthly_factors and name in monthly_factors:
        return monthly_factors[name][years * 12]

    factor = 1.0
    for year in range(years):
        factor *= 1 + annual_rate(args, name, year)
    return factor


def monthly_growth_factor(args: dict, name: str, month: int) -> float:
    monthly_factors = args.get("_mc_monthly_factors")
    if monthly_factors and name in monthly_factors:
        return monthly_factors[name][month]

    full_years, remaining_months = divmod(month, 12)
    factor = growth_factor(args, name, full_years)
    if remaining_months:
        factor *= (1 + annual_rate(args, name, full_years)) ** (remaining_months / 12.0)
    return factor


def monthly_stock_return(args: dict, name: str, year: int) -> float:
    monthly_returns = args.get("_mc_monthly_returns")
    if monthly_returns and name in monthly_returns:
        return monthly_returns[name][year]
    return (1 + annual_rate(args, name, year)) ** (1.0 / 12) - 1


def real_capital_value(args: dict, capital: float, month: int) -> float:
    return capital / monthly_growth_factor(args, "inflation_rate", month)


def signed_currency(value: float) -> str:
    sign = "+" if value >= 0 else "-"
    return f"{sign}${abs(value):,.0f}"


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
    std = args.get("standard_deduction", 0.0)
    fed_ded = interest_m + min(prop_tax_m, args["salt_cap"] / 12)
    fed_savings = args["fed_tax_rate"] * max(0.0, fed_ded - std / 12)
    state_savings = args["state_tax"] * max(0.0, interest_m + prop_tax_m - args["state_std_deduction"] / 12)
    return fed_savings + state_savings


def debt_to_income_ratio(args: dict, monthly_outlay: float) -> float:
    annual_income = args.get("annual_income")
    if annual_income is None:
        annual_income = args.get("monthly_budget", 0.0) * 12
    if annual_income <= 0:
        return float("inf") if monthly_outlay > 0 else 0.0
    return monthly_outlay * 12 / annual_income


def monthly_pmi(args: dict, loan_amt: float, balance: float, home_value: float) -> float:
    if args["down_payment_pct"] >= 0.20 or balance <= 0:
        return 0.0
    if home_value > 0 and balance / home_value > 0.80:
        return loan_amt * args["pmi_rate"] / 12
    return 0.0


def stock_gains_tax(args: dict, stock_gain: float) -> float:
    annual_room = max(0.0, args["cap_gains_0pct"] - args["taxable_income"])
    taxable_gain = max(0.0, stock_gain - annual_room)
    return taxable_gain * args["cap_gains_tax"] + stock_gain * args["state_tax"]


def harvest_gains(args: dict, stocks: float, cost_basis: float) -> tuple[float, float]:
    annual_room = max(0.0, args["cap_gains_0pct"] - args["taxable_income"])
    unrealized_gain = max(0.0, stocks - cost_basis)
    realized = min(unrealized_gain, annual_room)
    if realized <= 0.0:
        return stocks, cost_basis
    stocks -= realized * args["state_tax"]
    cost_basis += realized
    return stocks, cost_basis


def annual_insurance(args: dict) -> float:
    if args["monthly_assessment"] > 0:
        return args["condo_insurance_annual"]
    return args["house_insurance_annual"]


def amortized_payment(loan_amt: float, r: float, months: int) -> float:
    if months <= 0:
        return 0.0
    if r == 0:
        return loan_amt / months
    return loan_amt * (r * (1 + r) ** months) / ((1 + r) ** months - 1)


def months_to_payoff(balance: float, r: float, payment: float) -> float:
    if balance <= 0 or payment <= 0:
        return 0.0
    if r == 0:
        return math.ceil(balance / payment)
    if payment <= balance * r:
        return float("inf")
    return math.ceil(math.log(payment / (payment - balance * r)) / math.log(1 + r))


def _terminal_annual_rate(args: dict, name: str) -> float:
    paths = args.get("_mc_paths")
    if paths and name in paths:
        return paths[name][-1]
    return args[name]


def _mortgage_payoff_month(
    args: dict,
    balance: float,
    current_rate: float,
    current_r: float,
    current_pmt_min: float,
    elapsed_months: int,
    projection_years: int,
    term_months: int,
    end_tax: float,
    end_hoa: float,
    end_ins: float,
    end_maint: float,
    end_budget: float,
) -> int | None:
    if balance <= 0:
        return elapsed_months

    appreciation_rate = _terminal_annual_rate(args, "appreciation_rate")
    inflation_rate = _terminal_annual_rate(args, "inflation_rate")
    hoa_growth_rate = _terminal_annual_rate(args, "hoa_growth_rate")
    max_months = max(term_months, elapsed_months) + 1200
    terminal_year = max(0, projection_years - 1)

    for month in range(elapsed_months + 1, max_months + 1):
        years_after_projection = (month - 1) // 12 - terminal_year
        tax = end_tax * (1 + appreciation_rate) ** years_after_projection
        hoa = end_hoa * (1 + hoa_growth_rate) ** years_after_projection
        insurance = end_ins * (1 + inflation_rate) ** years_after_projection
        maintenance = end_maint * (1 + appreciation_rate) ** years_after_projection
        budget = end_budget * (1 + inflation_rate) ** years_after_projection

        interest = balance * current_r
        mandatory = current_pmt_min + tax + hoa + insurance + maintenance - monthly_tax_savings(args, interest, tax)
        extra = max(0.0, budget - mandatory) if current_rate > args["stock_return"] else 0.0
        payment = min(current_pmt_min + extra, balance + interest)
        balance = max(0.0, balance - (payment - interest))
        if balance < 1e-6:
            return month

    return None


def mortgage_rate_offer(args: dict, option_rate: float, year: int) -> float:
    path = args.get("_mc_mortgage_rate_path")
    if path is None:
        return option_rate
    anchor = args.get("_mc_mortgage_anchor", args["mortgage_rate"])
    return path[year] + (option_rate - anchor)


def get_stay_home_scenario(args: dict) -> dict:
    projection_years = args["projection_years"]
    projection_months = projection_years * 12
    stocks = args["total_capital"]
    cost_basis = stocks
    total_costs = 0.0
    lowest_total_capital = real_capital_value(args, stocks, 0)

    tax_m = args.get("annual_taxes", args.get("_stay_home_tax_annual", 600.0)) / 12

    for m in range(1, projection_months + 1):
        yr = (m - 1) // 12
        stocks *= 1 + monthly_stock_return(args, "stock_return", yr)

        inflation_factor = growth_factor(args, "inflation_rate", yr)
        tax_curr = tax_m * inflation_factor
        monthly_budget = args["monthly_budget"] * inflation_factor

        total_costs += tax_curr / monthly_growth_factor(args, "stock_return", m)
        net_cash_flow = monthly_budget - tax_curr
        stocks += net_cash_flow
        lowest_total_capital = min(lowest_total_capital, real_capital_value(args, stocks, m))
        if net_cash_flow > 0:
            cost_basis += net_cash_flow

        if m % 12 == 0 and m < projection_months:
            stocks, cost_basis = harvest_gains(args, stocks, cost_basis)

    stock_gain = max(0, stocks - cost_basis)
    stock_tax = stock_gains_tax(args, stock_gain)
    stocks_after_tax = stocks - stock_tax

    inflation_factor = growth_factor(args, "inflation_rate", projection_years)
    end_year_outlay = tax_m * inflation_factor

    return {
        "scenario": "Stay Home",
        "initial_outlay": tax_m,
        "extra_payment": 0.0,
        "mortgage_duration": 0.0,
        "end_year_outlay": end_year_outlay,
        "total_costs": total_costs,
        "debt_to_income": debt_to_income_ratio(args, tax_m),
        "max_drawdown": lowest_total_capital - args["total_capital"],
        "final_stocks": stocks_after_tax,
        "final_home_val": 0.0,
        "total_net_worth": stocks_after_tax / inflation_factor,
    }


def buyer_initial_outlay(args: dict, term_years: int, mortgage_rate: float) -> float:
    r = mortgage_rate / 12
    loan_amt = args["price"] * (1 - args["down_payment_pct"])
    pmt_min = amortized_payment(loan_amt, r, term_years * 12)
    annual_taxes = args.get("annual_taxes", args["price"] * args["effective_tax_rate"])
    tax_m = annual_taxes / 12
    hoa_m = args["monthly_assessment"]
    insurance_m = annual_insurance(args) / 12
    maint_m = (args["price"] * args["maintenance_pct"]) / 12
    pmi_curr = monthly_pmi(args, loan_amt, loan_amt, args["price"])
    return pmt_min + tax_m + hoa_m + insurance_m + maint_m + pmi_curr - monthly_tax_savings(args, loan_amt * r, tax_m)


def calculate_buyer_net_worth(
    args: dict,
    term_years: int = 15,
    mortgage_rate: float | None = None,
    record_schedule: bool = False,
    horizon_years: int | None = None,
) -> dict:
    projection_years = args["projection_years"]
    projection_months = projection_years * 12
    if horizon_years is not None:
        projection_years = horizon_years
        projection_months = horizon_years * 12
    if mortgage_rate is None:
        mortgage_rate = args["mortgage_rate"]
    r = mortgage_rate / 12

    dp_amt = args["price"] * args["down_payment_pct"]
    loan_amt = args["price"] - dp_amt

    term_months = term_years * 12
    pmt_min = amortized_payment(loan_amt, r, term_months)

    buyer_stocks = args["total_capital"] - dp_amt
    annual_taxes = args.get("annual_taxes", args["price"] * args["effective_tax_rate"])
    tax_m = annual_taxes / 12
    hoa_m = args["monthly_assessment"]
    insurance_m = annual_insurance(args) / 12
    maint_m = (args["price"] * args["maintenance_pct"]) / 12

    cost_basis = buyer_stocks
    total_costs = dp_amt
    lowest_total_capital = real_capital_value(args, buyer_stocks, 0)
    loan_balance = loan_amt

    current_rate = mortgage_rate
    current_r = r
    current_pmt_min = pmt_min

    pay_extra = False
    refinanced = False
    min_outlay_y1 = 0.0
    extra_payment_y1 = 0.0
    payoff_month = None
    schedule = [] if record_schedule else None

    for m in range(1, projection_months + 1):
        refinanced = False
        yr = (m - 1) // 12
        buyer_stocks *= 1 + monthly_stock_return(args, "stock_return", yr)

        appr_factor = growth_factor(args, "appreciation_rate", yr)
        infl_factor = growth_factor(args, "inflation_rate", yr)
        hoa_growth_factor = growth_factor(args, "hoa_growth_rate", yr)
        tax_curr = tax_m * appr_factor
        hoa_curr = hoa_m * hoa_growth_factor
        insurance_curr = insurance_m * infl_factor
        maint_curr = maint_m * appr_factor

        if loan_balance > 0:
            interest_curr = loan_balance * current_r
            pmt_curr_min = current_pmt_min
        else:
            interest_curr = 0.0
            pmt_curr_min = 0.0

        pmi_curr = monthly_pmi(args, loan_amt, loan_balance, args["price"] * appr_factor)

        mandatory = (
            pmt_curr_min
            + tax_curr
            + hoa_curr
            + insurance_curr
            + maint_curr
            + pmi_curr
            - monthly_tax_savings(args, interest_curr, tax_curr)
        )
        monthly_budget = args["monthly_budget"] * infl_factor
        surplus = monthly_budget - mandatory

        if (m - 1) % 6 == 0:
            pay_extra = current_rate > args["stock_return"]

        if loan_balance > 0 and m > 1 and m % 12 == 1:
            offer = mortgage_rate_offer(args, mortgage_rate, yr)
            if offer < current_rate:
                remaining_months = max(1, term_months - (m - 1))
                proj_excess = max(surplus, 0.0) if pay_extra else 0.0
                payoff_horizon = months_to_payoff(loan_balance, current_r, current_pmt_min + proj_excess)
                if payoff_horizon != float("inf"):
                    remaining_months = min(remaining_months, int(payoff_horizon))
                new_pmt = amortized_payment(loan_balance, offer / 12, remaining_months)
                if (current_pmt_min - new_pmt) * remaining_months > args["refinance_cost"]:
                    current_rate = offer
                    current_r = offer / 12
                    current_pmt_min = new_pmt
                    refinanced = True

        if loan_balance > 0:
            desired_excess = surplus if pay_extra else 0.0
            desired_excess = max(0.0, min(desired_excess, loan_balance))
            payment = pmt_curr_min + desired_excess
            payment = min(payment, loan_balance + interest_curr)
        else:
            desired_excess = 0.0
            payment = 0.0

        principal = (payment - interest_curr) if loan_balance > 0 else 0.0
        if loan_balance > 0:
            loan_balance = max(0.0, loan_balance - principal)
            if loan_balance < 1e-6:
                loan_balance = 0.0
                if payoff_month is None:
                    payoff_month = m

        buyer_outlay = (
            payment
            + tax_curr
            + hoa_curr
            + insurance_curr
            + maint_curr
            + pmi_curr
            - monthly_tax_savings(args, interest_curr, tax_curr)
        )
        if refinanced:
            buyer_outlay += args["refinance_cost"]
        net_cash_flow = monthly_budget - buyer_outlay

        total_costs += buyer_outlay / monthly_growth_factor(args, "stock_return", m)
        buyer_stocks += net_cash_flow
        lowest_total_capital = min(lowest_total_capital, real_capital_value(args, buyer_stocks, m))
        if net_cash_flow > 0:
            cost_basis += net_cash_flow

        if m % 12 == 0 and m < projection_months:
            buyer_stocks, cost_basis = harvest_gains(args, buyer_stocks, cost_basis)

        if m == 1:
            min_outlay_y1 = mandatory
            extra_payment_y1 = max(0.0, payment - pmt_curr_min)

        if record_schedule:
            schedule.append(
                {
                    "month": m,
                    "payment": payment,
                    "interest": interest_curr,
                    "principal": principal,
                    "excess": max(0.0, payment - pmt_curr_min),
                    "balance": loan_balance,
                    "pay_extra": pay_extra,
                    "refinanced": refinanced,
                    "outlay": buyer_outlay,
                    "stocks": buyer_stocks,
                    "home_value": args["price"] * appr_factor,
                    "pmi": pmi_curr,
                }
            )

    stock_gain = max(0, buyer_stocks - cost_basis)
    stock_tax = stock_gains_tax(args, stock_gain)
    buyer_stocks_after_tax = buyer_stocks - stock_tax

    appreciation_factor = growth_factor(args, "appreciation_rate", projection_years)
    inflation_factor = growth_factor(args, "inflation_rate", projection_years)

    nominal_home_val = args["price"] * appreciation_factor
    selling_costs = nominal_home_val * args["selling_cost_pct"]
    home_gain = nominal_home_val - selling_costs - args["price"]
    taxable_home_gain = max(0, home_gain - args["home_gain_exclusion"])
    home_tax = taxable_home_gain * args["cap_gains_tax"] + home_gain * args["state_tax"]
    remaining_loan = loan_balance
    net_home = nominal_home_val - selling_costs - home_tax - remaining_loan

    final_home_val = net_home / inflation_factor
    final_net_worth = (buyer_stocks_after_tax / inflation_factor) + final_home_val

    hoa_factor = growth_factor(args, "hoa_growth_rate", projection_years)
    end_tax = tax_m * appreciation_factor
    end_hoa = hoa_m * hoa_factor
    end_ins = insurance_m * inflation_factor
    end_maint = maint_m * appreciation_factor
    if loan_balance > 0:
        end_interest = loan_balance * current_r
        end_pmt_min = current_pmt_min
        end_pmi = monthly_pmi(args, loan_amt, loan_balance, args["price"] * appreciation_factor)
        end_mandatory = (
            end_pmt_min
            + end_tax
            + end_hoa
            + end_ins
            + end_maint
            + end_pmi
            - monthly_tax_savings(args, end_interest, end_tax)
        )
        end_surplus = args["monthly_budget"] * inflation_factor - end_mandatory
        end_pay = current_rate > args["stock_return"]
        end_excess = end_surplus if end_pay else 0.0
        end_excess = max(0.0, min(end_excess, loan_balance))
        end_pmt = min(end_pmt_min + end_excess, loan_balance + end_interest)
    else:
        end_interest = 0.0
        end_pmt = 0.0
        end_pmi = 0.0
    end_year_outlay = (
        end_pmt + end_tax + end_hoa + end_ins + end_maint + end_pmi - monthly_tax_savings(args, end_interest, end_tax)
    )

    if payoff_month is None:
        payoff_month = _mortgage_payoff_month(
            args,
            loan_balance,
            current_rate,
            current_r,
            current_pmt_min,
            projection_months,
            projection_years,
            term_months,
            end_tax,
            end_hoa,
            end_ins,
            end_maint,
            args["monthly_budget"] * inflation_factor,
        )

    address = args.get("_address", "")
    if address:
        label = address
    else:
        label = f"Condo {term_years}-yr (${args['price']:,.0f} | Tax: ${annual_taxes:,.0f} | HOA: ${args['monthly_assessment']:.0f})"

    result = {
        "scenario": label,
        "initial_outlay": min_outlay_y1,
        "extra_payment": extra_payment_y1,
        "mortgage_duration": payoff_month / 12 if payoff_month is not None else float("inf"),
        "end_year_outlay": end_year_outlay,
        "total_costs": total_costs,
        "debt_to_income": debt_to_income_ratio(args, min_outlay_y1),
        "max_drawdown": lowest_total_capital - args["total_capital"],
        "final_stocks": buyer_stocks_after_tax,
        "final_home_val": final_home_val,
        "total_net_worth": final_net_worth,
    }
    if record_schedule:
        result["_schedule"] = schedule
        result["_term_years"] = term_years
        result["_rate"] = mortgage_rate
        result["_stocks_pre_tax"] = buyer_stocks
        result["_cost_basis"] = cost_basis
        result["_stock_gain"] = stock_gain
        result["_stock_tax"] = stock_tax
        result["_home_gain"] = home_gain
        result["_home_tax"] = home_tax
        result["_home_gross"] = nominal_home_val - selling_costs
        result["_net_home"] = net_home
    return result


def evaluate_mortgage_options(sc: dict) -> tuple[list[tuple], tuple]:
    options = sc.get("mortgage_options")
    if not options:
        options = [(sc.get("mortgage_term", 15), sc.get("mortgage_rate", 0.061))]
    results = []
    for option in options:
        if isinstance(option, dict):
            term_years = int(option["term"])
            rate = float(option["rate"])
        else:
            term_years = int(option[0])
            rate = float(option[1])
        res = calculate_buyer_net_worth(sc, term_years=term_years, mortgage_rate=rate)
        results.append((term_years, rate, res))
    best = max(results, key=lambda item: item[2]["total_net_worth"])
    return results, best


def choose_mortgage_for_scenario(sc: dict) -> tuple:
    _, best = evaluate_mortgage_options(sc)
    term_years, rate, res = best
    sc["_chosen_term"] = term_years
    sc["_chosen_rate"] = rate
    sc["_est_nw"] = res["total_net_worth"]
    return best


def get_base_renter_scenarios(args: dict) -> list[dict]:
    projection_years = args["projection_years"]
    projection_months = projection_years * 12
    renter_results = []

    renters_insurance_m = args["renters_insurance_annual"] / 12

    for start_rent in RENTER_START_RENTS:
        renter_stocks = args["total_capital"]
        cost_basis = renter_stocks
        total_costs = 0.0
        lowest_total_capital = real_capital_value(args, renter_stocks, 0)

        for m in range(1, projection_months + 1):
            yr = (m - 1) // 12
            renter_stocks *= 1 + monthly_stock_return(args, "stock_return", yr)

            rent_curr = start_rent * growth_factor(args, "rent_growth_rate", yr) * renter_rent_factor(args, yr)
            insurance_curr = renters_insurance_m * growth_factor(args, "inflation_rate", yr)
            moving_cost = renter_move_cost(args, yr) if m % 12 == 1 else 0.0
            renter_outlay = rent_curr + insurance_curr + moving_cost
            monthly_budget = args["monthly_budget"] * growth_factor(args, "inflation_rate", yr)

            total_costs += renter_outlay / monthly_growth_factor(args, "stock_return", m)
            net_cash_flow = monthly_budget - renter_outlay
            renter_stocks += net_cash_flow
            lowest_total_capital = min(lowest_total_capital, real_capital_value(args, renter_stocks, m))
            if net_cash_flow > 0:
                cost_basis += net_cash_flow

            if m % 12 == 0 and m < projection_months:
                renter_stocks, cost_basis = harvest_gains(args, renter_stocks, cost_basis)

        stock_gain = max(0, renter_stocks - cost_basis)
        stock_tax = stock_gains_tax(args, stock_gain)
        renter_stocks_after_tax = renter_stocks - stock_tax

        initial_outlay = start_rent * renter_rent_factor(args, 0) + renters_insurance_m + renter_move_cost(args, 0)
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
                "extra_payment": 0.0,
                "mortgage_duration": 0.0,
                "end_year_outlay": end_year_outlay,
                "total_costs": total_costs,
                "debt_to_income": debt_to_income_ratio(args, initial_outlay),
                "max_drawdown": lowest_total_capital - args["total_capital"],
                "final_stocks": renter_stocks_after_tax,
                "final_home_val": 0.0,
                "total_net_worth": renter_stocks_after_tax / growth_factor(args, "inflation_rate", projection_years),
            }
        )

    return renter_results


def _resolve_mortgage(args: dict) -> None:
    options = args.get("mortgage_options")
    if options:
        normalized = []
        for opt in options:
            if isinstance(opt, dict):
                normalized.append({"term": int(opt["term"]), "rate": float(opt["rate"])})
            else:
                normalized.append({"term": int(opt[0]), "rate": float(opt[1])})
        args["mortgage_options"] = normalized
    else:
        args["mortgage_options"] = [
            {
                "term": int(args.get("mortgage_term", 15)),
                "rate": float(args.get("mortgage_rate", 0.061)),
            }
        ]
    args["mortgage_rate"] = args["mortgage_options"][0]["rate"]


def load_toml_config(filepath: str) -> tuple[dict, list[dict]]:
    with open(filepath, "rb") as f:
        data = tomllib.load(f)

    defaults = {
        "total_capital": 130000,
        "annual_income": 77000,
        "debt_to_income": 0.43,
        "monthly_budget": 2100,
        "projection_years": 30,
        "mortgage_options": None,
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
        "standard_deduction": 31500,
        "state_std_deduction": 10400,
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
        "refinance_cost": 5000,
        "stock_volatility": 0.18,
        "appreciation_volatility": 0.10,
        "inflation_volatility": 0.015,
        "rent_growth_volatility": 0.02,
        "hoa_growth_volatility": 0.03,
        "mortgage_rate_volatility": 0.01,
        "appreciation_inflation_beta": 0.9,
        "rent_growth_inflation_beta": 0.75,
        "hoa_growth_inflation_beta": 0.35,
        "stock_inflation_beta": 0.15,
        "mortgage_inflation_beta": 0.7,
        "macro_shock_beta": 0.3,
        "appreciation_rate_sensitivity": -1.5,
        "tax_volatility": 0.10,
        "maintenance_volatility": 0.35,
        "inflation_ar_coeffs": [0.85],
        "appreciation_ar_coeffs": [0.70],
        "rent_growth_ar_coeffs": [0.60],
        "hoa_growth_ar_coeffs": [0.60],
        "stock_ar_coeffs": [],
        "monte_carlo_simulations": 1000,
        "monte_carlo_seed": 42,
        "max_debt_to_income": 0.43,
    }

    for key in defaults:
        if key in data:
            defaults[key] = data[key]
    if "monthly_budget" not in data:
        defaults["monthly_budget"] = defaults["annual_income"] / 12 * defaults["debt_to_income"]
    if "taxable_income" not in data:
        defaults["taxable_income"] = max(0.0, defaults["annual_income"] - defaults["standard_deduction"])
    _resolve_mortgage(defaults)

    scenarios = []
    if "scenario" in data:
        for address, params in data["scenario"].items():
            merged = defaults.copy()
            merged.update(params)
            if "annual_taxes" not in params:
                merged["annual_taxes"] = merged["price"] * merged["effective_tax_rate"]
            merged["_address"] = address
            _resolve_mortgage(merged)
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


def _solve_linear(a: list[list[float]], b: list[float]) -> list[float]:
    n = len(b)
    for col in range(n):
        pivot = col
        for row in range(col + 1, n):
            if abs(a[row][col]) > abs(a[pivot][col]):
                pivot = row
        if abs(a[pivot][col]) < 1e-12:
            raise ValueError("AR coefficients do not describe a stationary process")
        if pivot != col:
            a[col], a[pivot] = a[pivot], a[col]
            b[col], b[pivot] = b[pivot], b[col]
        for row in range(col + 1, n):
            factor = a[row][col] / a[col][col]
            if factor == 0.0:
                continue
            for k in range(col, n):
                a[row][k] -= factor * a[col][k]
            b[row] -= factor * b[col]
    x = [0.0] * n
    for row in range(n - 1, -1, -1):
        total = b[row]
        for k in range(row + 1, n):
            total -= a[row][k] * x[k]
        x[row] = total / a[row][row]
    return x


def _ar_autocorrelations(phi: list[float]) -> list[float]:
    p = len(phi)
    a = [[0.0] * p for _ in range(p)]
    b = [0.0] * p
    for r in range(p):
        b[r] = phi[r]
        for c in range(p):
            coeff = 1.0 if r == c else 0.0
            if r > c:
                coeff -= phi[r - c - 1]
            if r + c + 2 <= p:
                coeff -= phi[r + c + 1]
            a[r][c] = coeff
    return _solve_linear(a, b)


def _ar_innov_sigma(phi: list[float], volatility: float) -> float:
    if not phi:
        return volatility
    rho = _ar_autocorrelations(phi)
    scale = 1.0 - sum(ph * r for ph, r in zip(phi, rho))
    if scale <= 0.0 or any(abs(r) >= 1.0 for r in rho):
        raise ValueError(
            f"AR coefficients {phi} do not describe a stationary process "
            f"(Yule-Walker variance scale {scale:.3g} <= 0)"
        )
    return volatility * math.sqrt(scale)


def ar_log_returns(
    rng: random.Random,
    mean_returns: list[float],
    volatility: float,
    ar_coeffs: list[float] | float,
    minimum: float,
    maximum: float,
    shared: list[float] | None = None,
    shared_beta: float = 0.0,
) -> list[float]:
    if isinstance(ar_coeffs, (int, float)):
        coeffs = [float(ar_coeffs)] if ar_coeffs else []
    else:
        coeffs = [float(c) for c in ar_coeffs]
    innov_sigma = _ar_innov_sigma(coeffs, volatility)
    idio_sigma = innov_sigma * math.sqrt(max(0.0, 1.0 - shared_beta**2))
    path = []
    history = []
    for t, mean in enumerate(mean_returns):
        w = sum(phi * past for phi, past in zip(coeffs, history))
        if shared is not None:
            w += innov_sigma * shared_beta * shared[t]
        w += rng.gauss(0, idio_sigma)
        history.insert(0, w)
        if len(history) > len(coeffs):
            history.pop()
        gross_mean = max(0.01, 1 + mean)
        value = math.exp(math.log(gross_mean) - 0.5 * volatility**2 + w) - 1
        path.append(min(max(value, minimum), maximum))
    return path


def make_market_paths(args: dict, rng: random.Random) -> dict:
    years = args["projection_years"]
    inflation_mean = args["inflation_rate"]
    macro_beta = args["macro_shock_beta"]

    macro = []
    shock = 0.0
    persistence = 0.3
    for _ in range(years):
        shock = persistence * shock + rng.gauss(0, math.sqrt(1 - persistence**2))
        macro.append(shock)

    inflation = ar_log_returns(
        rng,
        [inflation_mean] * years,
        args["inflation_volatility"],
        args["inflation_ar_coeffs"],
        -0.01,
        0.12,
    )

    expected_rate = args["mortgage_rate"] + args["mortgage_inflation_beta"] * (inflation[0] - inflation_mean)
    mortgage_rate = bounded_normal(
        rng,
        expected_rate + macro_beta * args["mortgage_rate_volatility"] * macro[0],
        args["mortgage_rate_volatility"],
        0.03,
        0.10,
    )
    rate_surprise = mortgage_rate - expected_rate

    mortgage_rate_path = [mortgage_rate]
    for i in range(1, years):
        mean = args["mortgage_rate"] + args["mortgage_inflation_beta"] * (inflation[i] - inflation_mean)
        mean += macro_beta * args["mortgage_rate_volatility"] * macro[i]
        value = bounded_normal(
            rng,
            0.7 * mortgage_rate_path[-1] + 0.3 * mean,
            args["mortgage_rate_volatility"],
            0.03,
            0.10,
        )
        mortgage_rate_path.append(value)

    appreciation_mean = [
        args["appreciation_rate"]
        + args["appreciation_inflation_beta"] * (infl - inflation_mean)
        + args["appreciation_rate_sensitivity"] * rate_surprise
        for infl in inflation
    ]
    appreciation = ar_log_returns(
        rng,
        appreciation_mean,
        args["appreciation_volatility"],
        args["appreciation_ar_coeffs"],
        -0.30,
        0.30,
        shared=macro,
        shared_beta=macro_beta,
    )
    rent_growth = ar_log_returns(
        rng,
        [args["rent_growth_rate"] + args["rent_growth_inflation_beta"] * (infl - inflation_mean) for infl in inflation],
        args["rent_growth_volatility"],
        args["rent_growth_ar_coeffs"],
        -0.05,
        0.12,
        shared=macro,
        shared_beta=macro_beta,
    )
    hoa_growth = ar_log_returns(
        rng,
        [args["hoa_growth_rate"] + args["hoa_growth_inflation_beta"] * (infl - inflation_mean) for infl in inflation],
        args["hoa_growth_volatility"],
        args["hoa_growth_ar_coeffs"],
        -0.05,
        0.20,
        shared=macro,
        shared_beta=macro_beta,
    )
    stock = ar_log_returns(
        rng,
        [args["stock_return"] + args["stock_inflation_beta"] * (infl - inflation_mean) for infl in inflation],
        args["stock_volatility"],
        args["stock_ar_coeffs"],
        -0.80,
        1.00,
        shared=macro,
        shared_beta=macro_beta,
    )
    return {
        "stock_return": stock,
        "inflation_rate": inflation,
        "appreciation_rate": appreciation,
        "rent_growth_rate": rent_growth,
        "hoa_growth_rate": hoa_growth,
        "mortgage_rate": mortgage_rate,
        "mortgage_rate_path": mortgage_rate_path,
    }


def make_trial_args(args: dict, market: dict, rng: random.Random, include_renter_risk: bool = False) -> dict:
    trial = args.copy()
    trial["_mc_paths"] = {key: values for key, values in market.items() if key != "mortgage_rate"}
    monthly_factors = {}
    monthly_returns = {}
    for name, rates in trial["_mc_paths"].items():
        factors = [1.0]
        year_returns = []
        for rate in rates:
            monthly_return = (1 + rate) ** (1.0 / 12) - 1
            year_returns.append(monthly_return)
            for _ in range(12):
                factors.append(factors[-1] * (1 + monthly_return))
        monthly_factors[name] = factors
        monthly_returns[name] = year_returns
    trial["_mc_monthly_factors"] = monthly_factors
    trial["_mc_monthly_returns"] = monthly_returns
    trial["_mc_mortgage_anchor"] = args["mortgage_rate"]
    trial["mortgage_rate"] = market["mortgage_rate"]
    trial["_mc_mortgage_rate_path"] = market["mortgage_rate_path"]
    trial["maintenance_pct"] = args["maintenance_pct"] * lognormal_factor(
        rng, args["maintenance_volatility"], 0.50, 3.00
    )
    if "annual_taxes" in args:
        trial["annual_taxes"] = args["annual_taxes"] * lognormal_factor(rng, args["tax_volatility"], 0.80, 1.25)
    else:
        trial["_stay_home_tax_annual"] = 600.0 * lognormal_factor(rng, args["tax_volatility"], 0.80, 1.25)
    if include_renter_risk:
        rent_factor = 1.0
        trial["_mc_move_costs"] = []
        trial["_mc_rent_factors"] = []
        for _ in range(args["projection_years"] + 1):
            if rng.random() < args["forced_move_probability"]:
                rent_factor *= 1 + args["moving_rent_premium"]
                move_cost = args["moving_cost"] * lognormal_factor(rng, args["moving_cost_volatility"], 0.70, 1.50)
            else:
                move_cost = 0.0
            trial["_mc_move_costs"].append(move_cost)
            trial["_mc_rent_factors"].append(rent_factor)
    return trial


def filter_expensive_scenarios(defaults: dict, scenarios_config: list[dict]) -> tuple[list[dict], list[dict], float]:
    renter_baseline = get_base_renter_scenarios(defaults)[-1]["total_net_worth"]
    renter_bar = renter_baseline * RENTER_PRUNING_FACTOR
    kept = []
    skipped = []
    for sc in scenarios_config:
        estimate = sc["_est_nw"]
        if estimate < renter_bar:
            skipped.append({"address": sc.get("_address", ""), "price": sc["price"], "est_nw": estimate})
        else:
            kept.append(sc)
    return kept, skipped, renter_bar


def aggregate_scenario(results: list[dict | None]) -> dict | None:
    valid = [r for r in results if r is not None]
    if not valid:
        return None
    n = len(valid)
    row = dict(valid[0])
    for key in valid[0]:
        if key != "scenario":
            row[key] = sorted(r[key] for r in valid)[n // 2]
    return row


_MASK64 = (1 << 64) - 1


def derive_seed(seed: int, *parts: int) -> int:
    x = (seed & _MASK64) ^ 0x9E3779B97F4A7C15
    for part in parts:
        x ^= part & _MASK64
        x = (x * 0xBF58476D1CE4E5B9 + 0x94D049BB133111EB) & _MASK64
    x ^= x >> 30
    x = (x * 0xBF58476D1CE4E5B9) & _MASK64
    x ^= x >> 27
    x = (x * 0x94D049BB133111EB) & _MASK64
    x ^= x >> 31
    return x & _MASK64


def bootstrap_median_se(samples: list[float], resamples: int = 200) -> float:
    if len(samples) < 2:
        return 0.0
    rng = random.Random(0)
    n = len(samples)
    medians = []
    for _ in range(resamples):
        resample = [samples[rng.randrange(n)] for _ in range(n)]
        medians.append(sorted(resample)[n // 2])
    return stdev(medians)


def _bootstrap_se_from_nw(nw_sorted: list[float]) -> float:
    return bootstrap_median_se(nw_sorted)


def _run_one_simulation(sim: int, defaults: dict, scenarios_config: list[dict], seed: int) -> list[dict | None]:
    market = make_market_paths(defaults, random.Random(derive_seed(seed, sim, 0)))
    trial_defaults = make_trial_args(
        defaults, market, random.Random(derive_seed(seed, sim, 1)), include_renter_risk=True
    )
    trial_results: list[dict | None] = [
        get_stay_home_scenario(trial_defaults),
        *get_base_renter_scenarios(trial_defaults),
    ]
    for index, sc_config in enumerate(scenarios_config):
        trial_scenario = make_trial_args(sc_config, market, random.Random(derive_seed(seed, sim, 2, index)))
        term_years = trial_scenario["_chosen_term"]
        mortgage_rate = trial_scenario["_chosen_rate"]
        max_dti = trial_scenario.get("max_debt_to_income", 0.43)
        if (
            debt_to_income_ratio(trial_scenario, buyer_initial_outlay(trial_scenario, term_years, mortgage_rate))
            > max_dti
        ):
            trial_results.append(None)
            continue
        trial_results.append(
            calculate_buyer_net_worth(trial_scenario, term_years=term_years, mortgage_rate=mortgage_rate)
        )
    return trial_results


def run_monte_carlo(
    defaults: dict,
    scenarios_config: list[dict],
    simulations: int,
    seed: int,
    skip_expensive: bool = True,
    workers: int | None = None,
) -> tuple[list[dict], list[list[dict]], dict]:
    skipped = []
    renter_bar = None
    if skip_expensive:
        scenarios_config, skipped, renter_bar = filter_expensive_scenarios(defaults, scenarios_config)

    n_workers = min(workers if workers and workers > 0 else (os.cpu_count() or 1), simulations)
    task = partial(_run_one_simulation, defaults=defaults, scenarios_config=scenarios_config, seed=seed)
    chunksize = max(1, simulations // (n_workers * 4))
    results = [[] for _ in range(1 + len(RENTER_START_RENTS) + len(scenarios_config))]
    skip_counts = [0] * len(scenarios_config)
    renter_offset = 1 + len(RENTER_START_RENTS)
    with ProcessPoolExecutor(max_workers=n_workers) as executor:
        per_sim = executor.map(task, range(simulations), chunksize=chunksize)
        for trial_results in per_sim:
            for index, result in enumerate(trial_results):
                results[index].append(result)
                if result is None and index >= renter_offset:
                    skip_counts[index - renter_offset] += 1
        bootstrap_se = list(
            executor.map(
                _bootstrap_se_from_nw,
                (
                    sorted(r["total_net_worth"] for r in scenario_results if r is not None)
                    for scenario_results in results
                ),
                chunksize=1,
            )
        )

    return (
        [s for s in (aggregate_scenario(scenario_results) for scenario_results in results) if s is not None],
        results,
        {
            "renter_bar": renter_bar,
            "skipped": skipped,
            "bootstrap_se": bootstrap_se,
            "dti_skipped": [
                {"address": sc.get("_address", ""), "price": sc["price"], "skipped": count}
                for sc, count in zip(scenarios_config, skip_counts)
                if count
            ],
        },
    )


def print_decision_table(scenarios: list[dict], projection_years: int):
    stay_home = [s for s in scenarios if s["scenario"] == "Stay Home"]
    others = [s for s in scenarios if s["scenario"] != "Stay Home"]
    others.sort(key=lambda x: x["total_net_worth"], reverse=True)

    all_sorted = stay_home + others

    headers = [
        "Scenario",
        "Min Outlay",
        "Extra Payment",
        "Mortgage Duration",
        f"Yr {projection_years + 1} Outlay",
        "NPV Total Costs",
        "NPV Net Worth",
        "Debt to Income",
        "Max Drawdown",
    ]
    table = []

    for s in all_sorted:
        row = [
            s["scenario"],
            f"${s['initial_outlay']:,.0f}",
            f"${s['extra_payment']:,.0f}" if s["mortgage_duration"] else "-",
            (
                f"{s['mortgage_duration']:.1f} yr"
                if s["mortgage_duration"] > 0 and math.isfinite(s["mortgage_duration"])
                else "N/A" if not math.isfinite(s["mortgage_duration"]) else "-"
            ),
            f"${s['end_year_outlay']:,.0f}",
            f"${s['total_costs']:,.0f}",
            f"${s['total_net_worth']:,.0f}",
            f"{s['debt_to_income']:.1%}",
            signed_currency(s["max_drawdown"]),
        ]
        table.append(row)

    print(tabulate(table, headers=headers, tablefmt="simple") + "\n")


def print_risk_summary_table(results: list[list[dict | None]]) -> None:
    def summarize(scenario_results: list[dict | None]) -> tuple | None:
        valid = [(i, r) for i, r in enumerate(scenario_results) if r is not None]
        if not valid:
            return None
        name = valid[0][1]["scenario"]
        nw = sorted(r["total_net_worth"] for _, r in valid)
        n = len(nw)
        nw_median = nw[n // 2]
        beat_home = sum(1 for i, r in valid if r["total_net_worth"] > results[0][i]["total_net_worth"]) / n * 100
        underwater = sum(1 for value in nw if value < 0) / n * 100
        return (
            name,
            beat_home,
            underwater,
            nw[int(0.25 * (n - 1))],
            nw_median,
            nw[int(0.75 * (n - 1))],
        )

    rows = [summarize(results[0])] + sorted(
        (row for row in (summarize(scenario_results) for scenario_results in results[1:]) if row is not None),
        key=lambda row: row[4],
        reverse=True,
    )
    headers = ["Scenario", "P(Beat Home)", "Underwater", "NW P25", "NW Median", "NW P75"]
    table = [
        [
            name,
            f"{beat_home:.1f}%",
            f"{underwater:.1f}%",
            f"${p25:,.0f}",
            f"${p50:,.0f}",
            f"${p75:,.0f}",
        ]
        for name, beat_home, underwater, p25, p50, p75 in rows
    ]
    print("Risk Summary (across all trials):")
    print(tabulate(table, headers=headers, tablefmt="simple") + "\n")


def print_convergence_note(results: list[list[dict | None]], bootstrap_se: list[float] | None = None) -> None:
    worst = None
    for index, scenario_results in enumerate(results):
        scenario_results = [r for r in scenario_results if r is not None]
        if not scenario_results:
            continue
        nw = sorted(r["total_net_worth"] for r in scenario_results)
        n = len(nw)
        nw_median = nw[n // 2]
        se = bootstrap_se[index] if bootstrap_se else bootstrap_median_se(nw)
        relative = se / abs(nw_median) if nw_median != 0 else 0.0
        if worst is None or relative > worst[2]:
            worst = (scenario_results[0]["scenario"], se, relative)
    if worst is None:
        return
    name, se, relative = worst
    if relative <= 0.05:
        return
    print(
        f"Warning: median net worth convergence is weakest for {name}: "
        f"\u00b1${se:,.0f} ({relative * 100:.1f}% of |median|)."
    )
    print("  Consider increasing --simulations for a tighter estimate.")


def print_skipped_note(skip_info: dict) -> None:
    skipped = skip_info["skipped"]
    if not skipped:
        return
    renter_bar = skip_info["renter_bar"]
    print(
        f"Skipped {len(skipped)} scenario(s) whose deterministic net worth falls below the "
        f"{RENTER_PRUNING_FACTOR:.0%} of the worst-case renter "
        f"(${RENTER_START_RENTS[-1]:,}/mo) baseline: ${renter_bar:,.0f}:"
    )
    for item in skipped:
        print(f"  - {item['address']} (${item['price']:,.0f}) est net worth ${item['est_nw']:,.0f}")
    print()


def print_dti_skip_note(skip_info: dict) -> None:
    dti_skipped = skip_info.get("dti_skipped")
    if not dti_skipped:
        return
    print("Skipped Monte Carlo trials where the year-one Debt-to-Income ratio exceeded the cap:")
    for item in dti_skipped:
        print(f"  - {item['address']} (${item['price']:,.0f}): skipped {item['skipped']} trial(s)")
    print()


def parse_float_with_commas(s: str) -> float:
    return float(str(s).replace(',', ''))


def main():
    parser = argparse.ArgumentParser(description="Real Estate vs Renting Decision Table Evaluator")

    parser.add_argument("config", help="Path to TOML configuration file with scenarios")
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
    parser.add_argument(
        "--workers",
        type=int,
        help="Number of parallel worker processes (default: CPU count)",
    )
    parser.add_argument(
        "--no-skip",
        action="store_true",
        help="Run Monte Carlo simulations for every scenario, even ones whose deterministic "
        "net worth can't beat the worst-case renter baseline",
    )

    args = parser.parse_args()

    defaults, scenarios_config = load_toml_config(args.config)

    for sc in scenarios_config:
        choose_mortgage_for_scenario(sc)

    simulations = args.simulations if args.simulations is not None else defaults["monte_carlo_simulations"]
    seed = args.seed if args.seed is not None else defaults["monte_carlo_seed"]
    if simulations < 1:
        parser.error("--simulations must be at least 1")

    all_scenarios, raw_results, skip_info = run_monte_carlo(
        defaults,
        scenarios_config,
        simulations,
        seed,
        skip_expensive=not args.no_skip,
        workers=args.workers,
    )
    print_decision_table(all_scenarios, defaults["projection_years"])
    print_risk_summary_table(raw_results)
    print_convergence_note(raw_results, skip_info.get("bootstrap_se"))
    print_skipped_note(skip_info)
    print_dti_skip_note(skip_info)


if __name__ == "__main__":
    main()
