#!/usr/bin/env python
r"""
╔══════════════════════════════════════════════════════════════╗
║             INTEGRACAO TRADEFY - GERADOR DE ARQUIVOS        ║
║                                                             ║
║  Gera os 3 arquivos diarios (SELLOUT, ESTOQUE, PAINEL)     ║
║  e envia via SFTP para o servidor da Tradefy.              ║
╚══════════════════════════════════════════════════════════════╝

Uso:
  python main.py                          # Executa rotina completa
  python main.py --tipo estoque           # Gera apenas ESTOQUE
  python main.py --tipo sellout           # Gera apenas SELLOUT
  python main.py --tipo painel            # Gera apenas PAINEL
  python main.py --primeiro-envio         # Gera com historico completo (Sellout)
  python main.py --sem-envio-fisico       # Gera arquivos sem enviar via SFTP
  python main.py --empresa 01             # Especifica qual empresa processar

Configuracao:
  As configuracoes de banco, FTP, etc. estao em src/config.py
  ou podem ser definidas via variaveis de ambiente.

  Exemplo de variaveis de ambiente:
    set DB_PATH=C:\Ecosis\dados\ECODADOS.ECO
    set CODIGO_EMPRESA=01
    set SFTP_USER=meuusuario
    set SFTP_PASSWORD=minhasenha
"""

import argparse
import sys
from datetime import datetime

import src.config as cfg
from src.db import get_connection, get_empresa, release_connection
from src.generators.estoque import EstoqueGenerator
from src.generators.painel import PainelGenerator
from src.generators.sellout import SelloutGenerator
from src.sftp import enviar_arquivo


def gerar_tudo(conn, empresa: str, primeiro_envio: bool = False, enviar_fisico: bool = True):
    """Gera todos os 3 templates e envia via SFTP."""

    print(f"\n{'='*60}")
    print("  INICIANDO ROTINA TRADEFY")
    print(f"  Empresa: {empresa}")
    print(f"  Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    if primeiro_envio:
        print("  Modo: PRIMEIRO ENVIO (historico completo)")
    else:
        print("  Modo: ROTINA DIARIA (ultimos 30 dias)")
    print(f"{'='*60}")

    arquivos_gerados = []

    # ────────────── 1. ESTOQUE ──────────────
    print("\n[1/3] Gerando ESTOQUE...")
    try:
        gen = EstoqueGenerator()
        path = gen.gerar_arquivo(conn, empresa)
        if path:
            arquivos_gerados.append(path)
    except Exception as e:
        print(f"  [ERRO] ESTOQUE: {e}")

    # ────────────── 2. SELLOUT ──────────────
    print("\n[2/3] Gerando SELLOUT...")
    try:
        gen = SelloutGenerator()
        path = gen.gerar_arquivo(conn, empresa, primeiro_envio=primeiro_envio)
        if path:
            arquivos_gerados.append(path)
    except Exception as e:
        print(f"  [ERRO] SELLOUT: {e}")

    # ────────────── 3. PAINEL ──────────────
    print("\n[3/3] Gerando PAINEL...")
    try:
        gen = PainelGenerator()
        path = gen.gerar_arquivo(conn, empresa)
        if path:
            arquivos_gerados.append(path)
    except Exception as e:
        print(f"  [ERRO] PAINEL: {e}")

    # ────────────── ENVIO SFTP ──────────────
    print(f"\n{'='*60}")
    if enviar_fisico:
        for arq in arquivos_gerados:
            enviar_arquivo(arq)
    else:
        print("  Envio SFTP desabilitado (--sem-envio-fisico)")
        print(f"  Arquivos salvos em: {cfg.OUTPUT_DIR}/")

    print(f"{'='*60}")
    print(f"  ROTINA FINALIZADA - {len(arquivos_gerados)} arquivo(s) gerado(s)")
    print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description="Integracao Tradefy")
    parser.add_argument(
        "--tipo",
        choices=["estoque", "sellout", "painel", "todos"],
        default="todos",
        help="Tipo de arquivo a gerar (default: todos)",
    )
    parser.add_argument(
        "--primeiro-envio",
        action="store_true",
        help="Habilita modo primeiro envio (historico completo de vendas)",
    )
    parser.add_argument(
        "--sem-envio-fisico",
        action="store_true",
        help="Gera arquivos sem enviar para o SFTP",
    )
    parser.add_argument(
        "--empresa",
        default=cfg.CODIGO_EMPRESA,
        help=f"Codigo da empresa (default: {cfg.CODIGO_EMPRESA})",
    )
    args = parser.parse_args()

    print("Conectando ao banco Firebird...")
    try:
        conn = get_connection()
        empresa_info = get_empresa(conn, args.empresa)
        if empresa_info:
            print(f"  Empresa: {empresa_info['fantasia']} (CNPJ: {empresa_info['cnpj']})")
        else:
            print(f"  [AVISO] Empresa {args.empresa} nao encontrada!")
        print("  Conectado!")
    except Exception as e:
        print(f"  [ERRO] Falha ao conectar no banco: {e}")
        sys.exit(1)

    try:
        if args.tipo == "todos":
            gerar_tudo(conn, args.empresa, args.primeiro_envio, not args.sem_envio_fisico)
        elif args.tipo == "estoque":
            print("\n[Gerando apenas ESTOQUE]")
            gen = EstoqueGenerator()
            path = gen.gerar_arquivo(conn, args.empresa)
            if path and not args.sem_envio_fisico:
                enviar_arquivo(path)
        elif args.tipo == "sellout":
            print("\n[Gerando apenas SELLOUT]")
            gen = SelloutGenerator()
            path = gen.gerar_arquivo(conn, args.empresa, primeiro_envio=args.primeiro_envio)
            if path and not args.sem_envio_fisico:
                enviar_arquivo(path)
        elif args.tipo == "painel":
            print("\n[Gerando apenas PAINEL]")
            gen = PainelGenerator()
            path = gen.gerar_arquivo(conn, args.empresa)
            if path and not args.sem_envio_fisico:
                enviar_arquivo(path)
    finally:
        release_connection(conn)


if __name__ == "__main__":
    main()
