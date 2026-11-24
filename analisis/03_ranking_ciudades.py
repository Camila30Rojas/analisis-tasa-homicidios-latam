from pathlib import Path

import altair as alt
import pandas as pd

from esquema_colores import CITY_COLUMN


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "datos" / "crudo" / "homicidios_latam.xlsx"
OUTPUT_DIR = PROJECT_ROOT / "docs" / "graficos"
CHART_PATH = OUTPUT_DIR / "ranking_ciudades.html"
SUMMARY_PATH = OUTPUT_DIR / "resumen_ranking_ciudades.md"
VALUE_COLUMN = "value"


def main() -> None:
    df = pd.read_excel(DATA_PATH, sheet_name="datos")
    df[VALUE_COLUMN] = pd.to_numeric(df[VALUE_COLUMN], errors="coerce")

    ranking = (
        df.dropna(subset=[CITY_COLUMN, VALUE_COLUMN])
        .groupby(CITY_COLUMN, as_index=False)[VALUE_COLUMN]
        .mean()
        .rename(columns={VALUE_COLUMN: "tasa_promedio"})
        .sort_values("tasa_promedio", ascending=False)
    )

    if ranking.empty:
        raise ValueError("No hay datos validos para calcular el ranking por ciudad.")

    print("Tasa promedio de homicidios por ciudad:")
    print(
        ranking.to_string(
            index=False,
            formatters={"tasa_promedio": lambda value: f"{value:.4f}"},
        )
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    chart = (
        alt.Chart(ranking)
        .mark_bar()
        .encode(
            x=alt.X(
                "tasa_promedio:Q",
                title="Tasa promedio (por 100.000 habitantes)",
            ),
            y=alt.Y(
                f"{CITY_COLUMN}:N",
                sort="-x",
                title="Ciudad",
            ),
            color=alt.Color(
                "Ciudad (País):N",
                scale=alt.Scale(
                    domain=[
                        "MONTEVIDEO - DEPARTAMENTO (URUGUAY)",
                        "MÉXICO D.F. (MÉXICO)",
                        "MUNICIPIO DE SAO PAULO (BRASIL)",
                    ],
                    range=[
                        "#0B5563",
                        "#1D70A2",
                        "#8ECAE6",
                    ],
                ),
                legend=alt.Legend(title="Ciudad"),
            ),
            tooltip=[
                alt.Tooltip(f"{CITY_COLUMN}:N", title="Ciudad"),
                alt.Tooltip(
                    "tasa_promedio:Q",
                    title="Tasa promedio",
                    format=".4f",
                ),
            ],
        )
        .properties(
            title="Ranking de ciudades segun tasa promedio de homicidios",
            width=700,
            height=300,
        )
    )
    chart.save(CHART_PATH)

    highest = ranking.iloc[0]
    lowest = ranking.iloc[-1]
    difference = highest["tasa_promedio"] - lowest["tasa_promedio"]

    ranking_lines = "\n".join(
        f"{position}. {row[CITY_COLUMN]}: {row['tasa_promedio']:.4f}"
        for position, (_, row) in enumerate(ranking.iterrows(), start=1)
    )

    summary = (
        "# Ranking de tasas promedio por ciudad\n\n"
        "## Resultados\n\n"
        f"{ranking_lines}\n\n"
        "## Interpretacion\n\n"
        f"La ciudad con la tasa promedio mas alta es "
        f"{highest[CITY_COLUMN]}, con {highest['tasa_promedio']:.4f} "
        "homicidios por 100.000 habitantes. "
        f"La tasa promedio mas baja corresponde a "
        f"{lowest[CITY_COLUMN]}, con {lowest['tasa_promedio']:.4f}. "
        f"La diferencia entre ambas es {difference:.4f}."
    )
    SUMMARY_PATH.write_text(summary, encoding="utf-8")

    print("\nInterpretacion:")
    print(
        f"{highest[CITY_COLUMN]} presenta la tasa promedio mas alta "
        f"({highest['tasa_promedio']:.4f}); "
        f"{lowest[CITY_COLUMN]} presenta la mas baja "
        f"({lowest['tasa_promedio']:.4f}). "
        f"Diferencia: {difference:.4f}."
    )
    print(f"Grafico guardado en: {CHART_PATH}")
    print(f"Resumen guardado en: {SUMMARY_PATH}")


if __name__ == "__main__":
    main()
