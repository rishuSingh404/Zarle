import streamlit as st
import pandas as pd
import tempfile
import os
from datetime import datetime
import openai

from step1 import convert_md_to_excel
from step2 import process_step2
from step3 import process_step3, build_prompt, parse_response_and_flag
from step4 import process_step4

openai.api_key = st.secrets["OPENAI_API_KEY"]

# Streamlit app configuration with dark mode vibe
st.set_page_config(
    page_title="🧠 Markdown to Excel Automator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark futuristic theme
st.markdown("""
    <style>
        body, .stApp { background-color: #1e1e2f !important; color: #f0f0f0 !important; }
        .stButton>button { background-color: #00bcd4; color: white; font-weight: bold; border-radius: 0.5rem; }
        .stFileUploader { background: #2a2a40 !important; border-radius: 10px; }
        .stTabs [data-baseweb="tab"] { background-color: #252638 !important; border-radius: 10px 10px 0 0; color: #ffffff; }
        .stTabs [aria-selected="true"] { background-color: #00bcd4 !important; color: #000000; font-weight: bold; }
        .stDownloadButton button { background: #673ab7; color: white; }
    </style>
""", unsafe_allow_html=True)

# Sidebar branding and navigation
st.sidebar.image("logo.png", width=150)
st.sidebar.markdown("""
### 🚀 Zarle AI Automator
Fastest way to convert 900-page books into AI-verified Excel quizzes.
""")

# Tabbed navigation
tab1, tab2, tab3, tab4 = st.tabs(["🧾 Step 1", "🔀 Step 2", "🤖 Step 3", "🧼 Step 4"])

def _save_temp(uploaded, suffix):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(uploaded.getvalue())
    tmp.close()
    return tmp.name

# STEP 1: Markdown to Excel
with tab1:
    st.markdown("## 🧾 Step 1: Markdown → Excel")
    md = st.file_uploader("Upload Markdown file", type="md")
    if st.button("🚀 Convert"):
        if not md:
            st.warning("Please upload a .md file.")
        else:
            path = _save_temp(md, ".md")
            out = convert_md_to_excel(path)
            st.success("Conversion complete.")
            df = pd.read_excel(out)
            st.dataframe(df, use_container_width=True)
            with open(out, "rb") as f:
                st.download_button("⬇️ Download 1.xlsx", f, file_name=os.path.basename(out))

# STEP 2: Merge Answer + Solution
with tab2:
    st.markdown("## 🔀 Step 2: Merge Answer Key & Solutions")
    c1, c2 = st.columns(2)
    md1 = c1.file_uploader("Upload Answer Key (.md)", type="md")
    md2 = c2.file_uploader("Upload Solutions (.md)", type="md")
    x1 = st.file_uploader("Upload 1.xlsx file", type="xlsx")
    if st.button("🔄 Merge"):
        if not (md1 and md2 and x1):
            st.warning("Please upload 2 .md files and 1.xlsx")
        else:
            p1 = _save_temp(md1, ".md")
            p2 = _save_temp(md2, ".md")
            p3 = _save_temp(x1, ".xlsx")
            out = process_step2(p1, p2, p3)
            df = pd.read_excel(out)
            st.success("✅ Merged Answer + Solutions")
            st.dataframe(df, use_container_width=True)
            with open(out, "rb") as f:
                st.download_button("⬇️ Download 2.xlsx", f, file_name=os.path.basename(out))

# STEP 3: OpenAI Explanations
with tab3:
    st.markdown("## 🤖 Step 3: Generate AI Explanations")
    x2 = st.file_uploader("Upload 2.xlsx", type="xlsx")
    if st.button("💡 Generate Explanations"):
        if not x2:
            st.warning("Please upload 2.xlsx")
        else:
            path = _save_temp(x2, ".xlsx")
            df = pd.read_excel(path)
            progress = st.progress(0)
            status = st.empty()
            for i, row in df.iterrows():
                sys, usr = build_prompt(
                    row['Serial Number'], row['Question No'], row['Question'],
                    row['Type'], row['Options'], row['Answer'], row['Explanation']
                )
                try:
                    res = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "system", "content": sys}, {"role": "user", "content": usr}],
                        temperature=0.2,
                        max_tokens=1200
                    )
                    raw = res.choices[0].message.content
                except Exception as e:
                    raw = f"Error: {e}\nFlag: Yes"
                expl, flag = parse_response_and_flag(raw)
                df.at[i, 'Detailed Explanation'] = expl
                df.at[i, 'Flag'] = flag
                progress.progress((i+1)/len(df))
                status.info(f"Processing {i+1}/{len(df)}")

            ts = datetime.now().strftime('%Y%m%d_%H%M%S')
            out = os.path.join(os.path.dirname(path), f"3_{ts}.xlsx")
            df.to_excel(out, index=False)
            st.success("🤖 AI Processing Complete!")
            st.dataframe(df, use_container_width=True)
            with open(out, "rb") as f:
                st.download_button("⬇️ Download 3.xlsx", f, file_name=os.path.basename(out))

# STEP 4: Final Cleanup
with tab4:
    st.markdown("## 🧼 Step 4: Final Cleanup")
    x3 = st.file_uploader("Upload 3.xlsx", type="xlsx")
    if st.button("🧹 Finalize"):
        if not x3:
            st.warning("Please upload 3.xlsx")
        else:
            path = _save_temp(x3, ".xlsx")
            out = process_step4(path)
            df = pd.read_excel(out)
            st.success("🎉 Final file ready!")
            st.dataframe(df, use_container_width=True)
            with open(out, "rb") as f:
                st.download_button("⬇️ Download Final Excel", f, file_name=os.path.basename(out))