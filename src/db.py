import contextlib
import os
import threading
import time

import fdb

import src.config as cfg


class FirebirdPool:
    def __init__(self, min_size: int = 1, max_size: int = 5, idle_timeout: int = 300):
        self._min = min_size
        self._max = max_size
        self._idle_timeout = idle_timeout
        self._lock = threading.Lock()
        self._pool: list[fdb.Connection] = []
        self._in_use: set[int] = set()
        self._closed = False

    def _create_conn(self) -> fdb.Connection:
        if not cfg.DB_PATH:
            raise ValueError("DB_PATH nao configurado. Verifique o arquivo .env")
        if not cfg.DB_USER:
            raise ValueError("DB_USER nao configurado. Verifique o arquivo .env")
        host = cfg.DB_HOST.strip() if cfg.DB_HOST else ""
        if not host or host in ("localhost", "0.0.0.0"):
            host = "127.0.0.1"
        dsn = f"{host}:{cfg.DB_PATH}"
        return fdb.connect(dsn=dsn, user=cfg.DB_USER, password=cfg.DB_PASSWORD)

    def _is_conn_alive(self, conn: fdb.Connection) -> bool:
        try:
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM RDB$DATABASE")
            cur.fetchone()
            return True
        except Exception:
            return False

    def acquire(self) -> fdb.Connection:
        if self._closed:
            raise RuntimeError("Pool esta fechado")

        with self._lock:
            while self._pool:
                conn = self._pool.pop()
                conn_id = id(conn)
                if conn_id in self._in_use:
                    continue
                if not self._is_conn_alive(conn):
                    with contextlib.suppress(Exception):
                        conn.close()
                    continue
                self._in_use.add(conn_id)
                return conn

            if len(self._in_use) >= self._max:
                raise RuntimeError(
                    f"Pool esgotado: {self._max} conexoes em uso. "
                    "Aumente FIREBIRD_POOL_MAX ou aguarde liberacao."
                )

            conn = self._create_conn()
            self._in_use.add(id(conn))
            return conn

    def release(self, conn: fdb.Connection | None):
        if conn is None:
            return
        conn_id = id(conn)
        with self._lock:
            self._in_use.discard(conn_id)
            if self._closed:
                with contextlib.suppress(Exception):
                    conn.close()
                return
            if len(self._pool) < self._max:
                self._pool.append(conn)
            else:
                with contextlib.suppress(Exception):
                    conn.close()

    def close_all(self):
        self._closed = True
        with self._lock:
            for conn in self._pool:
                with contextlib.suppress(Exception):
                    conn.close()
            self._pool.clear()
            self._in_use.clear()

    def cleanup_idle(self):
        time.time()
        with self._lock:
            keep = []
            for conn in self._pool:
                conn_id = id(conn)
                if conn_id in self._in_use:
                    keep.append(conn)
                    continue
                if len(keep) < self._min:
                    keep.append(conn)
                else:
                    with contextlib.suppress(Exception):
                        conn.close()
            self._pool = keep


_pool: FirebirdPool | None = None
_pool_lock = threading.Lock()


def get_pool() -> FirebirdPool:
    global _pool
    if _pool is None:
        with _pool_lock:
            if _pool is None:
                max_size = int(os.getenv("FIREBIRD_POOL_MAX", "5"))
                min_size = int(os.getenv("FIREBIRD_POOL_MIN", "1"))
                idle_timeout = int(os.getenv("FIREBIRD_POOL_IDLE", "300"))
                _pool = FirebirdPool(
                    min_size=min_size,
                    max_size=max_size,
                    idle_timeout=idle_timeout,
                )
    return _pool


def close_pool():
    global _pool
    if _pool is not None:
        _pool.close_all()
        _pool = None


# Para compatibilidade com codigo existente:
# get_connection() agora retorna uma conexao do pool
_connection_context = threading.local()


def get_connection() -> fdb.Connection:
    conn = get_pool().acquire()
    _connection_context.current = conn
    return conn


def release_connection(conn: fdb.Connection | None = None):
    if conn is None:
        conn = getattr(_connection_context, "current", None)
    if conn is not None:
        get_pool().release(conn)
        _connection_context.current = None


def get_empresa(conn, codigo_empresa: str):
    cur = conn.cursor()
    cur.execute(
        "select CODIGO, NOMEFANTASIA, RAZAOSOCIAL, CPFCNPJ, INDUSTRIA "
        "from TGEREMPRESA where CODIGO = ?",
        (codigo_empresa,),
    )
    row = cur.fetchone()
    if row:
        return {
            "codigo": row[0].strip(),
            "fantasia": row[1].strip(),
            "razao": row[2].strip(),
            "cnpj": row[3].strip(),
            "industria": row[4].strip() if row[4] else "",
        }
    return None
