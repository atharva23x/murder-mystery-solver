from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="Murder Mystery Logic Solver")

STREAMLIT_URL = None  # set to your Streamlit Cloud URL after deploying there, e.g. "https://your-app.streamlit.app"

LANDING_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Murder Mystery Logic Solver</title>
  <style>
    body { font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
           background: #0E1218; color: #F1F5F9; display: flex; align-items: center;
           justify-content: center; min-height: 100vh; margin: 0; padding: 24px; }
    .card { max-width: 640px; background: #151C28; border: 1px solid #2A364F;
            border-radius: 14px; padding: 32px; box-shadow: 0 10px 30px rgba(0,0,0,.4); }
    h1 { color: #D4AF37; margin-top: 0; }
    a { color: #D4AF37; }
    .btn { display: inline-block; margin-top: 16px; padding: 10px 18px; background: #D4AF37;
           color: #0E1218; border-radius: 8px; text-decoration: none; font-weight: 700; }
    code { background: #0E1218; padding: 2px 6px; border-radius: 4px; }
  </style>
</head>
<body>
  <div class="card">
    <h1>🕵️ Murder Mystery Logic Solver</h1>
    <p>This app is built with <b>Streamlit</b>, which needs a long-running server with
       WebSockets. Vercel only supports serverless functions, so the interactive app cannot
       run here directly.</p>
    <p>👉 Deploy the Streamlit app on <a href="https://share.streamlit.io">Streamlit Community Cloud</a>
       (free, 2 minutes) and paste its URL into <code>api/index.py</code> as <code>STREAMLIT_URL</code>
       to make this page redirect automatically.</p>
    <p>Or run it locally:</p>
    <pre><code>pip install -r requirements.txt
streamlit run app.py</code></pre>
    {f'<a class="btn" href="{STREAMLIT_URL}">Open the app →</a>' if STREAMLIT_URL else ''}
  </div>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def index():
    if STREAMLIT_URL:
        return HTMLResponse(
            f'<meta http-equiv="refresh" content="0; url={STREAMLIT_URL}">',
            status_code=302,
            headers={"Location": STREAMLIT_URL},
        )
    return LANDING_HTML


@app.get("/health")
def health():
    return {"status": "ok"}
