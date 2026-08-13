"""Minimal raw-ASGI app: serves a Hello page at / and 404s everything else."""

import os

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


async def app(scope, receive, send):
    if scope["type"] == "lifespan":
        while True:
            message = await receive()
            if message["type"] == "lifespan.startup":
                await send({"type": "lifespan.startup.complete"})
            elif message["type"] == "lifespan.shutdown":
                await send({"type": "lifespan.shutdown.complete"})
                return
        return

    if scope["type"] != "http":
        return

    if scope["path"] != "/":
        body = b"Not Found\n"
        status, content_type = 404, "text/plain; charset=utf-8"
    else:
        client = scope.get("client")
        body = PAGE.format(
            host=HOSTNAME,
            client=client[0] if client else "unknown",
        ).encode()
        status, content_type = 200, "text/html; charset=utf-8"

    await send({
        "type": "http.response.start",
        "status": status,
        "headers": [
            (b"content-type", content_type.encode()),
            (b"content-length", str(len(body)).encode()),
        ],
    })
    await send({"type": "http.response.body", "body": body})
