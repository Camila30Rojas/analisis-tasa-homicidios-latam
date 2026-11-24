from pathlib import Path

import altair as alt
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "datos" / "crudo" / "homicidios_latam.xlsx"
OUTPUT_DIR = PROJECT_ROOT / "docs" / "graficos"
CHART_PATH = OUTPUT_DIR / "distribucion_value.html"
SUMMARY_PATH = OUTPUT_DIR / "resumen_distribucion.md"


def main() -> None:
    df = pd.read_excel(DATA_PATH, sheet_name="datos")
    value = pd.to_numeric(df["value"], errors="coerce").dropna()

    if value.empty:
        raise ValueError("La columna 'value' no contiene valores numericos.")

    mean = value.mean()
    median = value.median()
    minimum = value.min()
    maximum = value.max()
    std = value.std()

    stats = pd.DataFrame(
        {
            "estadistica": ["media", "mediana", "minimo", "maximo", "desviacion_estandar"],
            "valor": [mean, median, minimum, maximum, std],
        }
    )
    print("Estadisticas descriptivas de value:")
    print(stats.to_string(index=False, formatters={"valor": lambda value: f"{value:.4f}"}))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    chart = (
        alt.Chart(pd.DataFrame({"value": value}))
        .mark_bar()
        .encode(
            x=alt.X(
                "value:Q",
                bin=alt.Bin(maxbins=30),
                title="Tasa de homicidios (por 100.000 habitantes)",
            ),
            y=alt.Y("count():Q", title="Frecuencia"),
            tooltip=[
                alt.Tooltip("value:Q", bin=alt.Bin(maxbins=30), title="Rango"),
                alt.Tooltip("count():Q", title="Frecuencia"),
            ],
        )
        .properties(
            title="Distribucion de la tasa de homicidios",
            width=700,
            height=400,
        )
    )
    chart.save(CHART_PATH)

    if mean > median:
        shape = "La media supera a la mediana, lo que indica una cola hacia valores altos."
    elif mean < median:
        shape = "La media es menor que la mediana, lo que indica una cola hacia valores bajos."
    else:
        shape = "La media y la mediana son iguales, sin una asimetria evidente."

    dispersion = "alta" if std > (mean / 2) else "moderada o baja"
    summary = (
        "# Resumen de la distribucion de `value`\n\n"
        f"- Observaciones validas: {len(value)}\n"
        f"- Media: {mean:.4f}\n"
        f"- Mediana: {median:.4f}\n"
        f"- Minimo: {minimum:.4f}\n"
        f"- Maximo: {maximum:.4f}\n"
        f"- Desviacion estandar: {std:.4f}\n\n"
        "## Interpretacion\n\n"
        f"Las tasas observadas van de {minimum:.4f} a {maximum:.4f}. "
        f"La tasa media es {mean:.4f} y la mediana es {median:.4f}. "
        f"{shape} "
        f"La desviacion estandar de {std:.4f} muestra una dispersion {dispersion} "
        "respecto al nivel medio de las observaciones.\n"
    )
    SUMMARY_PATH.write_text(summary, encoding="utf-8")

    print("\nResumen interpretativo:")
    print(summary)
    print(f"Histograma guardado en: {CHART_PATH}")
    print(f"Resumen guardado en: {SUMMARY_PATH}")


if __name__ == "__main__":
    main()
