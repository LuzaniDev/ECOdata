"""
GERADOR DO TEMPLATE SELLOUT
─────────────────────────────
Gera o arquivo: SELLOUT_V3_AAAAMMDDHHMMSS.txt

Colunas do template:
  CNPJ_Filial_Distribuidor | CNPJ_Industria | Data_Nota_Fiscal |
  Numero_Nota_Fiscal | Chave_NFE | EAN | Cod_interno | Nome_Produto |
  Unidade_Venda | Fator_Para_Pacote | Tipo_Documento | Tipo_Envio |
  VendaValorBruta | VendaValorLiquida | VendaUnidades | Preco_Sku_NF |
  Canal_Venda | Cod_Vendedor_Hierarquia | Cod_Fiscal_Vendedor |
  CNPJ_PDV | Formato_PDV | Razao_Social | UF | Municipio | CEP |
  Endereco | Numero | Cod_Pedido | Data_Pedido

Mapeamento com o banco:
  TVENPEDIDO (PED)     - dados do pedido/nota fiscal
  TVENPRODUTO (PDV)    - itens do pedido
  TRECCLIENTE (CLI)    - CPFCNPJ do cliente
  TRECCLIENTEGERAL (CLG) - dados cadastrais do cliente
  TESTPRODUTOGERAL (PRD) - dados do produto
  TESTPRODUTO (PRO)    - CNPJFABRICANTE da industria
  TGEREMPRESA (EMP)    - CNPJ do distribuidor
  TVENVENDEDOR (VEN)   - dados do vendedor

De-Para Formato_PDV (conforme documentacao Tradefy):
  65 = Distribuidor Especializado (produtos de limpeza)

Fluxo de dados:
  - Primeiro envio: historico de janeiro do ano anterior ate a data atual
  - Rotina diaria: venda do dia + ultimos 30 dias
"""

from datetime import date, timedelta

import src.config as cfg
from src.generators.base import BaseGenerator
from src.utils.file_utils import format_decimal_br, format_int, format_text


