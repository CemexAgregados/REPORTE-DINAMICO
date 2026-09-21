"""
Dashboard Cerro Jardín — Reportes de Calidad
Corre con: streamlit run streamlit_app.py
Requiere: streamlit>=1.32, plotly
"""

import datetime as dt

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from material_catalog import MATERIAL_SCHEMA, ORDEN_MALLAS
from transform import promedio_del_promedio, wide_to_long_bitacora
# ============================================================
# Configuración y tema (rojo / azul / blanco)
# ============================================================

# Límites normativos CEMEX por malla (% que pasa). Valores fijos por
# especificación, no varían por prueba. Bases Hidráulicas: sin banda.
LIMITES_GRANULOMETRICOS = {
    "Arena No.4": {
        "3/8": {"min": 100, "max": 100},
        "No.4": {"min": 95, "max": 100},
        "No.8": {"min": 70, "max": 100},
        "No.16": {"min": 50, "max": 85},
        "No.30": {"min": 25, "max": 60},
        "No.50": {"min": 10, "max": 30},
        "No.100": {"min": 2, "max": 20},
        "Ch": {"min": 0, "max": 0},
    },
    "Grava 10mm-3/8": {
        "1/2": {"min": 100, "max": 100},
        "3/8": {"min": 85, "max": 100},
        "No.4": {"min": 10, "max": 30},
        "No.8": {"min": 0, "max": 10},
        "No.16": {"min": 0, "max": 5},
        "Ch": {"min": 0, "max": 0},
    },
    "Grava 20mm-3/4": {
        "1": {"min": 100, "max": 100},
        "3/4": {"min": 87, "max": 93},
        "3/8": {"min": 20, "max": 55},
        "No.4": {"min": 0, "max": 10},
        "No.8": {"min": 0, "max": 5},
        "Ch": {"min": 0, "max": 0},
    },
    "Grava 40mm-1½": {
        "2": {"min": 100, "max": 100},
        "1 1/2": {"min": 90, "max": 100},
        "1": {"min": 20, "max": 55},
        "3/4": {"min": 0, "max": 15},
        "3/8": {"min": 0, "max": 5},
        "Ch": {"min": 0, "max": 0},
    },
}


