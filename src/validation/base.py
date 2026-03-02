from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class Validator:
    def validate(self, dataset_path: Path) -> ValidationResult:
        raise NotImplementedError
