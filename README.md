# ZingTel Agent

ZingTel Agent is a Streamlit-based customer support assistant that answers service, billing, and troubleshooting questions using a small retrieval-augmented knowledge base plus support tools.

## What It Does

- Delivers a polished, full-page Streamlit chat experience
- Uses `ZingTel_guide.txt` for grounded answers about ZingTel policies and support
- Includes web search and utility tools for broader support tasks
- Falls back gracefully when the Gemini API key is unavailable

## Requirements

- Python 3.11 or newer
- A Gemini API key in `.env` as `GEMINI_API_KEY` or `GOOGLE_API_KEY`

## Local Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_key_here
```

You can use `GOOGLE_API_KEY` instead if you prefer.

## Run Locally

Start the app with Streamlit:

```powershell
python -m streamlit run streamlit_app.py
```

If you want to use the virtual environment interpreter directly:

```powershell
.\venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

## Deploy on Streamlit Cloud

1. Push this repository to GitHub.
2. Connect the GitHub repo to Streamlit Cloud.
3. Set the main file path to `streamlit_app.py`.
4. Set the Python version to `3.11` or `3.12` in Streamlit Cloud. Do not use `3.14` for this app.
5. Add `GEMINI_API_KEY` in the Streamlit Cloud secrets/settings panel.
6. Deploy and share the generated app URL.

If Streamlit Cloud shows a `chromadb` or `protobuf` import error, the first thing to check is that the app is not running on Python `3.14`.

## Project Structure

- `app.py` - backend agent, tools, and RAG setup
- `streamlit_app.py` - Streamlit user interface
- `ZingTel_guide.txt` - support knowledge base
- `requirements.txt` - Python dependencies
- `.streamlit/config.toml` - Streamlit theme settings

## Notes

- Do not commit `.env`, backup files, or log files.
- The app still starts without a Gemini key, but chat responses will use a friendly unavailable message until a key is configured.
