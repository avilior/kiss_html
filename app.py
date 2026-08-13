"""Minimal FastAPI app: a Hello page at /, plus /health and /version."""

import os
import platform
from datetime import datetime, timezone
from importlib.metadata import version as pkg_version

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
    <dt>served at</dt><dd>{now}</dd>
    <dt>your address</dt><dd>{client}</dd>
  </dl>
</main>
</body>
</html>
"""

HOSTNAME = os.uname().nodename

# Overridable at run time so a deploy can stamp which build is actually live.
APP_VERSION = os.environ.get("APP_VERSION", "0.1.0")

app = FastAPI(title="kiss_html", docs_url="/docs")


@app.get("/", response_class=HTMLResponse)
async def hello(request: Request) -> HTMLResponse:
    body = PAGE.format(
        host=HOSTNAME,
        now=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        client=request.client.host if request.client else "unknown",
    )
    # Without this the browser may serve a reload from cache and the timestamp
    # would look frozen — the opposite of what it is there to show.
    return HTMLResponse(body, headers={"Cache-Control": "no-store"})


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "host": HOSTNAME}


@app.get("/version")
async def version() -> dict[str, str]:
    return {
        "version": APP_VERSION,
        "python": platform.python_version(),
        "fastapi": pkg_version("fastapi"),
        "host": HOSTNAME,
    }
