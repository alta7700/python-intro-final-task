from typing import Iterator, TextIO, TYPE_CHECKING, Literal, Self

if TYPE_CHECKING:
    from .quality_score_reader import QualityScoreHelper
    from .adapter_cutter import AdapterCutter


__all__ = ["FastQFileReader", "FastQRecord", "FastQRecordCollection"]


class FastQFileReader:

    def __init__(
            self,
            stream: TextIO,
            quality_helper: "QualityScoreHelper",
    ):
        assert stream.readable()
        self.stream = stream
        self.quality_helper = quality_helper

    @property
    def closed(self):
        return self.stream.closed

    def __iter__(self) -> Iterator["FastQRecord"]:
        return self

    def __next__(self) -> "FastQRecord":
        head = self._get_line()
        seq = self._get_line()
        _sep = self._get_line()
        quality_string = self._get_line()
        if any(s is None for s in (head, seq, _sep, quality_string)):
            self.stream.seek(0)
            raise StopIteration
        if not head.startswith("@"):
            raise Exception(f"Record is formatted incorrectly\n{head}\n{seq}\n{_sep}\n{quality_string}\n")

        return FastQRecord(
            head=head,
            seq=seq,
            quality=self.quality_helper.read(seq=quality_string),
        )

    def _get_line(self) -> str | None:
        line = self.stream.readline()
        if '\n' not in line:
            return None
        line = line.strip("\n")
        if len(line) == 0:
            return self._get_line()
        return line

    def get_all_records(self) -> "FastQRecordCollection":
        return FastQRecordCollection([record for record in self])


class FastQRecord:
    def __init__(
            self,
            head: str,
            seq: str,
            quality: tuple[int, ...],
            cut_start: int | None = None,
            cut_end: int | None = None,
    ):
        self.head = head
        self.seq = seq
        self.quality = quality
        self.cut_start = cut_start
        self.cut_end = cut_end

    @property
    def cuts_count(self) -> int:
        return (self.cut_start is not None) + (self.cut_end is not None)

    def cut(self, adapter_cutter: "AdapterCutter") -> Self:
        cut_start, cut_end = adapter_cutter.get_cut_points(self.seq)
        return FastQRecord(
            head=self.head,
            seq=self.seq[cut_start:cut_end],
            quality=self.quality[cut_start:cut_end],
            cut_start=cut_start,
            cut_end=cut_end,
        )

    def get_seq_len(self):
        return len(self.seq)

    def get_nucleotides_percentage(self, nucleotide: Literal["A", "T", "G", "C"]):
        seq: str = self.seq
        return seq.count(nucleotide) / len(seq) * 100

    def to_fastq(self, quality_helper: "QualityScoreHelper"):
        return "\n".join((
            self.head,
            self.seq,
            "+",
            quality_helper.write(self.quality),
        )) + "\n"


class FastQRecordCollection:
    def __init__(self, records: list[FastQRecord]) -> None:
        self.records = records

    def __iter__(self):
        return self.records.__iter__()

    @property
    def count(self) -> int:
        return len(self.records)

    def get_seq_len_moda(self) -> int:
        values = [rec.get_seq_len() for rec in self.records]
        return max(set(values), key=values.count)

    def get_agv_cg_composition(self) -> float:
        return sum(
            rec.get_nucleotides_percentage("G")
            + rec.get_nucleotides_percentage("C")
            for rec in self.records
        ) / self.count

    def get_avg_nucleotide_composition(self) -> dict[str, float]:
        count = self.count
        return {
            "A": sum(rec.get_nucleotides_percentage("A") for rec in self.records) / count,
            "T": sum(rec.get_nucleotides_percentage("T") for rec in self.records) / count,
            "G": sum(rec.get_nucleotides_percentage("G") for rec in self.records) / count,
            "C": sum(rec.get_nucleotides_percentage("C") for rec in self.records) / count,
        }

    def get_cuts_count(self):
        return sum(rec.cuts_count for rec in self.records)

    def get_cut_records_count(self):
        return sum(rec.cuts_count > 0 for rec in self.records)

    def cut(self, adapter_cutter: "AdapterCutter"):
        return FastQRecordCollection([rec.cut(adapter_cutter) for rec in self.records])

    def get_distinct_len(self, full_range: bool = False):
        records_lens = [rec.get_seq_len() for rec in self.records]
        if full_range:
            r = range(min(records_lens), max(records_lens) + 1)
            return list(zip(r, map(records_lens.count, r)))
        else:
            unique_records_lens = set(records_lens)
            return sorted(zip(unique_records_lens, map(records_lens.count, unique_records_lens)))

    def get_distinct_gc_percentages(self):
        values = [
            round(rec.get_nucleotides_percentage("G") + rec.get_nucleotides_percentage("C"))
            for rec in self.records
        ]
        return list(zip(range(1, 101), map(values.count, range(1, 101))))

    def get_sequence_content_across_all_bases(self):
        res = tuple(
            {"A": 0, "T": 0, "G": 0, "C": 0, "N": 0}
            for _ in range(max(rec.get_seq_len() for rec in self.records))
        )
        for rec in self.records:
            for i, n in enumerate(rec.seq):
                res[i][n] += 1
        for pos in res:
            pos["sum"] = sum(pos.values())

        return {
            "x": range(1, len(res) + 1),
            "A": [pos["A"] / pos["sum"] * 100 for pos in res],
            "T": [pos["T"] / pos["sum"] * 100 for pos in res],
            "G": [pos["G"] / pos["sum"] * 100 for pos in res],
            "C": [pos["C"] / pos["sum"] * 100 for pos in res],
            "N": [pos["N"] / pos["sum"] * 100 for pos in res],
        }

    def average_quality_per_read(self):
        # умножаем на 5 чтобы удобнее было работать с range
        # небольшой хак, чтобы получить step=0.2 :)
        values = [
            round(sum(rec.quality) / len(rec.quality) * 5)
            for rec in self.records
        ]
        r = range(min(values), max(values) + 1)
        return list(zip((v / 5 for v in r), map(values.count, r)))

    def quality_scores_across_all_bases(self):
        res: tuple[list[int], ...] = tuple([] for _ in range(max(rec.get_seq_len() for rec in self.records)))

        for rec in self.records:
            for i, q in enumerate(rec.quality):
                res[i].append(q)

        return tuple((i, sum(pos) / len(pos)) for i, pos in enumerate(res))
