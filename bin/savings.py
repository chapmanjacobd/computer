#!/usr/bin/python3
"""Compare where recurring savings should be invested.

The simulator compares priority orders for emergency fund, Roth IRA, solo
401(k), Roth 401(k), taxable brokerage, and HSA destinations. The annual
after-tax cash budget may be supplied directly as ``annual_savings`` for
backward compatibility, or derived from income, expenses, and current taxes.
Age-based schedule tables can replace the scalar income and expense values.
Traditional solo 401(k) contributions are grossed up for their current-year
tax deduction, while plan values are reported as after-tax net present value
(NPV).

This is an educational planning model, not tax advice.  Tax brackets,
contribution limits, and account rules are configurable in TOML. Employer
matches and early-withdrawal exceptions are not modeled. Required minimum
distributions are modeled from the configured RMD age and reinvested in the
brokerage account after estimated taxes by default.
"""

import argparse
import math
import os
import random
import re
import sys
from concurrent.futures import ProcessPoolExecutor
from statistics import mean

from tabulate import tabulate

DEFAULT_WORKERS = os.cpu_count() or 1

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        print(
            "Error: TOML support requires Python 3.11+ or 'tomli' package. "
            "Install with: pip install tomli"
        )
        sys.exit(1)


ACCOUNT_NAMES = (
    "emergency_fund",
    "roth_ira",
    "solo_401k",
    "roth_401k",
    "brokerage",
    "hsa",
)
ACCOUNT_LABELS = {
    "emergency_fund": "Emergency fund",
    "roth_ira": "Roth IRA",
    "solo_401k": "Solo 401k",
    "roth_401k": "Roth 401k",
    "brokerage": "Brokerage",
    "hsa": "HSA",
}
BASIS_ACCOUNTS = ("brokerage", "roth_ira", "roth_401k")


def _owners(args: dict) -> tuple[str, ...]:
    """Return the ordered owners, defaulting to a single primary owner."""
    tables = args.get("owner")
    if isinstance(tables, dict) and tables:
        return tuple(str(name) for name in tables)
    return ("primary",)


def _owner_config(args: dict, owner: str) -> dict:
    tables = args.get("owner")
    if isinstance(tables, dict):
        return tables.get(owner) or {}
    return {}


def _base_account(name: str) -> tuple[str, str]:
    """Split a per-owner account name into (base account, owner)."""
    account, _, owner = name.rpartition("_")
    return (account, owner) if owner else (name, "")


def _account_names(args: dict) -> tuple[str, ...]:
    """Return every per-owner account name."""
    return tuple(
        f"{account}_{owner}"
        for account in ACCOUNT_NAMES
        for owner in _owners(args)
    )
