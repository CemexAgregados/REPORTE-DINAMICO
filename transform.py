"""
Transformación de la bitácora de laboratorio de formato ancho (wide, tal como
vive en el Excel de SharePoint) a formato largo (long/tidy) para usar en el
dashboard de Streamlit.

El formato ancho NUNCA se modifica en la fuente — esta transformación vive
enteramente en el programa (ver decisión de arquitectura documentada).

Uso típico:

    from transform import wide_to_long_bitacora, promedio_del_promedio

    df = wide_to_long_bitacora("bitacora_sintetica.xlsx")
    resultado = promedio_del_promedio(
        df, material="Arena No.4", start="2025-01-01", end="2025-01-31",
        solo_cliente=True,
    )
"""

import pandas as pd

from material_catalog import category_lookup

TIPOS_RESUMEN = ("Promedio", "Desv. Std")


def _normalizar_propiedad(nombre: str) -> str:
    """'Malla No.4' -> 'No.4'; 'Malla 1½' -> '1 1/2'. Otras columnas, sin cambio."""
    nombre = str(nombre).strip()
    if nombre.startswith("Malla "):
        nombre = nombre[len("Malla "):].replace("1½", "1 1/2")
    return nombre


def wide_to_long_bitacora(path: str, sheet_name: str = "Bitacora") -> pd.DataFrame:
    """Lee la hoja ancha de la bitácora y la convierte a formato largo/tidy.

    Devuelve un DataFrame con una fila por (Fecha, Hora/Tipo, Material,
    Propiedad) y columnas:
        Fecha      : fecha del registro (datetime)
        Hora       : 1-24 para filas horarias, o "Promedio" / "Desv. Std"
                     para las filas de resumen diario
        Tipo       : "Horaria", "Promedio" o "Desv. Std" (deriva de Hora,
                     conveniente para filtrar sin comparar contra números)
        Material   : nombre del material (catálogo de 6 materiales)
        Propiedad  : nombre de la columna original; las mallas se normalizan
                     ("Malla No.4" -> "No.4", "Malla 1½" -> "1 1/2")
        Categoria  : "sieve" | "client" | "internal", según el catálogo
                     canónico — así el dashboard puede filtrar de una sola
                     vez lo que SÍ es apto para mostrarle al cliente
        Valor      : valor medido (float, o "NP" como texto para
                     Límites de Consistencia no aplicables en gravas)

    Los huecos de producción (material no probado ese día) llegan como NaN
    en el Excel y se descartan aquí — no tiene sentido una fila "vacía" en
    formato largo.
    """
    df = pd.read_excel(path, sheet_name=sheet_name, header=[0, 1])

    # Aplanar el encabezado de dos niveles (Material, Propiedad); las dos
    # primeras columnas (Fecha, Hora) llegan con sub-nivel "Unnamed: ..." por
    # las celdas combinadas del Excel, así que se renombran por posición.
    flat_cols = []
    for i, (top, sub) in enumerate(df.columns):
        if i == 0:
            flat_cols.append("Fecha")
        elif i == 1:
            flat_cols.append("Hora")
        else:
            flat_cols.append(f"{top}||{sub}")
    df.columns = flat_cols

    long_df = df.melt(id_vars=["Fecha", "Hora"], var_name="mat_prop", value_name="Valor")
    long_df[["Material", "Propiedad"]] = long_df["mat_prop"].str.split(r"\|\|", expand=True)
    long_df["Propiedad"] = long_df["Propiedad"].map(_normalizar_propiedad)
    long_df = long_df.drop(columns="mat_prop").dropna(subset=["Valor"])

    long_df["Tipo"] = long_df["Hora"].apply(
        lambda h: h if h in TIPOS_RESUMEN else "Horaria"
    )

    lookup = category_lookup()
    long_df["Categoria"] = [
        lookup.get((mat, prop), "desconocida")
        for mat, prop in zip(long_df["Material"], long_df["Propiedad"])
    ]

    desconocidas = long_df.loc[long_df["Categoria"] == "desconocida",
                                ["Material", "Propiedad"]].drop_duplicates()
    if not desconocidas.empty:
        raise ValueError(
            "Columnas presentes en el Excel que no están en material_catalog.py "
            f"(revisar catálogo o el archivo fuente):\n{desconocidas}"
        )

    return long_df.reset_index(drop=True)


def promedio_del_promedio(
    df_long: pd.DataFrame,
    material: str,
    start: str,
    end: str,
    solo_cliente: bool = True,
) -> pd.DataFrame:
    """Calcula el reporte de un material para un periodo: el promedio de los
    promedios DIARIOS (nunca el promedio directo de los datos horarios), que
    es la metodología real de negocio.

    solo_cliente=True filtra a las propiedades marcadas como "client" en el
    catálogo (lo que debe ver el cliente en el dashboard); False regresa
    también mallas e internas, útil para vistas de laboratorio.
    """
    mask = (
        (df_long["Material"] == material)
        & (df_long["Tipo"] == "Promedio")
        & (df_long["Fecha"] >= pd.Timestamp(start))
        & (df_long["Fecha"] <= pd.Timestamp(end))
    )
    if solo_cliente:
        mask &= df_long["Categoria"] == "client"

    subset = df_long.loc[mask].copy()
    # "NP" (No Plástico) se excluye del promedio numérico pero se reporta aparte
    subset["Valor_num"] = pd.to_numeric(subset["Valor"], errors="coerce")

    resumen = (
        subset.groupby("Propiedad")
        .agg(
            promedio=("Valor_num", "mean"),
            dias_con_dato=("Valor", "count"),
            es_no_plastico=("Valor", lambda s: (s == "NP").all() and s.notna().any()),
        )
        .reset_index()
    )
    return resumen


if __name__ == "__main__":
    import sys

    #path = sys.argv[1] if len(sys.argv) > 1 else "/mnt/user-data/outputs/bitacora_sintetica.xlsx"

    path = "bitacora_sintetica.xlsx"
    long_df = wide_to_long_bitacora(path)
    print(sorted(long_df["Propiedad"].unique()))
    print(f"Formato largo: {long_df.shape[0]:,} filas, {long_df.shape[1]} columnas")
    print(long_df.head())

    reporte = promedio_del_promedio(long_df, "Arena No.4", "2025-01-01", "2025-01-31")
    print("\nReporte cliente Arena No.4 — enero 2025:")
    print(reporte)