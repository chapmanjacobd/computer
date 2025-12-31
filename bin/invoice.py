#!/usr/bin/env python3
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

import pypandoc
import yaml
from jinja2 import Environment, FileSystemLoader


def latex_escape(s: str) -> str:
    return s.replace("&", r"\&").replace("%", r"\%").replace("_", r"\_").replace("#", r"\#").replace("$", r"\$")


def latex_or_url(s: str) -> str:
    if s.startswith("http"):
        return rf"\href{{{s}}}{{{s}}}"
    return latex_escape(s)


def main():
    if len(sys.argv) != 4:
        print("Usage: invoice.py template.tex.j2 invoice.yaml output.pdf")
        sys.exit(1)

    template_path = Path(sys.argv[1])
    data = yaml.safe_load(Path(sys.argv[2]).read_text())
    output_pdf = Path(sys.argv[3])

    for item in data["items"]:
        item["due"] = item["rate"] * (item.get("quantity") or 1) - (item.get("discount") or 0)
        item["service"] = pypandoc.convert_text(item["service"], to='latex', format='md').strip()

    total = sum(i["due"] for i in data["items"])
    received = data.get("payment_received", 0.0)

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

    tex = env.get_template(template_path.name).render(
        company=data["company"],
        bill_to=data["bill_to"],
        invoice={
            "id": data["invoice_id"],
            "date": date.today().isoformat(),
            "terms": data["payment_terms"],
        },
        items=data["items"],
        totals={
            "total": total,
            "received": received,
            "balance": total - received,
        },
        payments=data.get("payments") or [],
    )

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        tex_file = tmp / "invoice.tex"
        tex_file.write_text(tex)

        subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", tex_file.name],
            cwd=tmp,
            check=True,
        )

        shutil.move(tmp / "invoice.pdf", output_pdf)

    print(f"Generated {output_pdf}")


if __name__ == "__main__":
    main()
