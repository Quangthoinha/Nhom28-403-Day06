import os
from typing import Dict, Iterable, Optional, Tuple

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

BACKEND_BASE = os.environ.get("BACKEND_BASE", "http://127.0.0.1:5050").rstrip("/")

app = FastAPI()


def _filter_hop_by_hop_headers(headers: Iterable[Tuple[str, str]]) -> Dict[str, str]:
    # Hop-by-hop headers must not be forwarded by proxies (RFC 7230).
    drop = {
        "connection",
        "keep-alive",
        "proxy-authenticate",
        "proxy-authorization",
        "te",
        "trailer",
        "transfer-encoding",
        "upgrade",
        "host",
        "content-length",
    }
    out: Dict[str, str] = {}
    for k, v in headers:
        lk = k.lower()
        if lk in drop:
            continue
        out[k] = v
    return out


@app.get("/")
def root() -> FileResponse:
    return FileResponse("index.html")


@app.api_route("/chat", methods=["POST"])
async def proxy_chat(request: Request) -> Response:
    return await _proxy(request, "/chat")


@app.api_route("/health", methods=["GET"])
async def proxy_health(request: Request) -> Response:
    return await _proxy(request, "/health")


async def _proxy(request: Request, path: str) -> Response:
    url = f"{BACKEND_BASE}{path}"
    body = await request.body()
    headers = _filter_hop_by_hop_headers(request.headers.items())

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            upstream = await client.request(
                method=request.method,
                url=url,
                params=request.query_params,
                content=body,
                headers=headers,
            )
    except httpx.RequestError as e:
        return JSONResponse(
            status_code=502,
            content={"error": "Không kết nối được backend", "backend": BACKEND_BASE, "detail": str(e)},
        )

    resp_headers = _filter_hop_by_hop_headers(upstream.headers.items())
    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        headers=resp_headers,
        media_type=upstream.headers.get("content-type"),
    )


# Serve the prototype static files (prototype.html, prototype-data.js, rag_data.json, etc.)
app.mount("/", StaticFiles(directory=".", html=True), name="static")

