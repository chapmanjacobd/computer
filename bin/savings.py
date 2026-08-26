#!/usr/bin/python3
"""Compare where recurring savings should be invested.

The simulator compares priority orders for five destinations:
emergency fund, Roth IRA, solo 401(k), Roth 401(k), and taxable brokerage.
Each order receives the same annual after-tax savings budget.  The budget is
filled in priority order, subject to account limits; any remainder goes to the
next account.  Traditional solo 401(k) contributions are grossed up for their
current-year tax deduction, while terminal values are reported after estimated
withdrawal taxes.

This is an educational planning model, not tax advice.  Tax brackets,
contribution limits, and account rules are configurable in TOML. Employer
matches and early-withdrawal exceptions are not modeled. Required minimum
distributions are modeled from the configured RMD age and reinvested in the
brokerage account after estimated taxes by default.
"""

import argparse
import itertools
import math
import random
import sys
from concurrent.futures import ProcessPoolExecutor
from statistics import mean

from tabulate import tabulate

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        print("Error: TOML support requires Python 3.11+ or 'tomli' package. Install with: pip install tomli")
        sys.exit(1)


ACCOUNT_NAMES = (
    "emergency_fund",
    "roth_ira",
    "solo_401k",
    "roth_401k",
    "brokerage",
)
ACCOUNT_LABELS = {
    "emergency_fund": "Emergency fund",
    "roth_ira": "Roth IRA",
    "solo_401k": "Solo 401k",
    "roth_401k": "Roth 401k",
    "brokerage": "Brokerage",
}
ALLOCATION_OBJECTIVES = (
    "median",
    "mean",
    "p10",
    "p25",
    "min_tax",
    "emergency",
    "drawdown",
)

FEDERAL_BRACKETS_MFJ = [
    (24800, 0.10),
    (100800, 0.12),
    (211400, 0.22),
    (403550, 0.24),
    (512450, 0.32),
    (768700, 0.35),
]
FEDERAL_BRACKETS_SINGLE = [
    (12400, 0.10),
    (50400, 0.12),
    (105700, 0.22),
    (201775, 0.24),
    (256225, 0.32),
    (384350, 0.35),
]

UNIFORM_LIFETIME = {
    70: 30.0,
    71: 28.9,
    72: 27.4,
    73: 26.5,
    74: 25.5,
    75: 24.6,
    76: 23.7,
    77: 22.9,
    78: 22.0,
    79: 21.1,
    80: 20.2,
    81: 19.4,
    82: 18.5,
    83: 17.7,
    84: 16.8,
    85: 16.0,
    86: 15.2,
    87: 14.4,
    88: 13.7,
    89: 12.9,
    90: 12.2,
    91: 11.5,
    92: 10.8,
    93: 10.1,
    94: 9.5,
    95: 8.9,
    96: 8.4,
    97: 7.8,
    98: 7.3,
    99: 6.8,
    100: 6.4,
    101: 6.0,
    102: 5.6,
    103: 5.2,
    104: 4.9,
    105: 4.6,
    106: 4.3,
    107: 4.1,
    108: 3.9,
    109: 3.7,
    110: 3.5,
    111: 3.4,
    112: 3.3,
    113: 3.1,
    114: 3.0,
    115: 2.9,
    116: 2.8,
    117: 2.7,
    118: 2.5,
    119: 2.3,
    120: 2.0,
}


def _normalize_brackets(value) -> list[tuple[float, float]]:
    brackets = []
    for item in value:
        if isinstance(item, dict):
            limit = item.get("up_to", item.get("limit"))
            rate = item["rate"]
        else:
            limit, rate = item
        if limit is None or str(limit).lower() in {"inf", "infinity"}:
            limit = float("inf")
        brackets.append((float(limit), float(rate)))
    if not brackets or any(rate < 0 or rate >= 1 for _, rate in brackets):
        raise ValueError("federal tax brackets must contain non-negative rates below 100%")
    return sorted(brackets)


def ordinary_income_tax(taxable_income: float, brackets: list[tuple[float, float]]) -> float:
    """Return tax on ordinary taxable income using progressive brackets."""
    remaining = max(0.0, taxable_income)
    lower = 0.0
    tax = 0.0
    last_rate = brackets[-1][1]
    for upper, rate in brackets:
        if remaining <= lower:
            break
        amount = min(remaining, upper) - lower
        tax += max(0.0, amount) * rate
        lower = upper
        last_rate = rate
    if remaining > lower:
        tax += (remaining - lower) * last_rate
    return tax


def marginal_ordinary_rate(taxable_income: float, brackets: list[tuple[float, float]]) -> float:
    income = max(0.0, taxable_income)
    for upper, rate in brackets:
        if income <= upper:
            return rate
    return brackets[-1][1]


def _status_value(
    args: dict, name: str, status: str, inflation_factor: float = 1.0
) -> float:
    if name in args:
        return float(args[name]) * inflation_factor
    return float(args[f"{name}_{status}"]) * inflation_factor


def federal_brackets(
    args: dict, inflation_factor: float = 1.0
) -> list[tuple[float, float]]:
    configured = args.get("federal_brackets")
    if configured is not None:
        brackets = _normalize_brackets(configured)
    else:
        status = str(args.get("filing_status", "mfj")).lower()
        brackets = _normalize_brackets(
            args.get(
                "federal_brackets_single"
                if status in {"single", "s"}
                else "federal_brackets_mfj",
                FEDERAL_BRACKETS_SINGLE
                if status in {"single", "s"}
                else FEDERAL_BRACKETS_MFJ,
            )
        )
    return [
        (upper * inflation_factor, rate) for upper, rate in brackets
    ]


def _state_tax(
    args: dict,
    gross_income: float,
    pretax_contribution: float = 0.0,
    inflation_factor: float = 1.0,
) -> float:
    taxable = max(
        0.0,
        gross_income
        - pretax_contribution
        - float(args.get("state_standard_deduction", 0.0)) * inflation_factor,
    )
    return taxable * float(args.get("state_tax_rate", 0.0))


def current_taxable_income(
    args: dict, pretax_contribution: float = 0.0, inflation_factor: float = 1.0
) -> float:
    return max(
        0.0,
        float(args["annual_income"])
        - float(args.get("standard_deduction", 0.0)) * inflation_factor
        - pretax_contribution,
    )


