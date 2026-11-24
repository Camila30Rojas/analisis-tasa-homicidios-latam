from pathlib import Path

import altair as alt
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "datos" / "crudo" / "homicidios_latam.xlsx"
OUTPUT_DIR = PROJECT_ROOT / "docs" / "graficos"
CHART_PATH = OUTPUT_DIR / "comparacion_ciudades.html"
SUMMARY_PATH = OUTPUT_DIR / "resumen_comparacion_ciudades.md"
CITY_COLUMN = "Ciudad (País)"
VALUE_COLUMN = "value"


def main() -> None:
    df = pd.read_excel(DATA_PATH, sheet_name="datos")
    df[VALUE_COLUMN] = pd.to_numeric(df[VALUE_COLUMN], errors="coerce")

    comparison = (
        df.dropna(subset=[CITY_COLUMN, VALUE_COLUMN])
        .groupby(CITY_COLUMN, as_index=False)[VALUE_COLUMN]
        .agg(promedio="mean", maximo="max", minimo="min")
        .sort_values("promedio", ascending=False)
    )

    if comparison.empty:
        raise ValueError("No hay datos validos para comparar las ciudades.")

    print("Comparacion de tasas de homicidios por ciudad:")
    print(
        comparison.to_string(
            index=False,
            formatters={
                "promedio": lambda value: f"{value:.4f}",
                "maximo": lambda value: f"{value:.4f}",
                "minimo": lambda value: f"{value:.4f}",
            },
        )
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    measures = comparison.melt(
        id_vars=CITY_COLUMN,
        value_vars=["promedio", "maximo", "minimo"],
        var_name="medida",
        value_name="tasa",
    )

    chart = (
        alt.Chart(measures)
        .mark_bar()
        .encode(
            x=alt.X(
                f"{CITY_COLUMN}:N",
                sort=comparison[CITY_COLUMN].tolist(),
                title="Ciudad",
            ),
            xOffset=alt.XOffset("medida:N"),
            y=alt.Y("tasa:Q", title="Tasa (por 100.000 habitantes)"),
            color=alt.Color(
                "medida:N",
                title="Medida",
                sort=["promedio", "maximo", "minimo"],
            ),
            tooltip=[
                alt.Tooltip(f"{CITY_COLUMN}:N", title="Ciudad"),
                alt.Tooltip("medida:N", title="Medida"),
                alt.Tooltip("tasa:Q", title="Tasa", format=".4f"),
            ],
        )
        .properties(
            title="Promedio, minimo y maximo de homicidios por ciudad",
            width=700,
            height=400,
        )
    )
    chart.save(CHART_PATH)

    highest_average = comparison.iloc[0]
    lowest_average = comparison.iloc[-1]
    widest_range_city = (
        comparison.assign(rango=comparison["maximo"] - comparison["minimo"])
        .sort_values("rango", ascending=False)
        .iloc[0]
    )

    result_lines = "\n".join(
        f"- {row[CITY_COLUMN]}: promedio {row['promedio']:.4f}, "
        f"maximo {row['maximo']:.4f}, minimo {row['minimo']:.4f}"
        for _, row in comparison.iterrows()
    )

    summary = (
        "# Comparacion de tasas de homicidios por ciudad\n\n"
        "## Resultados\n\n"
        f"{result_lines}\n\n"
        "## Conclusiones\n\n"
        f"- {highest_average[CITY_COLUMN]} tiene el promedio mas alto "
        f"({highest_average['promedio']:.4f}).\n"
        f"- {lowest_average[CITY_COLUMN]} tiene el promedio mas bajo "
        f"({lowest_average['promedio']:.4f}).\n"
        f"- La ciudad con mayor amplitud entre su minimo y su maximo es "
        f"{widest_range_city[CITY_COLUMN]}, con un rango de "
        f"{widest_range_city['rango']:.4f}.\n"
        "- Las barras permiten comparar simultaneamente el nivel promedio "
        "y los extremos observados en cada ciudad."
    )
    SUMMARY_PATH.write_text(summary, encoding="utf-8")

    print("\nConclusiones:")
    print(
        f"- {highest_average[CITY_COLUMN]} tiene el promedio mas alto "
        f"({highest_average['promedio']:.4f})."
    )
    print(
        f"- {lowest_average[CITY_COLUMN]} tiene el promedio mas bajo "
        f"({lowest_average['promedio']:.4f})."
    )
    print(
        f"- Mayor amplitud: {widest_range_city[CITY_COLUMN]} "
        f"(rango {widest_range_city['rango']:.4f})."
    )
    print(f"Grafico guardado en: {CHART_PATH}")
    print(f"Resultados guardados en: {SUMMARY_PATH}")


if __name__ == "__main__":
    main()
