import streamlit as st
import pandas as pd
import tempfile, os

# ─── Import your implementations ─────────────────────────────────────
from step1 import convert_md_to_excel
from step2 import process_step2
from step3 import process_step3
from step4 import process_step4
import openai

# Load your API key (set in Streamlit Cloud secrets)
openai.api_key = st.secrets["OPENAI_API_KEY"]

# ─── App config & CSS ───────────────────────────────────────────────
st.set_page_config(
    page_title="Markdown→Excel Pipeline",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown(
    "<style>.stButton > button{margin-top:10px;}</style>",
    unsafe_allow_html=True
)

# ─── Sidebar ────────────────────────────────────────────────────────
# Optional logo display (place logo.png in repo root)
LOGO_PATH = "logo.png"
if os.path.exists(LOGO_PATH):
    st.sidebar.image(LOGO_PATH, width=150)

st.sidebar.title("🚀 Pipeline Navigator")
step = st.sidebar.radio(
    "Select Step:",
    [
        "Step 1: MD → 1.xlsx",
        "Step 2: MD+MD+1.xlsx → 2.xlsx",
        "Step 3: 2.xlsx → 3.xlsx",
        "Step 4: 3.xlsx → Final"
    ]
)
st.sidebar.markdown("---")

# ─── Main ───────────────────────────────────────────────────────────
st.title("📄 ➡️ 📊 4-Step Markdown→Excel Pipeline")
st.markdown("Upload files, click **Run**, preview & download results.")

# Utility to save uploads to temp file

def _save_temp(uploaded, suffix):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(uploaded.getvalue())
    tmp.close()
    return tmp.name

# Step 1
if step == "Step 1: MD → 1.xlsx":
    st.header("Step 1: Convert Markdown to Excel")
    md = st.file_uploader("Upload one .md file", type="md")
    if st.button("Run Step 1"):
        if not md:
            st.error("Please upload a Markdown file.")
        else:
            try:
                st.info("Converting…")
                path = _save_temp(md, ".md")
                out = convert_md_to_excel(path)
                st.success("Done!")
                df = pd.read_excel(out)
                st.dataframe(df, use_container_width=True)
                with open(out, "rb") as f:
                    st.download_button(
                        label="Download 1.xlsx",
                        data=f,
                        file_name=os.path.basename(out),
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            except Exception as e:
                st.error(f"Error: {e}")

# Step 2
elif step == "Step 2: MD+MD+1.xlsx → 2.xlsx":
    st.header("Step 2: Merge answers & solutions")
    c1, c2 = st.columns(2)
    md1 = c1.file_uploader("Answer-key .md", type="md")
    md2 = c2.file_uploader("Solutions .md", type="md")
    x1 = st.file_uploader("Upload 1.xlsx", type="xlsx")
    if st.button("Run Step 2"):
        if not (md1 and md2 and x1):
            st.error("Upload both .md files and 1.xlsx.")
        else:
            try:
                st.info("Processing…")
                p1 = _save_temp(md1, ".md")
                p2 = _save_temp(md2, ".md")
                p3 = _save_temp(x1, ".xlsx")
                out = process_step2(p1, p2, p3)
                st.success("Done!")
                df = pd.read_excel(out)
                st.dataframe(df, use_container_width=True)
                with open(out, "rb") as f:
                    st.download_button(
                        label="Download 2.xlsx",
                        data=f,
                        file_name=os.path.basename(out),
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            except Exception as e:
                st.error(f"Error: {e}")

# Step 3
elif step == "Step 3: 2.xlsx → 3.xlsx":
    st.header("Step 3: Generate Detailed Explanations")
    x2 = st.file_uploader("Upload 2.xlsx", type="xlsx")
    if st.button("Run Step 3"):
        if not x2:
            st.error("Please upload 2.xlsx.")
        else:
            try:
                st.info("Calling OpenAI…")
                p = _save_temp(x2, ".xlsx")
                out = process_step3(p, openai_key=st.secrets.get("OPENAI_API_KEY"))
                st.success("Done!")
                df = pd.read_excel(out)
                st.dataframe(df, use_container_width=True)
                with open(out, "rb") as f:
                    st.download_button(
                        label="Download 3.xlsx",
                        data=f,
                        file_name=os.path.basename(out),
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            except Exception as e:
                st.error(f"Error: {e}")

# Step 4
else:
    st.header("Step 4: Final Cleanup & Output")
    x3 = st.file_uploader("Upload 3.xlsx", type="xlsx")
    if st.button("Run Step 4"):
        if not x3:
            st.error("Please upload 3.xlsx.")
        else:
            try:
                st.info("Cleaning up…")
                p = _save_temp(x3, ".xlsx")
                out = process_step4(p)
                st.success("Pipeline Complete! 🎉")
                df = pd.read_excel(out)
                st.dataframe(df, use_container_width=True)
                with open(out, "rb") as f:
                    st.download_button(
                        label="Download Final Excel",
                        data=f,
                        file_name=os.path.basename(out),
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            except Exception as e:
                st.error(f"Error: {e}")