def current_income_tax(
    args: dict, pretax_contribution: float = 0.0, inflation_factor: float = 1.0
) -> float:
    taxable = current_taxable_income(args, pretax_contribution, inflation_factor)
    federal = ordinary_income_tax(taxable, federal_brackets(args, inflation_factor))
    return federal + _state_tax(
        args, args["annual_income"], pretax_contribution, inflation_factor
    )


def long_term_capital_gains_tax(
    args: dict,
    gain: float,
    ordinary_taxable_income: float = 0.0,
    inflation_factor: float = 1.0,
) -> float:
    """Return federal and state tax on qualified dividends or LTCG.

    The federal calculation stacks gains above ordinary taxable income, so
    ordinary income consumes the 0% capital-gains band before gains do.
    """
    gain = max(0.0, gain)
    ordinary = max(0.0, ordinary_taxable_income)
    status = "single" if str(args.get("filing_status", "mfj")).lower() in {"single", "s"} else "mfj"
    zero_limit = _status_value(args, "ltcg_0pct_limit", status, inflation_factor)
    fifteen_limit = _status_value(
        args, "ltcg_15pct_limit", status, inflation_factor
    )
    zero_amount = min(gain, max(0.0, zero_limit - ordinary))
    remaining = gain - zero_amount
    fifteen_room = max(0.0, fifteen_limit - max(ordinary, zero_limit))
    fifteen_amount = min(remaining, fifteen_room)
    twenty_amount = remaining - fifteen_amount
    federal = fifteen_amount * float(args["ltcg_15pct_rate"]) + twenty_amount * float(
        args["ltcg_20pct_rate"]
    )
    state = gain * float(args.get("state_tax_rate", 0.0))
    return federal + state


def pretax_cash_cost(
    args: dict,
    contribution: float,
    other_pretax: float = 0.0,
    inflation_factor: float = 1.0,
) -> float:
    """Cash cost of a traditional contribution after its current tax savings."""
    contribution = max(0.0, contribution)
    before = current_income_tax(args, other_pretax, inflation_factor)
    after = current_income_tax(
        args, other_pretax + contribution, inflation_factor
    )
    return contribution - max(0.0, before - after)


def gross_contribution_for_cash(
    args: dict,
    cash: float,
    maximum: float,
    other_pretax: float = 0.0,
    inflation_factor: float = 1.0,
) -> float:
    """Solve for the largest traditional contribution affordable with cash."""
    cash = max(0.0, cash)
    maximum = max(0.0, maximum)
    if cash == 0.0 or maximum == 0.0:
        return 0.0
    if pretax_cash_cost(
        args, maximum, other_pretax, inflation_factor
    ) <= cash:
        return maximum
    low, high = 0.0, maximum
    for _ in range(48):
        middle = (low + high) / 2.0
        if pretax_cash_cost(
            args, middle, other_pretax, inflation_factor
        ) <= cash:
            low = middle
        else:
            high = middle
    return low


def _starting_age(args: dict) -> int:
    return int(args.get("starting_age", 30))


def _annual_age(args: dict, year: int) -> int:
    return _starting_age(args) + year


def _inflation_factor(args: dict, year: int) -> float:
    rate = float(args.get("inflation_rate", 0.0))
    if rate <= -1.0:
        raise ValueError("inflation rate must be greater than -100%")
    return (1.0 + rate) ** max(0, int(year))


def _catchup(
    args: dict, name: str, age: int, inflation_factor: float = 1.0
) -> float:
    if age < int(args.get("catchup_age", 50)):
        return 0.0
    return float(args.get(name, 0.0)) * inflation_factor


def _employee_401k_limit(
    args: dict, age: int, inflation_factor: float = 1.0
) -> float:
    return float(args["employee_401k_limit"]) * inflation_factor + _catchup(
        args, "employee_401k_catchup", age, inflation_factor
    )


def _solo_401k_total_limit(
    args: dict, age: int, inflation_factor: float = 1.0
) -> float:
    return float(args["solo_401k_limit"]) * inflation_factor + _catchup(
        args, "employee_401k_catchup", age, inflation_factor
    )


def _solo_401k_employer_contribution(
    args: dict, age: int, inflation_factor: float = 1.0
) -> float:
    rate = float(args.get("solo_401k_employer_rate", 0.0))
    if rate <= 0.0 or float(args["annual_income"]) <= 0.0:
        return 0.0
    return min(
        max(0.0, float(args["annual_income"]) * rate),
        _solo_401k_total_limit(args, age, inflation_factor),
    )


def roth_ira_limit(
    args: dict, age: int | None = None, inflation_factor: float = 1.0
) -> float:
    if not args.get("roth_ira_eligible", True):
        return 0.0
    if age is None:
        age = _starting_age(args)
    income = float(args["annual_income"])
    status = "single" if str(args.get("filing_status", "mfj")).lower() in {"single", "s"} else "mfj"
    start = _status_value(
        args, "roth_ira_phaseout_start", status, inflation_factor
    )
    end = _status_value(
        args, "roth_ira_phaseout_end", status, inflation_factor
    )
    limit = float(args["roth_ira_limit"]) * inflation_factor + _catchup(
        args, "roth_ira_catchup", age, inflation_factor
    )
    if income <= start:
        return limit
    if income >= end:
        return 0.0
    return limit * (end - income) / (end - start)


def allocate_savings(
    args: dict, order: tuple[str, ...], balances: dict[str, float], year: int = 0
) -> dict[str, float]:
    """Allocate one year's after-tax cash budget according to an account order."""
    if set(order) != set(ACCOUNT_NAMES) or len(order) != len(ACCOUNT_NAMES):
        raise ValueError(f"order must contain each account exactly once: {ACCOUNT_NAMES}")

    contributions = {name: 0.0 for name in ACCOUNT_NAMES}
    usage = _new_annual_usage(args, year)
    cash = _annual_savings(args, year)

    for account in order:
        if cash <= 1e-9:
            break
        amount, cash = _apply_account_cash(args, account, cash, balances, year, usage)
        contributions[account] += amount

    contributions["_cash_remaining"] = max(0.0, cash)
    contributions["_employer_contribution"] = usage["employer_contribution"]
    return contributions


