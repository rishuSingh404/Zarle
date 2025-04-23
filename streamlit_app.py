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

# Load your API key from Streamlit secrets
openai.api_key = os.environ.get("OPENAI_API_KEY")

# ─── Page Config ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Zarle AI Automator",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Global CSS ─────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stButton > button {
        background-color: #9C27B0;
        color: white;
        font-weight: 600;
        border-radius: 8px;
        padding: 0.6em 1.2em;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #BA68C8;
        transform: scale(1.03);
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
        header { visibility: hidden; }
        .block-container {
            padding-top: 0rem;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown(
    """
    <style>
      /* Backgrounds & text */
      .stApp { background-color: #121212; color: #EEE; }
      /* Sidebar */
      [data-testid="stSidebar"] {
        background-color: #1F1F1F;
        padding-top: 1rem;
      }
      /* File uploader container */
      .stFileUploader > label {
        width: 100%; 
        padding: 1rem; 
        background-color: #212121; 
        border: 2px dashed #444; 
        border-radius: 8px;
        color: #CCC;
      }
      /* Option menu icons */
      .menu-icon {
        color: #00BFA6 !important;
      }
      /* Selected menu item */
      .nav-link-selected {
        background-color: #00BFA6 !important;
        color: #121212 !important;
      }
      /* Buttons */
      .stButton > button {
        background-color: #00BFA6;
        color: #121212;
        font-weight: bold;
        border-radius: 0.5rem;
      }
      .stDownloadButton > button {
        background-color: #673AB7;
        color: #FFF;
      }
    </style>
    """,
    unsafe_allow_html=True
)

# ─── Sidebar Navigation ─────────────────────────────────────────────────
from streamlit_option_menu import option_menu

st.markdown("""
    <style>
        /* Shift sidebar content upward */
        section[data-testid="stSidebar"] > div:first-child {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.sidebar.markdown(
    "<div style='text-align: center;'>"
    "<img src='https://raw.githubusercontent.com/rishuSingh404/Zarle/main/logo.png' width='150'/>"
    "</div>",
    unsafe_allow_html=True
)

    st.markdown(
        '''
        <div style="color: white;">
            <h3 style='margin-bottom: 0.2em;'>Zarle AI Automator</h3>
            <p style='margin-top: 0;'>Fast conversion of Markdown quizzes into AI-verified Excel workbooks.</p>
        </div>
        ''',
        unsafe_allow_html=True
    )
    selected = option_menu(
        menu_title=None,
        options=["Step 1", "Step 2", "Step 3", "Step 4"],
        icons=["file-earmark-text", "layers-half", "robot", "brush"],
        menu_icon="cast",
        default_index=0,
        orientation="vertical",
        styles={
        "container": {"padding": "0", "background-color": "#1F1F1F"},
        "icon": {"font-size": "20px", "color": "#9C27B0"},  # purple icon
        "nav-link": {"font-size": "16px", "color": "#ECECEC", "text-align": "left"},
        "nav-link-selected": {
            "background-color": "#9C27B0",  # purple highlight
            "color": "#FFFFFF",
            "font-weight": "bold"
        },
    }
)

# ─── Helpers ─────────────────────────────────────────────────────────────
def _save_temp(uploaded, suffix):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(uploaded.getvalue())
    tmp.close()
    return tmp.name

# ─── Main App Logic ──────────────────────────────────────────────────────
if selected == "Step 1":
    st.header("🧾 Step 1: Markdown → Excel")
    md = st.file_uploader("Drag & drop your Markdown file (.md)", type="md")
    if st.button("Convert to Excel ⏩"):
        if not md:
            st.warning("Please upload a Markdown file first.")
        else:
            path = _save_temp(md, ".md")
            out = convert_md_to_excel(path)
            st.success("Conversion successful!")
            df = pd.read_excel(out)
            st.dataframe(df, use_container_width=True)
            with open(out, "rb") as f:
                st.download_button("⬇️ Download 1.xlsx", f, file_name=os.path.basename(out))

elif selected == "Step 2":
    st.header("🔀 Step 2: Merge Answer Key & Solutions")
    c1, c2 = st.columns(2)
    md1 = c1.file_uploader("Upload Answer Key (.md)", type="md")
    md2 = c2.file_uploader("Upload Solutions (.md)", type="md")
    x1 = st.file_uploader("Upload 1.xlsx", type="xlsx")
    if st.button("Merge Files 🔄"):
        if not (md1 and md2 and x1):
            st.warning("Please upload both .md files and the 1.xlsx file.")
        else:
            p1 = _save_temp(md1, ".md")
            p2 = _save_temp(md2, ".md")
            p3 = _save_temp(x1, ".xlsx")
            out = process_step2(p1, p2, p3)
            st.success("Merge complete!")
            df = pd.read_excel(out)
            st.dataframe(df, use_container_width=True)
            with open(out, "rb") as f:
                st.download_button("⬇️ Download 2.xlsx", f, file_name=os.path.basename(out))

elif selected == "Step 3":
    st.header("🤖 Step 3: AI-Powered Explanations")
    x2 = st.file_uploader("Upload 2.xlsx", type="xlsx")
    if st.button("Generate Solutions ⚡️"):
        if not x2:
            st.warning("Please upload the 2.xlsx file.")
        else:
            path = _save_temp(x2, ".xlsx")
            df = pd.read_excel(path)
            total = len(df)
            progress = st.progress(0)
            status = st.empty()

            # Ensure columns exist
            df.setdefault('Detailed Explanation', '')
            df.setdefault('Flag', '')

            for i, row in df.iterrows():
                sys, usr = build_prompt(
                    row['Serial Number'],
                    row['Question No'],
                    row['Question'],
                    row['Type'],
                    row['Options'],
                    row['Answer'],
                    row['Explanation']
                )
                try:
                    res = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role":"system","content":sys}, {"role":"user","content":usr}],
                        temperature=0.2,
                        max_tokens=1200
                    )
                    raw = res.choices[0].message.content
                except Exception as e:
                    raw = f"Error: {e}\nFlag: Yes"

                expl, flag = parse_response_and_flag(raw)
                df.at[i, 'Detailed Explanation'] = expl
                df.at[i, 'Flag'] = flag
                progress.progress((i+1)/total)
                status.info(f"Processed {i+1}/{total} rows")

            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            out = os.path.join(os.path.dirname(path), f"3_{ts}.xlsx")
            df.to_excel(out, index=False)

            st.success("AI explanations generated!")
            st.dataframe(df, use_container_width=True)
            with open(out, "rb") as f:
                st.download_button("⬇️ Download 3.xlsx", f, file_name=os.path.basename(out))

else:  # Step 4
    st.header("🧼 Step 4: Final Cleanup")
    x3 = st.file_uploader("Upload 3.xlsx", type="xlsx")
    if st.button("Finalize ✔️"):
        if not x3:
            st.warning("Please upload the 3.xlsx file.")
        else:
            path = _save_temp(x3, ".xlsx")
            out = process_step4(path)
            st.success("Final cleanup done! 🎉")
            df = pd.read_excel(out)
            st.dataframe(df, use_container_width=True)
            with open(out, "rb") as f:
                st.download_button("🏁 Download Final Workbook", f, file_name=os.path.basename(out))
