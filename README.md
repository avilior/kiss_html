# kiss_html

A deliberately minimal containerized HTTP endpoint, for testing network
plumbing — is the container reachable from the LAN, is the port mapped, does
the health check pass.

One endpoint, `/`, returns a Hello page showing the container's hostname and
the address it saw the request come from. Everything else returns 404.

## Run it

```sh
docker compose up -d --build
```

Then open <http://localhost:8000/>.

```sh
docker compose logs -f   # watch requests arrive
docker compose down      # stop
```

## Testing LAN reachability

The port is published on all host interfaces, so the container answers on your
machine's LAN address:

```sh
# macOS
curl "http://$(ipconfig getifaddr en0):8000/"

# Linux
curl "http://$(hostname -I | awk '{print $1}'):8000/"
```

The page echoes back the client address it saw, which is a quick way to tell a
direct hit apart from one that passed through NAT or a proxy.

To restrict the service to the local machine instead, change the port mapping
in `docker-compose.yml` to `"127.0.0.1:8000:8000"`.

## How it works

- **`app.py`** — a raw [ASGI](https://asgi.readthedocs.io/) application. No web
  framework, so `uvicorn` and its three pure-Python dependencies are the only
  moving parts. To grow past a plumbing test, add `starlette` or `fastapi` to
  the `uv pip install` line in the Dockerfile.
- **`Dockerfile`** — multi-stage. The builder installs [uv](https://github.com/astral-sh/uv)
  and uses it to build a virtualenv; only that venv is copied into the runtime
  stage, so uv and its caches never ship. The container runs unprivileged as
  uid 10001. Final image is roughly 80 MB, most of which is `python:3.13-alpine`.
- **`docker-compose.yml`** — builds the image, publishes port 8000, restarts
  unless explicitly stopped, and health-checks via stdlib `urllib` (there is no
  `curl` in the alpine image).