def _annual_savings(args: dict, year: int) -> float:
    return max(
        0.0,
        float(args["annual_savings"])
        * (1.0 + float(args.get("savings_growth_rate", 0.0))) ** year,
    )


def _new_annual_usage(args: dict, year: int) -> dict[str, float]:
    age = _annual_age(args, year)
    inflation_factor = _inflation_factor(args, year)
    return {
        "age": age,
        "inflation_factor": inflation_factor,
        "annual_401k": 0.0,
        "annual_roth_ira": 0.0,
        "annual_solo": 0.0,
        "employer_contribution": _solo_401k_employer_contribution(
            args, age, inflation_factor
        ),
    }


def _apply_account_cash(
    args: dict,
    account: str,
    cash: float,
    balances: dict[str, float],
    year: int,
    usage: dict[str, float],
) -> tuple[float, float]:
    """Apply cash to one account, returning (gross contribution, unused cash)."""
    cash = max(0.0, cash)
    age = int(usage["age"])
    inflation_factor = float(usage["inflation_factor"])
    if account == "emergency_fund":
        room = max(0.0, float(args["emergency_fund_target"]) - balances[account])
        amount = min(cash, room)
        return amount, cash - amount
    if account == "roth_ira":
        room = max(
            0.0,
            roth_ira_limit(args, age, inflation_factor)
            - usage["annual_roth_ira"],
        )
        amount = min(cash, room)
        usage["annual_roth_ira"] += amount
        return amount, cash - amount
    if account == "solo_401k":
        employee_room = max(
            0.0,
            _employee_401k_limit(args, age, inflation_factor)
            - usage["annual_401k"],
        )
        total_room = max(
            0.0,
            _solo_401k_total_limit(args, age, inflation_factor)
            - usage["employer_contribution"]
            - usage["annual_solo"],
        )
        earned_income_room = max(0.0, float(args["annual_income"]) - usage["annual_solo"])
        maximum = min(employee_room, total_room, earned_income_room)
        amount = gross_contribution_for_cash(
            args, cash, maximum, inflation_factor=inflation_factor
        )
        cost = pretax_cash_cost(
            args, amount, inflation_factor=inflation_factor
        )
        usage["annual_solo"] += amount
        usage["annual_401k"] += amount
        return amount, max(0.0, cash - cost)
    if account == "roth_401k":
        employee_room = max(
            0.0,
            _employee_401k_limit(args, age, inflation_factor)
            - usage["annual_401k"],
        )
        account_room = max(
            0.0,
            float(args["roth_401k_limit"]) * inflation_factor
            + _catchup(
                args, "employee_401k_catchup", age, inflation_factor
            ),
        )
        amount = min(cash, employee_room, account_room)
        usage["annual_401k"] += amount
        return amount, cash - amount
    if account == "brokerage":
        return cash, 0.0
    raise ValueError(f"unknown account: {account}")


def allocate_fixed_savings(
    args: dict,
    allocation: dict[str, float],
    balances: dict[str, float],
    year: int = 0,
) -> dict[str, float]:
    """Allocate a fixed annual cash split, sending capped amounts to brokerage."""
    if set(allocation) != set(ACCOUNT_NAMES):
        raise ValueError(f"allocation must contain each account: {ACCOUNT_NAMES}")
    weights = {name: max(0.0, float(allocation[name])) for name in ACCOUNT_NAMES}
    total_weight = sum(weights.values())
    if total_weight <= 0.0:
        raise ValueError("allocation must contain a positive total")
    weights = {name: value / total_weight for name, value in weights.items()}

    annual_cash = _annual_savings(args, year)
    contributions = {name: 0.0 for name in ACCOUNT_NAMES}
    usage = _new_annual_usage(args, year)
    unused = annual_cash * weights["brokerage"]
    for account in ACCOUNT_NAMES:
        if account == "brokerage":
            continue
        requested = annual_cash * weights[account]
        amount, remainder = _apply_account_cash(
            args, account, requested, balances, year, usage
        )
        contributions[account] += amount
        unused += remainder

    contributions["brokerage"] = unused
    contributions["_cash_remaining"] = 0.0
    contributions["_employer_contribution"] = usage["employer_contribution"]
    return contributions


def _sample_return(rng: random.Random, mean_return: float, volatility: float) -> float:
    if volatility <= 0.0:
        return mean_return
    if mean_return <= -1.0:
        raise ValueError("mean returns must be greater than -100%")
    gross = math.exp(
        math.log(1.0 + mean_return) - 0.5 * volatility**2 + rng.gauss(0.0, volatility)
    )
    return max(-0.95, gross - 1.0)


def make_market_paths(args: dict, rng: random.Random) -> tuple[list[float], list[float]]:
    months = int(args["projection_years"]) * 12
    monthly_return = (1.0 + float(args["stock_return"])) ** (1.0 / 12.0) - 1.0
    monthly_inflation = (1.0 + float(args["inflation_rate"])) ** (1.0 / 12.0) - 1.0
    stock = [
        _sample_return(rng, monthly_return, float(args["stock_volatility"]) / math.sqrt(12.0))
        for _ in range(months)
    ]
    inflation = [
        _sample_return(
            rng, monthly_inflation, float(args["inflation_volatility"]) / math.sqrt(12.0)
        )
        for _ in range(months)
    ]
    return stock, inflation


def _starting_balances(args: dict) -> tuple[dict[str, float], dict[str, float]]:
    balances = {
        account: float(args.get(f"starting_{account}", 0.0)) for account in ACCOUNT_NAMES
    }
    basis = {
        "brokerage": float(args.get("starting_brokerage_basis", balances["brokerage"])),
        "roth_ira": float(
            args.get("starting_roth_ira_basis", balances["roth_ira"])
        ),
        "roth_401k": float(
            args.get("starting_roth_401k_basis", balances["roth_401k"])
        ),
    }
    return balances, basis


def _terminal_withdrawal_age(args: dict, years: int) -> float:
    configured = args.get("terminal_withdrawal_age")
    if configured is not None:
        return float(configured)
    return float(_starting_age(args) + years)


def _early_withdrawal_penalty_rate(args: dict) -> float:
    rate = float(args.get("early_withdrawal_penalty_rate", 0.10))
    if not 0.0 <= rate <= 1.0:
        raise ValueError("early withdrawal penalty rate must be between 0% and 100%")
    return rate


