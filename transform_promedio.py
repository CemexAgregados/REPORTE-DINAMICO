"""
transform_promedio.py

Transformación de la hoja "Promedio" del archivo real
de calidad Cerro Jardín a formato largo (tidy)
para consumo del dashboard.
"""

import re
import pandas as pd


# ============================================================
# Normalización
# ============================================================

def limpiar_material(material):

    return str(material).strip()


def limpiar_grupo(grupo):

    return str(grupo).strip()


def limpiar_propiedad(prop, grupo):

    prop = str(prop).strip()

    # Normalizar tamices
    prop = prop.replace("⅜", "3/8")
    prop = prop.replace("¾", "3/4")
    prop = prop.replace("1½", "1 1/2")
    prop = prop.replace('"', "")

    # Quitar únicamente sufijos .1
    prop = re.sub(r"\.1$", "", prop)

    # Columnas simples (%PXL, M.F., etc.)
    if "Unnamed" in prop:
        return grupo

    return prop.strip()


# ============================================================
# Transformación principal
# ============================================================

def wide_to_long_promedio(
    path: str,
    sheet_name: str = "Promedio"
) -> pd.DataFrame:

    df = pd.read_excel(
        path,
        sheet_name=sheet_name,
        header=[3, 4, 5]
    )


    fecha_col = df.columns[1]

    filas = []

    for _, row in df.iterrows():

        fecha = pd.to_datetime(
            row[fecha_col],
            errors="coerce"
        )

        if pd.isna(fecha):
            continue

        for col in df.columns[2:]:

            material = limpiar_material(col[0])

            grupo = limpiar_grupo(col[1])

            propiedad = limpiar_propiedad(
                col[2],
                grupo
            )

            valor = row[col]

            if pd.isna(valor):
                continue

            filas.append(
                {
                    "Fecha": fecha,
                    "Material": material,
                    "Grupo": grupo,
                    "Propiedad": propiedad,
                    "Valor": valor,
                }
            )

    long_df = pd.DataFrame(filas)

    return long_df.reset_index(drop=True)


# ============================================================
# Resumen para dashboard
# ============================================================

def reporte_material(
    df_long: pd.DataFrame,
    material: str,
    start: str,
    end: str,
):

    mask = (
        (df_long["Material"] == material)
        & (df_long["Fecha"] >= pd.Timestamp(start))
        & (df_long["Fecha"] <= pd.Timestamp(end))
    )

    subset = df_long.loc[mask].copy()

    subset["Valor_num"] = pd.to_numeric(
        subset["Valor"],
        errors="coerce"
    )

    resumen = (
        subset
        .groupby(
            ["Grupo", "Propiedad"],
            as_index=False
        )
        .agg(
            promedio=("Valor_num", "mean"),
            dias_con_dato=("Fecha", "nunique"),
        )
    )

    return resumen


# ============================================================
# Debug local
# ============================================================

if __name__ == "__main__":

    path = "08. Bitácora de Calidad Cerro Jardín Agosto 2026.xlsx"

    df = wide_to_long_promedio(path)

    print("\nCOLUMNAS")
    print(df.columns.tolist())

    print("\nSHAPE")
    print(df.shape)

    print("\nMATERIALES")
    print(sorted(df["Material"].unique()))

    print("\nGRUPOS")
    print(sorted(df["Grupo"].unique()))

    print("\nHEAD")
    print(df.head(20))

    print("\nCATALOGO REAL")

    print(
        df[
            ["Material", "Grupo", "Propiedad"]
        ]
        .drop_duplicates()
        .sort_values(
            ["Material", "Grupo", "Propiedad"]
        )
        .to_string(index=False)
    )
