import os
from datetime import datetime
from pathlib import Path

DB_HOST: str = ""
DB_PATH: str = ""
DB_USER: str = ""
DB_PASSWORD: str = ""
SFTP_HOST: str = ""
SFTP_PORT: int = 2222
SFTP_USER: str = ""
SFTP_PASSWORD: str = ""
SFTP_REMOTE_DIR: str = "/"
SFTP_HOST_KEY: str = ""
CNPJ_DISTRIBUIDOR: str = ""
OUTPUT_DIR: str = "output"
CODIGO_EMPRESA: str = "01"


def _load_env() -> dict[str, str]:
    config: dict[str, str] = {}
    root = os.getenv("ECODATA_ROOT", Path(__file__).resolve().parents[1])
    env_path = Path(root) / ".env"
    if os.path.exists(env_path):
        for line in Path(env_path).read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            config[key.strip()] = val.strip().strip("\"'")
    return config


def reload_config():
    global DB_HOST, DB_PATH, DB_USER, DB_PASSWORD
    global SFTP_HOST, SFTP_PORT, SFTP_USER, SFTP_PASSWORD, SFTP_REMOTE_DIR, SFTP_HOST_KEY
    global CNPJ_DISTRIBUIDOR, OUTPUT_DIR, CODIGO_EMPRESA

    env = _load_env()

    DB_HOST = env.get("DB_HOST", os.getenv("DB_HOST", "127.0.0.1"))
    DB_PATH = env.get("DB_PATH", os.getenv("DB_PATH", ""))
    DB_USER = env.get("DB_USER", os.getenv("DB_USER", ""))
    DB_PASSWORD = env.get("DB_PASSWORD", os.getenv("DB_PASSWORD", ""))
    SFTP_HOST = env.get("SFTP_HOST", os.getenv("SFTP_HOST", ""))
    SFTP_PORT = int(env.get("SFTP_PORT") or os.getenv("SFTP_PORT") or "2222")
    SFTP_USER = env.get("SFTP_USER", os.getenv("SFTP_USER", ""))
    SFTP_PASSWORD = env.get("SFTP_PASSWORD", os.getenv("SFTP_PASSWORD", ""))
    SFTP_REMOTE_DIR = env.get("SFTP_REMOTE_DIR", os.getenv("SFTP_REMOTE_DIR", "/"))
    SFTP_HOST_KEY = env.get("SFTP_HOST_KEY", os.getenv("SFTP_HOST_KEY", ""))
    CNPJ_DISTRIBUIDOR = env.get("CNPJ_DISTRIBUIDOR", os.getenv("CNPJ_DISTRIBUIDOR", ""))
    OUTPUT_DIR = env.get("OUTPUT_DIR", os.getenv("OUTPUT_DIR", "output"))
    CODIGO_EMPRESA = env.get("CODIGO_EMPRESA", os.getenv("CODIGO_EMPRESA", "01"))


def get_timestamp() -> str:
    return datetime.now().strftime("%Y%m%d%H%M%S")


reload_config()
