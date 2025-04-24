# step5.py
import pandas as pd
import re
import os
from datetime import datetime

def to_roman(num: int) -> str:
    romans = ["I","II","III","IV","V","VI","VII","VIII","IX","X"]
    return romans[num-1] if 1 <= num <= len(romans) else str(num)

def process_step5(input_xlsx: str) -> str:
    """
    Reads the final Excel, groups questions into difficulty sections,
    and writes out a questions.md file. Returns the path to questions.md.
    """
    df = pd.read_excel(input_xlsx, engine="openpyxl")
    df.columns = df.columns.str.strip()

    lines = []
    section = 0
    prev_qno = None

    for _, row in df.iterrows():
        # parse question number
        try:
            qno = int(row.get("Question No", 0))
        except:
            qno = row.get("Question No", "")

        # new section if it's the first row or Q resets
        if prev_qno is None or (isinstance(qno, int) and isinstance(prev_qno, int) and qno <= prev_qno):
            section += 1
            roman = to_roman(section)
            lines.append(f"# Level of Difficulty {roman}")
            lines.append("")  # blank line

        prev_qno = qno

        # grab fields
        qtxt     = str(row.get("Question", "")).strip()
        opts     = row.get("Options", "")
        ans_raw  = row.get("Correct Answer", "")
        expl     = str(row.get("Detailed Explanation", "")).strip()

        # format answer
        if pd.notna(ans_raw):
            if isinstance(ans_raw, float) and ans_raw.is_integer():
                ans = str(int(ans_raw))
            else:
                ans = str(ans_raw).strip()
        else:
            ans = ""

        # build markdown
        lines.append(f"## Question {qno}")
        lines.append("")
        lines.append(qtxt)
        lines.append("")

        if pd.notna(opts) and str(opts).strip():
            parts = re.split(r';\s*|\r?\n', str(opts))
            for part in parts:
                part = part.strip()
                if part:
                    if not part.startswith("-"):
                        part = f"- {part}"
                    lines.append(part)
            lines.append("")

        lines.append(f"**Answer:** {ans}")
        lines.append("")
        if expl:
            lines.append("**Explanation:**")
            lines.append("")
            for ex_line in expl.splitlines():
                lines.append(ex_line.strip())
            lines.append("")

        lines.append("---")
        lines.append("")

    # write out
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_md = os.path.join(os.path.dirname(input_xlsx), f"questions_{ts}.md")
    with open(out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return out_md
