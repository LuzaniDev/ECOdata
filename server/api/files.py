import os
import csv
import io

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

router = APIRouter(prefix="/api/files", tags=["Files"])


class FileData(BaseModel):
    columns: list[str]
    rows: list[list[str]]


def _get_output_dir():
    d = os.getenv("OUTPUT_DIR") or os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "output"
    )
    return os.path.realpath(os.path.normpath(d))


def _is_safe_path(filepath: str, output_dir: str) -> bool:
    return os.path.realpath(filepath).startswith(os.path.realpath(output_dir) + os.sep)


def _parse_txt(filepath: str) -> tuple[list[str], list[list[str]]]:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read().strip()
    if not content:
        return [], []
    lines = content.split("\n")
    columns = lines[0].split("|")
    rows = [line.split("|") for line in lines[1:]]
    return columns, rows


@router.get("")
async def list_files():
    output_dir = _get_output_dir()
    if not os.path.exists(output_dir):
        return {"items": [], "total": 0}

    files = []
    for f in os.listdir(output_dir):
        if f.endswith(".txt"):
            filepath = os.path.join(output_dir, f)
            stat = os.stat(filepath)
            files.append({
                "name": f,
                "path": filepath,
                "size": stat.st_size,
                "modified": stat.st_mtime,
            })

    files.sort(key=lambda x: x["modified"], reverse=True)
    return {"items": files, "total": len(files)}


@router.get("/download/{filename}")
async def download_file(filename: str):
    output_dir = _get_output_dir()
    filepath = os.path.join(output_dir, filename)
    if not _is_safe_path(filepath, output_dir) or not os.path.isfile(filepath):
        raise HTTPException(404, "Arquivo não encontrado")
    return FileResponse(filepath, filename=filename)


@router.get("/{filename}/data")
async def get_file_data(filename: str):
    output_dir = _get_output_dir()
    filepath = os.path.join(output_dir, filename)
    if not _is_safe_path(filepath, output_dir) or not os.path.isfile(filepath):
        raise HTTPException(404, "Arquivo não encontrado")
    columns, rows = _parse_txt(filepath)
    return {"filename": filename, "columns": columns, "rows": rows, "total": len(rows)}


@router.put("/{filename}/data")
async def save_file_data(filename: str, data: FileData):
    output_dir = _get_output_dir()
    filepath = os.path.join(output_dir, filename)
    if not _is_safe_path(filepath, output_dir) or not os.path.isfile(filepath):
        raise HTTPException(404, "Arquivo não encontrado")
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("|".join(data.columns) + "\n")
            for row in data.rows:
                f.write("|".join(str(v) if v is not None else "" for v in row) + "\n")
        return {"message": "Arquivo salvo", "filename": filename, "rows": len(data.rows)}
    except Exception as e:
        raise HTTPException(500, f"Erro ao salvar: {e}")
