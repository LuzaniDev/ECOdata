"""
MODULO DE ENVIO VIA SFTP
─────────────────────────
Envia os arquivos gerados para o servidor da Tradefy.
Suporta retry com backoff exponencial e validacao de host key.
"""

import os
import time

import paramiko

import src.config as cfg

MAX_RETRIES = 3
BACKOFF_BASE = 1


def _upload_file(filepath: str, remote_path: str) -> bool:
    transport = paramiko.Transport((cfg.SFTP_HOST, cfg.SFTP_PORT))

    if cfg.SFTP_HOST_KEY:
        try:
            key = paramiko.RSAKey(data=cfg.SFTP_HOST_KEY.encode())
            transport.connect(username=cfg.SFTP_USER, password=cfg.SFTP_PASSWORD, hostkey=key)
        except paramiko.SSHException:
            key = paramiko.Ed25519Key(data=cfg.SFTP_HOST_KEY.encode())
            transport.connect(username=cfg.SFTP_USER, password=cfg.SFTP_PASSWORD, hostkey=key)
    else:
        transport.connect(username=cfg.SFTP_USER, password=cfg.SFTP_PASSWORD)

    sftp = paramiko.SFTPClient.from_transport(transport)
    try:
        sftp.put(filepath, remote_path)
    finally:
        sftp.close()
        transport.close()
    return True


def enviar_arquivo(filepath: str) -> bool:
    if not cfg.SFTP_USER:
        print("  [AVISO] SFTP_USER nao configurado. Pulando envio FTP.")
        return False

    if not os.path.exists(filepath):
        print(f"  [ERRO] Arquivo nao encontrado: {filepath}")
        return False

    remote_path = os.path.join(cfg.SFTP_REMOTE_DIR, os.path.basename(filepath))

    for tentativa in range(1, MAX_RETRIES + 1):
        try:
            _upload_file(filepath, remote_path)
            print(f"  -> Enviado para SFTP: {remote_path}")
            return True

        except Exception as e:
            print(f"  [ERRO] Tentativa {tentativa}/{MAX_RETRIES} falhou: {e}")
            if tentativa < MAX_RETRIES:
                wait = BACKOFF_BASE * (tentativa ** 2)
                print(f"  -> Nova tentativa em {wait}s...")
                time.sleep(wait)

    print(f"  [ERRO] Todas as {MAX_RETRIES} tentativas falharam.")
    return False
