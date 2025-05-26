from typing import Any
from threading import Lock
from ssl import create_default_context, SSLError
from socket import create_connection, error
from queue import LifoQueue
from urllib.request import Request, ProxyHandler, build_opener
from helpers import DEBUG, HTTP_TIMEOUT, HTTP_RETRIES

# *************** Connection ***************

class _Connection:
    def __init__(self, host: str, port: int, timeout: int, ssl: bool = False) -> None:
        self.host, self.port, self._lock, self._socket, self.timeout, self._ssl = host, port, Lock(), None, timeout, create_default_context() if ssl else None
    def __str__(self) -> str: return f"{type(self).__name__}(host={self.host}, port={self.port})"
    def __enter__(self) -> "_Connection": self.connect(); return self
    def __exit__(self, type, instance, traceback) -> None: self.close();
    def connect(self) -> "_Connection":
        with self._lock:
            if self._socket: self.close()
            socket = create_connection((self.host, self.port), self.timeout)
            if self._ssl: socket = self._ssl.wrap_socket(socket, server_hostname=self.host)
            self._socket = socket
            return socket
    def close(self) -> None:
        with self._lock:
            if self._socket:
                try:
                    if self._ssl: self._socket.unwrap()
                    self._socket.close()
                except: pass
                finally: self._socket = None
    def send(self, path: str, headers: dict = None, method: str ="GET") -> str:
        if not self._socket: self.connect()
        headers = headers or {}
        headers.setdefault("Host", self.host)
        headers.setdefault("Connection", "keep-alive")
        request = (
            f"{method} {path} HTTP/1.1\r\n" +
            "\r\n".join([f"{k}: {v}" for k, v in headers.items()]) +
            "\r\n\r\n"
        )
        try:
            with self._lock:
                self._socket.sendall(request.encode())
                return self.read()
        except (error, SSLError): self.close(); raise
    def read(self) -> str:
        response = b""
        while True:
            chunk = self._socket.recv(2048)
            if not chunk: break
            response += chunk
            if self.__is_readed(response): break
        return response
    def __is_readed(self, response) -> bool:
        if b"\r\n\r\n" not in response: return False
        end = response.index(b"\r\n\r\n") + 4
        lines = response[:end].decode("latin-1").splitlines()
        for line in lines:
            if line.lower().startswith("content-length:"):
                size = int(line.split(":")[1].strip())
                return len(response[end:]) >= size
        if any(line.lower() == "transfer-encoding: chunked" for line in lines):
            return response.endswith(b"0\r\n\r\n")
        return True
            

# *************** Pool ***************

class __ConnectionPool:
    CONN_QUEUE = LifoQueue
    def __init__(self, host: str, port: int = None) -> None:
        self.host, self.port = host, port
    def __str__(self) -> str: return f"{type(self).__name__}(host={self.host}, port={self.port})"
    def __enter__(self) -> "__ConnectionPool": return self
    def __exit__(self) -> None: self.close()
    def close() -> None: """Close all pooled connections and the pool"""

class _HTTPConnectionPool(__ConnectionPool):
    def __init__(self, host: str, port: int = None, timeout: int | None = HTTP_TIMEOUT, maxsize: int = 1, headers: str = None, retries: int | None = HTTP_RETRIES) -> None:
        __ConnectionPool.__init__(self, host, port)
        self.timeout, self.retries = timeout, retries
        self._pool: LifoQueue[Any] | None = self.CONN_QUEUE(maxsize)
        self.connections_size, requests_size = 0, 0
        for _ in range(maxsize): self._pool.put(None)
    def _new_connection(self):
        self.connections_size += 1
        if DEBUG > 0: print(f"Starting new HTTP connection [{self.connections_size}]: {self.host}:{self.port or "80"}")

# _HTTPSConnectionPool


# CONN POOL
# defined for specific host
# keeps connection alive, to be reused
# connections are stored in queue
    # so they can be used by different threads
    # threads wait or create new conn, if queue is empty (depends on maxsize)
# 