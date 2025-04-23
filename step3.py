import os
import time
import pandas as pd
import openai
from tqdm import tqdm
from datetime import datetime


def build_prompt(sn, qn, qt, qtype, opts, ans, expl):
    system = (
        "You are an expert teacher. Provide step-by-step solutions. "
        "At end, write exactly 'Flag: Yes' or 'Flag: No'."
    )
    header = (
        f"Serial Number: {sn}\n"
        f"Question No: {qn}\n"
        f"Type: {qtype}\n\n"
        f"Question:\n{qt}\n\n"
        f"Options:\n{opts}\n\n"
        f"Provided Answer: {ans}\n\n"
    )
    if pd.notna(expl) and str(expl).strip():
        header += f"Provided Short Explanation:\n{expl}\n\n"
    return system, header + "Now provide detailed explanation..."


def parse_response_and_flag(resp: str):
    lines = resp.splitlines()
    flag = 'No'
    for line in reversed(lines):
        if line.startswith('Flag:'):
            flag = line.split(':',1)[1].strip()
            break
    expl = resp.rsplit('Flag:',1)[0].strip()
    return expl, flag


def process_step3(input_xlsx: str, output_path: str = None, openai_key: str = None) -> str:
    """
    Reads input_xlsx, calls OpenAI to generate Detailed Explanation & Flag, writes new Excel.
    """
    if openai_key:
        openai.api_key = openai_key

    df = pd.read_excel(input_xlsx)
    if 'Detailed Explanation' not in df.columns:
        df['Detailed Explanation'] = ''
    if 'Flag' not in df.columns:
        df['Flag'] = ''

    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Step 3"):  
        sys, usr = build_prompt(
            row['Serial Number'], row['Question No'], row['Question'],
            row['Type'], row['Options'], row['Answer'], row['Explanation']
        )
        try:
            res = openai.ChatCompletion.create(
                model='gpt-3.5-turbo',
                messages=[{'role':'system','content':sys},{'role':'user','content':usr}],
                temperature=0.2, max_tokens=1200
            )
            raw = res.choices[0].message.content
        except Exception as e:
            raw = f"Error: {e}\nFlag: Yes"

        expl, flag = parse_response_and_flag(raw)
        df.at[idx, 'Detailed Explanation'] = expl
        df.at[idx, 'Flag'] = flag
        time.sleep(1)

    if not output_path:
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        base = os.path.dirname(input_xlsx)
        output_path = os.path.join(base, f"3_{ts}.xlsx")
    df.to_excel(output_path, index=False)
    return output_path