def _rmd_factor(args: dict, age: int) -> float:
    start_age = int(args.get("rmd_start_age", 73))
    if age < start_age:
        return float("inf")
    if start_age < min(UNIFORM_LIFETIME):
        raise ValueError("rmd_start_age must be at least 70")
    return UNIFORM_LIFETIME.get(min(age, 120), 2.0)


def _rmd_tax(args: dict, distribution: float, inflation_factor: float) -> float:
    """Estimate incremental federal and state tax on one RMD."""
    taxable_income = float(
        args.get("rmd_taxable_income", args.get("retirement_taxable_income", 0.0))
    )
    brackets = federal_brackets(args, inflation_factor)
    federal = ordinary_income_tax(
        taxable_income + distribution, brackets
    ) - ordinary_income_tax(taxable_income, brackets)
    state = distribution * float(args.get("state_tax_rate", 0.0))
    return max(0.0, federal + state)


def _terminal_after_tax_value(
    args: dict,
    balances: dict[str, float],
    basis: dict[str, float],
    years: int,
) -> dict:
    retirement_income = float(args.get("retirement_taxable_income", 0.0))
    inflation_factor = _inflation_factor(args, years)
    brackets = federal_brackets(args, inflation_factor)
    brokerage_gain = max(0.0, balances["brokerage"] - basis["brokerage"])
    brokerage_tax = long_term_capital_gains_tax(
        args, brokerage_gain, retirement_income, inflation_factor
    )
    brokerage = max(0.0, balances["brokerage"] - brokerage_tax)

    solo_tax = (
        ordinary_income_tax(retirement_income + balances["solo_401k"], brackets)
        - ordinary_income_tax(retirement_income, brackets)
        + balances["solo_401k"] * float(args.get("state_tax_rate", 0.0))
    )
    terminal_age = _terminal_withdrawal_age(args, years)
    penalty_age = float(args.get("early_withdrawal_penalty_age", 59.5))
    penalty_rate = _early_withdrawal_penalty_rate(args)
    penalty_applies = terminal_age < penalty_age
    early_penalties = {
        "solo_401k": penalty_rate * balances["solo_401k"] if penalty_applies else 0.0,
        "roth_ira": (
            penalty_rate
            * max(0.0, balances["roth_ira"] - basis["roth_ira"])
            if penalty_applies
            else 0.0
        ),
        "roth_401k": (
            penalty_rate
            * max(0.0, balances["roth_401k"] - basis["roth_401k"])
            if penalty_applies
            else 0.0
        ),
    }
    early_withdrawal_penalty = sum(early_penalties.values())
    solo = max(0.0, balances["solo_401k"] - solo_tax - early_penalties["solo_401k"])
    roth_ira = max(0.0, balances["roth_ira"] - early_penalties["roth_ira"])
    roth_401k = max(0.0, balances["roth_401k"] - early_penalties["roth_401k"])
    after_tax = (
        balances["emergency_fund"]
        + roth_ira
        + roth_401k
        + brokerage
        + solo
    )
    return {
        "final_value": after_tax,
        "final_brokerage": brokerage,
        "final_solo_401k": solo,
        "final_roth_ira": roth_ira,
        "final_roth_401k": roth_401k,
        "terminal_tax": brokerage_tax + solo_tax,
        "early_withdrawal_penalty": early_withdrawal_penalty,
        "early_withdrawal_penalties": early_penalties,
        "terminal_cost": brokerage_tax + solo_tax + early_withdrawal_penalty,
        "terminal_withdrawal_age": terminal_age,
    }


def _monthly_path(
    values: list[float], years: int, name: str
) -> list[float]:
    months = years * 12
    if len(values) == months:
        return list(values)
    if len(values) == years:
        monthly = []
        for value in values:
            if value <= -1.0:
                raise ValueError(f"{name} returns must be greater than -100%")
            monthly.extend([(1.0 + value) ** (1.0 / 12.0) - 1.0] * 12)
        return monthly
    raise ValueError(f"{name} path must contain projection_years or projection_years * 12 values")


