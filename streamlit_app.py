import streamlit as st
import pandas as pd
import tempfile
import os
from datetime import datetime
import openai
from streamlit_option_menu import option_menu

# Processing modules
from step1 import convert_md_to_excel
from step2 import process_step2
from step3 import build_prompt, parse_response_and_flag
from step4 import process_step4

# Load API key
openai.api_key = st.secrets.get("OPENAI_API_KEY")
if not openai.api_key:
    st.error("🔑 OPENAI_API_KEY not found. Add it under Manage App → Secrets.")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Zarle AI Automator",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark theme CSS
st.markdown("""
<style>
  .stApp { background-color: #121212; color: #ECECEC; }
  .sidebar .css-1v3fvcr { background-color: #1F1F1F; }
  .stButton>button {
    background-color: #00BFA6; color: #121212;
    font-weight: bold; border-radius: 8px; padding: 0.6em 1.2em;
  }
  .stFileUploader > label {
    background-color: #242436; border: 2px dashed #444;
    border-radius: 8px; padding: 1em; color: #ECECEC;
  }
  .stDownloadButton>button {
    background-color: #673AB7; color: #FFFFFF;
    border-radius: 8px; padding: 0.6em 1.2em;
  }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    st.image("logo.png", width=140)
    st.markdown(
        "<h3 style='color: #FFFFFF; margin-bottom: 0.2em;'>Zarle AI Automator</h3>"
        "<p style='color: #DDDDDD; margin-top: 0;'>Fast conversion of Markdown quizzes into AI-verified Excel workbooks.</p>",
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
            "icon": {"color": "#00BFA6", "font-size": "20px"},
            "nav-link": {"font-size": "16px", "color": "#ECECEC", "text-align": "left"},
            "nav-link-selected": {"background-color": "#00BFA6", "color": "#121212", "font-weight": "bold"}
        }
    )

def _save_temp(uploaded, suffix):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(uploaded.getvalue())
    tmp.close()
    return tmp.name

# Step 1: Markdown to Excel
if selected == "Step 1":
    st.header("🧾 Step 1: Convert Markdown to Excel")
    md_file = st.file_uploader("Drag & drop your .md file", type="md")
    if st.button("Convert ⏩"):
        if not md_file:
            st.warning("Upload a Markdown file.")
        else:
            path = _save_temp(md_file, ".md")
            out1 = convert_md_to_excel(path)
            st.success("✅ 1.xlsx generated!")
            df1 = pd.read_excel(out1)
            st.dataframe(df1, use_container_width=True)
            with open(out1, "rb") as f:
                st.download_button("Download 1.xlsx", f, file_name=os.path.basename(out1))

# Step 2: Merge Answer & Solutions
elif selected == "Step 2":
    st.header("🔀 Step 2: Merge Answer Key & Solutions")
    col1, col2 = st.columns(2)
    md_ans = col1.file_uploader("Answer Key (.md)", type="md")
    md_sol = col2.file_uploader("Solutions (.md)", type="md")
    xls1 = st.file_uploader("Upload 1.xlsx", type="xlsx")
    if st.button("Merge 🔄"):
        if not (md_ans and md_sol and xls1):
            st.warning("Upload both .md files and 1.xlsx.")
        else:
            p1 = _save_temp(md_ans, ".md")
            p2 = _save_temp(md_sol, ".md")
            p3 = _save_temp(xls1, ".xlsx")
            out2 = process_step2(p1, p2, p3)
            st.success("✅ 2.xlsx generated!")
            df2 = pd.read_excel(out2)
            st.dataframe(df2, use_container_width=True)
            with open(out2, "rb") as f:
                st.download_button("Download 2.xlsx", f, file_name=os.path.basename(out2))

# Step 3: AI Explanations
elif selected == "Step 3":
    st.header("🤖 Step 3: Generate AI Explanations")
    xls2 = st.file_uploader("Upload 2.xlsx", type="xlsx")
    if st.button("Generate 💡"):
        if not xls2:
            st.warning("Upload 2.xlsx.")
        else:
            path2 = _save_temp(xls2, ".xlsx")
            df3 = pd.read_excel(path2)
            total = len(df3)
            progress = st.progress(0)
            status = st.empty()
            df3.setdefault('Detailed Explanation', '')
            df3.setdefault('Flag', '')
            for i, row in df3.iterrows():
                sys_msg, usr_msg = build_prompt(
                    row['Serial Number'], row['Question No'], row['Question'],
                    row['Type'], row['Options'], row['Answer'], row['Explanation']
                )
                try:
                    resp = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": sys_msg},
                            {"role": "user",   "content": usr_msg}
                        ],
                        temperature=0.2, max_tokens=1200
                    )
                    raw = resp.choices[0].message.content
                except Exception as e:
                    raw = f"Error: {e}\nFlag: Yes"
                expl, flag = parse_response_and_flag(raw)
                df3.at[i, 'Detailed Explanation'] = expl
                df3.at[i, 'Flag'] = flag
                progress.progress((i + 1) / total)
                status.info(f"Processed {i+1}/{total}")
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            out3 = os.path.join(os.path.dirname(path2), f"3_{ts}.xlsx")
            df3.to_excel(out3, index=False)
            st.success("✅ 3.xlsx generated!")
            st.dataframe(df3, use_container_width=True)
            with open(out3, "rb") as f:
                st.download_button("Download 3.xlsx", f, file_name=os.path.basename(out3))

# Step 4: Final Cleanup
else:
    st.header("🧼 Step 4: Final Cleanup")
    xls3 = st.file_uploader("Upload 3.xlsx", type="xlsx")
    if st.button("Finalize ✔️"):
        if not xls3:
            st.warning("Upload 3.xlsx.")
        else:
            path3 = _save_temp(xls3, ".xlsx")
            out4 = process_step4(path3)
            st.success("🎉 Final workbook ready!")
            df4 = pd.read_excel(out4)
            st.dataframe(df4, use_container_width=True)
            with open(out4, "rb") as f:
                st.download_button("Download Final Workbook", f, file_name=os.path.basename(out4))
