"""Testes dos formatadores e utilitarios."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.utils.file_utils import format_decimal_br, format_int, format_text


class TestFormatDecimalBr:
    def test_formata_valor_normal(self):
        assert format_decimal_br(1234.56) == "1.234,56"

    def test_formata_valor_inteiro(self):
        assert format_decimal_br(42) == "42,00"

    def test_formata_valor_zero(self):
        assert format_decimal_br(0) == "0,00"

    def test_formata_valor_none(self):
        assert format_decimal_br(None) == "0,00"

    def test_formata_valor_milhao(self):
        assert format_decimal_br(1000000.50) == "1.000.000,50"

    def test_formata_valor_negativo(self):
        assert format_decimal_br(-500.25) == "-500,25"

    def test_formata_string_invalida(self):
        assert format_decimal_br("nao_e_numero") == "0,00"


class TestFormatText:
    def test_texto_normal(self):
        assert format_text("hello", 10) == "hello"

    def test_texto_truncado(self):
        assert format_text("hello world", 5) == "hello"

    def test_texto_none(self):
        assert format_text(None, 10) == ""

    def test_texto_sem_tamanho_max(self):
        assert format_text("hello world", 0) == "hello world"

    def test_texto_com_espacos(self):
        assert format_text("  texto  ", 10) == "texto"


class TestFormatInt:
    def test_int_normal(self):
        assert format_int(42) == "42"

    def test_int_float(self):
        assert format_int(3.14) == "3"

    def test_int_none(self):
        assert format_int(None) == "0"

    def test_int_string_invalida(self):
        assert format_int("abc") == "0"

    def test_int_zero(self):
        assert format_int(0) == "0"
