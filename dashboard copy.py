"""
Dashboard Cerro Jardín — Reportes de Calidad
Corre con: streamlit run streamlit_app.py
Requiere: streamlit>=1.32, plotly
"""

import datetime as dt

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from material_catalog import ORDEN_MALLAS
from transform_promedio import (
    wide_to_long_promedio,
    reporte_material,
)
from specs import (
    ESPECIFICACIONES,
    NOMBRES_REPORTE,
)
# ============================================================
# Configuración y tema (rojo / azul / blanco)
# ============================================================

# Límites normativos CEMEX por malla (% que pasa). Valores fijos por
# especificación, no varían por prueba. Bases Hidráulicas: sin banda.
LIMITES_GRANULOMETRICOS = {

    "Arena No. 4": {
        "3/8":  {"min": 100, "max": 100},
        "No.4": {"min": 95,  "max": 100},
        "No.8": {"min": 70,  "max": 100},
        "No.16": {"min": 50, "max": 85},
        "No.30": {"min": 25, "max": 60},
        "No.50": {"min": 10, "max": 30},
        "No.100": {"min": 2, "max": 20},
        "Ch": {"min": 0, "max": 0},
    },

    "Grava 10 mm": {
        "1/2":  {"min": 100, "max": 100},
        "3/8":  {"min": 85,  "max": 100},
        "No.4": {"min": 10,  "max": 30},
        "No.8": {"min": 0,   "max": 10},
        "No.16": {"min": 0,  "max": 5},
        "Ch": {"min": 0, "max": 0},
    },

    "Grava 20 mm": {
        "1":    {"min": 100, "max": 100},
        "3/4":  {"min": 87,  "max": 93},
        "3/8":  {"min": 20,  "max": 55},
        "No.4": {"min": 0,   "max": 10},
        "No.8": {"min": 0,   "max": 5},
        "Ch": {"min": 0, "max": 0},
    },

    "Grava 40 mm": {
        "2":      {"min": 100, "max": 100},
        "1 1/2":  {"min": 90,  "max": 100},
        "1":      {"min": 20,  "max": 55},
        "3/4":    {"min": 0,   "max": 15},
        "3/8":    {"min": 0,   "max": 5},
        "Ch":     {"min": 0,   "max": 0},
    },

    "Mezcla 60% finos + 40% gruesos": {
        "2":      {"min": 85, "max": 100},
        "1 1/2":  {"min": 75, "max": 100},
        "1":      {"min": 58, "max": 98},
        "3/4":    {"min": 49, "max": 92},
        "3/8":    {"min": 36, "max": 70},
        "No.4":   {"min": 25, "max": 53},
        "No.10":  {"min": 15, "max": 41},
        "No.20":  {"min": 10, "max": 31},
        "No.40":  {"min": 7,  "max": 26},
        "No.60":  {"min": 5,  "max": 22},
        "No.100": {"min": 3,  "max": 18},
        "No.200": {"min": 0,  "max": 12},
        "Ch":     {"min": 0,  "max": 0},
    },

    "Mezcla 80% finos + 20% gruesos": {
        "2":      {"min": 85, "max": 100},
        "1 1/2":  {"min": 75, "max": 100},
        "1":      {"min": 62, "max": 100},
        "3/4":    {"min": 54, "max": 100},
        "3/8":    {"min": 40, "max": 100},
        "No.4":   {"min": 30, "max": 80},
        "No.10":  {"min": 21, "max": 60},
        "No.20":  {"min": 13, "max": 44},
        "No.40":  {"min": 8,  "max": 31},
        "No.60":  {"min": 5,  "max": 23},
        "No.100": {"min": 3,  "max": 17},
        "No.200": {"min": 0,  "max": 10},
        "Ch":     {"min": 0,  "max": 0},
    },

}

NOMBRES_REPORTE = {

    "%H": "Contenido de Agua (%Humedad)",

    "M.F.": "Módulo de Finura",

    "%PXL": "Contenido de Finos",

    "Densidad": "Densidad Relativa",

    "Absorción": "Absorción",

    "Coef. De Forma": "Coeficiente de Forma",

    "Equivalente Arena": "Equivalente de Arena",

    "Suelto": "Masa Volumétrica Suelta",

    "Compacto": "Masa Volumétrica Compactada",
}

