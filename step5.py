import pandas as pd
import re
import os
from datetime import datetime

# ─── 1) Core TeXifier: catches a/b, sqrt(...), 45°, pi, ^, _ ────────────────
def texify_inline(s: str) -> str:
    s = re.sub(
        r"(?<!\\)\b([A-Za-z0-9\)\]\}]+)\s*/\s*([A-Za-z0-9\(\[\{]+)\b",
        r"\\frac{\1}{\2}", s
    )
    s = re.sub(r"sqrt\(\s*([^)]+?)\s*\)", r"\\sqrt{\1}", s)
    s = re.sub(r"(\d+)\s*°", r"\1^\\circ", s)
    s = re.sub(r"\bpi\b", r"\\pi", s, flags=re.IGNORECASE)
    s = re.sub(r"(?<!\^)\^([A-Za-z0-9\(\[]+)(?!\})", r"^{\1}", s)
    s = re.sub(r"\^\{\{([^}]+)\}\}", r"^{\1}", s)
    s = re.sub(r"(?<!_)_([A-Za-z0-9\(\[]+)(?!\})", r"_{\1}", s)
    s = re.sub(r"_\{\{([^}]+)\}\}", r"_{\1}", s)
    return s

# regex for any LaTeX snippet we just produced
MATH_SNIPPET = re.compile(
    r"(\\frac\{[^}]+\}\{[^}]+\}"
    r"|\\sqrt\{[^}]+\}"
    r"|\^\{[^}]+\}"
    r"|_\{[^}]+\}"
    r"|\\pi)"
)

def wrap_math_in_text(s: str) -> str:
    t = texify_inline(s)
    return MATH_SNIPPET.sub(lambda m: f"${m.group(0)}$", t)

# ─── 2) Roman numerals for headings ──────────────────────────────────────
ROMAN = ["I","II","III","IV","V","VI","VII","VIII","IX","X",
         "XI","XII","XIII","XIV","XV","XVI","XVII","XVIII","XIX","XX"]
def to_roman(n: int) -> str:
    return ROMAN[n-1] if 1 <= n <= len(ROMAN) else str(n)

# ─── 3) Exporter: final Excel → questions.md ────────────────────────────
def process_step5(input_xlsx: str) -> str:
    """
    Reads the final Excel from Step 4, then writes out a Markdown file
    grouping by difficulty and formatting:
      ## Question N
      (question text)
      ### Correct Answer
      (answer)
      #### Solution
      (detailed explanation)
    Returns the path to the generated .md.
    """
    df = pd.read_excel(input_xlsx, engine="openpyxl")
    df.columns = df.columns.str.strip()

    lines = []
    section = 0
    prev_qno = None

    for _, row in df.iterrows():
        raw = str(row.get("Question No", "")).strip()
        try:
            qno = int(raw)
        except:
            qno = None

        # new level when Q resets to 1 (or first row)
        if prev_qno is None or qno == 1:
            section += 1
            lines.append(f"# Level of Difficulty {to_roman(section)}")
            lines.append("")

        prev_qno = qno

        # Question
        lines.append(f"## Question {raw}")
        lines.append("")
        lines.append(wrap_math_in_text(str(row.get("Question", "")).strip()))
        lines.append("")

        # Correct Answer
        answer = str(row.get("Correct Answer", "")).strip()
        lines.append("### Correct Answer")
        lines.append(wrap_math_in_text(answer))
        lines.append("")

        # Solution / Explanation
        expl = str(row.get("Detailed Explanation", "")).strip()
        if expl and expl.lower() not in ("nan", "none"):
            lines.append("#### Solution")
            lines.append("")
            for ln in expl.splitlines():
                ln = ln.strip()
                if ln:
                    lines.append(wrap_math_in_text(ln))
                    lines.append("")

        lines.append("---")
        lines.append("")

    # write out
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_md = os.path.join(os.path.dirname(input_xlsx), f"questions_{ts}.md")
    with open(out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return out_md


# Optional standalone execution
if __name__ == "__main__":
    md_out = process_step5("final.xlsx")
    print(f"→ {md_out} generated.")
