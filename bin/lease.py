#!/usr/bin/env python3
import calendar
import io
import shutil
import subprocess
import sys
import tempfile
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

import pypandoc
from pypdf import PdfReader
from pypdf.errors import PdfReadError
import yaml
from jinja2 import Environment, FileSystemLoader


ATTACHMENT_KEYS = (
    "safe_homes_summary",
    "flood_disclosure",
    "radon_guide",
    "radon_disclosure",
    "lead_disclosure",
    "move_in_report",
)


def latex_escape(s: str) -> str:
    replacements = {
        ord("\\"): r"\textbackslash{}",
        ord("&"): r"\&",
        ord("%"): r"\%",
        ord("_"): r"\_",
        ord("#"): r"\#",
        ord("$"): r"\$",
        ord("{"): r"\{",
        ord("}"): r"\}",
        ord("~"): r"\textasciitilde{}",
        ord("^"): r"\textasciicircum{}",
    }
    return str(s).translate(replacements)


def latex_or_url(s: str) -> str:
    if str(s).startswith(("http://", "https://")):
        escaped_url = str(s).replace("%", r"\%").replace("#", r"\#").replace("_", r"\_")
        return rf"\href{{{escaped_url}}}{{{escaped_url}}}"
    return latex_escape(s)


def md_to_latex(s: str) -> str:
    return pypandoc.convert_text(s, to='latex', format='md').strip()


def parse_date(value, field_name: str) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value))
    except ValueError as exc:
        raise ValueError(f"{field_name} must be an ISO date (YYYY-MM-DD)") from exc


def parse_money(value, field_name: str) -> Decimal:
    try:
        amount = Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be a monetary amount") from exc
    if not amount.is_finite():
        raise ValueError(f"{field_name} must be a finite monetary amount")
    if amount < 0:
        raise ValueError(f"{field_name} cannot be negative")
    return amount


def format_money(amount: Decimal) -> str:
    return rf"\${amount:,.2f}"


def rent_periods(start: date, end: date, monthly_rent: Decimal) -> list[dict[str, object]]:
    if end < start:
        raise ValueError("term.end_date must be on or after term.start_date")

    periods = []
    cursor = start
    while cursor <= end:
        month_days = calendar.monthrange(cursor.year, cursor.month)[1]
        period_end = min(end, date(cursor.year, cursor.month, month_days))
        period_days = (period_end - cursor).days + 1
        amount = (monthly_rent * Decimal(period_days) / Decimal(month_days)).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )
        periods.append(
            {
                "start": cursor.isoformat(),
                "end": period_end.isoformat(),
                "amount": format_money(amount),
                "is_full_month": period_days == month_days,
            }
        )
        cursor = period_end + timedelta(days=1)
    return periods


def normalize_tenant_names(data: dict) -> list[str]:
    raw_tenants = data.get("tenants")
    if raw_tenants is None:
        raw_tenants = data.get("tenant")
    if raw_tenants is None:
        return []
    if isinstance(raw_tenants, (str, dict)):
        raw_tenants = [raw_tenants]
    if not isinstance(raw_tenants, list):
        raise ValueError("tenant or tenants must be a name or list of names")

    names = []
    for tenant in raw_tenants:
        name = tenant.get("name") if isinstance(tenant, dict) else tenant
        if not isinstance(name, str):
            raise ValueError("each tenant must have a name")
        if name.strip():
            names.append(name.strip())
    return names


def normalize_occupants(raw_occupants) -> list[dict[str, str]]:
    if raw_occupants is None:
        return []
    if not isinstance(raw_occupants, list):
        raise ValueError("occupants must be a list")

    occupants = []
    for occupant in raw_occupants:
        if isinstance(occupant, str):
            occupants.append({"name": occupant, "role": "Occupant"})
            continue
        if not isinstance(occupant, dict) or not isinstance(occupant.get("name"), str):
            raise ValueError("each occupant must have a name")
        occupants.append(
            {
                "name": occupant["name"],
                "role": str(occupant.get("role") or "Occupant"),
            }
        )
    return occupants


def pdf_page_count(source, field_name: str) -> int:
    try:
        page_count = len(PdfReader(source, strict=True).pages)
    except (OSError, PdfReadError, ValueError) as exc:
        raise ValueError(f"{field_name} must decode as a PDF") from exc
    if page_count < 1:
        raise ValueError(f"{field_name} must contain at least one PDF page")
    return page_count


