import hashlib
import io
import os
import time
import traceback
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime

import src.config as cfg
from server.core.debug_events import add_event
from server.core.log_core import add_log
from src.db import get_connection, get_empresa, release_connection
from src.generators.estoque import EstoqueGenerator
from src.generators.painel import PainelGenerator
from src.generators.sellout import SelloutGenerator


def run_generator(tipo: str, empresa: str = None, send_sftp: bool = True, primeiro_envio: bool = False):
    tipo = tipo.lower() if tipo else tipo
    output_capture = io.StringIO()
    start_time = time.time()
    result = {
        "tipo": tipo,
        "status": "running",
        "started_at": datetime.now(),
        "file_path": None,
        "rows_count": 0,
        "error_message": None,
        "output_log": "",
        "empresa_utilizada": None,
        "empresa_nome": None,
        "available_companies": None,
    }

    add_event("generator_step", {"tipo": tipo, "step": "iniciando", "empresa": empresa or cfg.CODIGO_EMPRESA}, "executor")

    try:
        with redirect_stdout(output_capture), redirect_stderr(output_capture):
            add_event("generator_step", {"tipo": tipo, "step": "conectando banco"}, "executor")
            conn = get_connection()
            empresa_info = get_empresa(conn, empresa or cfg.CODIGO_EMPRESA)
            empresa_cod = empresa or cfg.CODIGO_EMPRESA
            result["empresa_utilizada"] = empresa_cod
            result["empresa_nome"] = empresa_info["fantasia"] if empresa_info else None

            add_event("generator_step", {"tipo": tipo, "step": "conectado", "empresa": empresa_cod, "nome": empresa_info.get("fantasia") if empresa_info else None}, "executor")
            print(f"Conectado: {empresa_info['fantasia'] if empresa_info else empresa_cod}")

            arquivos_gerados = []

            if tipo in ("estoque", "todos"):
                add_event("generator_step", {"tipo": tipo, "step": "gerando estoque"}, "executor")
                print("\n[Gerando ESTOQUE]")
                gen = EstoqueGenerator()
                path = gen.gerar_arquivo(conn, empresa_cod)
                if path:
                    arquivos_gerados.append(path)
                    add_event("generator_step", {"tipo": tipo, "step": "estoque ok", "arquivo": os.path.basename(path)}, "executor")
                    print(f"  OK: {os.path.basename(path)}")
                else:
                    add_event("generator_step", {"tipo": tipo, "step": "estoque sem dados"}, "executor")
                    print("  [AVISO] Estoque: nenhum dado encontrado.")

            if tipo in ("sellout", "todos"):
                add_event("generator_step", {"tipo": tipo, "step": "gerando sellout"}, "executor")
                print("\n[Gerando SELLOUT]")
                gen = SelloutGenerator()
                path = gen.gerar_arquivo(conn, empresa_cod, primeiro_envio=primeiro_envio)
                if path:
                    arquivos_gerados.append(path)
                    add_event("generator_step", {"tipo": tipo, "step": "sellout ok", "arquivo": os.path.basename(path)}, "executor")
                    print(f"  OK: {os.path.basename(path)}")
                else:
                    add_event("generator_step", {"tipo": tipo, "step": "sellout sem dados"}, "executor")
                    print("  [AVISO] Sellout: nenhum dado encontrado.")
                if getattr(gen, 'available_companies', []):
                    result["available_companies"] = [
                        {"codigo": c, "nome": n} for c, n in gen.available_companies
                    ]
                    add_event("generator_step", {"tipo": tipo, "step": "empresas disponiveis", "empresas": result["available_companies"]}, "executor")

            if tipo in ("painel", "todos"):
                add_event("generator_step", {"tipo": tipo, "step": "gerando painel"}, "executor")
                print("\n[Gerando PAINEL]")
                gen = PainelGenerator()
                path = gen.gerar_arquivo(conn, empresa_cod)
                if path:
                    arquivos_gerados.append(path)
                    add_event("generator_step", {"tipo": tipo, "step": "painel ok", "arquivo": os.path.basename(path)}, "executor")
                    print(f"  OK: {os.path.basename(path)}")
                else:
                    add_event("generator_step", {"tipo": tipo, "step": "painel sem dados"}, "executor")
                    print("  [AVISO] Painel: nenhum dado encontrado.")

            duration = time.time() - start_time
            print(f"\nFinalizado em {duration:.2f}s")
            add_event("generator_step", {"tipo": tipo, "step": "finalizado", "duration_s": round(duration, 2)}, "executor")

    except Exception as e:
        result["status"] = "failed"
        result["error_message"] = str(e)
        tb = traceback.format_exc()
        add_event("error", {"message": str(e), "traceback": tb, "tipo": tipo}, "executor")
        print(f"\n[ERRO] {e}")
        add_log("ERROR", f"Execução {tipo} falhou: {result['error_message']}", "executor")
    finally:
        if "conn" in locals():
            release_connection(conn)

    result["duration_ms"] = int((time.time() - start_time) * 1000)
    result["output_log"] = output_capture.getvalue()

    if result["error_message"] is None:
        if arquivos_gerados:
            result["status"] = "success"
            result["file_path"] = arquivos_gerados[0]
            result["rows_count"] = len(arquivos_gerados)
        else:
            result["status"] = "warning"
        add_log(result["status"].upper(), f"Execução {tipo} concluída em {result['duration_ms']/1000:.1f}s", "executor")
    else:
        add_log("ERROR", f"Execução {tipo} falhou: {result['error_message']}", "executor")

    result["finished_at"] = datetime.now()

    if result["file_path"] and os.path.exists(result["file_path"]):
        result["file_size"] = os.path.getsize(result["file_path"])
        with open(result["file_path"], "rb") as f:
            result["file_hash"] = hashlib.md5(f.read()).hexdigest()

    return result