def _simulate_plan(
    args: dict,
    allocator,
    label: str,
    stock_returns: list[float] | None = None,
    inflation_rates: list[float] | None = None,
    rng: random.Random | None = None,
) -> dict:
    """Simulate one allocation plan and return nominal and real terminal values."""
    years = int(args["projection_years"])
    if stock_returns is None or inflation_rates is None:
        if rng is None:
            rng = random.Random()
        stock_returns, inflation_rates = make_market_paths(args, rng)
    stock_returns = _monthly_path(stock_returns, years, "stock")
    inflation_rates = _monthly_path(inflation_rates, years, "inflation")

    balances, basis = _starting_balances(args)
    annual_contributions = []
    annual_employer_contributions = []
    annual_rmds = []
    real_history = []
    inflation_factor = 1.0
    rmd_total = 0.0
    rmd_tax_total = 0.0
    rmd_reinvested = 0.0
    min_emergency = float("inf")
    peak = 0.0
    max_drawdown = 0.0
    monthly_emergency_return = (1.0 + float(args["emergency_fund_return"])) ** (
        1.0 / 12.0
    ) - 1.0
    monthly_dividend_yield = (1.0 + float(args["brokerage_dividend_yield"])) ** (
        1.0 / 12.0
    ) - 1.0

    for year in range(years):
        year_inflation_factor = _inflation_factor(args, year)
        brackets = federal_brackets(args, year_inflation_factor)
        rmd_basis_balance = balances["solo_401k"]
        contributions = allocator(year, balances)
        annual_contributions.append(
            {name: contributions[name] for name in ACCOUNT_NAMES}
        )
        annual_employer_contributions.append(contributions["_employer_contribution"])
        solo_contribution = contributions["solo_401k"]
        taxable_income = current_taxable_income(
            args, solo_contribution, year_inflation_factor
        )

        monthly_contributions = {
            name: contributions[name] / 12.0 for name in ACCOUNT_NAMES
        }
        monthly_contributions["solo_401k"] += (
            contributions["_employer_contribution"] / 12.0
        )
        for month in range(year * 12, (year + 1) * 12):
            stock_return = stock_returns[month]
            inflation_rate = inflation_rates[month]
            for account in ACCOUNT_NAMES:
                contribution = monthly_contributions[account]
                before_return = balances[account] + contribution
                if account == "emergency_fund":
                    interest = before_return * monthly_emergency_return
                    tax_rate = marginal_ordinary_rate(taxable_income, brackets) + float(
                        args.get("state_tax_rate", 0.0)
                    )
                    balances[account] = max(
                        0.0, before_return + interest * (1.0 - tax_rate)
                    )
                elif account == "brokerage":
                    dividend = max(0.0, before_return * monthly_dividend_yield)
                    dividend_tax = long_term_capital_gains_tax(
                        args, dividend, taxable_income, year_inflation_factor
                    )
                    balances[account] = max(
                        0.0, before_return * (1.0 + stock_return) - dividend_tax
                    )
                    basis[account] += contribution + max(0.0, dividend - dividend_tax)
                else:
                    balances[account] = max(
                        0.0, before_return * (1.0 + stock_return)
                    )
                    if account in {"roth_ira", "roth_401k"}:
                        basis[account] += contribution
            inflation_factor *= max(0.01, 1.0 + inflation_rate)
            gross_value = sum(balances.values())
            real_value = gross_value / inflation_factor
            real_history.append(real_value)
            min_emergency = min(min_emergency, balances["emergency_fund"])
            peak = max(peak, real_value)
            if peak > 0.0:
                max_drawdown = max(max_drawdown, (peak - real_value) / peak)

        age = _annual_age(args, year)
        rmd_factor = _rmd_factor(args, age)
        rmd = (
            min(balances["solo_401k"], rmd_basis_balance / rmd_factor)
            if math.isfinite(rmd_factor) and rmd_basis_balance > 0.0
            else 0.0
        )
        if rmd > 0.0:
            rmd_tax = _rmd_tax(args, rmd, year_inflation_factor)
            net_rmd = max(0.0, rmd - rmd_tax)
            balances["solo_401k"] = max(0.0, balances["solo_401k"] - rmd)
            if args.get("rmd_reinvest_after_tax", True):
                balances["brokerage"] += net_rmd
                basis["brokerage"] += net_rmd
                rmd_reinvested += net_rmd
            rmd_total += rmd
            rmd_tax_total += rmd_tax
            annual_rmds.append(
                {
                    "age": age,
                    "factor": rmd_factor,
                    "gross": rmd,
                    "tax": rmd_tax,
                    "reinvested": net_rmd
                    if args.get("rmd_reinvest_after_tax", True)
                    else 0.0,
                }
            )
            real_value = sum(balances.values()) / inflation_factor
            real_history[-1] = real_value
            peak = max(peak, real_value)
            if peak > 0.0:
                max_drawdown = max(max_drawdown, (peak - real_value) / peak)

    terminal = _terminal_after_tax_value(args, balances, basis, years)
    terminal["strategy"] = label
    terminal["balances"] = balances
    terminal["basis"] = basis
    terminal["annual_contributions"] = annual_contributions
    terminal["annual_employer_contributions"] = annual_employer_contributions
    terminal["annual_rmds"] = annual_rmds
    terminal["rmd_total"] = rmd_total
    terminal["rmd_tax"] = rmd_tax_total
    terminal["rmd_reinvested"] = rmd_reinvested
    terminal["total_tax_cost"] = terminal["terminal_cost"] + rmd_tax_total
    terminal["history"] = real_history
    terminal["max_drawdown"] = max_drawdown
    terminal["min_emergency"] = min_emergency if real_history else balances["emergency_fund"]
    terminal["real_value"] = terminal["final_value"] / inflation_factor
    return terminal


def simulate_strategy(
    args: dict,
    order: tuple[str, ...],
    stock_returns: list[float] | None = None,
    inflation_rates: list[float] | None = None,
    rng: random.Random | None = None,
) -> dict:
    """Simulate one priority order and return nominal and real terminal values."""
    if set(order) != set(ACCOUNT_NAMES) or len(order) != len(ACCOUNT_NAMES):
        raise ValueError(f"order must contain each account exactly once: {ACCOUNT_NAMES}")
    return _simulate_plan(
        args,
        lambda year, balances: allocate_savings(args, order, balances, year),
        " -> ".join(ACCOUNT_LABELS[name] for name in order),
        stock_returns,
        inflation_rates,
        rng,
    )


def simulate_allocation(
    args: dict,
    allocation: dict[str, float],
    stock_returns: list[float] | None = None,
    inflation_rates: list[float] | None = None,
    rng: random.Random | None = None,
) -> dict:
    """Simulate a fixed annual cash allocation across the five destinations."""
    weights = _normalize_allocation(allocation)
    label = ", ".join(
        f"{ACCOUNT_LABELS[name]} {weights[name]:.0%}"
        for name in ACCOUNT_NAMES
        if weights[name] > 1e-9
    )
    return _simulate_plan(
        args,
        lambda year, balances: allocate_fixed_savings(args, weights, balances, year),
        label or "No allocation",
        stock_returns,
        inflation_rates,
        rng,
    )


def _normalize_allocation(allocation: dict[str, float]) -> dict[str, float]:
    if set(allocation) != set(ACCOUNT_NAMES):
        raise ValueError(f"allocation must contain each account: {ACCOUNT_NAMES}")
    values = {name: max(0.0, float(allocation[name])) for name in ACCOUNT_NAMES}
    total = sum(values.values())
    if total <= 0.0:
        raise ValueError("allocation must contain a positive total")
    return {name: value / total for name, value in values.items()}


def _derive_seed(seed: int, simulation: int) -> int:
    return (seed + simulation * 1000003) & ((1 << 64) - 1)


def _run_trial(payload: tuple[dict, int, list[tuple[str, ...]]]) -> list[float]:
    args, seed, orders = payload
    stock, inflation = make_market_paths(args, random.Random(seed))
    return [
        simulate_strategy(
            args,
            order,
            stock_returns=stock,
            inflation_rates=inflation,
        )["real_value"]
        for order in orders
    ]


def _percentile(values: list[float], fraction: float) -> float:
    if not values:
        return 0.0
    index = int(fraction * (len(values) - 1))
    return sorted(values)[index]