def resolve_attachments(raw_attachments, yaml_path: Path) -> dict[str, Path | bytes]:
    if raw_attachments is None:
        return {}
    if not isinstance(raw_attachments, dict):
        raise ValueError("attachments must be a mapping")
    unknown_keys = set(raw_attachments) - set(ATTACHMENT_KEYS)
    if unknown_keys:
        raise ValueError("unsupported attachment keys: " + ", ".join(sorted(unknown_keys)))

    resolved = {}
    for key in ATTACHMENT_KEYS:
        raw_path = raw_attachments.get(key)
        if raw_path is None:
            continue
        if not isinstance(raw_path, str) or not raw_path.strip():
            raise ValueError(f"attachments.{key} must be a PDF path or HTTP URL")

        raw_path = raw_path.strip()
        parsed_url = urlparse(raw_path)
        if parsed_url.scheme.lower() in ("http", "https"):
            if not parsed_url.netloc:
                raise ValueError(f"attachments.{key} must be a valid HTTP URL")
            try:
                request = Request(raw_path, headers={"User-Agent": "lease.py"})
                with urlopen(request, timeout=30) as response:
                    source = response.read()
            except (OSError, URLError) as exc:
                raise ValueError(f"could not download attachments.{key}") from exc
            pdf_page_count(io.BytesIO(source), f"attachments.{key}")
            resolved[key] = source
            continue

        source = Path(raw_path)
        if not source.is_absolute():
            source = yaml_path.parent / source
        if source.suffix.lower() != ".pdf" or not source.is_file():
            raise ValueError(f"attachments.{key} must point to an existing PDF")
        pdf_page_count(source, f"attachments.{key}")
        resolved[key] = source
    return resolved


