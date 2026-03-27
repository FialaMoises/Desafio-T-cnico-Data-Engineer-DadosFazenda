import json
from pathlib import Path
from typing import Set


class CheckpointManager:
    def __init__(self, checkpoint_dir: Path):
        self.checkpoint_dir = checkpoint_dir

    def load(self, uf: str) -> Set[str]:
        path = self.checkpoint_dir / f"{uf}.json"
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            return set(data.get("concluidos", []))
        return set()

    def save(self, uf: str, concluidos: Set[str]) -> None:
        path = self.checkpoint_dir / f"{uf}.json"
        data = {"concluidos": sorted(concluidos)}
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
