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


def md_to_latex(s):
    return pypandoc.convert_text(s, to='latex', format='md').strip()


def main():
    if len(sys.argv) != 4:
        print("Usage: contract.py template.tex.j2 contract.yaml output.pdf")
        sys.exit(1)

    template_path = Path(sys.argv[1])
    data = yaml.safe_load(Path(sys.argv[2]).read_text())
    output_pdf = Path(sys.argv[3])

    if data.get("scope_of_work"):
        data["scope_of_work"] = md_to_latex(data["scope_of_work"])

    timeline = data.get("timeline") or {}
    for m in timeline.get("milestones", []):
        if m.get("description"):
            m["description"] = md_to_latex(m["description"])

    for key in ("intellectual_property", "confidentiality", "limitation_of_liability"):
        if isinstance(data.get(key), str):
            data[key] = md_to_latex(data[key])

    term = data.get("termination")
    if isinstance(term, str):
        data["termination"] = {"clause": md_to_latex(term)}
    elif isinstance(term, dict) and term.get("clause"):
        term["clause"] = md_to_latex(term["clause"])

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
        company=data.get("company") or {},
        client=data.get("client"),
        contractor=data.get("contractor"),
        agreement={
            "id": data.get("agreement_id"),
            "date": data.get("date") or date.today().isoformat(),
        },
        scope=data.get("scope_of_work"),
        timeline=timeline,
        payment=data.get("payment"),
        independent=data.get("independent_status"),
        ip=data.get("intellectual_property"),
        confidentiality=data.get("confidentiality"),
        limitation_of_liability=data.get("limitation_of_liability"),
        termination=data.get("termination"),
    )

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        tex_file = tmp / "contract.tex"
        tex_file.write_text(tex)

        subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", tex_file.name],
            cwd=tmp,
            check=True,
        )

        shutil.move(tmp / "contract.pdf", output_pdf)

    print(f"Generated {output_pdf}")


if __name__ == "__main__":
    main()