def main():
    if len(sys.argv) != 4:
        print("Usage: lease.py template.tex.j2 lease.yaml output.pdf")
        sys.exit(1)

    template_path = Path(sys.argv[1])
    yaml_path = Path(sys.argv[2])
    data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    output_pdf = Path(sys.argv[3])
    if not isinstance(data, dict):
        raise ValueError("lease YAML must contain a mapping")

    company = data.get("company") or {}
    landlord = data.get("landlord") or {}
    premises = data.get("premises") or {}
    term = data.get("term") or {}
    draft = bool(data.get("draft", False))
    tenant_names = normalize_tenant_names(data)
    occupants = normalize_occupants(data.get("occupants"))
    max_occupants = data.get("max_occupants")
    if isinstance(max_occupants, bool) or not isinstance(max_occupants, int) or max_occupants < 1:
        raise ValueError("max_occupants must be a positive integer")
    if not draft and not tenant_names:
        raise ValueError("tenant name is required for a non-draft lease")
    if not draft and not occupants:
        raise ValueError("occupants are required for a non-draft lease")
    if len(occupants) > max_occupants:
        raise ValueError(f"occupancy cannot exceed {max_occupants} people")
    if not isinstance(landlord, dict) or not landlord.get("name"):
        raise ValueError("landlord.name is required")
    if not isinstance(premises, dict) or not premises.get("address"):
        raise ValueError("premises.address is required")
    missing_premises_fields = [
        field for field in ("city", "state", "zip", "county") if not premises.get(field)
    ]
    if missing_premises_fields:
        raise ValueError("premises fields are required: " + ", ".join(missing_premises_fields))
    if not isinstance(term, dict) or not term.get("start_date") or not term.get("end_date"):
        raise ValueError("term.start_date and term.end_date are required")
    if not data.get("date"):
        raise ValueError("date is required")
    if data.get("rent_amount") is None:
        raise ValueError("rent_amount is required")

    term_start = parse_date(term["start_date"], "term.start_date")
    term_end = parse_date(term["end_date"], "term.end_date")
    monthly_rent = parse_money(data["rent_amount"], "rent_amount")
    periods = rent_periods(term_start, term_end, monthly_rent)
    first_period = periods[0]
    last_period = periods[-1]
    regular_periods = periods[1:-1] if len(periods) > 2 else []
    if len(periods) == 1:
        regular_periods = []

    resolved_attachments = {} if draft else resolve_attachments(data.get("attachments"), yaml_path)
    if not draft:
        required_attachments = ("safe_homes_summary", "flood_disclosure", "radon_guide", "radon_disclosure")
        missing_attachments = [key for key in required_attachments if key not in resolved_attachments]
        if missing_attachments:
            raise ValueError(
                "non-draft leases require PDF attachments: " + ", ".join(missing_attachments)
            )

    for key in ("premises", "rent", "utilities", "pets", "late_fees", "flood_disclosure"):
        if isinstance(data.get(key), str):
            data[key] = md_to_latex(data[key])

    env = Environment(
        loader=FileSystemLoader(template_path.parent),
        block_start_string="~<",
        block_end_string=">~",
        variable_start_string="<<",
        variable_end_string=">>",
        comment_start_string="<#",
        comment_end_string="#>",
        trim_blocks=True,
        lstrip_blocks=True,
    )

    env.filters["latex"] = latex_escape
    env.filters["latex_or_url"] = latex_or_url

    notices = data.get("notices") or {}
    if not isinstance(notices, dict):
        raise ValueError("notices must be a mapping")
    emergency_contact = data.get("emergency_contact") or {}
    if not isinstance(emergency_contact, dict):
        raise ValueError("emergency_contact must be a mapping")
    tenant_display_names = tenant_names or [""]
    attachment_filenames = {
        key: f"attachment-{index}.pdf"
        for index, key in enumerate(resolved_attachments, start=1)
    }
    tex = env.get_template(template_path.name).render(
        draft=draft,
        company=company,
        landlord=landlord,
        tenant=", ".join(tenant_names),
        tenant_names=tenant_display_names,
        occupants=occupants,
        max_occupants=max_occupants,
        notices=notices,
        emergency_contact=emergency_contact,
        addenda=data.get("addenda") or [],
        attachments=attachment_filenames,
        flood_disclosure=data.get("flood_disclosure"),
        lease={
            "id": data.get("lease_id"),
            "date": data["date"],
        },
        premises=premises,
        term=term,
        rent=data.get("rent"),
        rent_amount=format_money(monthly_rent),
        rent_schedule={
            "first": first_period,
            "last": last_period,
            "regular": regular_periods,
            "periods": periods,
        },
        deposit=data.get("deposit"),
        utilities=data.get("utilities"),
        pets=data.get("pets"),
        late_fees=data.get("late_fees"),
        renters_insurance=data.get("renters_insurance"),
        parking=data.get("parking"),
        repairs=data.get("repairs"),
        entry=data.get("entry"),
        abandonment=data.get("abandonment"),
        subletting=data.get("subletting"),
        occupancy=data.get("occupancy"),
        default=data.get("default"),
        governing_law=data.get("governing_law"),
        whole=data.get("whole_agreement"),
    )
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        tex_file = tmp / "lease.tex"
        tex_file.write_text(tex, encoding="utf-8")
        for key, source in resolved_attachments.items():
            destination = tmp / attachment_filenames[key]
            if isinstance(source, bytes):
                destination.write_bytes(source)
            else:
                shutil.copyfile(source, destination)

        subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", tex_file.name],
            cwd=tmp,
            check=True,
        )

        log_file = tmp / "lease.log"
        try:
            build_log = "".join(log_file.read_text(encoding="utf-8").split())
        except OSError as exc:
            raise ValueError("pdflatex did not produce a build log") from exc
        missing_attachments = [
            filename
            for filename in attachment_filenames.values()
            if filename not in build_log
        ]
        if missing_attachments:
            raise ValueError(
                "generated lease did not include PDF attachments: "
                + ", ".join(missing_attachments)
            )

        generated_pdf = tmp / "lease.pdf"
        generated_page_count = pdf_page_count(generated_pdf, "generated lease")
        attachment_page_count = sum(
            pdf_page_count(
                io.BytesIO(source) if isinstance(source, bytes) else source,
                f"attachments.{key}",
            )
            for key, source in resolved_attachments.items()
        )
        if generated_page_count < attachment_page_count:
            raise ValueError("generated lease does not contain all PDF attachments")

        output_pdf.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(generated_pdf, output_pdf)

    print(f"Generated {output_pdf}")


if __name__ == "__main__":
    main()
