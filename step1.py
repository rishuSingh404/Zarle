import os
import re
import pandas as pd
from datetime import datetime


def clean_latex(text: str) -> str:
    """
    Cleans up LaTeX/Markdown syntax for readability.
    """
    # Convert any \frac{x}{y} into x/(y)
    text = re.sub(r'\\frac\s*\{([^}]*)\}\s*\{([^}]*)\}', r'\1/(\2)', text)
    # Remove all $ signs
    text = text.replace('$', '')
    # Convert ^{\text{th}} to th
    text = re.sub(r'\^\{\\text\s*\{th\}\}', 'th', text)
    # Remove leftover commands
    text = re.sub(r'\\[a-zA-Z]+\{[^}]*\}', '', text)
    text = re.sub(r'\\[a-zA-Z]+', '', text)
    # Collapse whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def parse_markdown_questions(md_path: str):
    """
    Parse questions and options from a .md file into a list of dicts.
    """
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    blocks = re.split(r'\n(?=\d+\.\s)', content)
    questions = []
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        m = re.match(r'^(\d+)\.\s*(.*?)(?=\n\s*\(a\)|$)', block, flags=re.DOTALL)
        if not m:
            continue
        q_no, q_text = m.group(1), m.group(2).strip()
        q_text = clean_latex(q_text)
        opts = re.findall(r'^\(\s*([a-zA-Z])\s*\)\s*(.*?)(?=\n\(\s*[a-zA-Z]\)|$)', block, flags=re.MULTILINE|re.DOTALL)
        options = []
        for letter, opt in opts:
            options.append(f"({letter.lower()}) {clean_latex(opt.strip())}")
        q_type = 'MCQ' if options else 'Short Answer'
        questions.append({
            'Question No': int(q_no),
            'Question': q_text,
            'Type': q_type,
            'Options': '; '.join(options),
            'Answer': '',
            'Explanation': ''
        })
    return questions


def convert_md_to_excel(md_path: str, output_path: str = None) -> str:
    """
    Converts markdown to Excel. Returns the path of the generated .xlsx.
    """
    questions = parse_markdown_questions(md_path)
    df = pd.DataFrame(questions)
    df.insert(0, 'Serial Number', range(1, len(df)+1))
    df = df[['Serial Number','Question No','Question','Type','Options','Answer','Explanation']]

    if not output_path:
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        base = os.path.dirname(md_path)
        output_path = os.path.join(base, f"1_{ts}.xlsx")
    df.to_excel(output_path, index=False)
    return output_path