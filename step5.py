# step5.py

import pandas as pd
import re
import os
from datetime import datetime

# ─── Inline TeXifier ────────────────────────────────────────────────────────
def texify_inline(s: str) -> str:
    s = re.sub(
        r"(?<!\\)\b([A-Za-z0-9\)\]\}]+)\s*/\s*([A-Za-z0-9\(\[\{]+)\b",
        r"\\frac{\1}{\2}", s
    )
    s = re.sub(r"sqrt\(\s*([^)]+?)\s*\)", r"\\sqrt{\1}", s)
    s = re.sub(r"(\d+)\s*°", r"\1^\\circ", s)
    s = re.sub(r"\bpi\b", r"\\pi", s, flags=re.IGNORECASE)
    s = re.sub(r"(?<!\^)\^([A-Za-z0-9\(\[]+)(?!\})", r"^{\1}", s)
    s = re.sub(r"(?<!_)_([A-Za-z0-9\(\[]+)(?!\})", r"_{\1}", s)
    s = re.sub(r"\^\{\{([^}]+)\}\}", r"^{\1}", s)
    s = re.sub(r"_\{\{([^}]+)\}\}", r"_{\1}", s)
    return s.replace('${$', '{').replace('$}', '}')

MATH_SNIPPET = re.compile(
    r"(\\frac\{[^}]+\}\{[^}]+\}|\\sqrt\{[^}]+\}|\^\{[^}]+\}|_\{[^}]+\}|\\pi)"
)

def wrap_math_in_text(s: str) -> str:
    t = texify_inline(s)
    return MATH_SNIPPET.sub(lambda m: f"${m.group(0)}$", t)

# ─── Roman Helper ──────────────────────────────────────────────────────────
ROMAN = ["I","II","III","IV","V","VI","VII","VIII","IX","X"]
def to_roman(n: int) -> str:
    return ROMAN[n-1] if 1 <= n <= len(ROMAN) else str(n)

# ─── Exporter Function ─────────────────────────────────────────────────────
def process_step5(input_xlsx: str) -> str:
    """
    Reads the final Excel from Step 4, groups questions into difficulty levels,
    marks up all math in $...$, and writes out a Markdown file.
    Returns the path to the generated .md.
    """
    df = pd.read_excel(input_xlsx, engine="openpyxl")
    df.columns = df.columns.str.strip()

    section = 0
    prev_q = None

    # build lines
    lines = []
    for _, row in df.iterrows():
        raw_qno = row.get("Question No", "")
        try:
            qno = int(raw_qno)
        except:
            qno = None

        # new difficulty section when Q-numbers reset
        if prev_q is None or (isinstance(qno,int) and isinstance(prev_q,int) and qno <= prev_q):
            section += 1
            lines.append(f"# Level of Difficulty {to_roman(section)}")
            lines.append("")

        prev_q = qno

        # Question header & text
        lines.append(f"## Question {raw_qno}")
        lines.append("")
        lines.append(wrap_math_in_text(str(row.get("Question",""))))
        lines.append("")

        # Options
        opts = str(row.get("Options","")).strip()
        if opts.lower() not in ("nan","none",""):
            for opt in re.split(r";\s*|\r?\n", opts):
                o = opt.strip()
                if not o:
                    continue
                if o[0] not in "-*":
                    o = f"- {o}"
                lines.append(wrap_math_in_text(o))
            lines.append("")

        # Answer
        ans = str(row.get("Correct Answer","")).strip()
        lines.append(f"**Answer:** {wrap_math_in_text(ans)}")
        lines.append("")

        # Detailed Explanation
        expl = str(row.get("Detailed Explanation","")).strip()
        if expl.lower() not in ("nan",""):
            lines.append("**Explanation:**")
            lines.append("")
            for l in expl.splitlines():
                if l.strip():
                    lines.append(wrap_math_in_text(l))
            lines.append("")

        lines.append("---")
        lines.append("")

    # write to file
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_md = os.path.join(os.path.dirname(input_xlsx), f"questions_{ts}.md")
    with open(out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return out_md