def run_monte_carlo(
    args: dict,
    simulations: int | None = None,
    seed: int | None = None,
    workers: int = 1,
) -> tuple[list[dict], list[list[float]]]:
    simulations = int(
        simulations if simulations is not None else args["monte_carlo_simulations"]
    )
    seed = int(seed if seed is not None else args["monte_carlo_seed"])
    if simulations < 1:
        raise ValueError("simulations must be at least 1")
    orders = list(itertools.permutations(ACCOUNT_NAMES))
    payloads = ((args, _derive_seed(seed, index), orders) for index in range(simulations))

    if workers > 1:
        with ProcessPoolExecutor(max_workers=workers) as executor:
            trials = list(executor.map(_run_trial, payloads))
    else:
        trials = [_run_trial(payload) for payload in payloads]

    raw = [[trial[index] for trial in trials] for index in range(len(orders))]
    best_counts = [0] * len(orders)
    for trial in trials:
        best = max(trial)
        for index, value in enumerate(trial):
            if value == best:
                best_counts[index] += 1

    summaries = []
    for index, (order, values) in enumerate(zip(orders, raw)):
        summaries.append(
            {
                "strategy": " -> ".join(ACCOUNT_LABELS[name] for name in order),
                "order": order,
                "median": _percentile(values, 0.50),
                "p25": _percentile(values, 0.25),
                "p75": _percentile(values, 0.75),
                "mean": mean(values),
                "probability_best": best_counts[index] / simulations,
            }
        )
    summaries.sort(key=lambda row: row["median"], reverse=True)
    return summaries, raw


def _compact_result(result: dict) -> dict[str, float]:
    return {
        "real_value": result["real_value"],
        "final_value": result["final_value"],
        "terminal_tax": result["terminal_tax"],
        "early_withdrawal_penalty": result["early_withdrawal_penalty"],
        "terminal_cost": result["terminal_cost"],
        "rmd_tax": result["rmd_tax"],
        "total_tax_cost": result["total_tax_cost"],
        "min_emergency": result["min_emergency"],
        "max_drawdown": result["max_drawdown"],
    }


def _run_allocation_trial(
    payload: tuple[dict, int, list[dict[str, float]]]
) -> list[dict[str, float]]:
    args, seed, allocations = payload
    stock, inflation = make_market_paths(args, random.Random(seed))
    return [
        _compact_result(
            simulate_allocation(
                args,
                allocation,
                stock_returns=stock,
                inflation_rates=inflation,
            )
        )
        for allocation in allocations
    ]


def _objective_value(result: dict[str, float], objective: str) -> float:
    if objective in {"median", "mean", "p10", "p25"}:
        return result["real_value"]
    if objective == "min_tax":
        return -result["total_tax_cost"]
    if objective == "emergency":
        return result["min_emergency"]
    if objective == "drawdown":
        return -result["max_drawdown"]
    raise ValueError(f"unknown objective: {objective}")


def _summarize_allocations(
    allocations: list[dict[str, float]],
    trials: list[list[dict[str, float]]],
    objective: str,
) -> list[dict]:
    summaries = []
    best_counts = [0] * len(allocations)
    for trial in trials:
        scores = [_objective_value(result, objective) for result in trial]
        best = max(scores)
        for index, score in enumerate(scores):
            if score == best:
                best_counts[index] += 1

    for index, allocation in enumerate(allocations):
        results = [trial[index] for trial in trials]
        values = [result["real_value"] for result in results]
        taxes = [result["terminal_tax"] for result in results]
        penalties = [result["early_withdrawal_penalty"] for result in results]
        terminal_costs = [result["terminal_cost"] for result in results]
        rmd_taxes = [result["rmd_tax"] for result in results]
        total_tax_costs = [result["total_tax_cost"] for result in results]
        emergencies = [result["min_emergency"] for result in results]
        drawdowns = [result["max_drawdown"] for result in results]
        objective_values = [
            _objective_value(result, objective) for result in results
        ]
        if objective == "mean":
            score = mean(objective_values)
        elif objective == "p10":
            score = _percentile(objective_values, 0.10)
        elif objective == "p25":
            score = _percentile(objective_values, 0.25)
        elif objective == "min_tax":
            score = -mean(total_tax_costs)
        elif objective == "emergency":
            score = mean(emergencies)
        elif objective == "drawdown":
            score = -mean(drawdowns)
        else:
            score = _percentile(objective_values, 0.50)
        summaries.append(
            {
                "allocation": _normalize_allocation(allocation),
                "strategy": _allocation_label(allocation),
                "median": _percentile(values, 0.50),
                "p10": _percentile(values, 0.10),
                "p25": _percentile(values, 0.25),
                "p75": _percentile(values, 0.75),
                "mean": mean(values),
                "terminal_tax": mean(taxes),
                "early_withdrawal_penalty": mean(penalties),
                "terminal_cost": mean(terminal_costs),
                "rmd_tax": mean(rmd_taxes),
                "total_tax_cost": mean(total_tax_costs),
                "min_emergency": mean(emergencies),
                "max_drawdown": mean(drawdowns),
                "objective": objective,
                "score": score,
                "probability_best": best_counts[index] / len(trials),
            }
        )
    return summaries


def run_allocation_monte_carlo(
    args: dict,
    allocations: list[dict[str, float]],
    simulations: int | None = None,
    seed: int | None = None,
    workers: int = 1,
    objective: str = "median",
) -> tuple[list[dict], list[list[dict[str, float]]]]:
    """Evaluate fixed dollar splits using common monthly market paths."""
    if objective not in ALLOCATION_OBJECTIVES:
        raise ValueError(f"objective must be one of {ALLOCATION_OBJECTIVES}")
    simulations = int(
        simulations if simulations is not None else args["monte_carlo_simulations"]
    )
    seed = int(seed if seed is not None else args["monte_carlo_seed"])
    if simulations < 1:
        raise ValueError("simulations must be at least 1")
    normalized = [_normalize_allocation(allocation) for allocation in allocations]
    payloads = (
        (args, _derive_seed(seed, index), normalized)
        for index in range(simulations)
    )
    if workers > 1:
        with ProcessPoolExecutor(max_workers=workers) as executor:
            trials = list(executor.map(_run_allocation_trial, payloads))
    else:
        trials = [_run_allocation_trial(payload) for payload in payloads]

    raw = [
        [trial[index] for trial in trials] for index in range(len(normalized))
    ]
    summaries = _summarize_allocations(normalized, trials, objective)
    summaries.sort(key=lambda row: row["score"], reverse=True)
    return summaries, raw


