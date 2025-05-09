# step5.py

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

# regex to detect any LaTeX snippet we produced
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

# ─── 2) Roman numerals for Level headings ─────────────────────────────────
ROMAN = ["I","II","III","IV","V","VI","VII","VIII","IX","X",
         "XI","XII","XIII","XIV","XV","XVI","XVII","XVIII","XIX","XX"]
def to_roman(n: int) -> str:
    return ROMAN[n-1] if 1 <= n <= len(ROMAN) else str(n)

# ─── 3) Exporter: final Excel → questions.md ─────────────────────────────
def process_step5(input_xlsx: str) -> str:
    """
    Reads the final Excel (Step 4 output) and emits a Markdown file grouping:
      # Level of Difficulty I, II, …
      ## Question N
      (question text)
      - option A
      ...
      ### Correct Answer
      (Answer column)
      #### Solution
      (Detailed Explanation)
    Returns the generated .md filepath.
    """
    df = pd.read_excel(input_xlsx, engine="openpyxl")
    df.columns = df.columns.str.strip()

    lines = []
    section = 0
    prev_q = None

    for _, row in df.iterrows():
        raw_q = str(row.get("Question No", "")).strip()
        try:
            qno = int(raw_q)
        except:
            qno = None

        # New level when question resets to 1 (or first row)
        if prev_q is None or qno == 1:
            section += 1
            lines.append(f"# Level of Difficulty {to_roman(section)}")
            lines.append("")
        prev_q = qno

        # Question
        lines.append(f"## Question {raw_q}")
        lines.append("")
        qtxt = str(row.get("Question", "")).strip()
        lines.append(wrap_math_in_text(qtxt))
        lines.append("")

        # Options (if any)
        opts = row.get("Options", "")
        if pd.notna(opts) and str(opts).strip():
            for opt in re.split(r";\s*|\r?\n", str(opts)):
                o = opt.strip()
                if not o:
                    continue
                # strip bullets or numbering
                o = re.sub(r"^[\-\*\d\.\)]\s*", "", o)
                lines.append(f"- {wrap_math_in_text(o)}")
            lines.append("")

        # Correct Answer
        ans = str(row.get("Answer", "")).strip()
        lines.append("### Correct Answer")
        lines.append(wrap_math_in_text(ans))
        lines.append("")

        # Solution / Detailed Explanation
        sol = str(row.get("Detailed Explanation", "")).strip()
        if sol and sol.lower() not in ("nan", "none"):
            lines.append("#### Solution")
            lines.append("")
            for ln in sol.splitlines():
                ln = ln.strip()
                if ln:
                    lines.append(wrap_math_in_text(ln))
                    lines.append("")

        # Separator
        lines.append("---")
        lines.append("")

    # Write out
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_md = os.path.join(os.path.dirname(input_xlsx), f"questions_{ts}.md")
    with open(out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return out_md

# Optional: allow running this script standalone
if __name__ == "__main__":
    md = process_step5("final.xlsx")
    print(f"→ {md} generated.")
