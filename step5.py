import pandas as pd
import re
from openpyxl import load_workbook

# ─── 1) Core TeXifier: catches a/b, sqrt(...), 45°, pi, ^, _ ────────────────
def texify_inline(s: str) -> str:
    # fractions: numerator/denominator → \frac{num}{den}
    s = re.sub(
        r"(?<!\\)\b([A-Za-z0-9\)\]\}]+)\s*/\s*([A-Za-z0-9\(\[\{]+)\b",
        r"\\frac{\1}{\2}",
        s
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
    # wrap each match in $...$
    return MATH_SNIPPET.sub(lambda m: f"${m.group(0)}$", t)

# ─── 2) Excel → Markdown exporter ────────────────────────────────────────
def excel_to_markdown(xlsx: str, md: str):
    df = pd.read_excel(xlsx, engine="openpyxl")
    df.columns = df.columns.str.strip()

    with open(md, "w", encoding="utf-8") as out:
        for _, row in df.iterrows():
            qno   = str(row.get("Question No","")).strip()
            qtxt  = str(row.get("Question","")).strip()
            ans   = str(row.get("Correct Answer","")).strip()
            expl  = str(row.get("Detailed Explanation","")).strip()

            # ─── Step 1: Question heading ───────────────────────────
            out.write(f"## Question {qno}\n\n")
            out.write(wrap_math_in_text(qtxt) + "\n\n")

            # ─── Step 2: Correct Answer block ───────────────────────
            out.write("### Correct Answer\n")
            out.write(wrap_math_in_text(ans) + "\n\n")

            # ─── Step 5: Solution / Explanation block ───────────────  ← UPDATED
            if expl and expl.lower() not in ("nan","none",""):
                out.write("#### Solution\n\n")
                for line in expl.splitlines():
                    line = line.strip()
                    if line:
                        out.write(wrap_math_in_text(line) + "\n\n")

if __name__ == "__main__":
    excel_to_markdown(
        r"C:\Users\Rishu Singh\Favorites\Downloads\final_20250424_082407.xlsx",
        "questions.md"
    )
    print("→ questions.md generated in the new Q/A/Solution format.")