def _allocation_label(allocation: dict[str, float]) -> str:
    weights = _normalize_allocation(allocation)
    return " | ".join(
        f"{ACCOUNT_LABELS[name]} {weights[name]:.0%}"
        for name in ACCOUNT_NAMES
        if weights[name] > 1e-9
    )


def _priority_cash_allocation(args: dict, order: tuple[str, ...]) -> dict[str, float]:
    balances = {account: 0.0 for account in ACCOUNT_NAMES}
    contributions = allocate_savings(args, order, balances)
    allocation = {name: contributions[name] for name in ACCOUNT_NAMES}
    allocation["solo_401k"] = pretax_cash_cost(args, contributions["solo_401k"])
    return _normalize_allocation(allocation)


def _seed_allocations(args: dict) -> list[dict[str, float]]:
    seeds = []
    for account in ACCOUNT_NAMES:
        seeds.append(
            {
                name: 1.0 if name == account else 0.0
                for name in ACCOUNT_NAMES
            }
        )
    seeds.append(
        _priority_cash_allocation(
            args,
            ("emergency_fund", "roth_ira", "solo_401k", "roth_401k", "brokerage"),
        )
    )
    return seeds


def optimize_allocation(
    args: dict,
    simulations: int | None = None,
    seed: int | None = None,
    workers: int = 1,
    objective: str = "median",
) -> tuple[dict[str, float], dict]:
    """Search actual annual cash splits with coordinate descent."""
    annual_savings = max(0.0, float(args["annual_savings"]))
    if annual_savings == 0.0:
        allocation = {name: 1.0 if name == "brokerage" else 0.0 for name in ACCOUNT_NAMES}
        summaries, _ = run_allocation_monte_carlo(
            args, [allocation], simulations=simulations, seed=seed, workers=workers, objective=objective
        )
        return allocation, summaries[0]

    step = max(
        float(args.get("optimization_step", 1000.0)),
        annual_savings / 200.0,
    )
    passes = max(1, int(args.get("optimization_passes", 3)))
    starts = [_normalize_allocation(start) for start in _seed_allocations(args)]
    cache = {}

    def key(allocation):
        return tuple(round(allocation[name], 12) for name in ACCOUNT_NAMES)

    def evaluate(candidates):
        unique = []
        for candidate in candidates:
            candidate = _normalize_allocation(candidate)
            if key(candidate) not in cache:
                cache[key(candidate)] = None
                unique.append(candidate)
        if unique:
            summaries, _ = run_allocation_monte_carlo(
                args,
                unique,
                simulations=simulations,
                seed=seed,
                workers=workers,
                objective=objective,
            )
            by_key = {key(summary["allocation"]): summary for summary in summaries}
            cache.update({key(candidate): by_key[key(candidate)] for candidate in unique})
        return [cache[key(_normalize_allocation(candidate))] for candidate in candidates]

    best_allocation = starts[0]
    best_summary = evaluate([best_allocation])[0]
    for start in starts:
        current = start
        current_summary = evaluate([current])[0]
        for _ in range(passes):
            candidates = []
            for source in ACCOUNT_NAMES:
                source_cash = current[source] * annual_savings
                if source_cash < step:
                    continue
                for target in ACCOUNT_NAMES:
                    if target == source:
                        continue
                    transfer = step
                    while transfer <= source_cash + 1e-9:
                        candidate = current.copy()
                        candidate[source] -= transfer / annual_savings
                        candidate[target] += transfer / annual_savings
                        candidates.append(candidate)
                        transfer += step
            if not candidates:
                break
            candidate_summaries = evaluate(candidates)
            candidate_index = max(
                range(len(candidate_summaries)),
                key=lambda index: candidate_summaries[index]["score"],
            )
            candidate_summary = candidate_summaries[candidate_index]
            if candidate_summary["score"] <= current_summary["score"] + 1e-9:
                break
            current = candidate_summary["allocation"]
            current_summary = candidate_summary
        if current_summary["score"] > best_summary["score"]:
            best_allocation = current
            best_summary = current_summary
    return best_allocation, best_summary


def _allocation_with_dollars(args: dict, allocation: dict[str, float]) -> str:
    weights = _normalize_allocation(allocation)
    annual_savings = float(args["annual_savings"])
    return " | ".join(
        f"{ACCOUNT_LABELS[name]} {_currency(weights[name] * annual_savings)} ({weights[name]:.0%})"
        for name in ACCOUNT_NAMES
        if weights[name] > 1e-9
    )


def print_allocation_results(
    args: dict, summaries: list[dict], objective: str, top: int
) -> None:
    rows = [
        [
            index + 1,
            _allocation_with_dollars(args, summary["allocation"]),
            _currency(summary["median"]),
            _currency(summary["p10"]),
            _currency(summary["p75"]),
            _currency(summary["terminal_tax"]),
            _currency(summary["early_withdrawal_penalty"]),
            _currency(summary["rmd_tax"]),
            f"{summary['max_drawdown']:.1%}",
        ]
        for index, summary in enumerate(summaries[:top])
    ]
    print(f"Optimized annual cash allocations (objective: {objective}):")
    print(
        tabulate(
            rows,
            headers=[
                "Rank",
                "Annual allocation",
                "Median real",
                "P10 real",
                "P75 real",
                "Avg terminal tax",
                "Avg early penalty",
                "Avg RMD tax",
                "Avg drawdown",
            ],
            tablefmt="simple",
        )
    )
    best = summaries[0]
    print(f"\nRecommended annual allocation: {_allocation_with_dollars(args, best['allocation'])}")
    print(
        "Traditional solo 401k contributions receive a current tax deduction; "
        "brokerage gains use the configured stacked LTCG brackets. Limits and "
        "brackets are inflation-indexed; RMDs are reinvested after tax by "
        "default, and early withdrawal penalties use the configured terminal "
        "age and rate."
    )


