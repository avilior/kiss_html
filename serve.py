"""Entrypoint: bind one dual-stack socket, then hand it to uvicorn.

`uvicorn --host ::` is not dual-stack. asyncio sets IPV6_V6ONLY on AF_INET6
sockets it creates, so IPv4 clients get a RST — and `--host 0.0.0.0` has the
mirror problem, refusing IPv6 clients once IPv6 publishing is enabled.
Creating the socket here with dualstack_ipv6=True accepts both families on one
socket, regardless of the net.ipv6.bindv6only default.
"""

import socket

import uvicorn

PORT = 8000

if __name__ == "__main__":
    sock = socket.create_server(
        ("::", PORT), family=socket.AF_INET6, dualstack_ipv6=True, reuse_port=False
    )
    uvicorn.run("app:app", fd=sock.fileno())
