import json
from pathlib import Path
from extractor.domain.entities import ExtracaoMetadata


class MetadataWriter:
    def __init__(self, log_dir: Path):
        self.log_file = log_dir / "metadata.jsonl"

    def append(self, metadata: ExtracaoMetadata) -> None:
        record = {
            "timestamp": metadata.timestamp.isoformat(),
            "uf": metadata.uf,
            "municipio": metadata.municipio,
            "total_registros": metadata.total_registros,
            "arquivo": metadata.arquivo,
            "duracao_segundos": round(metadata.duracao_segundos, 2),
            "status": metadata.status,
        }
        if metadata.erro:
            record["erro"] = metadata.erro

        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
