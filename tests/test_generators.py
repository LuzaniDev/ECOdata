"""Testes dos generators com mock do Firebird."""

import os
import sys
from datetime import date
from unittest.mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.generators.estoque import EstoqueGenerator
from src.generators.painel import PainelGenerator
from src.generators.sellout import SelloutGenerator


def _make_conn():
    conn = MagicMock()
    cur = MagicMock()
    conn.cursor.return_value = cur
    return conn, cur


class TestEstoqueGenerator:
    def test_cabecalho_correto(self):
        gen = EstoqueGenerator()
        assert len(gen.CABECALHO) == 18
        assert gen.CABECALHO[0] == "CNPJ_Filial_Distribuidor"
        assert gen.prefixo == "ESTOQUE"

    def test_gerar_dados_com_linhas(self):
        conn, cur = _make_conn()
        cur.fetchall.return_value = [
            (
                "11222333000181",  # cnpj_filial
                "44555666000199",  # cnpj_industria
                "7891234560010",   # ean
                "12345",           # dun
                "PROD001",         # cod_interno
                "Produto Teste",   # nome
                "UN",              # unidade
                1,                 # fator
                10.50,             # preco_tabela
                7.30,              # preco_custo
                100,               # est_disponivel
                5,                 # est_transito
                2,                 # est_reservado
                0,                 # est_condicional
            )
        ]
        gen = EstoqueGenerator()
        cabecalho, linhas = gen.gerar_dados(conn, "01")
        assert len(linhas) == 1
        assert linhas[0][0] == "11222333000181"
        assert linhas[0][11] == "10,50"

    def test_ignora_produto_sem_ean(self):
        conn, cur = _make_conn()
        cur.fetchall.return_value = [
            ("11222333000181", "44555666000199", "", "", "", "", "UN", 1, 0, 0, 0, 0, 0, 0)
        ]
        gen = EstoqueGenerator()
        _, linhas = gen.gerar_dados(conn, "01")
        assert len(linhas) == 0


class TestSelloutGenerator:
    def test_cabecalho_correto(self):
        gen = SelloutGenerator()
        assert len(gen.CABECALHO) == 29
        assert gen.prefixo == "SELLOUT"

    def test_gerar_dados_venda_normal(self):
        conn, cur = _make_conn()
        cur.fetchall.return_value = [
            (
                "11222333000181", "44555666000199",
                date(2026, 6, 1), "NF123", "chave_nfe_123",
                "7891234560010", "PROD001", "Produto Teste",
                "UN", 1, 100.50, 10, 10.05, 5.0,
                "VEND001", "99888777000166", "Cliente Teste",
                "SAO PAULO", "01001000", "Rua Teste", "123",
                1001, date(2026, 5, 28), "F",
            )
        ]
        gen = SelloutGenerator()
        cabecalho, linhas = gen.gerar_dados(conn, "01")
        assert len(linhas) == 1
        assert linhas[0][10] == "F"  # tipo_documento

    def test_gerar_dados_devolucao(self):
        conn, cur = _make_conn()
        cur.fetchall.return_value = [
            (
                "11222333000181", "44555666000199",
                date(2026, 6, 1), "NF124", "chave_nfe_124",
                "7891234560010", "PROD001", "Produto Teste",
                "UN", 1, 100.50, 10, 10.05, 5.0,
                "VEND001", "99888777000166", "Cliente Teste",
                "SAO PAULO", "01001000", "Rua Teste", "123",
                1002, date(2026, 5, 28), "D",
            )
        ]
        gen = SelloutGenerator()
        cabecalho, linhas = gen.gerar_dados(conn, "01")
        assert len(linhas) == 1
        assert linhas[0][10] == "D"  # devolucao

    def test_lookback_configuravel(self):
        gen = SelloutGenerator()
        assert gen._get_lookback_days(0, False) == 30
        assert gen._get_lookback_days(0, True) == 400
        assert gen._get_lookback_days(45, False) == 45


class TestPainelGenerator:
    def test_cabecalho_correto(self):
        gen = PainelGenerator()
        assert len(gen.CABECALHO) == 19
        assert gen.prefixo == "PAINEL"

    def test_gerar_dados_com_vendedor(self):
        conn, cur = _make_conn()
        cur.fetchall.return_value = [
            (
                "11222333000181", "99888777000166",
                "VEND001", "Vendedor Um",
                "vendedor@teste.com", "11999999999", "12345678900",
            )
        ]
        gen = PainelGenerator()
        cabecalho, linhas = gen.gerar_dados(conn, "01")
        assert len(linhas) == 1
        assert linhas[0][0] == "11222333000181"
        assert linhas[0][1] == "99888777000166"
        assert linhas[0][3] == "65"
        assert linhas[0][4] == "VEND001"
        assert linhas[0][5] == "Vendedor Um"
        assert linhas[0][6] == "12345678900"
        assert linhas[0][7] == "vendedor@teste.com"
        assert linhas[0][8] == "11999999999"

    def test_ignora_pdv_sem_vendedor(self):
        conn, cur = _make_conn()
        cur.fetchall.return_value = [
            ("11222333000181", "99888777000166", "", "", "", "", "")
        ]
        gen = PainelGenerator()
        _, linhas = gen.gerar_dados(conn, "01")
        assert len(linhas) == 0
