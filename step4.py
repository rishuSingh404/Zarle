import os
import re
import pandas as pd
from datetime import datetime


def clean_latex(text: str) -> str:
    # fractions, inequalities, inline math cleanup
    text = re.sub(r'\\d?frac\{([^}]+)\}\{([^}]+)\}', r'\1/\2', text)
    ops = {r'\\times':'×',r'\\ldots':'...',r'\\pm':'±'}
    for pat, rep in ops.items():
        text = re.sub(pat, rep, text)
    text = re.sub(r'\$(.*?)\$', r'\1', text)
    text = re.sub(r'\\\((.*?)\\\)', r'\1', text)
    text = re.sub(r'\\begin\{.*?\}.*?\\end\{.*?\}', '', text, flags=re.S)
    text = text.replace('{','').replace('}','').replace('\\','')
    return text.strip()


def process_step4(input_xlsx: str, output_path: str = None) -> str:
    """
    Cleans LaTeX artifacts in Question, Explanation, and Detailed Explanation columns.
    """
    df = pd.read_excel(input_xlsx)

    columns_to_clean = ["Question", "Explanation", "Detailed Explanation"]
    for col in columns_to_clean:
        if col in df.columns:
            df[col] = df[col].astype(str).apply(clean_latex)

    if not output_path:
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        base = os.path.dirname(input_xlsx)
        output_path = os.path.join(base, f"final_{ts}.xlsx")

    df.to_excel(output_path, index=False)
    return output_path
