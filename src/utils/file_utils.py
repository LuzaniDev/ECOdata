import os
from pathlib import Path


def format_decimal_br(valor) -> str:
    if valor is None:
        return "0,00"
    try:
        v = float(valor)
        return f"{v:.2f}".replace(".", ",")
    except (ValueError, TypeError):
        return "0,00"


def format_text(texto: str, tamanho_max: int = 0) -> str:
    if texto is None:
        return ""
    t = str(texto).strip()
    if tamanho_max > 0:
        t = t[:tamanho_max]
    return t


def format_int(valor) -> str:
    if valor is None:
        return "0"
    try:
        return str(int(valor))
    except (ValueError, TypeError):
        return "0"


def save_txt(filename: str, cabecalho: list, linhas: list, output_dir: str = "output"):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("|".join(cabecalho) + "\n")
        for linha in linhas:
            valores_str = [str(v) if v is not None else "" for v in linha]
            f.write("|".join(valores_str) + "\n")

    print(f"Arquivo gerado: {filepath} ({len(linhas)} linhas)")
    return filepath
