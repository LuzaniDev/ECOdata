"""
GERADOR DO TEMPLATE PAINEL (HIERARQUIA COMERCIAL)
────────────────────────────────────────────────────
Gera o arquivo: PAINEL_V3_AAAAMMDDHHMMSS.txt

Colunas do template:
  CNPJ_Distribuidor | CNPJ_Industria | Cod_Divisao_Industria |
  CNPJ_PDV | Nivel_1_Codigo | Nivel_1_Nome | Nivel_1_Codigo_Fiscal |
  Nivel_1_Email | Nivel_1_Celular |
  Nivel_2_Codigo | Nivel_2_Nome | Nivel_2_Codigo_Fiscal |
  Nivel_2_Email | Nivel_2_Celular |
  Nivel_3_Codigo | Nivel_3_Nome | Nivel_3_Codigo_Fiscal |
  Nivel_3_Email | Nivel_3_Celular

Mapeamento com o banco:
  TRECCLIENTE (CLI)          - CPFCNPJ e vendedor do PDV (CNPJ_PDV)
  TRECCLIENTEGERAL (CLG)    - nome/fantasia do PDV
  TVENVENDEDOR (VEND)       - dados do vendedor (Nivel 1)
  TGEREMPRESA (EMP)         - CNPJ do distribuidor

Regras:
  - Apenas Nivel 1 (vendedor) e populado
  - Nivel 2 e Nivel 3 sao enviados com campos vazios
  - Clientes inativos sao excluidos (ATIVO = 'S')
  - Clientes sem vendedor sao enviados com campos Nivel_1 vazios
"""

import src.config as cfg
from src.generators.base import BaseGenerator
from src.utils.file_utils import format_text


class PainelGenerator(BaseGenerator):
    prefixo = "PAINEL"

    CABECALHO = [
        "CNPJ_Distribuidor",
        "CNPJ_Industria",
        "Cod_Divisao_Industria",
        "CNPJ_PDV",
        "Nivel_1_Codigo",
        "Nivel_1_Nome",
        "Nivel_1_Codigo_Fiscal",
        "Nivel_1_Email",
        "Nivel_1_Celular",
        "Nivel_2_Codigo",
        "Nivel_2_Nome",
        "Nivel_2_Codigo_Fiscal",
        "Nivel_2_Email",
        "Nivel_2_Celular",
        "Nivel_3_Codigo",
        "Nivel_3_Nome",
        "Nivel_3_Codigo_Fiscal",
        "Nivel_3_Email",
        "Nivel_3_Celular",
    ]

    SQL = """
        select
            EMP.CPFCNPJ                                           as CNPJ_DISTRIBUIDOR,
            coalesce(EMP.INDUSTRIA, EMP.CPFCNPJ)                  as CNPJ_INDUSTRIA,
            coalesce(CLI.VENDEDOR, '')                            as COD_VENDEDOR,
            coalesce(VEND.NOME, '')                               as NOME_VENDEDOR,
            coalesce(VEND.EMAIL, '')                              as EMAIL_VENDEDOR,
            coalesce(VEND.CELULAR, '')                            as CEL_VENDEDOR,
            coalesce(VEND.CPF, '')                                as CPF_VENDEDOR

        from TRECCLIENTE CLI
        left join TVENVENDEDOR VEND on
            VEND.EMPRESA = CLI.EMPRESA and VEND.CODIGO = CLI.VENDEDOR
        left join TGEREMPRESA EMP on
            EMP.CODIGO = CLI.EMPRESA

        where CLI.ATIVO = 'S'
          and CLI.EMPRESA = ?
    """

    def gerar_dados(self, conn, empresa: str = cfg.CODIGO_EMPRESA):
        cur = conn.cursor()
        cur.execute(self.SQL, (empresa,))

        linhas = []

        for row in cur.fetchall():
            (
                cnpj_dist,
                cnpj_industria,
                cod_vendedor,
                nome_vendedor,
                email_vendedor,
                cel_vendedor,
                cpf_vendedor,
            ) = row

            linha = [
                format_text(cnpj_dist, 14),
                format_text(cnpj_industria, 14),
                "",
                "65",
                format_text(cod_vendedor, 255),
                format_text(nome_vendedor, 255),
                format_text(cpf_vendedor, 255),
                format_text(email_vendedor, 255),
                format_text(cel_vendedor, 255),
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
            ]
            linhas.append(linha)

        return self.CABECALHO, linhas