def load_toml_config(filepath: str) -> dict:
    with open(filepath, "rb") as file:
        data = tomllib.load(file)

    defaults = {
        "annual_savings": 40000.0,
        "annual_income": 100000.0,
        "filing_status": "mfj",
        "starting_age": 30,
        "standard_deduction": 31500.0,
        "state_standard_deduction": 10400.0,
        "state_tax_rate": 0.0495,
        "projection_years": 30,
        "savings_growth_rate": 0.0,
        "emergency_fund_target": 30000.0,
        "emergency_fund_return": 0.03,
        "roth_ira_limit": 7000.0,
        "roth_ira_eligible": True,
        "roth_ira_phaseout_start_mfj": 242000.0,
        "roth_ira_phaseout_end_mfj": 252000.0,
        "roth_ira_phaseout_start_single": 153000.0,
        "roth_ira_phaseout_end_single": 168000.0,
        "employee_401k_limit": 23500.0,
        "employee_401k_catchup": 7500.0,
        "roth_ira_catchup": 1000.0,
        "catchup_age": 50,
        "solo_401k_limit": 70000.0,
        "roth_401k_limit": 23500.0,
        "solo_401k_employer_rate": 0.0,
        "stock_return": 0.07,
        "stock_volatility": 0.18,
        "inflation_rate": 0.03,
        "inflation_volatility": 0.015,
        "brokerage_dividend_yield": 0.02,
        "ltcg_0pct_limit_mfj": 98900.0,
        "ltcg_15pct_limit_mfj": 613700.0,
        "ltcg_0pct_limit_single": 49450.0,
        "ltcg_15pct_limit_single": 545500.0,
        "ltcg_15pct_rate": 0.15,
        "ltcg_20pct_rate": 0.20,
        "retirement_taxable_income": 0.0,
        "rmd_start_age": 73,
        "rmd_reinvest_after_tax": True,
        "early_withdrawal_penalty_rate": 0.10,
        "early_withdrawal_penalty_age": 59.5,
        "terminal_withdrawal_age": None,
        "monte_carlo_simulations": 1000,
        "monte_carlo_seed": 42,
        "optimization_simulations": 50,
        "optimization_step": 1000.0,
        "optimization_passes": 3,
        "federal_brackets_mfj": FEDERAL_BRACKETS_MFJ,
        "federal_brackets_single": FEDERAL_BRACKETS_SINGLE,
    }
    defaults.update(data)
    defaults["projection_years"] = int(defaults["projection_years"])
    defaults["rmd_start_age"] = int(defaults["rmd_start_age"])
    if defaults["rmd_start_age"] < min(UNIFORM_LIFETIME):
        raise ValueError("rmd_start_age must be at least 70")
    defaults["federal_brackets_mfj"] = _normalize_brackets(defaults["federal_brackets_mfj"])
    defaults["federal_brackets_single"] = _normalize_brackets(
        defaults["federal_brackets_single"]
    )
    if "federal_brackets" in defaults:
        defaults["federal_brackets"] = _normalize_brackets(defaults["federal_brackets"])
    if "starting_brokerage_basis" not in defaults:
        defaults["starting_brokerage_basis"] = defaults.get("starting_brokerage", 0.0)
    for account in ("roth_ira", "roth_401k"):
        basis_key = f"starting_{account}_basis"
        if basis_key not in defaults:
            defaults[basis_key] = defaults.get(f"starting_{account}", 0.0)
    defaults["early_withdrawal_penalty_rate"] = _early_withdrawal_penalty_rate(defaults)
    defaults["early_withdrawal_penalty_age"] = float(
        defaults["early_withdrawal_penalty_age"]
    )
    if defaults["terminal_withdrawal_age"] is not None:
        defaults["terminal_withdrawal_age"] = float(
            defaults["terminal_withdrawal_age"]
        )
    return defaults


def _currency(value: float) -> str:
    return f"${value:,.0f}"


def print_results(summaries: list[dict], top: int) -> None:
    rows = [
        [
            index + 1,
            summary["strategy"],
            _currency(summary["median"]),
            _currency(summary["p25"]),
            _currency(summary["p75"]),
            f"{summary['probability_best']:.1%}",
        ]
        for index, summary in enumerate(summaries[:top])
    ]
    print("After-tax real terminal value by priority order:")
    print(
        tabulate(
            rows,
            headers=["Rank", "Priority order", "Median", "P25", "P75", "P(best)"],
            tablefmt="simple",
        )
    )
    best = summaries[0]
    first_place = ACCOUNT_LABELS[best["order"][0]]
    print(
        f"\nRecommended priority order: {best['strategy']}"
        f"\nFirst destination for new savings: {first_place}"
    )
    print(
        "Traditional solo 401k contributions receive a current tax deduction; "
        "brokerage gains use the configured stacked LTCG brackets. Limits and "
        "brackets are inflation-indexed; RMDs are reinvested after tax by "
        "default, and early withdrawal penalties use the configured terminal "
        "age and rate."
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare savings allocations across taxable and retirement accounts"
    )
    parser.add_argument("config", help="Path to TOML configuration file")
    parser.add_argument("--simulations", type=int, help="Number of Monte Carlo trials")
    parser.add_argument("--seed", type=int, help="Random seed")
    parser.add_argument(
        "--objective",
        choices=ALLOCATION_OBJECTIVES,
        default="median",
        help="Optimization objective (default: median real terminal value)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Parallel worker processes (default: 1)",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=10,
        help="Number of priority orders to print (default: 10)",
    )
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("--workers must be at least 1")
    if args.top < 1:
        parser.error("--top must be at least 1")

    config = load_toml_config(args.config)
    simulations = (
        args.simulations
        if args.simulations is not None
        else config["monte_carlo_simulations"]
    )
    seed = args.seed if args.seed is not None else config["monte_carlo_seed"]
    optimized, _ = optimize_allocation(
        config,
        simulations=config["optimization_simulations"],
        seed=seed,
        objective=args.objective,
        workers=1,
    )
    allocations = [optimized]
    for allocation in _seed_allocations(config):
        if tuple(_normalize_allocation(allocation).values()) not in {
            tuple(_normalize_allocation(existing).values()) for existing in allocations
        }:
            allocations.append(allocation)
    summaries, _ = run_allocation_monte_carlo(
        config,
        allocations,
        simulations=simulations,
        seed=seed,
        workers=args.workers,
        objective=args.objective,
    )
    print_allocation_results(config, summaries, args.objective, args.top)


if __name__ == "__main__":
    main()
