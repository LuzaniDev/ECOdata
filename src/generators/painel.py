from datetime import datetime

import src.config as cfg
from src.generators.base import BaseGenerator
from src.utils.file_utils import format_text


class PainelGenerator(BaseGenerator):
    prefixo = "PAINEL"

    CABECALHO = [
        "CNPJ_Distribuidor",
        "CNPJ_Industria",
        "CNPJ_PDV",
        "Nivel_1_Codigo",
        "Nivel_1_Nome",
        "Nivel_1_Email",
        "Nivel_1_Celular",
    ]

    SQL = """
        select distinct
            EMP.CPFCNPJ,
            CLG.CPFCNPJ,
            CLI.VENDEDOR,
            VEND.NOME,
            VEND.EMAIL,
            VEND.CELULAR
        from TRECCLIENTE CLI
        inner join TRECCLIENTEGERAL CLG on CLG.CODIGO = CLI.CODIGO
        inner join TVENPEDIDO PED on PED.EMPRESA = CLI.EMPRESA and PED.CLIENTE = CLI.CODIGO
        inner join TVENPRODUTO PDV on PDV.EMPRESA = PED.EMPRESA and PDV.PEDIDO = PED.CODIGO
        inner join TESTPRODUTO PROD on PROD.EMPRESA = PED.EMPRESA and PROD.PRODUTO = PDV.PRODUTO
        left join TVENVENDEDOR VEND on VEND.EMPRESA = CLI.EMPRESA and VEND.CODIGO = CLI.VENDEDOR
        left join TGEREMPRESA EMP on EMP.CODIGO = CLI.EMPRESA
        where PROD.CNPJFABRICANTE = '16404287091959'
          and CLI.ATIVO = 'S'
          and CLG.CPFCNPJ is not null and CLG.CPFCNPJ <> ''
          and CLG.CPFCNPJ <> '88888888888'
          and PED.STATUS not in ('C', 'D')
          and CLI.EMPRESA = ?
    """

    def gerar_dados(self, conn, empresa: str = cfg.CODIGO_EMPRESA):
        cur = conn.cursor()
        cur.execute(self.SQL, (empresa,))

        linhas = []
        for row in cur.fetchall():
            (
                cnpj_dist,
                cnpj_pdv,
                cod_vendedor,
                nome_vendedor,
                email_vendedor,
                cel_vendedor,
            ) = row

            linha = [
                format_text(cnpj_dist, 14),
                "16404287091959",
                format_text(cnpj_pdv, 14),
                format_text(str(cod_vendedor or ""), 50),
                format_text(nome_vendedor, 255),
                format_text(email_vendedor, 255),
                format_text(cel_vendedor, 255),
            ]
            linhas.append(linha)

        if not linhas:
            print(f"  [AVISO] Nenhum cliente encontrado para empresa '{empresa}'.")

        return self.CABECALHO, linhas
