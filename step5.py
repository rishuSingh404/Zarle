import pandas as pd
import re
import os
from datetime import datetime

# ─── 1) Core TeXifier: catches a/b, sqrt(...), 45°, pi, ^, _ ────────────────
def texify_inline(s: str) -> str:
    # fractions: a/b → \frac{a}{b}
    s = re.sub(
        r"(?<!\\)\b([A-Za-z0-9\)\]\}]+)\s*/\s*([A-Za-z0-9\(\[\{]+)\b",
        r"\\frac{\1}{\2}", s
    )
    # sqrt(x) → \sqrt{x}
    s = re.sub(r"sqrt\(\s*([^)]+?)\s*\)", r"\\sqrt{\1}", s)
    # degrees: 45° → 45^\circ
    s = re.sub(r"(\d+)\s*°", r"\1^\\circ", s)
    # pi → \pi
    s = re.sub(r"\bpi\b", r"\\pi", s, flags=re.IGNORECASE)
    # superscripts: x^2 → x^{2}
    s = re.sub(r"(?<!\^)\^([A-Za-z0-9\(\[]+)(?!\})", r"^{\1}", s)
    # collapse accidental double‐braces
    s = re.sub(r"\^\{\{([^}]+)\}\}", r"^{\1}", s)
    # subscripts: a_1 → a_{1}
    s = re.sub(r"(?<!_)_([A-Za-z0-9\(\[]+)(?!\})", r"_{\1}", s)
    s = re.sub(r"_\{\{([^}]+)\}\}", r"_{\1}", s)
    return s

# regex to detect any LaTeX fragment we just produced
MATH_SNIPPET = re.compile(
    r"(\\frac\{[^}]+\}\{[^}]+\}"
    r"|\\sqrt\{[^}]+\}"
    r"|\^\{[^}]+\}"
    r"|_\{[^}]+\}"
    r"|\\pi)"
)

def wrap_math_in_text(s: str) -> str:
    t = texify_inline(s)
    # wrap each math snippet in $…$
    return MATH_SNIPPET.sub(lambda m: f"${m.group(0)}$", t)

# ─── 2) Excel → Markdown exporter ────────────────────────────────────────
def process_step5(input_xlsx: str) -> str:
    """
    Reads the final Excel from Step 4 and writes out questions.md
    with sections: Question, Correct Answer, Solution.
    Returns the path to the generated .md file.
    """
    df = pd.read_excel(input_xlsx, engine="openpyxl")
    df.columns = df.columns.str.strip()

    lines = []
    for _, row in df.iterrows():
        qno  = str(row.get("Question No", "")).strip()
        qtxt = str(row.get("Question", "")).strip()
        ans  = str(row.get("Correct Answer", "")).strip()
        expl = str(row.get("Detailed Explanation", "")).strip()

        # Question
        lines.append(f"## Question {qno}")
        lines.append("")
        lines.append(wrap_math_in_text(qtxt))
        lines.append("")

        # Correct Answer
        lines.append("### Correct Answer")
        lines.append(wrap_math_in_text(ans))
        lines.append("")

        # Solution / Explanation
        if expl.lower() not in ("","nan","none"):
            lines.append("#### Solution")
            lines.append("")
            for ln in expl.splitlines():
                ln = ln.strip()
                if ln:
                    lines.append(wrap_math_in_text(ln))
                    lines.append("")
        # separator
        lines.append("---")
        lines.append("")

    # write out
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_md = os.path.join(os.path.dirname(input_xlsx), f"questions_{ts}.md")
    with open(out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return out_md


# If you ever want to run this as a script:
if __name__ == "__main__":
    path_to_excel = "final.xlsx"  # adjust if needed
    print("Generating Markdown…")
    md_path = process_step5(path_to_excel)
    print(f"→ {md_path} written.")
