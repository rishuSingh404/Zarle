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

# Streamlit app with side nav & futuristic dark theme
from streamlit_option_menu import option_menu

# App config
st.set_page_config(
    page_title="Zarle AI Automator",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark mode and styling
st.markdown("""
    <style>
        /* Base colors */
        .stApp { background-color: #121212; color: #EEE; }
        /* Sidebar menu styling */
        .sidebar .css-1d391kg { background-color: #1F1F1F; }
        /* File uploader styling */
        .stFileUploader > label { width: 100%; padding: 1rem; background-color: #212121; border: 2px dashed #444; border-radius: 8px; }
        .stFileUploader > div { margin-top: 0.5rem; }
        /* Tab headers styling via option-menu */
        .menu-icon { color: #00BFA6!important; }
    </style>
""", unsafe_allow_html=True)

# Sidebar navigation via streamlit-option-menu
with st.sidebar:
    st.image("logo.png", width=120)
    st.markdown("### Zarle AI Automator")
    selected = option_menu(
        menu_title=None,
        options=["Step 1", "Step 2", "Step 3", "Step 4"],
        icons=["file-earmark-text", "layers-half", "robot", "brush"],
        menu_icon="cast",
        default_index=0,
        orientation="vertical",
        styles={
            "container": {"padding": "0!important", "background-color": "#1F1F1F"},
            "icon": {"color": "#00BFA6", "font-size": "20px"},
            "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "color": "#EEE"},
            "nav-link-selected": {"background-color": "#00BFA6", "color": "#121212"},
        }
    )

# File save helper
def _save_temp(uploaded, suffix):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(uploaded.getvalue())
    tmp.close()
    return tmp.name

# Main content based on navigation selection
if selected == "Step 1":
    st.header("🧾 Step 1: Markdown → Excel")
    md = st.file_uploader("Drag & drop a Markdown file (.md)", type="md")
    if st.button("Convert to Excel ⏩"):
        if not md:
            st.warning("Upload a Markdown file to proceed.")
        else:
            path = _save_temp(md, ".md")
            out = convert_md_to_excel(path)
            st.success("Conversion successful!")
            st.dataframe(pd.read_excel(out), use_container_width=True)
            with open(out, "rb") as f:
                st.download_button("Download 1.xlsx", f, file_name=os.path.basename(out))

elif selected == "Step 2":
    st.header("🔀 Step 2: Merge Answer Key & Solutions")
    col1, col2 = st.columns(2)
    md1 = col1.file_uploader("Answer Key (.md)", type="md")
    md2 = col2.file_uploader("Solutions (.md)", type="md")
    x1 = st.file_uploader("Drag & drop 1.xlsx file", type="xlsx")
    if st.button("Merge Files 🔄"):
        if not (md1 and md2 and x1):
            st.warning("Please upload both markdowns and 1.xlsx.")
        else:
            p1, p2 = _save_temp(md1, ".md"), _save_temp(md2, ".md")
            p3 = _save_temp(x1, ".xlsx")
            out = process_step2(p1, p2, p3)
            st.success("Merge complete!")
            st.dataframe(pd.read_excel(out), use_container_width=True)
            with open(out, "rb") as f:
                st.download_button("Download 2.xlsx", f, file_name=os.path.basename(out))

elif selected == "Step 3":
    st.header("🤖 Step 3: AI-Powered Explanations")
    x2 = st.file_uploader("Drag & drop 2.xlsx file", type="xlsx")
    if st.button("Generate Solutions ⚡️"):
        if not x2:
            st.warning("Upload 2.xlsx to generate explanations.")
        else:
            path = _save_temp(x2, ".xlsx")
            df = pd.read_excel(path)
            progress = st.progress(0)
            status = st.empty()
            df.setdefault('Detailed Explanation', '')
            df.setdefault('Flag', '')
            total = len(df)
            for i, row in df.iterrows():
                sys, usr = build_prompt(
                    row['Serial Number'], row['Question No'], row['Question'],
                    row['Type'], row['Options'], row['Answer'], row['Explanation']
                )
                try:
                    res = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role":"system","content":sys},{"role":"user","content":usr}],
                        temperature=0.2, max_tokens=1200
                    )
                    raw = res.choices[0].message.content
                except Exception as e:
                    raw = f"Error: {e}
Flag: Yes"
                expl, flag = parse_response_and_flag(raw)
                df.at[i, 'Detailed Explanation'] = expl
                df.at[i, 'Flag'] = flag
                progress.progress((i+1)/total)
                status.info(f"{i+1}/{total} processed...")
            ts = datetime.now().strftime('%Y%m%d_%H%M%S')
            out = os.path.join(os.path.dirname(path), f"3_{ts}.xlsx")
            df.to_excel(out, index=False)
            st.success("AI explanations generated!")
            st.dataframe(df, use_container_width=True)
            with open(out, "rb") as f:
                st.download_button("Download 3.xlsx ⚡️", f, file_name=os.path.basename(out))

else:
    # Step 4
    st.header("🧼 Step 4: Final Cleanup")
    x3 = st.file_uploader("Drag & drop 3.xlsx file", type="xlsx")
    if st.button("Finalize ✔️"):
        if not x3:
            st.warning("Upload 3.xlsx to finalize.")
        else:
            path = _save_temp(x3, ".xlsx")
            out = process_step4(path)
            st.success("Final cleanup done! 🎉")
            st.dataframe(pd.read_excel(out), use_container_width=True)
            with open(out, "rb") as f:
                st.download_button("Download Final Workbook 🏁", f, file_name=os.path.basename(out))