ALLOCATION_OBJECTIVES = (
    "median",
    "mean",
    "p10",
    "p25",
    "min_tax",
    "emergency",
    "drawdown",
    "retirement_success",
    "shortfall",
    "warnings",
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
FEDERAL_BRACKETS_MFS = [
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
        raise ValueError(
            "federal tax brackets must contain non-negative rates below 100%"
        )
    return sorted(brackets)


def ordinary_income_tax(
    taxable_income: float, brackets: list[tuple[float, float]]
) -> float:
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


def marginal_ordinary_rate(
    taxable_income: float, brackets: list[tuple[float, float]]
) -> float:
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
    key = f"{name}_{status}"
    if key in args:
        return float(args[key]) * inflation_factor
    fallback_status = (
        "single" if status in {"mfs", "married_filing_separately"} else "mfj"
    )
    fallback = f"{name}_{fallback_status}"
    return float(args.get(fallback, 0.0)) * inflation_factor


def _filing_status(args: dict) -> str:
    status = str(args.get("filing_status", "mfj")).lower()
    if status in {"single", "s"}:
        return "single"
    if status in {"mfs", "married_filing_separately"}:
        return "mfs"
    return "mfj"


def _single_or_mfj_status(args: dict) -> str:
    return "single" if _filing_status(args) in {"single", "mfs"} else "mfj"


def federal_brackets(
    args: dict, inflation_factor: float = 1.0
) -> list[tuple[float, float]]:
    configured = args.get("federal_brackets")
    if configured is not None:
        brackets = _normalize_brackets(configured)
    else:
        status = _filing_status(args)
        if status == "single":
            key, fallback = "federal_brackets_single", FEDERAL_BRACKETS_SINGLE
        elif status == "mfs":
            key, fallback = "federal_brackets_mfs", FEDERAL_BRACKETS_MFS
        else:
            key, fallback = "federal_brackets_mfj", FEDERAL_BRACKETS_MFJ
        brackets = _normalize_brackets(args.get(key, fallback))
    return [(upper * inflation_factor, rate) for upper, rate in brackets]


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


def _state_capital_gains_rate(args: dict) -> float:
    value = args.get("state_capital_gains_tax_rate")
    return float(args.get("state_tax_rate", 0.0) if value is None else value)


def current_taxable_income(
    args: dict,
    pretax_contribution: float = 0.0,
    inflation_factor: float = 1.0,
    annual_income: float | None = None,
) -> float:
    return max(
        0.0,
        (_annual_income(args, 0) if annual_income is None else annual_income)
        - float(args.get("standard_deduction", 0.0)) * inflation_factor
        - pretax_contribution,
    )


def current_income_tax(
    args: dict,
    pretax_contribution: float = 0.0,
    inflation_factor: float = 1.0,
    annual_income: float | None = None,
) -> float:
    income = _annual_income(args, 0) if annual_income is None else float(annual_income)
    taxable = current_taxable_income(
        args, pretax_contribution, inflation_factor, income
    )
    federal = ordinary_income_tax(taxable, federal_brackets(args, inflation_factor))
    return federal + _state_tax(args, income, pretax_contribution, inflation_factor)


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
    status = _single_or_mfj_status(args)
    zero_limit = _status_value(args, "ltcg_bracket0_limit", status, inflation_factor)
    fifteen_limit = _status_value(args, "ltcg_bracket1_limit", status, inflation_factor)
    zero_amount = min(gain, max(0.0, zero_limit - ordinary))
    remaining = gain - zero_amount
    fifteen_room = max(0.0, fifteen_limit - max(ordinary, zero_limit))
    fifteen_amount = min(remaining, fifteen_room)
    twenty_amount = remaining - fifteen_amount
    federal = (
        zero_amount * float(args["ltcg_bracket0_rate"])
        + fifteen_amount * float(args["ltcg_bracket1_rate"])
        + twenty_amount * float(args["ltcg_bracket2_rate"])
    )
    state = gain * _state_capital_gains_rate(args)
    return federal + state


def _ltcg_zero_percent_room(
    args: dict,
    ordinary_taxable_income: float,
    inflation_factor: float = 1.0,
) -> float:
    """Return the remaining federal 0% LTCG bracket room."""
    status = _single_or_mfj_status(args)
    zero_limit = _status_value(args, "ltcg_bracket0_limit", status, inflation_factor)
    return max(0.0, zero_limit - max(0.0, ordinary_taxable_income))


def _ltcg_harvest_request(
    args: dict,
    unrealized_gain: float,
    ordinary_taxable_income: float,
    inflation_factor: float = 1.0,
) -> float:
    """Return the configured amount of gain to realize this year."""
    setting = args["ltcg_harvesting"]
    if setting == "none":
        return 0.0
    if isinstance(setting, int) and not isinstance(setting, bool):
        return min(unrealized_gain, float(setting))
    if isinstance(setting, float):
        return unrealized_gain * setting
    if not isinstance(setting, str):
        raise ValueError(
            "ltcg_harvesting must be none, a non-negative integer, a rate from "
            "0 to 1, or a bracket target such as 0% or 0%70"
        )

    match = re.fullmatch(r"(\d+(?:\.\d+)?)%(?:(\d+(?:\.\d+)?))?", setting)
    if match is None:
        raise ValueError(
            "ltcg_harvesting must be none, a non-negative integer, a rate from "
            "0 to 1, or a bracket target such as 0% or 0%70"
        )
    target_rate = float(match.group(1)) / 100.0
    harvest_rate = 1.0 if match.group(2) is None else float(match.group(2)) / 100.0
    status = _single_or_mfj_status(args)
    zero_limit = _status_value(args, "ltcg_bracket0_limit", status, inflation_factor)
    fifteen_limit = _status_value(args, "ltcg_bracket1_limit", status, inflation_factor)
    zero_rate = float(args["ltcg_bracket0_rate"])
    fifteen_rate = float(args["ltcg_bracket1_rate"])
    twenty_rate = float(args["ltcg_bracket2_rate"])
    if math.isclose(target_rate, zero_rate):
        room = zero_limit - ordinary_taxable_income
    elif math.isclose(target_rate, fifteen_rate):
        room = fifteen_limit - ordinary_taxable_income
    elif math.isclose(target_rate, twenty_rate):
        room = unrealized_gain
    else:
        raise ValueError(
            "ltcg_harvesting bracket target must be 0%, "
            f"{fifteen_rate:.0%}, or {twenty_rate:.0%}"
        )
    return min(unrealized_gain * harvest_rate, max(0.0, room))


def _validate_ltcg_harvesting(args: dict) -> None:
    setting = args["ltcg_harvesting"]
    if setting == "none":
        return
    if isinstance(setting, bool):
        raise ValueError(
            "ltcg_harvesting must be none, a non-negative integer, a rate from "
            "0 to 1, or a bracket target such as 0% or 0%70"
        )
    if isinstance(setting, int):
        if setting < 0:
            raise ValueError("ltcg_harvesting amount must be non-negative")
        return
    if isinstance(setting, float):
        if not 0.0 <= setting <= 1.0:
            raise ValueError("ltcg_harvesting rate must be between 0 and 1")
        return
    if not isinstance(setting, str):
        raise ValueError(
            "ltcg_harvesting must be none, a non-negative integer, a rate from "
            "0 to 1, or a bracket target such as 0% or 0%70"
        )
    match = re.fullmatch(r"(\d+(?:\.\d+)?)%(?:(\d+(?:\.\d+)?))?", setting)
    if match is None or float(match.group(2) or 100.0) > 100.0:
        raise ValueError(
            "ltcg_harvesting must be none, a non-negative integer, a rate from "
            "0 to 1, or a bracket target such as 0% or 0%70"
        )
    target_rate = float(match.group(1)) / 100.0
    if not any(
        math.isclose(target_rate, rate)
        for rate in (
            float(args["ltcg_bracket0_rate"]),
            float(args["ltcg_bracket1_rate"]),
            float(args["ltcg_bracket2_rate"]),
        )
    ):
        raise ValueError("ltcg_harvesting bracket target must match an LTCG rate")


def pretax_cash_cost(
    args: dict,
    contribution: float,
    other_pretax: float = 0.0,
    inflation_factor: float = 1.0,
    annual_income: float | None = None,
) -> float:
    """Cash cost of a traditional contribution after its current tax savings."""
    contribution = max(0.0, contribution)
    before = current_income_tax(args, other_pretax, inflation_factor, annual_income)
    after = current_income_tax(
        args, other_pretax + contribution, inflation_factor, annual_income
    )
    return contribution - max(0.0, before - after)


def gross_contribution_for_cash(
    args: dict,
    cash: float,
    maximum: float,
    other_pretax: float = 0.0,
    inflation_factor: float = 1.0,
    annual_income: float | None = None,
) -> float:
    """Solve for the largest traditional contribution affordable with cash."""
    cash = max(0.0, cash)
    maximum = max(0.0, maximum)
    if cash == 0.0 or maximum == 0.0:
        return 0.0
    if (
        pretax_cash_cost(args, maximum, other_pretax, inflation_factor, annual_income)
        <= cash
    ):
        return maximum
    low, high = 0.0, maximum
    for _ in range(48):
        middle = (low + high) / 2.0
        if (
            pretax_cash_cost(
                args, middle, other_pretax, inflation_factor, annual_income
            )
            <= cash
        ):
            low = middle
        else:
            high = middle
    return low


def _validate_account_order(args: dict, order: tuple[str, ...]) -> None:
    accounts = _account_names(args)
    if not (set(order) == set(accounts) and len(order) == len(accounts)):
        raise ValueError(f"order must contain each account exactly once: {accounts}")
    if any(base not in ACCOUNT_NAMES for base, _ in map(_base_account, order)):
        raise ValueError(f"order contains unknown account: {order}")


def _validate_withdrawal_order(order: list[str]) -> None:
    if (
        not isinstance(order, list)
        or len(set(order)) != len(order)
        or any(account not in ACCOUNT_NAMES for account in order)
    ):
        raise ValueError("retirement_withdrawal_order must contain valid account names")


def _starting_age(args: dict) -> int:
    return int(args.get("starting_age", 30))


def _annual_age(args: dict, year: int) -> int:
    return _starting_age(args) + year


def _inflation_factor(args: dict, year: int) -> float:
    rate = float(args.get("inflation_rate", 0.0))
    if rate <= -1.0:
        raise ValueError("inflation rate must be greater than -100%")
    return (1.0 + rate) ** max(0, int(year))


def _discount_rate(args: dict) -> float:
    configured = args.get("discount_rate")
    rate = float(
        args.get("inflation_rate", 0.0) if configured is None else configured
    )
    if rate <= -1.0:
        raise ValueError("discount rate must be greater than -100%")
    return rate


def _discount_factor(args: dict, years: float) -> float:
    return (1.0 + _discount_rate(args)) ** max(0.0, float(years))


def _schedule_entries(args: dict, name: str) -> list[dict]:
    entries = args.get(name, [])
    if entries is None:
        return []
    if not isinstance(entries, list):
        raise ValueError(f"{name} must be a list of tables")
    return entries


def _schedule_active(entry: dict, age: int, year: int, base_age: int = 0) -> bool:
    if not isinstance(entry, dict):
        raise ValueError("schedule entries must be tables")
    if "start_age" in entry and age < int(entry["start_age"]):
        return False
    if "end_age" in entry and age > int(entry["end_age"]):
        return False
    if "duration" in entry:
        start = int(entry.get("start_age", base_age))
        if age >= start + int(entry["duration"]):
            return False
    if "start_year" in entry and year < int(entry["start_year"]):
        return False
    return "end_year" not in entry or year <= int(entry["end_year"])


def _scheduled_value(
    args: dict, name: str, year: int, default: float = 0.0, owner: str | None = None
) -> float:
    age = _annual_age(args, year)
    entries = _schedule_entries(args, name)
    if not entries:
        return default
    values = []
    for entry in entries:
        if _schedule_active(entry, age, year, _starting_age(args)) and (
            owner is None or entry.get("owner", owner) == owner
        ):
            value = entry.get("annual_amount", entry.get("amount"))
            if value is None:
                raise ValueError(f"{name} entries require annual_amount or amount")
            value = float(value)
            if value < 0:
                raise ValueError(f"{name} entries require non-negative annual_amount")
            values.append(value)
    return sum(values)


def _annual_income(args: dict, year: int, owner: str | None = None) -> float:
    configured = args.get("annual_income", 0.0)
    if isinstance(configured, dict):
        base = (
            float(configured.get(owner, 0.0))
            if owner is not None
            else sum(float(value) for value in configured.values())
        )
    else:
        by_owner = args.get("annual_income_by_owner")
        if owner is not None and isinstance(by_owner, dict) and owner in by_owner:
            base = float(by_owner[owner])
        elif owner is None and isinstance(by_owner, dict):
            base = sum(float(value) for value in by_owner.values())
        else:
            base = float(configured)
    return max(
        0.0,
        _scheduled_value(args, "incomes", year, base, owner),
    )


def _annual_expenses(args: dict, year: int) -> float:
    return max(
        0.0,
        _scheduled_value(
            args, "expenses", year, float(args.get("annual_expenses", 0.0))
        ),
    )


def _scheduled_contributions(args: dict, year: int) -> list[dict]:
    result = []
    for entry in _schedule_entries(args, "contribution_schedules"):
        if not _schedule_active(
            entry, _annual_age(args, year), year, _starting_age(args)
        ):
            continue
        account = entry.get("account", entry.get("destination"))
        if account not in ACCOUNT_NAMES:
            raise ValueError(f"unknown contribution schedule account: {account}")
        amount = entry.get("annual_amount", entry.get("amount"))
        if amount is None or float(amount) < 0:
            raise ValueError(
                "contribution schedules require non-negative annual_amount"
            )
        owners = [str(entry["owner"])] if entry.get("owner") else list(_owners(args))
        for owner in owners:
            result.append(
                {
                    "account": f"{account}_{owner}",
                    "amount": float(amount),
                    "owner": owner,
                }
            )
    return result


def _catchup(args: dict, name: str, age: int, inflation_factor: float = 1.0) -> float:
    if age < int(args.get("catchup_age", 50)):
        return 0.0
    return float(args.get(name, 0.0)) * inflation_factor


def _employee_401k_limit(
    args: dict,
    age: int,
    inflation_factor: float = 1.0,
    owner: str | None = None,
) -> float:
    return _owner_limit(
        args, "employee_401k_limit", owner, inflation_factor
    ) + _catchup(args, "employee_401k_catchup", age, inflation_factor)


def _solo_401k_total_limit(
    args: dict,
    age: int,
    inflation_factor: float = 1.0,
    owner: str | None = None,
) -> float:
    return _owner_limit(args, "solo_401k_limit", owner, inflation_factor) + _catchup(
        args, "employee_401k_catchup", age, inflation_factor
    )


def _owner_limit(
    args: dict, name: str, owner: str | None, inflation_factor: float = 1.0
) -> float:
    values = args.get(f"{name}_by_owner")
    if owner and isinstance(values, dict) and owner in values:
        return float(values[owner]) * inflation_factor
    if owner:
        table = _owner_config(args, owner)
        if table and name in table:
            return float(table[name]) * inflation_factor
    return float(args.get(name, 0.0)) * inflation_factor


def _solo_401k_employer_contribution(
    args: dict,
    age: int,
    inflation_factor: float = 1.0,
    year: int = 0,
    owner: str | None = None,
) -> float:
    rate = float(args.get("solo_401k_employer_rate", 0.0))
    if rate <= 0.0 or _annual_income(args, year) <= 0.0:
        return 0.0
    return min(
        max(0.0, _annual_income(args, year) * rate),
        _solo_401k_total_limit(args, age, inflation_factor, owner),
    )


def roth_ira_limit(
    args: dict,
    age: int | None = None,
    inflation_factor: float = 1.0,
    owner: str | None = None,
    year: int = 0,
) -> float:
    if not args.get("roth_ira_eligible", True):
        return 0.0
    if age is None:
        age = _starting_age(args)
    income = _annual_income(args, year, owner)
    status = _single_or_mfj_status(args)
    start = _status_value(args, "roth_ira_phaseout_start", status, inflation_factor)
    end = _status_value(args, "roth_ira_phaseout_end", status, inflation_factor)
    limit = _owner_limit(args, "roth_ira_limit", owner, inflation_factor) + _catchup(
        args, "roth_ira_catchup", age, inflation_factor
    )
    if income <= start:
        return limit
    if income >= end:
        return 0.0
    return limit * (end - income) / (end - start)


def hsa_limit(
    args: dict,
    age: int | None = None,
    inflation_factor: float = 1.0,
    owner: str | None = None,
) -> float:
    if not args.get("hsa_eligible", False):
        return 0.0
    if age is None:
        age = _starting_age(args)
    owner = owner or args.get("hsa_owner")
    family_configured = (
        "hsa_family_limit" in args or "hsa_family_limit_by_owner" in args
    )
    limit_name = (
        "hsa_family_limit"
        if args.get("hsa_family") and family_configured
        else "hsa_limit"
    )
    limit = _owner_limit(args, limit_name, owner, inflation_factor)
    catchup_age = int(args.get("hsa_catchup_age", args.get("catchup_age", 55)))
    if age >= catchup_age:
        limit += _owner_limit(args, "hsa_catchup", owner, inflation_factor)
    return max(0.0, limit)


def allocate_savings(
    args: dict, order: tuple[str, ...], balances: dict[str, float], year: int = 0
) -> dict[str, float]:
    """Allocate one year's after-tax cash budget according to an account order."""
    _validate_account_order(args, order)

    contributions = dict.fromkeys(_account_names(args), 0.0)
    usage = _new_annual_usage(args, year)
    cash = _annual_savings(args, year)

    scheduled = _scheduled_contributions(args, year)
    scheduled_accounts = set()
    for item in scheduled:
        requested = min(cash, item["amount"])
        amount, remainder = _apply_account_cash(
            args, item["account"], requested, balances, year, usage
        )
        contributions[item["account"]] += amount
        scheduled_accounts.add(item["account"])
        cash -= requested - remainder

    for account in order:
        if cash <= 1e-9:
            break
        if account in scheduled_accounts:
            continue
        amount, cash = _apply_account_cash(args, account, cash, balances, year, usage)
        contributions[account] += amount

    contributions["_cash_remaining"] = max(0.0, cash)
    contributions["_employer_contribution"] = usage["employer_contribution"]
    contributions["_employer_contribution_by_owner"] = usage[
        "employer_contribution_by_owner"
    ]
    return contributions


def _annual_savings(args: dict, year: int) -> float:
    configured = args.get("annual_savings")
    if configured is not None:
        return max(
            0.0,
            float(configured)
            * (1.0 + float(args.get("savings_growth_rate", 0.0))) ** year,
        )
    income = _annual_income(args, year)
    expenses = _annual_expenses(args, year)
    taxes = current_income_tax(
        args, inflation_factor=_inflation_factor(args, year), annual_income=income
    )
    return max(0.0, income - expenses - taxes)


def _annual_contribution_cash_cost(
    args: dict, contributions: dict[str, float], year: int, annual_income: float
) -> float:
    """Return the cash outflow for one year's employee contributions."""
    inflation_factor = _inflation_factor(args, year)
    cash_cost = 0.0
    for name in _account_names(args):
        base, _ = _base_account(name)
        if base == "solo_401k":
            cash_cost += pretax_cash_cost(
                args,
                contributions[name],
                inflation_factor=inflation_factor,
                annual_income=annual_income,
            )
        else:
            cash_cost += contributions[name]
    return cash_cost


def _new_annual_usage(args: dict, year: int) -> dict[str, float]:
    age = _annual_age(args, year)
    inflation_factor = _inflation_factor(args, year)
    return {
        "age": age,
        "inflation_factor": inflation_factor,
        "annual_401k": 0.0,
        "annual_401k_by_owner": {},
        "annual_roth_ira": 0.0,
        "annual_roth_ira_by_owner": {},
        "annual_emergency": 0.0,
        "annual_solo": 0.0,
        "annual_solo_by_owner": {},
        "annual_hsa": 0.0,
        "annual_hsa_by_owner": {},
        "employer_contribution": sum(
            _solo_401k_employer_contribution(
                args, age, inflation_factor, year, owner
            )
            for owner in _owners(args)
        ),
        "employer_contribution_by_owner": {
            owner: _solo_401k_employer_contribution(
                args, age, inflation_factor, year, owner
            )
            for owner in _owners(args)
        },
    }


def _apply_account_cash(
    args: dict,
    account: str,
    cash: float,
    balances: dict[str, float],
    year: int,
    usage: dict[str, float],
) -> tuple[float, float]:
    """Apply cash to one per-owner account, returning (gross, unused cash)."""
    cash = max(0.0, cash)
    age = int(usage["age"])
    inflation_factor = float(usage["inflation_factor"])
    base, owner = _base_account(account)
    if base == "emergency_fund":
        total_emergency = sum(
            balances[name]
            for name in balances
            if _base_account(name)[0] == "emergency_fund"
        )
        room = max(
            0.0,
            float(args["emergency_fund_target"])
            - total_emergency
            - usage["annual_emergency"],
        )
        amount = min(cash, room)
        usage["annual_emergency"] += amount
        return amount, cash - amount
    if base == "roth_ira":
        used_roth_ira = usage["annual_roth_ira_by_owner"].get(owner, 0.0)
        room = max(
            0.0,
            roth_ira_limit(args, age, inflation_factor, owner, year) - used_roth_ira,
        )
        amount = min(cash, room)
        usage["annual_roth_ira"] += amount
        usage["annual_roth_ira_by_owner"][owner] = used_roth_ira + amount
        return amount, cash - amount
    if base == "solo_401k":
        used_401k = usage["annual_401k_by_owner"].get(owner, 0.0)
        used_solo = usage["annual_solo_by_owner"].get(owner, 0.0)
        employee_room = max(
            0.0,
            _employee_401k_limit(args, age, inflation_factor, owner) - used_401k,
        )
        total_room = max(
            0.0,
            _solo_401k_total_limit(args, age, inflation_factor, owner)
            - usage["employer_contribution_by_owner"].get(owner, 0.0)
            - used_solo,
        )
        earned_income_room = max(0.0, _annual_income(args, year) - used_solo)
        maximum = min(employee_room, total_room, earned_income_room)
        amount = gross_contribution_for_cash(
            args,
            cash,
            maximum,
            inflation_factor=inflation_factor,
            annual_income=_annual_income(args, year),
        )
        cost = pretax_cash_cost(
            args,
            amount,
            inflation_factor=inflation_factor,
            annual_income=_annual_income(args, year),
        )
        usage["annual_solo"] += amount
        usage["annual_solo_by_owner"][owner] = used_solo + amount
        usage["annual_401k"] += amount
        usage["annual_401k_by_owner"][owner] = used_401k + amount
        return amount, max(0.0, cash - cost)
    if base == "roth_401k":
        used_401k = usage["annual_401k_by_owner"].get(owner, 0.0)
        employee_room = max(
            0.0,
            _employee_401k_limit(args, age, inflation_factor, owner) - used_401k,
        )
        account_room = max(
            0.0,
            _owner_limit(args, "roth_401k_limit", owner, inflation_factor)
            + _catchup(args, "employee_401k_catchup", age, inflation_factor),
        )
        amount = min(cash, employee_room, account_room)
        usage["annual_401k"] += amount
        usage["annual_401k_by_owner"][owner] = used_401k + amount
        return amount, cash - amount
    if base == "brokerage":
        return cash, 0.0
    if base == "hsa":
        used_hsa = (
            usage["annual_hsa"]
            if args.get("hsa_shared_limit", args.get("hsa_family", False))
            else usage["annual_hsa_by_owner"].get(owner, 0.0)
        )
        room = max(0.0, hsa_limit(args, age, inflation_factor, owner) - used_hsa)
        amount = min(cash, room)
        usage["annual_hsa"] += amount
        usage["annual_hsa_by_owner"][owner] = (
            usage["annual_hsa_by_owner"].get(owner, 0.0) + amount
        )
        return amount, cash - amount
    raise ValueError(f"unknown account: {account}")


def allocate_fixed_savings(
    args: dict,
    allocation: dict[str, float],
    balances: dict[str, float],
    year: int = 0,
) -> dict[str, float]:
    """Allocate a fixed annual cash split, sending capped amounts to brokerage."""
    weights = _normalize_allocation(args, allocation)

    annual_cash = _annual_savings(args, year)
    contributions = dict.fromkeys(_account_names(args), 0.0)
    usage = _new_annual_usage(args, year)
    brokerage_weights = {
        account: weights[account]
        for account in _account_names(args)
        if _base_account(account)[0] == "brokerage"
    }
    unused = sum(annual_cash * weight for weight in brokerage_weights.values())
    for account in _account_names(args):
        base, _ = _base_account(account)
        if base == "brokerage":
            continue
        requested = annual_cash * weights[account]
        amount, remainder = _apply_account_cash(
            args, account, requested, balances, year, usage
        )
        contributions[account] += amount
        unused += remainder

    total_brokerage_weight = sum(brokerage_weights.values())
    for account, weight in brokerage_weights.items():
        contributions[account] = (
            unused * (weight / total_brokerage_weight)
            if total_brokerage_weight > 0.0
            else 0.0
        )
    contributions["_cash_remaining"] = (
        unused if total_brokerage_weight <= 0.0 else 0.0
    )
    contributions["_employer_contribution"] = usage["employer_contribution"]
    contributions["_employer_contribution_by_owner"] = usage[
        "employer_contribution_by_owner"
    ]
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


def make_market_paths(
    args: dict, rng: random.Random
) -> tuple[list[float], list[float]]:
    months = int(args["projection_years"]) * 12
    monthly_return = (1.0 + float(args["stock_return"])) ** (1.0 / 12.0) - 1.0
    monthly_inflation = (1.0 + float(args["inflation_rate"])) ** (1.0 / 12.0) - 1.0
    stock = [
        _sample_return(
            rng, monthly_return, float(args["stock_volatility"]) / math.sqrt(12.0)
        )
        for _ in range(months)
    ]
    inflation = [
        _sample_return(
            rng,
            monthly_inflation,
            float(args["inflation_volatility"]) / math.sqrt(12.0),
        )
        for _ in range(months)
    ]
    return stock, inflation


def _starting_balances(args: dict) -> tuple[dict[str, float], dict[str, float]]:
    balances = {}
    basis = {}
    for account in ACCOUNT_NAMES:
        for owner in _owners(args):
            name = f"{account}_{owner}"
            config = _owner_config(args, owner)
            balance = float(config.get(f"{account}_balance", 0.0))
            balances[name] = balance
            if account in BASIS_ACCOUNTS:
                basis[name] = float(config.get(f"{account}_basis", balance))
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


def _incremental_ordinary_tax(
    args: dict,
    distribution: float,
    taxable_income: float,
    inflation_factor: float,
) -> float:
    distribution = max(0.0, float(distribution))
    taxable_income = max(0.0, float(taxable_income))
    brackets = federal_brackets(args, inflation_factor)
    federal = ordinary_income_tax(
        taxable_income + distribution, brackets
    ) - ordinary_income_tax(taxable_income, brackets)
    state = distribution * float(args.get("state_tax_rate", 0.0))
    return max(0.0, federal + state)


def _rmd_tax(
    args: dict,
    distribution: float,
    inflation_factor: float,
    taxable_income: float | None = None,
) -> float:
    """Estimate incremental federal and state tax on one RMD."""
    if taxable_income is None:
        taxable_income = float(
            args.get(
                "rmd_taxable_income",
                args.get("retirement_taxable_income", 0.0),
            )
        )
    else:
        taxable_income = max(0.0, float(taxable_income))
    return _incremental_ordinary_tax(
        args, distribution, taxable_income, inflation_factor
    )


def _terminal_after_tax_value(
    args: dict,
    balances: dict[str, float],
    basis: dict[str, float],
    years: int,
) -> dict:
    retirement_income = float(args.get("retirement_taxable_income", 0.0))
    inflation_factor = _inflation_factor(args, years)
    terminal_age = _terminal_withdrawal_age(args, years)
    penalty_age = float(args.get("early_withdrawal_penalty_age", 59.5))
    penalty_rate = _early_withdrawal_penalty_rate(args)
    account_names = _account_names(args)

    def total(base: str) -> float:
        return sum(
            balances[name] for name in account_names if _base_account(name)[0] == base
        )

    def total_basis(base: str) -> float:
        return sum(
            basis.get(name, balances[name])
            for name in account_names
            if _base_account(name)[0] == base
        )

    brokerage_balance = total("brokerage")
    brokerage_gain = max(0.0, brokerage_balance - total_basis("brokerage"))
    brokerage_tax = long_term_capital_gains_tax(
        args, brokerage_gain, retirement_income, inflation_factor
    )
    brokerage = max(0.0, brokerage_balance - brokerage_tax)

    solo_balance = total("solo_401k")
    solo_tax = _incremental_ordinary_tax(
        args,
        solo_balance,
        retirement_income,
        inflation_factor,
    )
    hsa_balance = total("hsa")
    hsa_tax = 0.0
    hsa_penalty = 0.0
    if not args.get("hsa_qualified_withdrawals", True):
        hsa_tax = hsa_balance * float(args.get("hsa_withdrawal_tax_rate", 0.20))
        if terminal_age < float(args.get("hsa_penalty_age", 65)):
            hsa_penalty = hsa_balance * float(args.get("hsa_penalty_rate", 0.20))
    penalty_applies = terminal_age < penalty_age
    roth_ira_penalty = (
        penalty_rate * max(0.0, total("roth_ira") - total_basis("roth_ira"))
        if penalty_applies
        else 0.0
    )
    roth_401k_penalty = (
        penalty_rate * max(0.0, total("roth_401k") - total_basis("roth_401k"))
        if penalty_applies
        else 0.0
    )
    early_penalties = {
        "solo_401k": penalty_rate * solo_balance if penalty_applies else 0.0,
        "roth_ira": roth_ira_penalty,
        "roth_401k": roth_401k_penalty,
        "hsa": hsa_penalty,
    }
    early_withdrawal_penalty = sum(early_penalties.values())
    solo = max(0.0, solo_balance - solo_tax - early_penalties["solo_401k"])
    roth_ira = max(0.0, total("roth_ira") - roth_ira_penalty)
    roth_401k = max(0.0, total("roth_401k") - roth_401k_penalty)
    hsa = max(0.0, hsa_balance - hsa_tax - hsa_penalty)
    after_tax = (
        total("emergency_fund") + hsa + roth_ira + roth_401k + brokerage + solo
    )
    return {
        "final_value": after_tax,
        "final_brokerage": brokerage,
        "final_solo_401k": solo,
        "final_roth_ira": roth_ira,
        "final_roth_401k": roth_401k,
        "final_hsa": hsa,
        "terminal_tax": brokerage_tax + solo_tax + hsa_tax,
        "early_withdrawal_penalty": early_withdrawal_penalty,
        "early_withdrawal_penalties": early_penalties,
        "terminal_cost": (
            brokerage_tax + solo_tax + hsa_tax + early_withdrawal_penalty
        ),
        "terminal_withdrawal_age": terminal_age,
    }


def _monthly_path(values: list[float], years: int, name: str) -> list[float]:
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
    raise ValueError(
        f"{name} path must contain projection_years or projection_years * 12 values"
    )


def _retirement_start_age(args: dict) -> float | None:
    value = args.get("retirement_start_age")
    return None if value is None else float(value)


def _social_security_monthly(args: dict, age: float, inflation_factor: float) -> float:
    claim_age = float(args.get("social_security_claim_age", 67))
    if age < claim_age:
        return 0.0
    return max(
        0.0,
        float(args.get("social_security_annual_benefit", 0.0))
        * inflation_factor
        / 12.0,
    )


def _pay_tax_from_balances(
    balances: dict[str, float],
    basis: dict[str, float],
    amount: float,
) -> float:
    """Pay a tax bill from taxable cash first, then the emergency fund."""
    remaining = max(0.0, float(amount))
    for base in ("brokerage", "emergency_fund"):
        if remaining <= 1e-9:
            break
        for account in sorted(
            (name for name in balances if _base_account(name)[0] == base)
        ):
            if remaining <= 1e-9:
                break
            available = max(0.0, balances.get(account, 0.0))
            payment = min(available, remaining)
            balances[account] = available - payment
            if base == "brokerage" and available > 0.0:
                cost_ratio = min(1.0, max(0.0, basis.get(account, 0.0)) / available)
                basis[account] = max(0.0, basis.get(account, 0.0) - payment * cost_ratio)
            remaining -= payment
    return remaining


def _withdraw_for_expenses(
    args: dict,
    balances: dict[str, float],
    basis: dict[str, float],
    need: float,
    age: float,
    taxable_income: float,
    inflation_factor: float,
) -> tuple[float, float, dict[str, float], list[str]]:
    """Withdraw liquid assets for retirement spending.

    Returns (cash raised, tax, distribution by account, warnings).  Traditional
    withdrawals are grossed up for estimated tax; Roth basis and HSA funds are
    treated as qualified by default.
    """
    if need <= 0.0:
        return 0.0, 0.0, {}, []
    order = args.get("retirement_withdrawal_order") or [
        "emergency_fund",
        "brokerage",
        "roth_ira",
        "hsa",
        "roth_401k",
        "solo_401k",
    ]
    _validate_withdrawal_order(order)
    expanded = [
        f"{base}_{owner}" for base in order for owner in _owners(args)
    ]
    tax = 0.0
    raised = 0.0
    distributions = {}
    warnings = []
    penalty_age = float(args.get("early_withdrawal_penalty_age", 59.5))
    penalty_rate = _early_withdrawal_penalty_rate(args)
    restrict_early_withdrawals = bool(args.get("restrict_early_withdrawals", False))
    for account in expanded:
        if raised >= need - 1e-9:
            break
        base, _ = _base_account(account)
        available = balances.get(account, 0.0)
        if available <= 0:
            continue
        if restrict_early_withdrawals and base == "solo_401k" and age < penalty_age:
            warnings.append(f"withdrawal restricted for {account}")
            continue
        if (
            restrict_early_withdrawals
            and base == "hsa"
            and not args.get("hsa_qualified_withdrawals", True)
            and age < float(args.get("hsa_penalty_age", 65))
        ):
            warnings.append(f"withdrawal restricted for {account}")
            continue
        if (
            restrict_early_withdrawals
            and base in {"roth_ira", "roth_401k"}
            and age < penalty_age
        ):
            available = min(available, max(0.0, basis.get(account, 0.0)))
        amount = min(available, need - raised)
        if amount <= 0.0:
            continue
        account_tax = 0.0
        if base == "solo_401k":
            account_tax = _rmd_tax(args, amount, inflation_factor, taxable_income)
        elif base == "brokerage":
            gain_ratio = (
                max(0.0, available - basis.get(account, available)) / available
            )
            account_tax = long_term_capital_gains_tax(
                args, amount * gain_ratio, taxable_income, inflation_factor
            )
            basis[account] = max(
                0.0, basis.get(account, 0.0) - amount * gain_ratio
            )
        elif base in {"roth_ira", "roth_401k"}:
            taxable_part = max(0.0, amount - basis.get(account, 0.0))
            if age < penalty_age:
                penalty = taxable_part * penalty_rate
                account_tax += penalty
                warnings.append(f"early withdrawal penalty on {account}")
            basis[account] = max(0.0, basis.get(account, 0.0) - amount)
        elif base == "hsa" and not args.get("hsa_qualified_withdrawals", True):
            account_tax = amount * float(args.get("hsa_withdrawal_tax_rate", 0.20))
            if age < float(args.get("hsa_penalty_age", 65)):
                account_tax += amount * float(args.get("hsa_penalty_rate", 0.20))
        if base == "solo_401k" and age < penalty_age:
            account_tax += amount * penalty_rate
            warnings.append("early withdrawal penalty on solo_401k")
        balances[account] = max(0.0, available - amount)
        raised += max(0.0, amount - account_tax)
        tax += account_tax
        distributions[account] = distributions.get(account, 0.0) + amount
    if raised < need - 1e-9:
        warnings.append("retirement liquidity shortfall")
    return raised, tax, distributions, warnings


def _roth_conversion_amount(args: dict, year: int) -> float:
    entries = args.get("roth_conversions", args.get("roth_conversion_schedule", []))
    if entries is None:
        return 0.0
    if isinstance(entries, (int, float)):
        return max(0.0, float(entries))
    if not isinstance(entries, list):
        raise ValueError("roth_conversions must be an amount or list of tables")
    age = _annual_age(args, year)
    total = 0.0
    for entry in entries:
        if _schedule_active(entry, age, year, _starting_age(args)):
            total += float(entry.get("annual_amount", entry.get("amount", 0.0)))
    return max(0.0, total)


def _simulate_plan(
    args: dict,
    allocator,
    label: str,
    stock_returns: list[float] | None = None,
    inflation_rates: list[float] | None = None,
    rng: random.Random | None = None,
) -> dict:
    """Simulate one allocation plan and return nominal terminal value and NPV."""
    years = int(args["projection_years"])
    if stock_returns is None or inflation_rates is None:
        if rng is None:
            rng = random.Random()
        stock_returns, inflation_rates = make_market_paths(args, rng)
    stock_returns = _monthly_path(stock_returns, years, "stock")
    inflation_rates = _monthly_path(inflation_rates, years, "inflation")

    balances, basis = _starting_balances(args)
    initial_investment = sum(balances.values())
    annual_contributions = []
    annual_employer_contributions = []
    annual_rmds = []
    annual_income = []
    annual_expenses = []
    annual_taxes = []
    annual_distributions = []
    annual_conversions = []
    monthly_contributions_history = []
    monthly_distributions_history = []
    monthly_income_history = []
    monthly_expenses_history = []
    monthly_taxes_history = []
    warnings = []
    retirement_shortfall = 0.0
    retirement_months = 0
    npv_history = []
    npv_cash_flow = -initial_investment
    inflation_factor = 1.0
    rmd_total = 0.0
    rmd_tax_total = 0.0
    rmd_reinvested = 0.0
    conversion_tax_total = 0.0
    harvested_total = 0.0
    harvesting_history = []
    min_emergency = float("inf")
    peak = 0.0
    max_drawdown = 0.0
    monthly_emergency_return = (1.0 + float(args["emergency_fund_return"])) ** (
        1.0 / 12.0
    ) - 1.0
    monthly_dividend_yield = (1.0 + float(args["brokerage_dividend_yield"])) ** (
        1.0 / 12.0
    ) - 1.0

    account_names = _account_names(args)

    for year in range(years):
        year_inflation_factor = _inflation_factor(args, year)
        brackets = federal_brackets(args, year_inflation_factor)
        rmd_basis_balance = sum(
            balances[name]
            for name in account_names
            if _base_account(name)[0] == "solo_401k"
        )
        contributions = allocator(year, balances)
        retirement_age_config = _retirement_start_age(args)
        if (
            retirement_age_config is not None
            and _annual_age(args, year) >= retirement_age_config
            and not args.get("continue_contributing_after_retirement", False)
        ):
            contributions = dict.fromkeys(account_names, 0.0)
            contributions["_cash_remaining"] = 0.0
            contributions["_employer_contribution"] = 0.0
            contributions["_employer_contribution_by_owner"] = {
                owner: 0.0 for owner in _owners(args)
            }
        income_for_year = _annual_income(args, year)
        expenses_for_year = _annual_expenses(args, year)
        annual_cash_contribution = _annual_contribution_cash_cost(
            args, contributions, year, income_for_year
        )
        annual_income.append(income_for_year)
        annual_expenses.append(expenses_for_year)
        annual_contributions.append(
            {name: contributions[name] for name in account_names}
        )
        annual_employer_contributions.append(contributions["_employer_contribution"])
        solo_contribution = sum(
            contributions[name]
            for name in account_names
            if _base_account(name)[0] == "solo_401k"
        )
        taxable_income = current_taxable_income(
            args, solo_contribution, year_inflation_factor, income_for_year
        )
        annual_income_tax = current_income_tax(
            args, solo_contribution, year_inflation_factor, income_for_year
        )
        year_taxes = annual_income_tax
        year_distributions = {}
        year_shortfall = 0.0

        monthly_contributions = {name: contributions[name] / 12.0 for name in account_names}
        employer_by_owner = contributions.get("_employer_contribution_by_owner", {})
        for name in account_names:
            base, owner = _base_account(name)
            if base == "solo_401k":
                monthly_contributions[name] += employer_by_owner.get(owner, 0.0) / 12.0
        for month in range(year * 12, (year + 1) * 12):
            monthly_cash_contribution = annual_cash_contribution / 12.0
            npv_cash_flow -= monthly_cash_contribution / _discount_factor(
                args, month / 12.0
            )
            stock_return = stock_returns[month]
            inflation_rate = inflation_rates[month]
            month_tax = 0.0
            for account in account_names:
                contribution = monthly_contributions[account]
                before_return = balances[account] + contribution
                base, _ = _base_account(account)
                if base == "emergency_fund":
                    interest = before_return * monthly_emergency_return
                    tax_rate = marginal_ordinary_rate(taxable_income, brackets) + float(
                        args.get("state_tax_rate", 0.0)
                    )
                    month_tax += max(0.0, interest * tax_rate)
                    balances[account] = max(
                        0.0, before_return + interest * (1.0 - tax_rate)
                    )
                elif base == "brokerage":
                    dividend = max(0.0, before_return * monthly_dividend_yield)
                    dividend_tax = long_term_capital_gains_tax(
                        args, dividend, taxable_income, year_inflation_factor
                    )
                    month_tax += dividend_tax
                    balances[account] = max(
                        0.0, before_return * (1.0 + stock_return) - dividend_tax
                    )
                    basis[account] += contribution + max(0.0, dividend - dividend_tax)
                else:
                    balances[account] = max(
                        0.0, before_return * (1.0 + stock_return)
                    )
                    if base in {"roth_ira", "roth_401k"}:
                        basis[account] += contribution
            retirement_age = _retirement_start_age(args)
            current_age = _starting_age(args) + month / 12.0
            month_expense = expenses_for_year / 12.0
            month_distributions = {}
            if retirement_age is not None and current_age >= retirement_age:
                retirement_months += 1
                if args.get("retirement_monthly_expenses") is not None:
                    configured_expenses = float(args["retirement_monthly_expenses"])
                elif args.get("retirement_annual_expenses") is not None:
                    configured_expenses = (
                        float(args["retirement_annual_expenses"]) / 12.0
                    )
                else:
                    configured_expenses = expenses_for_year / 12.0
                month_expense = max(0.0, configured_expenses * inflation_factor)
                social_security = _social_security_monthly(
                    args, current_age, inflation_factor
                )
                monthly_income_history.append(income_for_year / 12.0 + social_security)
                need = max(0.0, month_expense - social_security)
                raised, withdrawal_tax, month_distributions, month_warnings = (
                    _withdraw_for_expenses(
                        args,
                        balances,
                        basis,
                        need,
                        current_age,
                        taxable_income,
                        year_inflation_factor,
                    )
                )
                month_tax += withdrawal_tax
                warnings.extend(month_warnings)
                if raised < need:
                    year_shortfall += need - raised
                    retirement_shortfall += need - raised
                npv_cash_flow += raised / _discount_factor(args, (month + 1) / 12.0)
            else:
                monthly_income_history.append(income_for_year / 12.0)
            monthly_contributions_history.append(
                {
                    "month": month + 1,
                    "year": year,
                    "age": current_age,
                    **monthly_contributions,
                }
            )
            monthly_distributions_history.append(
                {
                    "month": month + 1,
                    "year": year,
                    "age": current_age,
                    **month_distributions,
                }
            )
            monthly_expenses_history.append(month_expense)
            monthly_taxes_history.append(annual_income_tax / 12.0 + month_tax)
            year_taxes += month_tax
            for account, amount in month_distributions.items():
                year_distributions[account] = (
                    year_distributions.get(account, 0.0) + amount
                )
            inflation_factor *= max(0.01, 1.0 + inflation_rate)
            gross_value = sum(balances.values())
            portfolio_value = gross_value / _discount_factor(args, (month + 1) / 12.0)
            npv_value = npv_cash_flow + portfolio_value
            npv_history.append(npv_value)
            min_emergency = min(
                min_emergency,
                sum(
                    balances[name]
                    for name in account_names
                    if _base_account(name)[0] == "emergency_fund"
                ),
            )
            peak = max(peak, portfolio_value)
            if peak > 0.0:
                max_drawdown = max(max_drawdown, (peak - portfolio_value) / peak)

        age = _annual_age(args, year)
        brokerage_names = [
            name for name in account_names if _base_account(name)[0] == "brokerage"
        ]
        solo_names = [
            name for name in account_names if _base_account(name)[0] == "solo_401k"
        ]
        total_brokerage = sum(balances[name] for name in brokerage_names)
        brokerage_gains = {
            name: max(0.0, balances[name] - basis.get(name, balances[name]))
            for name in brokerage_names
        }
        total_brokerage_gain = sum(brokerage_gains.values())
        harvested = 0.0
        harvest_tax = 0.0
        if total_brokerage_gain > 0.0:
            harvested = _ltcg_harvest_request(
                args, total_brokerage_gain, taxable_income, year_inflation_factor
            )
        if harvested > 0.0:
            harvest_tax = long_term_capital_gains_tax(
                args, harvested, taxable_income, year_inflation_factor
            )
            for name in brokerage_names:
                balance_share = (
                    balances[name] / total_brokerage if total_brokerage > 0.0 else 0.0
                )
                gain_share = (
                    brokerage_gains[name] / total_brokerage_gain
                    if total_brokerage_gain > 0.0
                    else 0.0
                )
                balances[name] = max(
                    0.0, balances[name] - harvest_tax * balance_share
                )
                # Realizing a gain raises basis by that gain; it does not reset
                # the basis of unrelated unrealized gains.
                basis[name] = basis.get(name, balances[name]) + harvested * gain_share
            harvested_total += harvested
            harvesting_history.append(
                {
                    "age": age,
                    "gain": harvested,
                    "tax": harvest_tax,
                    "zero_percent_room": _ltcg_zero_percent_room(
                        args, taxable_income, year_inflation_factor
                    ),
                }
            )
            year_taxes += harvest_tax
        total_solo = sum(balances[name] for name in solo_names)
        conversion = min(total_solo, _roth_conversion_amount(args, year))
        conversion_tax = 0.0
        if conversion > 0:
            conversion_tax = _incremental_ordinary_tax(
                args,
                conversion,
                taxable_income,
                year_inflation_factor,
            )
            for name in solo_names:
                share = balances[name] / total_solo if total_solo > 0.0 else 0.0
                amount = conversion * share
                balances[name] -= amount
                owner = _base_account(name)[1]
                roth = f"roth_ira_{owner}"
                balances[roth] += amount
                basis[roth] += amount
            unpaid_conversion_tax = _pay_tax_from_balances(
                balances, basis, conversion_tax
            )
            if unpaid_conversion_tax > 1e-9:
                warnings.append(
                    f"unable to pay Roth conversion tax: {unpaid_conversion_tax:.2f}"
                )
            annual_conversions.append(
                {"age": age, "gross": conversion, "tax": conversion_tax}
            )
            conversion_tax_total += conversion_tax
            year_taxes += conversion_tax
        rmd_factor = _rmd_factor(args, age)
        rmd_tax = 0.0
        total_solo_now = sum(balances[name] for name in solo_names)
        rmd = (
            min(total_solo_now, rmd_basis_balance / rmd_factor)
            if math.isfinite(rmd_factor) and rmd_basis_balance > 0.0
            else 0.0
        )
        if rmd > 0.0:
            rmd_tax = _rmd_tax(args, rmd, year_inflation_factor, taxable_income)
            net_rmd = max(0.0, rmd - rmd_tax)
            rmd_shares = {
                name: (balances[name] / total_solo_now if total_solo_now > 0.0 else 0.0)
                for name in solo_names
            }
            for name in solo_names:
                balances[name] = max(0.0, balances[name] - rmd * rmd_shares[name])
            if args.get("rmd_reinvest_after_tax", True):
                for name in brokerage_names:
                    owner = _base_account(name)[1]
                    amount = net_rmd * rmd_shares.get(f"solo_401k_{owner}", 0.0)
                    balances[name] += amount
                    basis[name] += amount
                    rmd_reinvested += amount
            rmd_total += rmd
            rmd_tax_total += rmd_tax
            year_taxes += rmd_tax
            if not args.get("rmd_reinvest_after_tax", True):
                npv_cash_flow += net_rmd / _discount_factor(args, year + 1.0)
            year_distributions["solo_401k"] = (
                year_distributions.get("solo_401k", 0.0) + rmd
            )
            annual_rmds.append(
                {
                    "age": age,
                    "factor": rmd_factor,
                    "gross": rmd,
                    "tax": rmd_tax,
                    "reinvested": (
                        net_rmd if args.get("rmd_reinvest_after_tax", True) else 0.0
                    ),
                }
            )
            portfolio_value = sum(balances.values()) / _discount_factor(
                args, year + 1.0
            )
            npv_value = npv_cash_flow + portfolio_value
            npv_history[-1] = npv_value
            peak = max(peak, portfolio_value)
            if peak > 0.0:
                max_drawdown = max(max_drawdown, (peak - portfolio_value) / peak)
        if harvest_tax > 0.0 or conversion_tax > 0.0 or rmd_tax_total > 0.0:
            monthly_taxes_history[-1] += (
                harvest_tax + conversion_tax + (rmd_tax if rmd > 0.0 else 0.0)
            )
        annual_taxes.append(year_taxes)
        annual_distributions.append(year_distributions)
        if year_shortfall > 0:
            warnings.append(f"retirement shortfall at age {age}: {year_shortfall:.2f}")

    terminal = _terminal_after_tax_value(args, balances, basis, years)
    terminal["strategy"] = label
    terminal["balances"] = balances
    terminal["basis"] = basis
    terminal["annual_contributions"] = annual_contributions
    terminal["annual_employer_contributions"] = annual_employer_contributions
    terminal["annual_rmds"] = annual_rmds
    terminal["annual_income"] = annual_income
    terminal["annual_expenses"] = annual_expenses
    terminal["annual_taxes"] = annual_taxes
    terminal["annual_distributions"] = annual_distributions
    terminal["annual_roth_conversions"] = annual_conversions
    terminal["monthly_contributions"] = monthly_contributions_history
    terminal["monthly_distributions"] = monthly_distributions_history
    terminal["monthly_income"] = monthly_income_history
    terminal["monthly_expenses"] = monthly_expenses_history
    terminal["monthly_taxes"] = monthly_taxes_history
    terminal["ltcg_harvesting"] = harvesting_history
    terminal["ltcg_harvested"] = harvested_total
    terminal["warnings"] = warnings
    terminal["retirement_shortfall"] = retirement_shortfall
    terminal["retirement_success"] = (
        retirement_months == 0 or retirement_shortfall <= 1e-9
    )
    terminal["retirement_months"] = retirement_months
    terminal["rmd_total"] = rmd_total
    terminal["rmd_tax"] = rmd_tax_total
    terminal["rmd_reinvested"] = rmd_reinvested
    terminal["roth_conversion_tax"] = conversion_tax_total
    terminal["total_taxes_paid"] = sum(annual_taxes) + terminal["terminal_cost"]
    # Preserve the historical optimizer metric: taxes caused by retirement
    # withdrawals and conversions, plus terminal taxes and penalties.
    terminal["total_tax_cost"] = (
        terminal["terminal_cost"] + rmd_tax_total + conversion_tax_total
    )
    terminal["history"] = npv_history
    terminal["npv_history"] = npv_history
    terminal["max_drawdown"] = max_drawdown
    terminal["min_emergency"] = (
        min_emergency
        if npv_history
        else sum(
            balances[name]
            for name in _account_names(args)
            if _base_account(name)[0] == "emergency_fund"
        )
    )
    terminal["npv"] = npv_cash_flow + terminal["final_value"] / _discount_factor(
        args, years
    )
    if npv_history:
        npv_history[-1] = terminal["npv"]
    return terminal


def simulate_strategy(
    args: dict,
    order: tuple[str, ...],
    stock_returns: list[float] | None = None,
    inflation_rates: list[float] | None = None,
    rng: random.Random | None = None,
) -> dict:
    """Simulate one priority order and return nominal terminal value and NPV."""
    _validate_account_order(args, order)
    labels = []
    for name in order:
        base, owner = _base_account(name)
        labels.append(f"{ACCOUNT_LABELS[base]} ({owner})")
    return _simulate_plan(
        args,
        lambda year, balances: allocate_savings(args, order, balances, year),
        " -> ".join(labels),
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
    """Simulate a fixed annual cash allocation across all destinations."""
    weights = _normalize_allocation(args, allocation)
    label = _allocation_label(args, weights, separator=", ")
    return _simulate_plan(
        args,
        lambda year, balances: allocate_fixed_savings(args, weights, balances, year),
        label or "No allocation",
        stock_returns,
        inflation_rates,
        rng,
    )


def _normalize_allocation(args: dict, allocation: dict[str, float]) -> dict[str, float]:
    accounts = _account_names(args)
    if set(allocation) != set(accounts):
        raise ValueError(f"allocation must contain each account: {accounts}")
    values = {name: max(0.0, float(allocation[name])) for name in accounts}
    total = sum(values.values())
    if total <= 0.0:
        raise ValueError("allocation must contain a positive total")
    return {name: value / total for name, value in values.items()}


def _derive_seed(seed: int, simulation: int) -> int:
    return (seed + simulation * 1000003) & ((1 << 64) - 1)


def _percentile(values: list[float], fraction: float) -> float:
    if not values:
        return 0.0
    index = int(fraction * (len(values) - 1))
    return sorted(values)[index]


def _monte_carlo_options(
    args: dict, simulations: int | None, seed: int | None
) -> tuple[int, int]:
    simulations = int(
        simulations if simulations is not None else args["monte_carlo_simulations"]
    )
    seed = int(seed if seed is not None else args["monte_carlo_seed"])
    if simulations < 1:
        raise ValueError("simulations must be at least 1")
    return simulations, seed


def _run_trials(payloads, trial_runner, workers: int):
    if workers > 1:
        with ProcessPoolExecutor(max_workers=workers) as executor:
            return list(executor.map(trial_runner, payloads))
    return [trial_runner(payload) for payload in payloads]


def _best_counts(trials: list[list[float]]) -> list[int]:
    best_counts = [0] * len(trials[0])
    for trial in trials:
        best = max(trial)
        for index, value in enumerate(trial):
            if value == best:
                best_counts[index] += 1
    return best_counts


def _compact_result(result: dict) -> dict:
    return {
        "npv": result["npv"],
        "final_value": result["final_value"],
        "terminal_tax": result["terminal_tax"],
        "early_withdrawal_penalty": result["early_withdrawal_penalty"],
        "terminal_cost": result["terminal_cost"],
        "rmd_tax": result["rmd_tax"],
        "roth_conversion_tax": result["roth_conversion_tax"],
        "total_tax_cost": result["total_tax_cost"],
        "min_emergency": result["min_emergency"],
        "max_drawdown": result["max_drawdown"],
        "retirement_success": float(result["retirement_success"]),
        "retirement_shortfall": result["retirement_shortfall"],
        "warning_count": float(len(result["warnings"])),
        "total_taxes_paid": result["total_taxes_paid"],
        "ltcg_harvested": result["ltcg_harvested"],
        "ltcg_harvesting": result["ltcg_harvesting"],
    }


def _run_allocation_trial(
    payload: tuple[dict, int, list[dict[str, float]]],
) -> list[dict]:
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
        return result["npv"]
    if objective == "min_tax":
        return -result["total_tax_cost"]
    if objective == "emergency":
        return result["min_emergency"]
    if objective == "drawdown":
        return -result["max_drawdown"]
    if objective == "retirement_success":
        return result["retirement_success"]
    if objective == "shortfall":
        return -result["retirement_shortfall"]
    if objective == "warnings":
        return -result["warning_count"]
    raise ValueError(f"unknown objective: {objective}")


def _summarize_allocations(
    args: dict,
    allocations: list[dict[str, float]],
    trials: list[list[dict[str, float]]],
    objective: str,
) -> list[dict]:
    summaries = []
    score_trials = [
        [_objective_value(result, objective) for result in trial] for trial in trials
    ]
    best_counts = _best_counts(score_trials)

    for index, allocation in enumerate(allocations):
        results = [trial[index] for trial in trials]
        values = [result["npv"] for result in results]
        taxes = [result["terminal_tax"] for result in results]
        penalties = [result["early_withdrawal_penalty"] for result in results]
        terminal_costs = [result["terminal_cost"] for result in results]
        rmd_taxes = [result["rmd_tax"] for result in results]
        conversion_taxes = [result["roth_conversion_tax"] for result in results]
        total_tax_costs = [result["total_tax_cost"] for result in results]
        emergencies = [result["min_emergency"] for result in results]
        drawdowns = [result["max_drawdown"] for result in results]
        successes = [result["retirement_success"] for result in results]
        shortfalls = [result["retirement_shortfall"] for result in results]
        warning_counts = [result["warning_count"] for result in results]
        harvested = [result["ltcg_harvested"] for result in results]
        objective_values = [_objective_value(result, objective) for result in results]
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
        elif objective == "retirement_success":
            score = mean(successes)
        elif objective == "shortfall":
            score = -mean(shortfalls)
        elif objective == "warnings":
            score = -mean(warning_counts)
        else:
            score = _percentile(objective_values, 0.50)
        summaries.append(
            {
                "allocation": _normalize_allocation(args, allocation),
                "strategy": _allocation_label(args, allocation),
                "median": _percentile(values, 0.50),
                "p10": _percentile(values, 0.10),
                "p25": _percentile(values, 0.25),
                "p75": _percentile(values, 0.75),
                "mean": mean(values),
                "terminal_tax": mean(taxes),
                "early_withdrawal_penalty": mean(penalties),
                "terminal_cost": mean(terminal_costs),
                "rmd_tax": mean(rmd_taxes),
                "roth_conversion_tax": mean(conversion_taxes),
                "total_tax_cost": mean(total_tax_costs),
                "min_emergency": mean(emergencies),
                "max_drawdown": mean(drawdowns),
                "retirement_success": mean(successes),
                "retirement_shortfall": mean(shortfalls),
                "warning_count": mean(warning_counts),
                "ltcg_harvested": mean(harvested),
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
    workers: int = DEFAULT_WORKERS,
    objective: str = "median",
) -> tuple[list[dict], list[list[dict]]]:
    """Evaluate fixed dollar splits using common monthly market paths."""
    if objective not in ALLOCATION_OBJECTIVES:
        raise ValueError(f"objective must be one of {ALLOCATION_OBJECTIVES}")
    simulations, seed = _monte_carlo_options(args, simulations, seed)
    normalized = [_normalize_allocation(args, allocation) for allocation in allocations]
    payloads = (
        (args, _derive_seed(seed, index), normalized) for index in range(simulations)
    )
    trials = _run_trials(payloads, _run_allocation_trial, workers)

    raw = [[trial[index] for trial in trials] for index in range(len(normalized))]
    summaries = _summarize_allocations(args, normalized, trials, objective)
    order = sorted(
        range(len(summaries)), key=lambda index: summaries[index]["score"], reverse=True
    )
    summaries = [summaries[index] for index in order]
    raw = [raw[index] for index in order]
    return summaries, raw


def _allocation_label(
    args: dict, allocation: dict[str, float], separator: str = " | "
) -> str:
    weights = _normalize_allocation(args, allocation)
    parts = []
    for name in ACCOUNT_NAMES:
        for owner in _owners(args):
            key = f"{name}_{owner}"
            if weights[key] > 1e-9:
                parts.append(f"{ACCOUNT_LABELS[name]} ({owner}) {weights[key]:.0%}")
    return separator.join(parts)


def _priority_cash_allocation(args: dict, order: tuple[str, ...]) -> dict[str, float]:
    balances = dict.fromkeys(_account_names(args), 0.0)
    contributions = allocate_savings(args, order, balances)
    allocation = {name: contributions[name] for name in _account_names(args)}
    for name in _account_names(args):
        base, _ = _base_account(name)
        if base == "solo_401k":
            allocation[name] = pretax_cash_cost(args, contributions[name])
    return _normalize_allocation(args, allocation)


def _seed_allocations(args: dict) -> list[dict[str, float]]:
    seeds = []
    for account in ACCOUNT_NAMES:
        for owner in _owners(args):
            name = f"{account}_{owner}"
            seeds.append(
                {key: 1.0 if key == name else 0.0 for key in _account_names(args)}
            )
    seeds.append(
        _priority_cash_allocation(
            args,
            tuple(
                f"{base}_{owner}"
                for base in (
                    "emergency_fund",
                    "roth_ira",
                    "solo_401k",
                    "roth_401k",
                    "brokerage",
                    "hsa",
                )
                for owner in _owners(args)
            ),
        )
    )
    return seeds


def optimize_allocation(
    args: dict,
    simulations: int | None = None,
    seed: int | None = None,
    workers: int = DEFAULT_WORKERS,
    objective: str = "median",
) -> tuple[dict[str, float], dict]:
    """Search actual annual cash splits with coordinate descent."""
    annual_savings = _annual_savings(args, 0)
    if annual_savings == 0.0:
        allocation = {
            name: 1.0 if _base_account(name)[0] == "brokerage" else 0.0
            for name in _account_names(args)
        }
        summaries, _ = run_allocation_monte_carlo(
            args,
            [allocation],
            simulations=simulations,
            seed=seed,
            workers=workers,
            objective=objective,
        )
        return allocation, summaries[0]

    step = max(
        float(args.get("optimization_step", 1000.0)),
        annual_savings / 200.0,
    )
    passes = max(1, int(args.get("optimization_passes", 3)))
    starts = [_normalize_allocation(args, start) for start in _seed_allocations(args)]
    cache = {}

    def key(allocation):
        return tuple(round(allocation[name], 12) for name in _account_names(args))

    def evaluate(candidates):
        unique = []
        for candidate in candidates:
            candidate = _normalize_allocation(args, candidate)
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
            cache.update(
                {key(candidate): by_key[key(candidate)] for candidate in unique}
            )
        return [
            cache[key(_normalize_allocation(args, candidate))] for candidate in candidates
        ]

    best_allocation = starts[0]
    best_summary = evaluate([best_allocation])[0]
    for start in starts:
        current = start
        current_summary = evaluate([current])[0]
        for _ in range(passes):
            candidates = []
            for source in _account_names(args):
                source_cash = current[source] * annual_savings
                if source_cash < step:
                    continue
                for target in _account_names(args):
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
    weights = _normalize_allocation(args, allocation)
    annual_savings = _annual_savings(args, 0)
    parts = []
    for name in _account_names(args):
        if weights[name] > 1e-9:
            base, owner = _base_account(name)
            parts.append(
                f"{ACCOUNT_LABELS[base]} ({owner}) "
                f"{_currency(weights[name] * annual_savings)} ({weights[name]:.0%})"
            )
    return " | ".join(parts)


def _harvest_plan_rows(args: dict, trials: list[dict]) -> list[list]:
    """Annual LTCG plan with conditional mean gains and median context."""
    years = int(args["projection_years"])
    start_age = _starting_age(args)
    rows = []
    for age in range(start_age, start_age + years):
        gains = []
        taxes = []
        rooms = []
        for trial in trials:
            gain = 0.0
            tax = 0.0
            for entry in trial.get("ltcg_harvesting", ()):
                if entry["age"] == age:
                    gain += entry["gain"]
                    tax += entry["tax"]
                    rooms.append(entry["zero_percent_room"])
            gains.append(gain)
            taxes.append(tax)
        if max(gains) <= 1e-9:
            continue
        share = sum(1 for gain in gains if gain > 1e-9) / len(gains)
        harvested_gains = [gain for gain in gains if gain > 1e-9]
        rows.append(
            [
                age,
                _currency(mean(harvested_gains)),
                _currency(_percentile(taxes, 0.5)),
                _currency(_percentile(rooms, 0.5)),
                f"{share:.0%}",
            ]
        )
    return rows


def print_allocation_results(
    args: dict,
    summaries: list[dict],
    objective: str,
    top: int,
    raw: list[list[dict]] | None = None,
) -> None:
    rows = [
        [
            _allocation_with_dollars(args, summary["allocation"]),
            _currency(summary["median"]),
            _currency(summary["p10"]),
            _currency(summary["p75"]),
            _currency(summary["terminal_tax"]),
            _currency(summary["early_withdrawal_penalty"]),
            _currency(summary["rmd_tax"]),
            f"{summary['max_drawdown']:.1%}",
        ]
        for summary in summaries[:top]
    ]
    print(f"Optimized annual cash allocations (objective: {objective}):")
    print(
        tabulate(
            rows,
            headers=[
                "Annual allocation",
                "Median NPV",
                "P10 NPV",
                "P75 NPV",
                "Avg terminal tax",
                "Avg early penalty",
                "Avg RMD tax",
                "Avg drawdown",
            ],
            tablefmt="simple",
        )
    )
    best = summaries[0]
    recommendation = _allocation_with_dollars(args, best["allocation"])
    print(f"\nRecommended annual allocation: {recommendation}")
    if raw and args.get("ltcg_harvesting", "none") != "none":
        plan = _harvest_plan_rows(args, raw[0])
        if plan:
            print("\nAnnual LTCG harvesting plan:")
            print(
                tabulate(
                    plan,
                    headers=[
                        "Age",
                        "Mean gain if harvested",
                        "Harvest tax (median)",
                        "0% room left (median)",
                        "Share of trials",
                    ],
                    tablefmt="simple",
                )
            )
            print(
                "Average lifetime LTCG harvested: "
                f"{_currency(best.get('ltcg_harvested', 0.0))}"
            )


def load_toml_config(filepath: str) -> dict:
    with open(filepath, "rb") as file:
        data = tomllib.load(file)

    defaults = {
        "annual_savings": None,
        "annual_expenses": 0.0,
        "annual_income": 100000.0,
        "filing_status": "mfj",
        "starting_age": 30,
        "standard_deduction": 31500.0,
        "state_standard_deduction": 10400.0,
        "state_tax_rate": 0.0495,
        "state_capital_gains_tax_rate": None,
        "projection_years": 30,
        "savings_growth_rate": 0.0,
        "discount_rate": None,
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
        "hsa_eligible": False,
        "hsa_limit": 0.0,
        "hsa_family_limit": 0.0,
        "hsa_catchup": 1000.0,
        "hsa_catchup_age": 55,
        "hsa_family": False,
        "hsa_shared_limit": False,
        "hsa_qualified_withdrawals": True,
        "solo_401k_employer_rate": 0.0,
        "stock_return": 0.07,
        "stock_volatility": 0.18,
        "inflation_rate": 0.03,
        "inflation_volatility": 0.015,
        "brokerage_dividend_yield": 0.02,
        "ltcg_bracket0_limit_mfj": 98900.0,
        "ltcg_bracket1_limit_mfj": 613700.0,
        "ltcg_bracket0_limit_single": 49450.0,
        "ltcg_bracket1_limit_single": 545500.0,
        "ltcg_bracket0_rate": 0.0,
        "ltcg_bracket1_rate": 0.15,
        "ltcg_bracket2_rate": 0.20,
        "retirement_taxable_income": 0.0,
        "retirement_start_age": None,
        "retirement_annual_expenses": None,
        "retirement_monthly_expenses": None,
        "social_security_claim_age": 67,
        "social_security_annual_benefit": 0.0,
        "retirement_withdrawal_order": None,
        "restrict_early_withdrawals": True,
        "roth_conversions": [],
        "ltcg_harvesting": "none",
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
        "federal_brackets_mfs": FEDERAL_BRACKETS_MFS,
    }
    defaults.update(data)
    defaults["projection_years"] = int(defaults["projection_years"])
    defaults["rmd_start_age"] = int(defaults["rmd_start_age"])
    if defaults["rmd_start_age"] < min(UNIFORM_LIFETIME):
        raise ValueError("rmd_start_age must be at least 70")
    defaults["federal_brackets_mfj"] = _normalize_brackets(
        defaults["federal_brackets_mfj"]
    )
    defaults["federal_brackets_single"] = _normalize_brackets(
        defaults["federal_brackets_single"]
    )
    defaults["federal_brackets_mfs"] = _normalize_brackets(
        defaults["federal_brackets_mfs"]
    )
    if "federal_brackets" in defaults:
        defaults["federal_brackets"] = _normalize_brackets(defaults["federal_brackets"])
    defaults["early_withdrawal_penalty_rate"] = _early_withdrawal_penalty_rate(defaults)
    _discount_rate(defaults)
    status = str(defaults.get("filing_status", "mfj")).lower()
    if status not in {"mfj", "single", "s", "mfs", "married_filing_separately"}:
        raise ValueError("filing_status must be mfj, single, or mfs")
    for key in (
        "annual_income",
        "annual_expenses",
        "hsa_limit",
        "hsa_catchup",
        "state_tax_rate",
        "state_capital_gains_tax_rate",
        "stock_volatility",
        "inflation_volatility",
    ):
        value = defaults.get(key)
        if isinstance(value, dict):
            if any(float(item) < 0 for item in value.values()):
                raise ValueError(f"{key} must be non-negative")
        elif value is not None and float(value) < 0:
            raise ValueError(f"{key} must be non-negative")
    if (
        defaults.get("annual_savings") is not None
        and float(defaults["annual_savings"]) < 0
    ):
        raise ValueError("annual_savings must be non-negative")
    for schedule_name in ("incomes", "expenses", "contribution_schedules"):
        _schedule_entries(defaults, schedule_name)
        for entry in _schedule_entries(defaults, schedule_name):
            if not isinstance(entry, dict):
                raise ValueError(f"{schedule_name} entries must be tables")
            if (
                "start_age" in entry
                and "end_age" in entry
                and int(entry["end_age"]) < int(entry["start_age"])
            ):
                raise ValueError(f"{schedule_name} end_age must not precede start_age")
            if "duration" in entry and int(entry["duration"]) <= 0:
                raise ValueError(f"{schedule_name} duration must be positive")
            if schedule_name != "contribution_schedules":
                amount = entry.get("annual_amount", entry.get("amount"))
                if amount is None or float(amount) < 0:
                    raise ValueError(
                        f"{schedule_name} entries require non-negative annual_amount"
                    )
            elif entry.get("account", entry.get("destination")) not in ACCOUNT_NAMES:
                raise ValueError(
                    f"unknown contribution schedule account: "
                    f"{entry.get('account', entry.get('destination'))}"
                )
    _annual_income(defaults, 0)
    _annual_expenses(defaults, 0)
    _scheduled_contributions(defaults, 0)
    withdrawal_order = defaults.get("retirement_withdrawal_order")
    if withdrawal_order is not None:
        _validate_withdrawal_order(withdrawal_order)
    conversions = defaults.get(
        "roth_conversions", defaults.get("roth_conversion_schedule", [])
    )
    if conversions is not None and not isinstance(conversions, (int, float, list)):
        raise ValueError("roth_conversions must be an amount or list of tables")
    if isinstance(conversions, list):
        for entry in conversions:
            if not isinstance(entry, dict):
                raise ValueError("roth conversion schedule entries must be tables")
            amount = entry.get("annual_amount", entry.get("amount"))
            if amount is None or float(amount) < 0:
                raise ValueError("roth conversion amounts must be non-negative")
    _validate_ltcg_harvesting(defaults)
    defaults["early_withdrawal_penalty_age"] = float(
        defaults["early_withdrawal_penalty_age"]
    )
    if defaults["terminal_withdrawal_age"] is not None:
        defaults["terminal_withdrawal_age"] = float(defaults["terminal_withdrawal_age"])
    return defaults


def _currency(value: float) -> str:
    return f"${value:,.0f}"


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
        help="Optimization objective (default: median NPV)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=DEFAULT_WORKERS,
        help=f"Parallel worker processes (default: {DEFAULT_WORKERS})",
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
        workers=args.workers,
    )
    allocations = [optimized]
    for allocation in _seed_allocations(config):
        if tuple(_normalize_allocation(config, allocation).values()) not in {
            tuple(_normalize_allocation(config, existing).values())
            for existing in allocations
        }:
            allocations.append(allocation)
    summaries, raw = run_allocation_monte_carlo(
        config,
        allocations,
        simulations=simulations,
        seed=seed,
        workers=args.workers,
        objective=args.objective,
    )
    print_allocation_results(config, summaries, args.objective, args.top, raw)


if __name__ == "__main__":
    main()