class SelloutGenerator(BaseGenerator):
    prefixo = "SELLOUT"

    def __init__(self):
        self.available_companies: list[tuple[str, str]] = []

    CABECALHO = [
        "CNPJ_Filial_Distribuidor",
        "CNPJ_Industria",
        "Data_Nota_Fiscal",
        "Numero_Nota_Fiscal",
        "Chave_NFE",
        "EAN",
        "Cod_interno",
        "Nome_Produto",
        "Unidade_Venda",
        "Fator_Para_Pacote",
        "Tipo_Documento",
        "Tipo_Envio",
        "VendaValorBruta",
        "VendaValorLiquida",
        "VendaUnidades",
        "Preco_Sku_NF",
        "Canal_Venda",
        "Cod_Vendedor_Hierarquia",
        "Cod_Fiscal_Vendedor",
        "CNPJ_PDV",
        "Formato_PDV",
        "Razao_Social",
        "UF",
        "Municipio",
        "CEP",
        "Endereco",
        "Numero",
        "Cod_Pedido",
        "Data_Pedido",
    ]

    SQL = """
        select
            EMP.CPFCNPJ                                            as CNPJ_DISTRIBUIDOR,
            coalesce(PRO.CNPJFABRICANTE, '')                       as CNPJ_INDUSTRIA,
            coalesce(PED.NFDATA, PED.DATAEFE)                     as DATA_NF,
            coalesce(PED.NOTAFISCAL, PED.CODIGO)                   as NUMERO_NF,
            coalesce(PED.CHAVENFECLIENTE, '')                      as CHAVE_NFE,
            coalesce(PRD.CODIGOBARRA, '')                          as EAN,
            coalesce(PRD.CODIGO, '')                               as COD_INTERNO,
            CASE
                WHEN PRD.produtograde is not null THEN PRD.descricaograde
                WHEN PDV.produtogenerico = 'S' THEN PDV.descricaoeditada
                ELSE PRD.DESCRICAO
            END                                                    as NOME_PRODUTO,
            coalesce(PRD.EMBALAGEM, 'UN')                          as UNIDADE_VENDA,
            coalesce(PRD.QTDEEMBALAGEM, 1)                         as FATOR_PACOTE,
            coalesce(PDV.VLRLIQUIDO, 0)                            as VALOR_LIQUIDO,
            coalesce(PDV.QTDE, 0)                                  as QTDE,
            coalesce(PDV.PRVENDIDO, 0)                             as PRECO_UNITARIO,
            coalesce(PDV.PERCDESC, 0)                              as PERC_DESCONTO,
            coalesce(PED.VENDEDOR, '')                             as COD_VENDEDOR,
            coalesce(CLI.CPFCNPJ, '')                              as CNPJ_PDV,
            coalesce(CLG.NOME, '')                                 as RAZAO_SOCIAL,
            coalesce(CLG.CIDADE, '')                              as CIDADE,
            coalesce(CLG.CEP, '')                                  as CEP,
            coalesce(CLG.ENDERECO, '')                             as ENDERECO,
            coalesce(CLG.NUMEROENDERECO, '')                       as NUMERO,
            PED.CODIGO                                             as COD_PEDIDO,
            coalesce(PED.DATAEFE, PED.DATA)                        as DATA_PEDIDO,
            coalesce(PDV.TIPOVENDA, 'F')                           as TIPO_VENDA

        from TVENPEDIDO PED
        inner join TVENPRODUTO PDV on
            PDV.EMPRESA = PED.EMPRESA and PDV.PEDIDO = PED.CODIGO
        left join TRECCLIENTE CLI on
            CLI.EMPRESA = PED.EMPRESA and CLI.CODIGO = PED.CLIENTE
        left join TRECCLIENTEGERAL CLG on
            CLG.CODIGO = PED.CLIENTE
        left join TESTPRODUTOGERAL PRD on
            PRD.CODIGO = PDV.PRODUTO
        left join TESTPRODUTO PRO on
            PRO.EMPRESA = PED.EMPRESA and PRO.PRODUTO = PDV.PRODUTO
        left join TGEREMPRESA EMP on
            EMP.CODIGO = PED.EMPRESA
        left join TVENVENDEDOR VEN on
            VEN.EMPRESA = PED.EMPRESA and VEN.CODIGO = PED.VENDEDOR

        where PED.STATUS not in ('C', 'D')
          and PED.EMPRESA = ?
          and PED.DATAEFE >= ?
          and coalesce(PDV.PRODUTOGARANTIA, 'N') <> 'S'
          and PRO.CNPJFABRICANTE = 16404287091959
    """

    def _get_lookback_days(self, dias_retroceder: int, primeiro_envio: bool = False) -> int:
        if dias_retroceder > 0:
            return dias_retroceder
        if primeiro_envio:
            return 400
        return 90

    def _empresas_com_dados(self, conn) -> list[tuple[str, str]]:
        cur = conn.cursor()
        cur.execute("""
            select distinct PED.EMPRESA, coalesce(EMP.NOMEFANTASIA, '')
            from TVENPEDIDO PED
            left join TGEREMPRESA EMP on EMP.CODIGO = PED.EMPRESA
            where PED.STATUS not in ('C', 'D')
              and coalesce(PED.DATAEFE, PED.DATA) >= ?
            order by 1
        """, (date.today() - timedelta(days=400),))
        return [(r[0].strip(), r[1].strip()) for r in cur.fetchall()]

    def gerar_dados(self, conn, empresa: str = cfg.CODIGO_EMPRESA,
                    dias_retroceder: int = 0, primeiro_envio: bool = False):
        """dias_retroceder: quantidade de dias para buscar historico.
        0 = usa config lookback_daily_days (ou 30 se nao configurado).
        primeiro_envio = True usa lookback de 400 dias.
        """
        dias = self._get_lookback_days(dias_retroceder, primeiro_envio)
        data_inicio = date.today() - timedelta(days=dias)

        cur = conn.cursor()
        cur.execute(self.SQL, (empresa, data_inicio))

        rows = cur.fetchall()

        if not rows:
            print(f"  [AVISO] Nenhum pedido encontrado para empresa '{empresa}' nos ultimos {dias} dias.")
            self.available_companies = self._empresas_com_dados(conn)
            if self.available_companies:
                print(f"  [INFO] Empresas com dados de venda disponiveis (ultimos 400 dias):")
                for cod, nome in self.available_companies:
                    print(f"         -> Codigo '{cod}': {nome}")
                print(f"  [INFO] Altere CODIGO_EMPRESA no .env ou execute com --empresa <codigo>")
            else:
                print(f"  [INFO] Nenhuma empresa possui dados de venda no banco.")
            return self.CABECALHO, []

        linhas = []
        for row in rows:
            (
                cnpj_dist,
                cnpj_industria,
                data_nf,
                numero_nf,
                chave_nfe,
                ean,
                cod_interno,
                nome_produto,
                unidade_venda,
                fator_pacote,
                valor_liquido,
                qtde,
                preco_unitario,
                perc_desconto,
                cod_vendedor,
                cnpj_pdv,
                razao_social,
                cidade,
                cep,
                endereco,
                numero,
                cod_pedido,
                data_pedido,
                tipo_venda,
            ) = row

            if not ean or not ean.strip():
                continue

            eh_devolucao = tipo_venda and tipo_venda.upper() == 'D'

            fator = float(fator_pacote) if fator_pacote else 1
            if fator <= 0:
                fator = 1

            qtde_float = float(qtde) if qtde else 0
            vl_liquido = float(valor_liquido) if valor_liquido else 0
            preco_unit = float(preco_unitario) if preco_unitario else 0
            float(perc_desconto) if perc_desconto else 0

            if eh_devolucao:
                qtde_float = qtde_float * -1
                vl_liquido = vl_liquido * -1

            valor_bruto = preco_unit * abs(qtde_float)
            if eh_devolucao:
                valor_bruto = valor_bruto * -1

            data_nf_str = ""
            if data_nf:
                data_nf_str = data_nf.strftime("%Y%m%d") if hasattr(data_nf, "strftime") else str(data_nf)[:8]

            data_pedido_str = ""
            if data_pedido:
                if hasattr(data_pedido, "strftime"):
                    data_pedido_str = data_pedido.strftime("%Y%m%d")
                else:
                    data_pedido_str = str(data_pedido)[:8]

            tipo_documento = "D" if eh_devolucao else "F"

            linha = [
                format_text(cnpj_dist, 14),
                format_text(cnpj_industria, 14),
                data_nf_str,
                format_text(str(numero_nf), 50),
                format_text(chave_nfe, 44),
                format_text(ean, 50),
                format_text(cod_interno, 50),
                format_text(nome_produto, 255),
                format_text(unidade_venda, 2),
                format_int(fator),
                format_text(tipo_documento, 2),
                "R",
                format_decimal_br(valor_bruto),
                format_decimal_br(vl_liquido),
                format_decimal_br(abs(qtde_float)),
                format_decimal_br(abs(preco_unit)),
                "1",
                format_text(cod_vendedor, 50),
                "",
                format_text(cnpj_pdv, 14),
                "65",
                format_text(razao_social, 255),
                format_text(cidade, 50),
                format_text(cep, 9),
                format_text(endereco, 255),
                format_text(str(numero), 50),
                format_text(str(cod_pedido), 255),
                data_pedido_str,
            ]
            linhas.append(linha)

        return self.CABECALHO, linhas