ESPECIFICACIONES = {

    "Arena No. 4": {

        "M.F.": {
            "metodo": "NMX-C-111",
            "min": 2.3,
            "max": 3.1,
            "unidad": "%"
        },

        "%H": {
            "metodo": "NMX-C-166",
            "min": "---",
            "max": "---",
            "unidad": "%"
        },

        "Densidad": {
            "metodo": "NMX-C-165",
            "min": "---",
            "max": "---",
            "unidad": "---"
        },

        "Absorción": {
            "metodo": "NMX-C-165",
            "min": "---",
            "max": "---",
            "unidad": "%"
        },

    },

}

BITACORA_PATH = "08. Bitácora de Calidad Cerro Jardín Agosto 2026.xlsx"

ROJO = "#C8102E"
ROJO_CLARO = "#FDEAEC"
AZUL = "#003DA5"
AZUL_CLARO = "#E8EEFA"
BLANCO = "#FFFFFF"
GRIS_TEXTO = "#2B2B2B"

st.set_page_config(page_title="Cerro Jardín — Reportes de Calidad", layout="wide")

st.markdown(
    f"""
    <style>

    .stApp {{
        background-color: #F1F3F5;
    }}

    .block-container {{
        max-width: 950px;
        margin: auto;
    }}

    /* ============================================================
       Tarjetas de sección (todas las keys empiezan con "card_")
    ============================================================ */

    div[class*="st-key-card_"] {{
        background-color: #F7F7F7 !important;
        border: 4px solid {AZUL} !important;
        border-radius: 18px !important;
        padding: 14px !important;
        margin-bottom: 1.2rem !important;
        box-shadow: 0 6px 16px rgba(0,0,0,0.18) !important;
    }}

    /* Header azul de cada sección */
    .seccion-header {{
        background-color: {AZUL};
        color: white;
        padding: 14px 18px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 1.1rem;
        margin-bottom: 15px;
    }}

    /* ============================================================
       Layout compacto
    ============================================================ */

    [data-testid="stToolbar"] {{
        display: none;
    }}

    [data-testid="stDecoration"] {{
        display: none;
    }}

    div[data-testid="stVerticalBlock"] {{
        gap: 0.5rem;
    }}

    /* ============================================================
       Títulos
    ============================================================ */

    h1, h2, h3 {{
        margin-top: 0.2rem !important;
        margin-bottom: 0.2rem !important;
        color: {AZUL};
    }}

    h2 {{
        font-size: 2rem !important;
    }}

    h3 {{
        font-size: 1.5rem !important;
    }}

    /* ============================================================
       Métricas
    ============================================================ */

    [data-testid="stMetric"] {{
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
    }}

    [data-testid="stMetricValue"] {{
        color: {ROJO};
        font-size: 1.6rem !important;
    }}

    [data-testid="stMetricLabel"] {{
        color: {GRIS_TEXTO};
    }}

    /* ============================================================
       Separadores
    ============================================================ */

    hr {{
        border-top: 3px solid {AZUL};
        opacity: 0.35;
    }}

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# Carga de datos
# ============================================================

@st.cache_data
def cargar_datos(path: str) -> pd.DataFrame:
    return wide_to_long_promedio(path)


try:
    df_long = cargar_datos(BITACORA_PATH)
except FileNotFoundError:
    st.error(
        f"No se encontró el archivo de la bitácora en '{BITACORA_PATH}'. "
        "Ajusta BITACORA_PATH al inicio de streamlit_app.py."
    )
    st.stop()

fecha_min = df_long["Fecha"].min().date()
fecha_max = df_long["Fecha"].max().date()

material = sorted(
    df_long["Material"].unique()
)[0]

fecha_inicio = fecha_max - dt.timedelta(days=30)

fecha_fin = fecha_max


# ============================================================
# Encabezado tipo reporte
# ============================================================

st.markdown(
    """
    <h1 style='text-align:center; margin-bottom:0;'>
        CEMEX AGREGADOS MÉXICO
    </h1>
    """,
    unsafe_allow_html=True,
)

st.divider()

st.markdown(
    """
    <h2 style='text-align:center; margin-bottom:0;'>
        Informe de Resultados
    </h2>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <h3 style='text-align:center; margin-top:0;'>
        {material}
    </h3>
    """,
    unsafe_allow_html=True,
)

st.divider()

# ============================================================
# Filtros principales
# ============================================================

f1, f2, f3 = st.columns([2, 1, 1])

with f1:

    material = st.selectbox(
        "Material",
        sorted(
            df_long["Material"].unique()
        )
    )

with f2:

    fecha_inicio = st.date_input(
        "Fecha inicial",
        value=max(
            fecha_min,
            fecha_max - dt.timedelta(days=30)
        ),
        min_value=fecha_min,
        max_value=fecha_max,
    )

with f3:

    fecha_fin = st.date_input(
        "Fecha final",
        value=fecha_max,
        min_value=fecha_min,
        max_value=fecha_max,
    )

if fecha_inicio > fecha_fin:

    st.error(
        "La fecha de inicio no puede ser posterior a la fecha final."
    )

    st.stop()

st.write("")

# ============================================================
# Reporte base (promedio del promedio)
# ============================================================

reporte = reporte_material(
    df_long,
    material=material,
    start=str(fecha_inicio),
    end=str(fecha_fin),
)

if reporte.empty or reporte["dias_con_dato"].sum() == 0:
    st.warning("No hay datos de este material en el periodo seleccionado.")
    st.stop()

dias_con_produccion = (
    df_long[
        (df_long["Material"] == material)
        & (df_long["Fecha"].dt.date >= fecha_inicio)
        & (df_long["Fecha"].dt.date <= fecha_fin)
    ]["Fecha"]
    .nunique()
)

dias_totales = (
    fecha_fin - fecha_inicio
).days + 1

cobertura_pct = round(100 * dias_con_produccion / dias_totales, 1) if dias_totales else 0

tamices_df = reporte[
    reporte["Grupo"] ==
    "Granulometría % Pasante"
].copy()

propiedades_df = reporte[
    reporte["Grupo"] !=
    "Granulometría % Pasante"
].copy()

# Eliminar propiedades duplicadas si existen
propiedades_df = (
    propiedades_df
    .drop_duplicates(
        subset=["Grupo", "Propiedad"]
    )
    .sort_values(
        ["Grupo", "Propiedad"]
    )
)

es_granular = not tamices_df.empty

tamices_material = (
    tamices_df["Propiedad"]
    .drop_duplicates()
    .tolist()
)

# ============================================================
# Datos Generales
# ============================================================

with st.container(border=True):

    st.markdown(
        """
        <div class="seccion-header">
            📄 Datos Generales
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.caption("Planta")
        st.markdown("**Cerro Jardín**")

    with c2:
        st.caption("Material")
        st.markdown(f"**{material}**")

    with c3:
        st.caption("Inicio")
        st.markdown(
            f"**{fecha_inicio.strftime('%d/%m/%Y')}**"
        )

    with c4:
        st.caption("Fin")
        st.markdown(
            f"**{fecha_fin.strftime('%d/%m/%Y')}**"
        )

    with c5:
        st.caption("Cobertura")
        st.markdown(
            f"**{cobertura_pct:.1f}%**"
        )

# ============================================================
# Especificaciones
# ============================================================

with st.container(border=True):

    st.markdown(
        """
        <div class="seccion-header">
            Especificaciones
        </div>
        """,
        unsafe_allow_html=True,
    )

    tabla_specs = propiedades_df.copy()

    tabla_specs["Resultado"] = (
        tabla_specs["promedio"]
        .round(2)
    )

    tabla_specs["Método"] = tabla_specs["Propiedad"].apply(
        lambda p: ESPECIFICACIONES
            .get(material, {})
            .get(p, {})
            .get("metodo", "---")
    )

    tabla_specs["Mínimo"] = tabla_specs["Propiedad"].apply(
        lambda p: ESPECIFICACIONES
            .get(material, {})
            .get(p, {})
            .get("min", "---")
    )

    tabla_specs["Máximo"] = tabla_specs["Propiedad"].apply(
        lambda p: ESPECIFICACIONES
            .get(material, {})
            .get(p, {})
            .get("max", "---")
    )

    tabla_specs["Unidad"] = tabla_specs["Propiedad"].apply(
        lambda p: ESPECIFICACIONES
            .get(material, {})
            .get(p, {})
            .get("unidad", "---")
    )
    tabla_specs = tabla_specs[
        [
            "Propiedad",
            "Método",
            "Mínimo",
            "Máximo",
            "Unidad",
            "Resultado",
        ]
    ]

    tabla_specs.columns = [
        "Especificación",
        "Método",
        "Mínimo",
        "Máximo",
        "Unidad",
        "Resultado",
    ]

    tabla_specs["Especificación"] = (
        tabla_specs["Especificación"]
        .map(
            lambda x: NOMBRES_REPORTE.get(x, x)
        )
    )

    tabla_specs["Especificación"] = (
    tabla_specs["Especificación"]
    .map(
        lambda x: NOMBRES_REPORTE.get(x, x)
    )
)


    st.dataframe(
        tabla_specs,
        hide_index=True,
        use_container_width=True,
    )

# ============================================================
# Granulometría
# ============================================================

if es_granular and not tamices_df.empty:

    col_curva, col_tabla_gran = st.columns([1.2, 1])

    # --------------------------------------------------------
    # Curva Granulométrica
    # --------------------------------------------------------

    with col_curva:

        with st.container(border=True):

            st.markdown(
                """
                <div class="seccion-header">
                    📈 Curva Granulométrica
                </div>
                """,
                unsafe_allow_html=True,
            )

            orden_presente = [
                t
                for t in ORDEN_MALLAS
                if t in tamices_df["Propiedad"].values
            ]

            tamices_ordenado = (
                tamices_df
                .set_index("Propiedad")
                .reindex(orden_presente)
                .reset_index()
            )


            fig_curva = go.Figure()

            limites = LIMITES_GRANULOMETRICOS.get(material)

            if limites:

                tamices_lim = [
                    t
                    for t in orden_presente
                    if t in limites
                ]

                mins = [
                    limites[t]["min"]
                    for t in tamices_lim
                ]

                maxs = [
                    limites[t]["max"]
                    for t in tamices_lim
                ]

                fig_curva.add_trace(
                    go.Scatter(
                        x=tamices_lim + tamices_lim[::-1],
                        y=maxs + mins[::-1],
                        fill="toself",
                        fillcolor="rgba(0,61,165,0.12)",
                        line=dict(color="rgba(0,0,0,0)"),
                        name="Banda de especificación",
                        hoverinfo="skip",
                    )
                )

                fig_curva.add_trace(
                    go.Scatter(
                        x=tamices_lim,
                        y=maxs,
                        mode="lines",
                        name="Límite superior",
                        line=dict(
                            color=AZUL,
                            width=1.5,
                            dash="dot"
                        ),
                    )
                )

                fig_curva.add_trace(
                    go.Scatter(
                        x=tamices_lim,
                        y=mins,
                        mode="lines",
                        name="Límite inferior",
                        line=dict(
                            color=AZUL,
                            width=1.5,
                            dash="dot"
                        ),
                    )
                )

            fig_curva.add_trace(
                go.Scatter(
                    x=tamices_ordenado["Propiedad"],
                    y=tamices_ordenado["promedio"],
                    mode="lines+markers",
                    name="% que pasa",
                    line=dict(
                        color=ROJO,
                        width=3,
                    ),
                    marker=dict(
                        size=9,
                        color=ROJO,
                        line=dict(
                            width=1,
                            color=BLANCO,
                        ),
                    ),
                )
            )

            fig_curva.update_layout(
                xaxis_title="Malla",
                yaxis_title="% que pasa",

                xaxis=dict(
                    type="category",
                    categoryorder="array",
                    categoryarray=orden_presente,
                ),

                plot_bgcolor=BLANCO,
                paper_bgcolor=BLANCO,
                font=dict(color=GRIS_TEXTO),

                yaxis=dict(
                    range=[0, 100],
                    gridcolor="#DDE4F0",
                ),

                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    x=0,
                ),

                margin=dict(t=30),
                height=320,
            )

            st.plotly_chart(
                fig_curva,
                use_container_width=True,
            )
    # --------------------------------------------------------
    # Tabla Granulométrica
    # --------------------------------------------------------

    with col_tabla_gran:

        with st.container(border=True):

            st.markdown(
                """
                <div class="seccion-header">
                    📋 Tabla Granulométrica
                </div>
                """,
                unsafe_allow_html=True,
            )

            filas = []

            for _, row in tamices_ordenado.iterrows():

                malla = row["Propiedad"]

                minimo = None
                maximo = None
                estado = "-"

                if limites and malla in limites:

                    minimo = limites[malla]["min"]
                    maximo = limites[malla]["max"]

                    estado = (
                        "✅"
                        if minimo <= row["promedio"] <= maximo
                        else "🔴"
                    )

                filas.append(
                    {
                        "Malla": malla,
                        "% Pasa": round(row["promedio"], 2),
                        "Min": minimo,
                        "Max": maximo,
                        "Estado": estado,
                    }
                )

            tabla_gran = pd.DataFrame(filas)

            st.dataframe(
                tabla_gran,
                hide_index=True,
                use_container_width=True,
                height=320,
            )
            
