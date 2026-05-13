"""Standard-library HTTP API for serving parsed PRD features."""

from __future__ import annotations

from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from nlt.prd import parse_prd_file


class NltRequestHandler(BaseHTTPRequestHandler):
    """HTTP handler exposing health and PRD feature endpoints."""

    server_version = "NLT/0.1"

    def do_GET(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        parsed_url = urlparse(self.path)

        if parsed_url.path == "/healthz":
            self._send_json({"status": "ok"})
            return

        if parsed_url.path == "/api/features":
            self._handle_features(parse_qs(parsed_url.query))
            return

        self._send_json({"error": "not_found"}, status=HTTPStatus.NOT_FOUND)

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002 - base class signature
        return

    def _handle_features(self, query: dict[str, list[str]]) -> None:
        configured_path = getattr(self.server, "prd_path", None)
        prd_path = query.get("prd", [configured_path])[0]

        if not prd_path:
            self._send_json(
                {"error": "missing_prd", "message": "Provide a PRD path when starting the server or as ?prd=."},
                status=HTTPStatus.BAD_REQUEST,
            )
            return

        path = Path(prd_path)
        if not path.exists():
            self._send_json(
                {"error": "prd_not_found", "message": f"PRD file does not exist: {path}"},
                status=HTTPStatus.NOT_FOUND,
            )
            return

        document = parse_prd_file(path)
        self._send_json(document.as_dict())

    def _send_json(self, payload: dict[str, object], *, status: HTTPStatus = HTTPStatus.OK) -> None:
        encoded = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


def create_server(host: str, port: int, *, prd_path: str | None = None) -> ThreadingHTTPServer:
    """Create a configured NLT HTTP server instance."""

    server = ThreadingHTTPServer((host, port), NltRequestHandler)
    server.prd_path = prd_path
    return server


def serve(host: str, port: int, *, prd_path: str | None = None) -> None:
    """Start the blocking HTTP server."""

    server = create_server(host, port, prd_path=prd_path)
    try:
        server.serve_forever()
    finally:
        server.server_close()
