from typing import Sequence


__all__ = ["QualityScoreHelper"]


class QualityScoreHelper:
    qs_types = {
        "Phred+33": 33,
        "Phred+64": 64,
    }

    def __init__(self, t: str):
        if t not in self.qs_types:
            raise Exception(f'Unknown quality score type: "{t}". Available types: {", ".join(self.qs_types.keys())}')
        self.offset: int = self.qs_types[t]

    def read(self, seq: Sequence[str]) -> tuple[int, ...]:
        return tuple(ord(char) - self.offset for char in seq)

    def write(self, seq: Sequence[int]) -> str:
        return "".join(chr(num + self.offset) for num in seq)
