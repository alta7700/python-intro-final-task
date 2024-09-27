from typing import Sequence, TextIO

from .quality_score_reader import QualityScoreHelper
from .fastq_file_reader import FastQRecord


__all__ = ["FastQFileWriter"]


class FastQFileWriter:
    def __init__(
            self,
            stream: TextIO,
            quality_helper: QualityScoreHelper,
    ):
        assert stream.writable()
        self.stream = stream
        self.quality_helper = quality_helper

    def write(self, records: Sequence[FastQRecord]):
        for record in records:
            self.stream.write(record.to_fastq(self.quality_helper))
