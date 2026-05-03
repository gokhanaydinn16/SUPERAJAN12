from __future__ import annotations

import errno
from contextlib import suppress

from src.agent_os.app import AgentOS
from src.agent_os.http_api import ApiServices, start_api_server


def _start_server_with_fallback(host: str, port: int, services: ApiServices, attempts: int = 10):
    last_error: OSError | None = None
    for candidate in range(port, port + attempts):
        try:
            return start_api_server(host, candidate, services), candidate
        except OSError as exc:
            if exc.errno != errno.EADDRINUSE:
                raise
            last_error = exc
    if last_error is not None:
        raise last_error
    raise RuntimeError("unable to start API server")


def main() -> None:
    app = AgentOS.bootstrap()
    services = ApiServices(
        health=app,
        dashboard=app,
        events=app,
        kill_switch=app,
        seed_cycle=app,
        stage_control=app,
        venue_control=app,
        reconciliation=app,
        release_control=app,
        static_dir=__import__("pathlib").Path("web"),
    )
    server, port = _start_server_with_fallback(app.config.host, app.config.port, services)
    print(f"Agent OS running at http://{app.config.host}:{port}")
    with suppress(KeyboardInterrupt):
        server.serve_forever()
    server.server_close()


if __name__ == "__main__":
    main()
