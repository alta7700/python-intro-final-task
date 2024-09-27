import sys

import altair as alt
import pandas as pd

from config import Config
from helpers import FastQFileReader, QualityScoreHelper, AdapterCutter, FastQFileWriter
from utils import show_to_user


def run(config: Config):

    result_data = {"Имя файла": config.datafile.name}

    quality_helper = QualityScoreHelper(config.quality_type)
    with open(config.datafile) as f:
        reader = FastQFileReader(
            stream=f,
            quality_helper=quality_helper,
        )
        records = reader.get_all_records()

    if config.remove_adapters:
        records = records.cut(
            adapter_cutter=AdapterCutter(
                start_adapter=config.start_adapter,
                end_adapter=config.end_adapter,
                min_len=config.adapter_min_length,
            )
        )

        result_data["Количество записей с адаптерами"] = records.get_cut_records_count()
        result_data["Удалено адаптеров"] = records.get_cuts_count()

        fastq_filepath = config.output_dir / "cut_result.fastq"
        with open(fastq_filepath, "w", encoding="utf-8") as f_out:
            FastQFileWriter(f_out, quality_helper).write(records.records)
        show_to_user(f"\nСобран новый файл с удаленными адаптерами.\n{fastq_filepath.absolute().as_uri()}")

    result_data["Количество записей"] = records.count
    result_data["Самая часто встречающаяся длина последовательности"] = records.get_seq_len_moda()
    result_data["Средний GC в составе (%)"] = round(records.get_agv_cg_composition(), 2)

    comp = records.get_avg_nucleotide_composition()
    result_data["Ср. сод. A (%)"] = round(comp["A"], 2)
    result_data["Ср. сод. T (%)"] = round(comp["T"], 2)
    result_data["Ср. сод. G (%)"] = round(comp["G"], 2)
    result_data["Ср. сод. C (%)"] = round(comp["C"], 2)

    first_chart = (
        alt
        .Chart(pd.DataFrame(
            records.get_distinct_len(full_range=True),
            columns=["x", "y"]
        ))
        .mark_bar(size=5)
        .encode(
            x=alt.X("x:Q", title="Sequence length"),
            y=alt.Y("y:Q", title="Number of sequences"),
        ).properties(
            title="Sequence length distribution",
            width=400, height=300,
        )
    )

    second_chart = (
        alt
        .Chart(pd.DataFrame(
            records.get_distinct_gc_percentages(),
            columns=["x", "y"]
        ))
        .mark_bar(size=3)
        .encode(
            x=alt.X("x:Q", title="GC - composition (%)").axis(values=list(range(0, 101, 10))),
            y=alt.Y("y:Q", title="Number of sequences"),
        ).properties(
            title="GC - composition distribution",
            width=400, height=300,
        )
    )

    third_chart_df = pd.DataFrame(records.get_sequence_content_across_all_bases())\
        .melt("x", var_name="Line", value_name="Values")
    third_chart = (
        alt
        .Chart(third_chart_df)
        .mark_line(interpolate="linear")
        .encode(
            x=alt.X("x:Q", title="Position in read").axis(),
            y=alt.Y("Values:Q", title="Nucleotide (%)",
                    scale=alt.Scale(domainMax=third_chart_df["Values"].max() + 3)),
            color=alt.Color("Line:N", sort=("A", "T", "G", "C", "N")),
        ).properties(
            title="Sequence content across all bases",
            width=400, height=300,
        )
    )

    fourth_chart = (
        alt
        .Chart(pd.DataFrame(
            records.average_quality_per_read(),
            columns=["x", "y"]
        ))
        .mark_bar(size=3)
        .encode(
            x=alt.X("x:Q", title="Mean sequence quality (phred score)").axis(),
            y=alt.Y("y:Q", title="Number of sequences"),
        ).properties(
            title="Average quality per read",
            width=400, height=300,
        )
    )

    fives_chart_df = pd.DataFrame(records.quality_scores_across_all_bases(), columns=["x", "y"])
    fives_chart = (
        alt
        .Chart(fives_chart_df)
        .mark_line()
        .encode(
            x=alt.X("x:Q", title="Position in read"),
            y=alt.Y("y:Q", title="Quality score",
                    scale=alt.Scale(domain=[fives_chart_df["y"].min() - 1, fives_chart_df["y"].max() + 1])),
        ).properties(
            title="Quality scores across all bases",
            width=400, height=300,
        )
    )

    first_chart.save(config.output_dir / "chart1.png", ppi=config.charts_quality)
    second_chart.save(config.output_dir / "chart2.png", ppi=config.charts_quality)
    third_chart.save(config.output_dir / "chart3.png", ppi=config.charts_quality)
    fourth_chart.save(config.output_dir / "chart4.png", ppi=config.charts_quality)
    fives_chart.save(config.output_dir / "chart5.png", ppi=config.charts_quality)

    if config.subplot:
        save_path = config.output_dir / "charts.png"
        alt.vconcat(
            alt.hconcat(first_chart, second_chart, third_chart),
            alt.hconcat(fourth_chart, fives_chart),
        ).save(save_path, ppi=config.charts_quality)
    show_to_user(f"\nГрафики сохранены в папку:\n{config.output_dir.absolute().as_uri()}")

    columns = [
        "Имя файла",
        "Количество записей",
        "Количество записей с адаптерами",
        "Удалено адаптеров",
        "Самая часто встречающаяся длина последовательности",
        "Средний GC в составе (%)",
        "Ср. сод. A (%)",
        "Ср. сод. T (%)",
        "Ср. сод. G (%)",
        "Ср. сод. C (%)",
    ]
    df_path = config.output_dir.parent / "dataframe.csv"
    pd.DataFrame(
        [[result_data.get(name) for name in columns]],
        columns=columns,
    ).to_csv(df_path, sep=";", mode="a", header=not df_path.exists(), index=False)


if __name__ == "__main__":
    run(Config(sys.argv[1:]))
