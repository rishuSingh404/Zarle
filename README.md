# 🚀📚 Automated Quiz Solution Generator & Excel Formatter


> **From Markdown quizzes to fully explained Excel workbooks in record time!**


---


## 🌟 What It Does


This Streamlit app isn’t just a file converter—it’s a **complete automation suite** that:


1. **Ingests** raw quiz content from Markdown (`.md`) files, parsing out questions, multiple-choice options, and metadata.

2. **Formats** the parsed data into a structured Excel workbook with columns for Question No, Question Text, Type (MCQ/Short Answer), Options, Answer, Explanation.

3. **Empowers** Step 3 by seamlessly integrating with the OpenAI API to **generate detailed, step-by-step solutions** and flag correctness—all without writing a single line of code!

4. **Cleans up** LaTeX artifacts and polishes the final explanations, delivering a pristine Excel file ready for sharing or publishing.


---


## ⚡️ Performance That Redefines Productivity


**Manually**, turning a 900‑page question bank into a fully explained workbook used to take a team 

**15 full days** of painstaking work.


**Now**, with this app, the entire process completes in **under 3 HOURS**—a **120× speedup**! 

Imagine what you’ll do with all that reclaimed time.


---


## 🏆 Key Highlights


- **Four-Step Wizard**: Navigate conversion, merging, AI‑powered explanation, and cleanup via a sleek sidebar.

- **Instant Previews**: View interactive DataFrames after each step to ensure accuracy.

- **Automated Expertise**: Leverage OpenAI’s world‑class LLM to generate clear, human‑readable, step‑by‑step solutions.

- **Timestamped Outputs**: Unique filenames like `3_20250423_150045.xlsx` keep your versions organized.

- **Zero Code Exposure**: Non-technical users run the entire pipeline from their browser—no Python required.


---


## 🚀 Quickstart Guide


1. **Clone the Repository**
   ```bash
   git clone [https://github.com/your-user/your-repo.git](https://github.com/rishuSingh404/Zarle.git)
   cd your-repo
   ```


2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```


3. **Configure Your OpenAI Key**
   Create `.streamlit/secrets.toml`:
   ```toml
   OPENAI_API_KEY = "sk-..."
   ```


4. **Run Locally**
   ```bash
   streamlit run streamlit_app.py
   ```
   Then open [http://localhost:8501](http://localhost:8501).


---


## ☁️ Deploy on Streamlit Community Cloud


1. Push all files to GitHub (`main` branch).

2. Confirm you’ve committed:
   - `.streamlit/config.toml`
   - `.streamlit/secrets.toml`
   - `streamlit_app.py`, `step1.py`–`step4.py`, `requirements.txt`, `logo.png` (optional)

3. Visit [share.streamlit.io](https://share.streamlit.io), log in, and click **New app**.

4. Select your repo, branch `main`, and `streamlit_app.py`.

5. Click **Deploy**—share the generated URL with your team or students!


---


## 🔧 Customization & Branding


- **Logo**: Drop `logo.png` in the repo root to showcase your brand.

- **Theme**: Tweak colors and fonts in `.streamlit/config.toml`.

- **File Names**: Modify helper functions in `streamlit_app.py` to adjust naming conventions.

- **Error Handling**: Enhance `try/except` blocks for tailored user messages.


---


## 📂 Repository Layout


```text
├── .streamlit/
│   ├── config.toml      # UI theme & server settings
│   └── secrets.toml     # OPENAI_API_KEY = "sk-..."
├── logo.png            # (Optional) Sidebar branding
├── README.md           # This guide
├── requirements.txt    # Python library dependencies
├── streamlit_app.py    # Main Streamlit application
├── step1.py            # parse Markdown → Excel format
├── step2.py            # merge answer key & solutions
├── step3.py            # generate AI explanations & flags
└── step4.py            # cleanup LaTeX & finalize workbook
```


---


## 💬 Feedback & Contributions


We welcome issues, feature requests, and pull requests. Let’s make quiz automation lightning-fast together!


---


*Built with ❤️ and OpenAI by Rishu Kumar Singh / Zarle Infotech*
