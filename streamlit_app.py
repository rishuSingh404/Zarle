import streamlit as st
import pandas as pd
import tempfile
import os
from datetime import datetime

# Step function imports
from step1 import convert_md_to_excel
from step2 import process_step2
from step3 import process_step3
from step4 import process_step4

# Set API key from secrets
import openai
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Modern theme configuration
st.set_page_config(
    page_title="⚙️ Quiz Pipeline Automator",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styling injection for cleaner look
st.markdown("""
    <style>
        .stApp { background-color: #f7f9fc; }
        .stButton > button { margin-top: 10px; }
        .step-box { padding: 1.5rem; background: #ffffff; border-radius: 12px; box-shadow: 0 4px 8px rgba(0,0,0,0.04); }
    </style>
""", unsafe_allow_html=True)

# Sidebar branding
st.sidebar.image("logo.png", width=160)
st.sidebar.title("🧭 Navigation")

# Step tabs
tab1, tab2, tab3, tab4 = st.tabs(["📄 Step 1", "🔀 Step 2", "🤖 Step 3", "🧹 Step 4"])

# Utility for file saving
def _save_temp(uploaded, suffix):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(uploaded.getvalue())
    tmp.close()
    return tmp.name

# STEP 1
with tab1:
    st.markdown("### 📄 Step 1: Convert Markdown to Excel")
    with st.container():
        md = st.file_uploader("Upload a Markdown (.md) file", type="md")
        if st.button("🚀 Run Step 1"):
            if not md:
                st.warning("⚠️ Please upload a Markdown file.")
            else:
                path = _save_temp(md, ".md")
                out = convert_md_to_excel(path)
                st.success("✅ Conversion complete!")
                df = pd.read_excel(out)
                st.dataframe(df, use_container_width=True)
                with open(out, "rb") as f:
                    st.download_button("⬇️ Download 1.xlsx", f, os.path.basename(out))

# STEP 2
with tab2:
    st.markdown("### 🔀 Step 2: Merge Answer Key and Solutions")
    col1, col2 = st.columns(2)
    md1 = col1.file_uploader("Answer-key (.md)", type="md")
    md2 = col2.file_uploader("Solutions (.md)", type="md")
    x1 = st.file_uploader("Upload 1.xlsx", type="xlsx")
    if st.button("🔄 Run Step 2"):
        if not (md1 and md2 and x1):
            st.warning("⚠️ Please upload both .md files and 1.xlsx")
        else:
            p1 = _save_temp(md1, ".md")
            p2 = _save_temp(md2, ".md")
            p3 = _save_temp(x1, ".xlsx")
            out = process_step2(p1, p2, p3)
            df = pd.read_excel(out)
            st.success("✅ Merged successfully")
            st.dataframe(df, use_container_width=True)
            with open(out, "rb") as f:
                st.download_button("⬇️ Download 2.xlsx", f, os.path.basename(out))

# STEP 3
with tab3:
    st.markdown("### 🤖 Step 3: Generate AI Explanations")
    x2 = st.file_uploader("Upload 2.xlsx", type="xlsx")
    if st.button("🤖 Run Step 3"):
        if not x2:
            st.warning("Please upload 2.xlsx")
        else:
            path = _save_temp(x2, ".xlsx")
            df = pd.read_excel(path)
            progress = st.progress(0)
            status = st.empty()
            if 'Detailed Explanation' not in df.columns:
                df['Detailed Explanation'] = ''
            if 'Flag' not in df.columns:
                df['Flag'] = ''

            from step3 import build_prompt, parse_response_and_flag
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
                progress.progress((i+1) / len(df))
                status.info(f"Processed {i+1} of {len(df)} questions")

            ts = datetime.now().strftime('%Y%m%d_%H%M%S')
            out = os.path.join(os.path.dirname(path), f"3_{ts}.xlsx")
            df.to_excel(out, index=False)
            st.success("✅ Step 3 completed!")
            st.dataframe(df)
            with open(out, "rb") as f:
                st.download_button("⬇️ Download 3.xlsx", f, os.path.basename(out))

# STEP 4
with tab4:
    st.markdown("### 🧹 Step 4: Final Cleanup")
    x3 = st.file_uploader("Upload 3.xlsx", type="xlsx")
    if st.button("🧼 Run Step 4"):
        if not x3:
            st.warning("Please upload 3.xlsx")
        else:
            path = _save_temp(x3, ".xlsx")
            out = process_step4(path)
            df = pd.read_excel(out)
            st.success("🎉 Final version ready!")
            st.dataframe(df)
            with open(out, "rb") as f:
                st.download_button("⬇️ Download Final Excel", f, os.path.basename(out))