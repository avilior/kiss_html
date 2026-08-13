# syntax=docker/dockerfile:1

# ---------------------------------------------------------------------------
# Build stage: use uv to build a self-contained virtualenv.
# uv itself never reaches the final image, only the venv it produced.
# ---------------------------------------------------------------------------
FROM python:3.13-alpine AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

RUN pip install --no-cache-dir uv

# Pin to the image's own interpreter so the venv's symlinks stay valid when the
# venv is copied into the runtime stage (identical base image).
RUN uv venv --python /usr/local/bin/python3.13 /app/.venv \
 && VIRTUAL_ENV=/app/.venv uv pip install --no-cache fastapi uvicorn

# ---------------------------------------------------------------------------
# Runtime stage
# ---------------------------------------------------------------------------
FROM python:3.13-alpine

COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# The whole app. Raw ASGI — no web framework, so the image stays small and the
# only moving part is uvicorn itself.
COPY app.py /app/app.py

# Run unprivileged.
RUN adduser -D -u 10001 app && chown -R app:app /app
USER app

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
