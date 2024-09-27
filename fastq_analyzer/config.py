from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path

from utils import show_to_user


class Config:
    _data_dir: Path
    _filename: Path

    _output_dir: Path

    remove_adapters: bool
    adapter_min_length: int
    _adapter: str | None
    _start_adapter: str | None
    _end_adapter: str | None
    quality_type: str

    charts_quality: int
    subplot: bool

    def __init__(self, args: list[str]):
        self.parser = ArgumentParser()
        self.add_args()
        self.parse(args)

    def add_args(self):
        self.parser.add_argument(
            "--data-dir", "-d", type=Path,
            default=Path(__file__).parent / "data",
            help="Папка с исходными данными",
        )
        self.parser.add_argument(
            "--filename", "-n", type=Path,
            required=True,
            help="Имя файла в папке с исходными данными",
        )

        self.parser.add_argument(
            "--output-dir", type=Path,
            default=Path(__file__).parent / "output",
            help="Папка с выводными данными",
        )

        self.parser.add_argument(
            "--remove-adapters", "-ra", type=int, default=None,
            help="Размер минимального вхождения адаптерной последовательности. "
                 "Если установлено, то будут удаляться адаптерные последовательности."
        )
        self.parser.add_argument(
            "--adapter", "-a", type=Path,
            default=Path("adapter.txt"),
            help="Имя файла со стандартной адаптерной последовательностью",
        )
        self.parser.add_argument(
            "--adapter-seq", type=str,
            default=None,
            help="Стандартная адаптерная последовательность"
        )
        self.parser.add_argument(
            "--start-adapter", type=Path,
            default=Path("start-adapter.txt"),
            help="Имя файла со стартовой адаптерной последовательностью",
        )
        self.parser.add_argument(
            "--start-adapter-seq", type=str,
            default=None,
            help="Стартовая адаптерная последовательность",
        )
        self.parser.add_argument(
            "--end-adapter", type=Path,
            default=Path("end-adapter.txt"),
            help="Имя файла со концевой адаптерной последовательностью",
        )
        self.parser.add_argument(
            "--end-adapter-seq", type=str,
            default=None,
            help="Концевая адаптерная последовательность",
        )

        self.parser.add_argument(
            "--quality-type", "-sq", choices=["Phred+33", "Phred+64"],
            default="Phred+33",
            help="Формат записи качества секвенирования"
        )

        self.parser.add_argument(
            "--charts-quality", "-cq", type=int,
            default=300,
            help="Качество графиков в dpi",
        )
        self.parser.add_argument(
            "--subplot", action="store_true",
            help="Объединить графики на одно полотно"
        )

    def parse(self, args: list[str]):
        args = self.parser.parse_args(args)
        self._data_dir = args.data_dir
        self._filename = args.filename

        self._output_dir = args.output_dir

        self.remove_adapters = args.remove_adapters is not None
        if self.remove_adapters:
            if args.remove_adapters < 3:
                self.adapter_min_length = 3
                show_to_user(
                    f"Минимальная длина адаптера 3. "
                    f"Установлено значение 3 вместо введенного {args.remove_adapters}"
                )
            else:
                self.adapter_min_length = args.remove_adapters
        else:
            self.adapter_min_length = 0

        self._adapter = \
            args.adapter_seq if args.adapter_seq is not None else self.get_file_content(args.adapter)
        self._start_adapter = \
            args.start_adapter_seq if args.start_adapter_seq is not None else self.get_file_content(args.start_adapter)
        self._end_adapter = \
            args.end_adapter_seq if args.end_adapter_seq is not None else self.get_file_content(args.end_adapter)

        self.quality_type = args.quality_type

        if args.charts_quality < 0:
            show_to_user("Качество графиков должно быть положительным числом. По умолчению установлено 300.")
            self.charts_quality = 300
        else:
            self.charts_quality = args.charts_quality
        self.subplot = args.subplot

    def get_file_content(self, path: Path) -> str | None:
        res_path = self._data_dir / path
        if not res_path.exists():
            return None
        assert res_path.is_file()
        return res_path.read_text().strip()

    @property
    def datafile(self):
        return Path(self._data_dir) / self._filename

    @property
    def start_adapter(self):
        value = self._start_adapter or self._adapter
        assert value, "Start adapter is not set"
        return value

    @property
    def end_adapter(self):
        value = self._end_adapter or self._adapter
        assert value, "End adapter is not set"
        return value

    @property
    def output_dir(self) -> Path:
        if not hasattr(self, "_calc_output_dir"):
            path = self._output_dir / f"{datetime.now().timestamp()}-{self.datafile.name.rstrip(".fastq")}"
            if not path.exists():
                path.mkdir(parents=True)
            setattr(self, "_calc_output_dir", path)
        return getattr(self, "_calc_output_dir")
