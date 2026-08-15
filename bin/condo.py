#!/usr/bin/python3
import argparse
import math
import random
import sys
from statistics import stdev

from tabulate import tabulate

RENTER_START_RENTS = (1100, 1300, 1500, 1700, 1900)

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

    tax_m = args.get("annual_taxes", args.get("_stay_home_tax_annual", 600.0)) / 12

    for m in range(1, projection_months + 1):
        yr = (m - 1) // 12
        stocks *= 1 + monthly_stock_return(args, "stock_return", yr)

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
    if r == 0:
        pmt = loan_amt / term_months
    else:
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
        buyer_stocks *= 1 + monthly_stock_return(args, "stock_return", yr)

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
        if r == 0:
            remaining_loan = loan_amt - pmt * projection_months
        else:
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
            renter_stocks *= 1 + monthly_stock_return(args, "stock_return", yr)

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

    expected_rate = args["mortgage_rate"] + args["mortgage_inflation_beta"] * (
        inflation[0] - inflation_mean
    )
    mortgage_rate = bounded_normal(
        rng,
        expected_rate + macro_beta * args["mortgage_rate_volatility"] * macro[0],
        args["mortgage_rate_volatility"],
        0.03,
        0.10,
    )
    rate_surprise = mortgage_rate - expected_rate

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
        [
            args["rent_growth_rate"] + args["rent_growth_inflation_beta"] * (infl - inflation_mean)
            for infl in inflation
        ],
        args["rent_growth_volatility"],
        args["rent_growth_ar_coeffs"],
        -0.05,
        0.12,
        shared=macro,
        shared_beta=macro_beta,
    )
    hoa_growth = ar_log_returns(
        rng,
        [
            args["hoa_growth_rate"] + args["hoa_growth_inflation_beta"] * (infl - inflation_mean)
            for infl in inflation
        ],
        args["hoa_growth_volatility"],
        args["hoa_growth_ar_coeffs"],
        -0.05,
        0.20,
        shared=macro,
        shared_beta=macro_beta,
    )
    stock = ar_log_returns(
        rng,
        [
            args["stock_return"] + args["stock_inflation_beta"] * (infl - inflation_mean)
            for infl in inflation
        ],
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
    }


def make_trial_args(
    args: dict, market: dict, rng: random.Random, include_renter_risk: bool = False
) -> dict:
    trial = args.copy()
    trial["_mc_paths"] = {
        key: values for key, values in market.items() if key != "mortgage_rate"
    }
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


def filter_expensive_scenarios(
    defaults: dict, scenarios_config: list[dict]
) -> tuple[list[dict], list[dict], float]:
    renter_bar = get_base_renter_scenarios(defaults)[-1]["total_net_worth"]
    kept = []
    skipped = []
    for sc in scenarios_config:
        estimate = calculate_buyer_net_worth(sc, term_years=sc["mortgage_term"])["total_net_worth"]
        if estimate < renter_bar:
            skipped.append(
                {"address": sc.get("_address", ""), "price": sc["price"], "est_nw": estimate}
            )
        else:
            kept.append(sc)
    return kept, skipped, renter_bar


def aggregate_scenario(results: list[dict]) -> dict:
    n = len(results)
    row = dict(results[0])
    for key in results[0]:
        if key != "scenario":
            row[key] = sorted(r[key] for r in results)[n // 2]
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


def run_monte_carlo(
    defaults: dict,
    scenarios_config: list[dict],
    simulations: int,
    seed: int,
    skip_expensive: bool = True,
) -> tuple[list[dict], list[list[dict]], dict]:
    skipped = []
    renter_bar = None
    if skip_expensive:
        scenarios_config, skipped, renter_bar = filter_expensive_scenarios(
            defaults, scenarios_config
        )
    results = [[] for _ in range(1 + len(RENTER_START_RENTS) + len(scenarios_config))]

    for sim in range(simulations):
        market = make_market_paths(defaults, random.Random(derive_seed(seed, sim, 0)))
        trial_defaults = make_trial_args(
            defaults, market, random.Random(derive_seed(seed, sim, 1)), include_renter_risk=True
        )
        trial_results = [
            get_stay_home_scenario(trial_defaults),
            *get_base_renter_scenarios(trial_defaults),
        ]
        for index, sc_config in enumerate(scenarios_config):
            trial_scenario = make_trial_args(
                sc_config, market, random.Random(derive_seed(seed, sim, 2, index))
            )
            trial_results.append(
                calculate_buyer_net_worth(trial_scenario, term_years=trial_scenario["mortgage_term"])
            )

        for index, result in enumerate(trial_results):
            results[index].append(result)

    return (
        [aggregate_scenario(scenario_results) for scenario_results in results],
        results,
        {"renter_bar": renter_bar, "skipped": skipped},
    )


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
            pct_baseline = f"{(s['total_net_worth'] - baseline_nw) / baseline_nw * 100:+.1f}%"
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


def print_risk_summary_table(results: list[list[dict]]) -> None:
    def summarize(scenario_results: list[dict]) -> tuple:
        name = scenario_results[0]["scenario"]
        nw = sorted(r["total_net_worth"] for r in scenario_results)
        n = len(nw)
        nw_median = nw[n // 2]
        beat_home = (
            sum(
                1
                for r, home in zip(scenario_results, results[0])
                if r["total_net_worth"] > home["total_net_worth"]
            )
            / n
            * 100
        )
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
        (summarize(scenario_results) for scenario_results in results[1:]),
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


def print_convergence_note(results: list[list[dict]]) -> None:
    worst = None
    for scenario_results in results:
        nw = sorted(r["total_net_worth"] for r in scenario_results)
        n = len(nw)
        nw_median = nw[n // 2]
        se = bootstrap_median_se(nw)
        relative = se / abs(nw_median) if nw_median != 0 else 0.0
        if worst is None or relative > worst[2]:
            worst = (scenario_results[0]["scenario"], se, relative)
    if worst is None:
        return
    name, se, relative = worst
    print(
        f"Convergence: widest bootstrap SE of median net worth is {name} at "
        f"\u00b1${se:,.0f} ({relative * 100:.1f}% of |median|)."
    )
    if relative > 0.05:
        print("  Consider increasing --simulations for a tighter estimate.")


def print_skipped_note(skip_info: dict) -> None:
    skipped = skip_info["skipped"]
    if not skipped:
        return
    renter_bar = skip_info["renter_bar"]
    print(
        f"Skipped {len(skipped)} scenario(s) whose deterministic net worth falls below the "
        f"worst-case renter (${RENTER_START_RENTS[-1]:,}/mo) baseline of ${renter_bar:,.0f}:"
    )
    for item in skipped:
        print(f"  - {item['address']} (${item['price']:,.0f}) est net worth ${item['est_nw']:,.0f}")
    print()


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
    parser.add_argument(
        "--no-skip",
        action="store_true",
        help="Run Monte Carlo simulations for every scenario, even ones whose deterministic "
        "net worth can't beat the worst-case renter baseline",
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

    all_scenarios, raw_results, skip_info = run_monte_carlo(
        defaults, scenarios_config, simulations, seed, skip_expensive=not args.no_skip
    )
    print_decision_table(all_scenarios, defaults["projection_years"])
    print_risk_summary_table(raw_results)
    print_convergence_note(raw_results)
    print_skipped_note(skip_info)


if __name__ == "__main__":
    main()