BITACORA_PATH = "bitacora_sintetica.xlsx"  # <-- ajustar a la ruta real

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
        zoom: 1;
    }}

    .block-container {{
        max-width: 950px;
        margin: auto;
    
    }}

    /* ============================================================
   Tarjetas de sección
============================================================ */

    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background-color: #F7F7F7 !important;
        border: 5px solid #003DA5 !important;
        border-radius: 18px !important;
        padding: 10px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.10) !important;
    }}

    /* Header de las secciones */

    .seccion-header {{
        background-color: #003DA5;
        color: white;
        padding: 14px 18px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 1.1rem;
        margin-bottom: 15px;
    }}

    /* ============================================================
       Compactar layout general
    ============================================================ */
   
    /* Ocultar toolbar superior */
    [data-testid="stToolbar"] {{
        display: none;
    }}

    /* Ocultar decoración superior */
    [data-testid="stDecoration"] {{
        display: none;
    }}

    /* Menos espacio entre elementos */
    div[data-testid="stVerticalBlock"] {{
        gap: 0.5rem;
    }}

    /* Títulos más compactos */
    h1, h2, h3 {{
        margin-top: 0.2rem !important;
        margin-bottom: 0.2rem !important;
    }}

    h2 {{
    font-size: 3rem !important;
    }}

    h3 {{
    font-size: 1.5rem !important;
    }}

    /* ============================================================
       Tarjetas de sección
    ============================================================ */

    div.st-key-kpis {{
        background-color: {ROJO_CLARO};
        border-left: 6px solid {ROJO};
        border-radius: 10px;
        padding: 1rem;
    }}

    div.st-key-granulometria {{
        background-color: {AZUL_CLARO};
        border-left: 6px solid {AZUL};
        border-radius: 10px;
        padding: 1rem;
    }}

    div.st-key-tabla {{
        background-color: {BLANCO};
        border: 1px solid #DDDDDD;
        border-top: 6px solid {AZUL};
        border-radius: 10px;
        padding: 1rem;
    }}

    div.st-key-tendencia {{
        background-color: {ROJO_CLARO};
        border-left: 6px solid {ROJO};
        border-radius: 10px;
        padding: 1rem;
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
    }}

    [data-testid="stMetricLabel"] {{
        color: {GRIS_TEXTO};
    }}

    /* ============================================================
       Títulos
    ============================================================ */

    h2, h3 {{
        color: {AZUL};
    }}

    /* ============================================================
       Separadores
    ============================================================ */

    hr {{
        border-top: 2px solid {AZUL_CLARO};
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
    return wide_to_long_bitacora(path)


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

material = list(MATERIAL_SCHEMA.keys())[0]

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
        list(MATERIAL_SCHEMA.keys())
    )

with f2:

    fecha_inicio = st.date_input(
        "Fecha inicial",
        value=fecha_max - dt.timedelta(days=30),
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

reporte = promedio_del_promedio(
    df_long,
    material=material,
    start=str(fecha_inicio),
    end=str(fecha_fin),
    solo_cliente=False,
)

if reporte.empty or reporte["dias_con_dato"].sum() == 0:
    st.warning("No hay datos de este material en el periodo seleccionado.")
    st.stop()

dias_totales = (fecha_fin - fecha_inicio).days + 1
dias_con_produccion = int(reporte["dias_con_dato"].max())
cobertura_pct = round(100 * dias_con_produccion / dias_totales, 1) if dias_totales else 0


tamices_material = MATERIAL_SCHEMA[material]["tamices"]
propiedades_material = MATERIAL_SCHEMA[material]["propiedades"]

es_granular = len(tamices_material) > 0

if es_granular:

    tamices_df = reporte[
        reporte["Propiedad"].isin(tamices_material)
    ].copy()

    propiedades_df = reporte[
        reporte["Propiedad"].isin(propiedades_material)
    ].copy()

else:

    tamices_df = pd.DataFrame()

    propiedades_df = reporte[
        reporte["Propiedad"].isin(propiedades_material)
    ].copy()

# ============================================================
# Datos Generales
# ============================================================

with st.container(border = True):

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
        st.markdown(f"**{fecha_inicio.strftime('%d/%m/%y')}**")

    with c4:
        st.caption("Fin")
        st.markdown(f"**{fecha_fin.strftime('%d/%m/%y')}**")

    with c5:
        st.caption("Cobertura")
        st.markdown(f"**{cobertura_pct}%**")

# ============================================================
# Resultados del periodo
# ============================================================

with st.container(border=True):

    st.markdown(
        """
        <div class="seccion-header">
            📋 Resultados del Periodo
        </div>
        """,
        unsafe_allow_html=True,
    )

    tabla_resumen = propiedades_df.copy()

    tabla_resumen["Resultado"] = tabla_resumen.apply(
        lambda r: (
            "NP"
            if r.get("es_no_plastico", False)
            else f"{r['promedio']:.2f}"
        ),
        axis=1,
    )

    n_cols = 7

    for i in range(0, len(tabla_resumen), n_cols):

        cols = st.columns(n_cols)

        bloque = tabla_resumen.iloc[i:i+n_cols]

        for col, (_, row) in zip(cols, bloque.iterrows()):

            with col:

                st.markdown(
                    f"""
                    <div style="
                        height:70px;
                        text-align:center;
                        font-size:14px;
                        color:#7a7a7a;
                        display:flex;
                        align-items:center;
                        justify-content:center;
                    ">
                        {row["Propiedad"]}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.markdown(
                    f"""
                    <div style="
                        text-align:center;
                        font-size:28px;
                        font-weight:700;
                        margin-top:-8px;
                    ">
                        {row["Resultado"]}
                    </div>
                    """,
                    unsafe_allow_html=True,
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
                        name="Límite superior CEMEX",
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
                        name="Límite inferior CEMEX",
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
                    name="% que pasa (real)",
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
                plot_bgcolor=BLANCO,
                paper_bgcolor=AZUL_CLARO,
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
            )

            st.plotly_chart(
                fig_curva,
                use_container_width=True,
                height = 300
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

                if limites and malla in limites:

                    minimo = limites[malla]["min"]
                    maximo = limites[malla]["max"]

                filas.append(
                    {
                        "Malla": malla,
                        "% Que pasa": round(row["promedio"], 2),
                        "Min. CEMEX": minimo,
                        "Max. CEMEX": maximo,
                    }
                )

            tabla_gran = pd.DataFrame(filas)

            st.dataframe(
                tabla_gran,
                hide_index=True,
                use_container_width=True,
                height=300,
            )

elif not es_granular:

    with st.container(border=True):

        st.markdown(
            """
            <div class="seccion-header">
                📈 Granulometría
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.info(
            "Este material no incluye curva granulométrica en el reporte a cliente."
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
            propiedades_df["Propiedad"].tolist(),
        )

        serie = (
            df_long[
                (df_long["Material"] == material)
                & (df_long["Propiedad"] == propiedad_tendencia)
                & (df_long["Tipo"] == "Promedio")
                & (df_long["Fecha"].dt.date >= fecha_inicio)
                & (df_long["Fecha"].dt.date <= fecha_fin)
            ]
            .copy()
        )

        if serie.empty:

            st.info(
                "Sin datos diarios para esta propiedad en el periodo."
            )

        else:

            serie["Valor_num"] = pd.to_numeric(
                serie["Valor"],
                errors="coerce"
            )

            fig_tendencia = go.Figure()

            fig_tendencia.add_trace(
                go.Scatter(
                    x=serie["Fecha"],
                    y=serie["Valor_num"],
                    mode="lines+markers",
                    line=dict(color=AZUL, width=2),
                    marker=dict(
                        size=6,
                        color=ROJO,
                    ),
                )
            )

            promedio_periodo = serie["Valor_num"].mean()

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
                paper_bgcolor=AZUL_CLARO,
                font=dict(color=GRIS_TEXTO),
                margin=dict(t=20),
            )

            st.plotly_chart(
                fig_tendencia,
                use_container_width=True,
                height = 250
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
                paper_bgcolor=AZUL_CLARO,
                font=dict(color=GRIS_TEXTO),
            )

            st.plotly_chart(
                fig_box,
                use_container_width=True,
                height = 325
            )


st.divider()

st.caption(
    "Nota: este reporte muestra únicamente propiedades de reporte a cliente. "
    "Los límites de consistencia y otras pruebas internas de laboratorio no "
    "se incluyen aquí."
)