# ============================================================
# Comportamiento Histórico
# ============================================================

col_tendencia, col_box = st.columns([1.5, 1])

# --------------------------------------------------------
# Tendencia diaria
# --------------------------------------------------------

with col_tendencia:

    with st.container(border=True):

        st.markdown(
            """
            <div class="seccion-header">
                📉 Tendencia Diaria
            </div>
            """,
            unsafe_allow_html=True,
        )

        propiedad_tendencia = st.selectbox(
            "Propiedad a graficar",
            sorted(
                propiedades_df["Propiedad"]
                .drop_duplicates()
                .tolist()
            ),
        )

        serie = (
            df_long[
                (df_long["Material"] == material)
                & (df_long["Propiedad"] == propiedad_tendencia)
                & (df_long["Fecha"].dt.date >= fecha_inicio)
                & (df_long["Fecha"].dt.date <= fecha_fin)
            ]
            .copy()
        )

        if serie.empty:

            st.info(
                "Sin datos para esta propiedad en el periodo."
            )

        else:

            serie["Valor_num"] = pd.to_numeric(
                serie["Valor"],
                errors="coerce"
            )

            serie = serie.dropna(
                subset=["Valor_num"]
            )

            fig_tendencia = go.Figure()

            fig_tendencia.add_trace(
                go.Scatter(
                    x=serie["Fecha"],
                    y=serie["Valor_num"],
                    mode="lines+markers",
                    line=dict(
                        color=AZUL,
                        width=2,
                    ),
                    marker=dict(
                        size=6,
                        color=ROJO,
                    ),
                )
            )

            promedio_periodo = (
                serie["Valor_num"]
                .mean()
            )

            fig_tendencia.add_hline(
                y=promedio_periodo,
                line_dash="dash",
                line_color=ROJO,
                annotation_text=f"Promedio: {promedio_periodo:.2f}",
            )

            fig_tendencia.update_layout(
                xaxis_title="Fecha",
                yaxis_title=propiedad_tendencia,
                plot_bgcolor=BLANCO,
                paper_bgcolor=BLANCO,
                font=dict(color=GRIS_TEXTO),
                margin=dict(t=20),
                height=320,
            )

            st.plotly_chart(
                fig_tendencia,
                use_container_width=True,
            )

# --------------------------------------------------------
# Distribución
# --------------------------------------------------------

with col_box:

    with st.container(border=True):

        st.markdown(
            """
            <div class="seccion-header">
                📦 Distribución
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not serie.empty:

            fig_box = go.Figure()

            fig_box.add_trace(
                go.Box(
                    y=serie["Valor_num"],
                    name=propiedad_tendencia,
                    boxpoints="outliers",
                    marker_color=AZUL,
                )
            )

            fig_box.update_layout(
                yaxis_title=propiedad_tendencia,
                plot_bgcolor=BLANCO,
                paper_bgcolor=BLANCO,
                font=dict(color=GRIS_TEXTO),
                height=320,
            )

            st.plotly_chart(
                fig_box,
                use_container_width=True,
            )

st.divider()

st.caption(
    "Nota: este reporte muestra únicamente propiedades de reporte a cliente. "
    "Los límites de consistencia y otras pruebas internas de laboratorio no "
    "se incluyen aquí."
)