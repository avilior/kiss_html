#!/usr/bin/env bash
#
# Run kiss_html with plain docker — everything docker-compose.yml does, without
# compose. The container always listens on 8000 internally; PORT sets the host
# side of the mapping.
#
#   ./run.sh up                      build and start
#   ./run.sh down                    stop and remove
#   ./run.sh logs                    follow logs
#   ./run.sh status                  health, ports, version
#
#   PORT=9000 ./run.sh up            publish on a different host port
#   APP_VERSION=1.2.3 ./run.sh up    stamp the build
#
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

IMAGE="${IMAGE:-kiss-html:latest}"
NAME="${NAME:-kiss-html}"
PORT="${PORT:-8000}"
APP_VERSION="${APP_VERSION:-0.1.0}"

# Compose carries the healthcheck, not the image, so plain docker must pass it.
# There is no curl in the alpine image; stdlib urllib does the job.
HEALTH_CMD='python -c "import urllib.request; urllib.request.urlopen(\"http://127.0.0.1:8000/health\").read()"'

up() {
  # `up` replaces any container holding the name. Refuse if that container
  # belongs to compose — otherwise running this script silently destroys a
  # `docker compose up` container, since both default to the name kiss-html.
  if docker inspect "$NAME" \
       --format '{{index .Config.Labels "com.docker.compose.project"}}' 2>/dev/null \
       | grep -q .; then
    echo "refusing: container '$NAME' is managed by docker compose." >&2
    echo "use 'docker compose down' first, or set NAME= to something else." >&2
    exit 1
  fi

  docker build -t "$IMAGE" "$SCRIPT_DIR"
  docker rm -f "$NAME" >/dev/null 2>&1 || true
  docker run -d \
    --name "$NAME" \
    --restart unless-stopped \
    --publish "${PORT}:8000" \
    --env "APP_VERSION=${APP_VERSION}" \
    --health-cmd "$HEALTH_CMD" \
    --health-interval 30s \
    --health-timeout 3s \
    --health-retries 3 \
    --health-start-period 5s \
    "$IMAGE" >/dev/null
  echo "$NAME is up at http://localhost:${PORT}/"
}

down() {
  # `docker rm -f` exits 0 on a missing container, so check before reporting.
  if [ -n "$(docker ps -aq --filter "name=^/${NAME}$")" ]; then
    docker rm -f "$NAME" >/dev/null
    echo "$NAME removed"
  else
    echo "$NAME does not exist"
  fi
}

logs() {
  docker logs -f "$NAME"
}

status() {
  docker ps --filter "name=^/${NAME}$" --format 'name={{.Names}} status={{.Status}} ports={{.Ports}}'
  curl -fsS "http://localhost:${PORT}/version" && echo || echo "not answering on ${PORT}"
}

case "${1:-up}" in
  up)     up ;;
  down)   down ;;
  logs)   logs ;;
  status) status ;;
  *)      sed -n '3,14p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 1 ;;
esac
