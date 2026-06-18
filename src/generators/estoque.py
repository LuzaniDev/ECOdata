"""
GERADOR DO TEMPLATE ESTOQUE
────────────────────────────
Gera o arquivo: ESTOQUE_V3_AAAAMMDDHHMMSS.txt

Colunas do template:
  CNPJ_Filial_Distribuidor | CNPJ_Industria | Data_Posicao | EAN | DUN |
  Cod_interno | Cod_Lote | Data_Validade | Nome_Produto | Unidade_Venda |
  Fator_Para_Pacote | Preco_Sku_TABELA | Preco_Sku_CUSTO |
  Estoque_Fisico | Estoque_Transito | Estoque_Faturado |
  Estoque_Avariado | Estoque_Reservado

Mapeamento com o banco:
  TESTESTOQUE (EST)
  TESTPRODUTO (PROD)
  TESTALMOX (ALM)
  TESTGRUPO (GRUPO)
  TESTSUBGRUPO (SUBG)
  TESTPRODUTOGERAL (PRODG)
  TESTMARCA (MARCA)
  TESTSETOR (SETOR)
  TESTFABRICANTE (FAB)
  TGEREMPRESA (EMP)
  TESTLOTEVALIDADEESTOQUE (LOTE) - opcional, para lote/validade

Campos sem equivalente direto:
  - Estoque_Faturado: nao existe no banco → enviar 0
  - Estoque_Avariado: nao existe no banco → enviar 0
"""

from datetime import datetime

import src.config as cfg
from src.generators.base import BaseGenerator
from src.utils.file_utils import format_decimal_br, format_int, format_text


class EstoqueGenerator(BaseGenerator):
    prefixo = "ESTOQUE"

    CABECALHO = [
        "CNPJ_Filial_Distribuidor",
        "CNPJ_Industria",
        "Data_Posicao",
        "EAN",
        "DUN",
        "Cod_interno",
        "Cod_Lote",
        "Data_Validade",
        "Nome_Produto",
        "Unidade_Venda",
        "Fator_Para_Pacote",
        "Preco_Sku_TABELA",
        "Preco_Sku_CUSTO",
        "Estoque_Fisico",
        "Estoque_Transito",
        "Estoque_Faturado",
        "Estoque_Avariado",
        "Estoque_Reservado",
    ]

    SQL = """
        select
            EMP.CPFCNPJ                                          as CNPJ_FILIAL,
            coalesce(PROD.CNPJFABRICANTE, '')                     as CNPJ_INDUSTRIA,
            PRODG.CODIGOBARRA                                     as EAN,
            coalesce(PRODG.CODIGOFABRICA, '')                     as DUN,
            PRODG.CODIGO                                          as COD_INTERNO,
            PRODG.DESCRICAO                                       as NOME_PRODUTO,
            PRODG.EMBALAGEM                                       as UNIDADE_VENDA,
            PRODG.QTDEEMBALAGEM                                   as FATOR_PACOTE,
            coalesce(PROD.PRPRATICADO, 0)                         as PRECO_TABELA,
            coalesce(PROD.CUSTOMEDIO, 0)                          as PRECO_CUSTO,
            coalesce(EST.ESTDISPONIVEL, 0)                        as EST_DISPONIVEL,
            coalesce(EST.ESTTRANSITO, 0)                          as EST_TRANSITO,
            coalesce(EST.ESTRESERVADO, 0)                         as EST_RESERVADO,
            coalesce(EST.ESTCONDICIONAL, 0)                       as EST_CONDICIONAL

        from TESTESTOQUE EST
        left join TESTPRODUTO PROD on
            PROD.EMPRESA = EST.EMPRESA and PROD.PRODUTO = EST.PRODUTO
        left join TESTPRODUTOGERAL PRODG on
            PRODG.CODIGO = PROD.PRODUTO
        left join TGEREMPRESA EMP on
            EMP.CODIGO = PROD.EMPRESA
        left join TESTALMOX ALM on
            EST.EMPRESA = ALM.EMPRESA and EST.ALMOX = ALM.CODIGO

        where PROD.ATIVO = 'S'
          and EST.EMPRESA = ?
          and PROD.cnpjfabricante = 16404287091959
    """

    def gerar_dados(self, conn, empresa: str = cfg.CODIGO_EMPRESA):
        cur = conn.cursor()
        cur.execute(self.SQL, (empresa,))

        data_posicao = datetime.now().strftime("%Y%m%d")
        linhas = []

        for row in cur.fetchall():
            (
                cnpj_filial,
                cnpj_industria,
                ean,
                dun,
                cod_interno,
                nome_produto,
                unidade_venda,
                fator_pacote,
                preco_tabela,
                preco_custo,
                est_disponivel,
                est_transito,
                est_reservado,
                est_condicional,
            ) = row

            if not ean or not ean.strip():
                continue

            qtde_emb = float(fator_pacote) if fator_pacote else 1
            if qtde_emb <= 0:
                qtde_emb = 1

            estoque_fisico = float(est_disponivel) / qtde_emb if est_disponivel else 0
            estoque_transito = float(est_transito) if est_transito else 0
            estoque_reservado = float(est_reservado) if est_reservado else 0

            linha = [
                format_text(cnpj_filial, 14),
                format_text(cnpj_industria, 14),
                data_posicao,
                format_text(ean, 50),
                format_text(dun, 50),
                format_text(cod_interno, 50),
                "",
                "",
                format_text(nome_produto, 255),
                format_text(unidade_venda, 2),
                format_int(qtde_emb),
                format_decimal_br(preco_tabela),
                format_decimal_br(preco_custo),
                format_decimal_br(estoque_fisico),
                format_decimal_br(estoque_transito),
                "0,00",
                "0,00",
                format_decimal_br(estoque_reservado),
            ]
            linhas.append(linha)

        return self.CABECALHO, linhas
