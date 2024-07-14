from dataclasses import dataclass, asdict


@dataclass
class BaseEntity:
    def get_dict(self) -> dict:
        return asdict(self)
