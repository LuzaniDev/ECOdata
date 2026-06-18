import os
import sys
import webbrowser
from pathlib import Path


_FB_CLIENT_PATHS = [
    r"C:\Program Files (x86)\Firebird\Firebird_2_5\bin",
    r"C:\Program Files\Firebird\Firebird_2_5\bin",
    r"C:\Program Files (x86)\Firebird\Firebird_3_0\bin",
    r"C:\Program Files\Firebird\Firebird_3_0\bin",
    r"C:\Program Files (x86)\Firebird\Firebird_4_0\bin",
    r"C:\Program Files\Firebird\Firebird_4_0\bin",
    r"C:\Program Files (x86)\Firebird\Firebird_5_0\bin",
    r"C:\Program Files\Firebird\Firebird_5_0\bin",
]


_FB_SERVICE_NAMES = [
    "Firebird Guardian",
    "FirebirdServerDefaultInstance",
    "FirebirdServer",
]


def _setup_firebird_dll():
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        bundled = os.path.join(meipass, "fbclient.dll")
        if os.path.isfile(bundled):
            if hasattr(os, "add_dll_directory"):
                os.add_dll_directory(meipass)
            os.environ["PATH"] = meipass + os.pathsep + os.environ.get("PATH", "")
            import fdb.ibase as fdb_ibase
            fdb_ibase.fb_library_name = bundled
            return
    for _p in _FB_CLIENT_PATHS:
        dll = os.path.join(_p, "fbclient.dll")
        if os.path.isfile(dll):
            os.environ["PATH"] = _p + os.pathsep + os.environ.get("PATH", "")
            import fdb.ibase as fdb_ibase
            fdb_ibase.fb_library_name = dll
            return
    print("[AVISO] fbclient.dll nao encontrada. Verifique se o Firebird esta instalado.")


def _start_firebird_service():
    import subprocess
    for name in _FB_SERVICE_NAMES:
        try:
            r = subprocess.run(
                ["sc", "query", name],
                capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW
            )
            if "RUNNING" in r.stdout:
                return
            if "STOPPED" in r.stdout or "PAUSED" in r.stdout:
                subprocess.run(
                    ["net", "start", name],
                    capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW
                )
                return
        except Exception:
            continue


def _get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent.resolve()
    return Path(__file__).parent.resolve()


def _create_dirs(base: Path):
    for d in ("data", "output", "logs"):
        (base / d).mkdir(parents=True, exist_ok=True)


def _create_default_env(base: Path):
    env_file = base / ".env"
    if env_file.exists():
        return
    env_file.write_text(
        "# ── BANCO DE DADOS FIREBIRD (OBRIGATORIO) ──\n"
        "DB_HOST=127.0.0.1\n"
        "DB_PATH=\n"
        "DB_USER=SYSDBA\n"
        "DB_PASSWORD=\n"
        "CODIGO_EMPRESA=01\n"
        "CNPJ_DISTRIBUIDOR=\n"
        "# ── SFTP (OBRIGATORIO para envio de arquivos) ──\n"
        "SFTP_HOST=\n"
        "SFTP_PORT=2222\n"
        "SFTP_USER=\n"
        "SFTP_PASSWORD=\n",
        encoding="utf-8",
    )


def main():
    _setup_firebird_dll()
    _start_firebird_service()
    base = _get_base_dir()

    os.environ["ECODATA_ROOT"] = str(base)
    os.environ["OUTPUT_DIR"] = str(base / "output")

    _create_dirs(base)
    _create_default_env(base)

    port = int(os.getenv("ECODATA_PORT", "8580"))

    webbrowser.open(f"http://localhost:{port}")

    from server.app import main as server_main
    server_main()


if __name__ == "__main__":
    main()
