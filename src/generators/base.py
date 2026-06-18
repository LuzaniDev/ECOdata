from abc import ABC, abstractmethod

import src.config as cfg


class BaseGenerator(ABC):
    prefixo: str = ""

    @abstractmethod
    def gerar_dados(self, conn, empresa: str):
        ...

    def get_filename(self) -> str:
        return f"{self.prefixo}_V3_{cfg.get_timestamp()}.txt"

    def gerar_arquivo(self, conn, empresa: str, **kwargs):
        cabecalho, linhas = self.gerar_dados(conn, empresa, **kwargs)
        if not linhas:
            print(f"  [AVISO] {self.prefixo}: nenhum dado encontrado. Nenhum arquivo gerado.")
            return None

        import os
        from pathlib import Path

        filename = self.get_filename()
        Path(cfg.OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
        filepath = os.path.join(cfg.OUTPUT_DIR, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("|".join(cabecalho) + "\n")
            for linha in linhas:
                valores_str = [str(v) if v is not None else "" for v in linha]
                f.write("|".join(valores_str) + "\n")

        print(f"  -> {filepath} ({len(linhas)} linhas)")
        return filepath
