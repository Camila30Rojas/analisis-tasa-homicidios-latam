from pathlib import Path

import pandas as pd


DATA_PATH = Path(__file__).resolve().parents[1] / "datos" / "crudo" / "homicidios_latam.xlsx"


def main() -> None:
    excel = pd.ExcelFile(DATA_PATH)
    print(f"Archivo: {DATA_PATH}")
    print(f"Hojas disponibles: {excel.sheet_names}")

    df = pd.read_excel(DATA_PATH, sheet_name=0)

    print("\nNumero de filas:", len(df))
    print("Numero de columnas:", len(df.columns))
    print("\nLista completa de columnas:")
    for position, column in enumerate(df.columns, start=1):
        print(f"{position}. {column}")

    print("\nPrimeros registros:")
    print(df.head().to_string(index=False))

    print("\nValores faltantes:")
    missing = df.isna().sum()
    missing_percent = df.isna().mean().mul(100)
    missing_report = pd.DataFrame(
        {"faltantes": missing, "porcentaje": missing_percent.round(2)}
    )
    print(missing_report.to_string())

    print("\nTipos de datos:")
    print(df.dtypes.to_string())

    print("\nPosibles problemas de calidad:")
    print(f"- Filas duplicadas: {df.duplicated().sum()}")

    for column in df.columns:
        series = df[column]
        unique_count = series.nunique(dropna=True)
        print(f"- {column}: {unique_count} valores unicos")

        if pd.api.types.is_object_dtype(series):
            whitespace_count = series.dropna().map(
                lambda value: isinstance(value, str) and value != value.strip()
            ).sum()
            if whitespace_count:
                print(f"  - Valores con espacios externos: {whitespace_count}")

            numeric = pd.to_numeric(series, errors="coerce")
            convertible_count = numeric.notna().sum()
            if 0 < convertible_count < len(series.dropna()):
                print(
                    f"  - Mezcla de textos y valores numericos; "
                    f"{convertible_count} valores convertibles"
                )

    if "Años__ESTANDAR" in df.columns:
        year = pd.to_numeric(df["Años__ESTANDAR"], errors="coerce")
        print(
            f"- Años no numericos o fuera de rango esperado: "
            f"{year.isna().sum() + ((year < 1900) | (year > 2100)).sum()}"
        )

    if "value" in df.columns:
        value = pd.to_numeric(df["value"], errors="coerce")
        print(f"- Valores de 'value' no numericos: {(value.isna() & df['value'].notna()).sum()}")
        if value.notna().any():
            print(f"- Valores negativos en 'value': {(value < 0).sum()}")


if __name__ == "__main__":
    main()
