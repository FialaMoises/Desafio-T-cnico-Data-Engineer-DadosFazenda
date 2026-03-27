import csv
from pathlib import Path
from typing import List, Dict


class CSVReader:
    @staticmethod
    def read(file_path: Path) -> List[Dict[str, str]]:
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return list(reader)
