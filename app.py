"""Minimal FastAPI app: a Hello page at /, a JSON health check at /health."""

import os

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Hello</title>
<style>
  body {{ font-family: system-ui, sans-serif; display: grid; place-items: center;
         min-height: 100vh; margin: 0; background: #0f172a; color: #e2e8f0; }}
  main {{ text-align: center; }}
  h1 {{ font-size: 3rem; margin: 0 0 1rem; }}
  dl {{ display: grid; grid-template-columns: auto auto; gap: .25rem 1rem;
        font-size: .9rem; color: #94a3b8; }}
  dt {{ text-align: right; }}
  dd {{ margin: 0; text-align: left; font-family: ui-monospace, monospace; }}
</style>
</head>
<body>
<main>
  <h1>Hello</h1>
  <dl>
    <dt>served by</dt><dd>{host}</dd>
    <dt>your address</dt><dd>{client}</dd>
  </dl>
</main>
</body>
</html>
"""

HOSTNAME = os.uname().nodename

app = FastAPI(title="kiss_html", docs_url="/docs")


@app.get("/", response_class=HTMLResponse)
async def hello(request: Request) -> str:
    return PAGE.format(
        host=HOSTNAME,
        client=request.client.host if request.client else "unknown",
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "host": HOSTNAME}
