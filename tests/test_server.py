from http import HTTPStatus
from threading import Thread
from urllib.request import urlopen

from nlt.server import create_server


def test_health_endpoint_returns_ok():
    server = create_server("127.0.0.1", 0)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address
        with urlopen(f"http://{host}:{port}/healthz", timeout=2) as response:
            assert response.status == HTTPStatus.OK
            assert response.read().decode("utf-8") == '{\n  "status": "ok"\n}'
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
