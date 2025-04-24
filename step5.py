import pandas as pd
import re

# helper to get Roman numerals I, II, III, IV…
def to_roman(num):
    romans = ["I","II","III","IV","V","VI","VII","VIII","IX","X"]
    return romans[num-1] if 1 <= num <= len(romans) else str(num)

df = pd.read_excel(r"C:\Users\Rishu Singh\Favorites\Downloads\final_20250424_082407.xlsx", engine="openpyxl")
df.columns = df.columns.str.strip()
# preserve original sheet order—not sorting by Question No here!
lines = []

section = 0
prev_qno = None

for _, row in df.iterrows():
    # parse question number
    try:
        qno = int(row.get("Question No", 0))
    except:
        qno = row.get("Question No", "")
    # new section if it's the very first row, or qno "resets" (<= previous)
    if prev_qno is None or (isinstance(qno, int) and isinstance(prev_qno, int) and qno <= prev_qno):
        section += 1
        roman = to_roman(section)
        lines.append(f"# Level of Difficulty {roman}")
        lines.append("")  # blank line

    prev_qno = qno

    # grab all fields
    qtxt  = str(row.get("Question", "")).strip()
    opts  = row.get("Options", "")
    ans_raw = row.get("Correct Answer", "")
    expl  = str(row.get("Detailed Explanation", "")).strip()

    # format answer
    if pd.notna(ans_raw):
        if isinstance(ans_raw, float) and ans_raw.is_integer():
            ans = str(int(ans_raw))
        else:
            ans = str(ans_raw).strip()
    else:
        ans = ""

    # question header
    lines.append(f"## Question {qno}")
    lines.append("")
    lines.append(qtxt)
    lines.append("")

    # options block (if present)
    if pd.notna(opts) and str(opts).strip():
        parts = re.split(r';\s*|\r?\n', str(opts))
        for part in parts:
            part = part.strip()
            if not part:
                continue
            if not part.startswith("-"):
                part = f"- {part}"
            lines.append(part)
        lines.append("")

    # answer + explanation
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
with open("./questions.md", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("✅ questions.md written with Level headings!")

