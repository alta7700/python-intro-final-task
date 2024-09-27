import sys
from pathlib import Path

if len(sys.argv) < 2:
    print("Выберите команду для запуска: fastq, geo")

match sys.argv[1]:
    case "fastq":
        sys.path.append((Path(__file__).parent / "fastq_analyzer").absolute().as_posix())
        from fastq_analyzer.run import run
        from fastq_analyzer.config import Config
        run(Config(sys.argv[2:]))
    case "geo":
        urls = sys.argv[2:]
        if len(urls) == 0:
            print("Передайте хотя бы одну ссылку")
        else:
            from geo_perser import run
            for url in urls:
                print(url)
                run(url)
