# Murder Mystery Logic Solver — Deploy Bundle

Streamlit app with dark/light theme toggle.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```
Open http://localhost:8501

## Deploy
- Streamlit Cloud: https://share.streamlit.io → New app → main file `app.py`
- Render: New → Blueprint (uses `render.yaml`)
- Docker: `docker build -t mms . && docker run -p 8501:8501 mms`
- Heroku/Railway: uses `Procfile`

Note: Vercel/Netlify are NOT supported (Streamlit needs a long-running server).
