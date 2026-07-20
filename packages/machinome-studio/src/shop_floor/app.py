import asyncio
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse


app = FastAPI(title="solid-node shop-floor")


PAGE = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>solid-node shop-floor</title>
  </head>
  <body>
    <main>
      <p id="shop-status" aria-live="polite">Shop is closed</p>
    </main>
    <script>
      const status = document.getElementById('shop-status');
      const lifecycle = new EventSource('/events/lifecycle');
      lifecycle.onopen = () => { status.textContent = 'Shop is open'; };
      lifecycle.onerror = () => { status.textContent = 'Shop is closed'; };
    </script>
  </body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def browser_page() -> str:
    return PAGE


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "open"}


async def lifecycle_events() -> AsyncIterator[str]:
    """Keep an SSE connection open for the lifetime of this service."""
    yield "event: lifecycle\ndata: open\n\n"
    while True:
        await asyncio.sleep(15)
        yield ": keepalive\n\n"


@app.get("/events/lifecycle")
def lifecycle_status() -> StreamingResponse:
    return StreamingResponse(lifecycle_events(), media_type="text/event-stream")
