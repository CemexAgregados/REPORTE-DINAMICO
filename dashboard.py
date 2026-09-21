"""
Dashboard Cerro Jardín — Reportes de Calidad
Corre con: streamlit run streamlit_app.py
Requiere: streamlit>=1.32, plotly
"""

import datetime as dt

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from material_catalog import MATERIAL_SCHEMA, ORDEN_TAMICES, LIMITES_GRANULOMETRICOS
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
    .stApp {{ background-color: {BLANCO}; }}

    /* ---- Header superior con franja de color ---- */
    .header-banner {{
        background: linear-gradient(90deg, {AZUL} 0%, {AZUL} 60%, {ROJO} 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
    }}
    .header-banner h1 {{
        color: {BLANCO} !important;
        margin: 0;
        font-size: 2rem;
    }}
    .header-banner p {{
        color: {BLANCO} !important;
        opacity: 0.9;
        margin: 0.3rem 0 0 0;
    }}

    /* ---- Sidebar: fondo azul, texto blanco ---- */
    [data-testid="stSidebar"] {{ background-color: {AZUL}; }}
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p {{ color: {BLANCO} !important; }}

    /* ---- Fix de contraste: inputs siempre con fondo blanco y texto oscuro ---- */
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] [data-baseweb="select"] > div,
    [data-testid="stSidebar"] [data-baseweb="input"] {{
        background-color: {BLANCO} !important;
        color: {GRIS_TEXTO} !important;
        border-radius: 6px;
    }}
    [data-testid="stSidebar"] [data-baseweb="select"] *,
    [data-testid="stSidebar"] input {{
        color: {GRIS_TEXTO} !important;
    }}
    [data-baseweb="popover"] * {{ color: {GRIS_TEXTO} !important; }}
    [data-testid="stSidebar"] hr {{ border-color: rgba(255,255,255,0.3); }}

    h2, h3 {{ color: {AZUL}; }}

    /* ---- Tarjetas de sección con color ---- */
    div.st-key-kpis {{
        background-color: {ROJO_CLARO};
        border-left: 6px solid {ROJO};
        border-radius: 10px;
        padding: 1.2rem 1.5rem;
    }}
    div.st-key-granulometria {{
        background-color: {AZUL_CLARO};
        border-left: 6px solid {AZUL};
        border-radius: 10px;
        padding: 1.2rem 1.5rem;
    }}
    div.st-key-tabla {{
        background-color: {BLANCO};
        border: 1px solid #DDDDDD;
        border-top: 6px solid {AZUL};
        border-radius: 10px;
        padding: 1.2rem 1.5rem;
    }}
    div.st-key-tendencia {{
        background-color: {ROJO_CLARO};
        border-left: 6px solid {ROJO};
        border-radius: 10px;
        padding: 1.2rem 1.5rem;
    }}

    [data-testid="stMetricValue"] {{ color: {ROJO}; }}
    [data-testid="stMetricLabel"] {{ color: {GRIS_TEXTO}; }}

    /* ---- Separador de secciones ---- */
    hr {{ border-top: 2px solid {AZUL_CLARO}; }}
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

# ============================================================
# Sidebar: material y periodo
# ============================================================

st.sidebar.title("🏗️ Cerro Jardín")
st.sidebar.caption("Reportes de calidad por material")
st.sidebar.divider()

material = st.sidebar.selectbox("Material", list(MATERIAL_SCHEMA.keys()))

rango = st.sidebar.date_input(
    "Periodo del reporte",
    value=(fecha_max - dt.timedelta(days=30), fecha_max),
    min_value=fecha_min,
    max_value=fecha_max,
)

if len(rango) != 2:
    st.sidebar.info("Selecciona una fecha de inicio y una de fin.")
    st.stop()

fecha_inicio, fecha_fin = rango
if fecha_inicio > fecha_fin:
    st.sidebar.error("La fecha de inicio no puede ser posterior a la de fin.")
    st.stop()

# ============================================================
# Header principal
# ============================================================

st.markdown(
    f"""
    <div class="header-banner">
        <h1>{material}</h1>
        <p>Periodo: {fecha_inicio.strftime('%d/%m/%Y')} — {fecha_fin.strftime('%d/%m/%Y')}</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# Reporte base (promedio del promedio)
# ============================================================

reporte = promedio_del_promedio(
    df_long, material=material, start=str(fecha_inicio), end=str(fecha_fin), solo_cliente=True
)

if reporte.empty or reporte["dias_con_dato"].sum() == 0:
    st.warning("No hay datos de este material en el periodo seleccionado.")
    st.stop()

dias_totales = (fecha_fin - fecha_inicio).days + 1
dias_con_produccion = int(reporte["dias_con_dato"].max())
cobertura_pct = round(100 * dias_con_produccion / dias_totales, 1) if dias_totales else 0

es_granular = material in ORDEN_TAMICES
if es_granular:
    tamices_material = ORDEN_TAMICES[material]
    tamices_df = reporte[reporte["Propiedad"].isin(tamices_material)].copy()
    propiedades_df = reporte[~reporte["Propiedad"].isin(tamices_material)].copy()
else:
    tamices_df = pd.DataFrame()
    propiedades_df = reporte.copy()

# ============================================================
# KPIs de calidad + métricas (tarjeta roja)
# ============================================================

with st.container(key="kpis"):
    st.subheader("📊 KPIs de calidad del periodo")

    col1, col2, col3 = st.columns(3)
    col1.metric("Cobertura del periodo", f"{cobertura_pct}%", f"{dias_con_produccion}/{dias_totales} días")
    col2.metric("Pruebas registradas", int(reporte["dias_con_dato"].sum()))
    col3.metric("Propiedades reportadas", len(propiedades_df))

    if cobertura_pct >= 80:
        st.success(f"✅ Cobertura de datos: {cobertura_pct}% — reporte representativo del periodo.")
    elif cobertura_pct >= 50:
        st.warning(f"⚠️ Cobertura de datos: {cobertura_pct}% — interpretar con cautela.")
    else:
        st.error(f"🔴 Cobertura de datos: {cobertura_pct}% — pocos datos disponibles en el periodo.")

st.write("")

# ============================================================
# Curva granulométrica (tarjeta azul)
# ============================================================

if es_granular and not tamices_df.empty:
    with st.container(key="granulometria"):
        st.subheader("📈 Curva granulométrica")

        orden_presente = [t for t in tamices_material if t in tamices_df["Propiedad"].values]
        tamices_ordenado = tamices_df.set_index("Propiedad").loc[orden_presente].reset_index()

        fig_curva = go.Figure()

        limites = LIMITES_GRANULOMETRICOS.get(material)
        if limites:
            tamices_lim = [t for t in orden_presente if t in limites]
            mins = [limites[t]["min"] for t in tamices_lim]
            maxs = [limites[t]["max"] for t in tamices_lim]

            # Banda de especificación (relleno entre mín y máx)
            fig_curva.add_trace(go.Scatter(
                x=tamices_lim + tamices_lim[::-1],
                y=maxs + mins[::-1],
                fill="toself",
                fillcolor="rgba(0,61,165,0.12)",
                line=dict(color="rgba(0,0,0,0)"),
                name="Banda de especificación",
                hoverinfo="skip",
            ))
            # Líneas de límite explícitas (mejor legibilidad que solo el relleno)
            fig_curva.add_trace(go.Scatter(
                x=tamices_lim, y=maxs, mode="lines", name="Límite superior CEMEX",
                line=dict(color=AZUL, width=1.5, dash="dot"),
            ))
            fig_curva.add_trace(go.Scatter(
                x=tamices_lim, y=mins, mode="lines", name="Límite inferior CEMEX",
                line=dict(color=AZUL, width=1.5, dash="dot"),
            ))

        fig_curva.add_trace(go.Scatter(
            x=tamices_ordenado["Propiedad"],
            y=tamices_ordenado["promedio"],
            mode="lines+markers",
            name="% que pasa (real)",
            line=dict(color=ROJO, width=3),
            marker=dict(size=9, color=ROJO, line=dict(width=1, color=BLANCO)),
        ))

        fig_curva.update_layout(
            xaxis_title="Malla",
            yaxis_title="% que pasa",
            plot_bgcolor=BLANCO,
            paper_bgcolor=AZUL_CLARO,
            font=dict(color=GRIS_TEXTO),
            yaxis=dict(range=[0, 100], gridcolor="#DDE4F0"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
            margin=dict(t=30),
        )
        st.plotly_chart(fig_curva, use_container_width=True)

        if not limites:
            st.caption(
                "⚠️ No hay límites normativos (mín/máx) cargados para este material — "
                "se muestra solo la curva real, sin banda de especificación."
            )
        else:
            fuera_de_norma = tamices_ordenado[
                tamices_ordenado.apply(
                    lambda r: r["Propiedad"] in limites and not (
                        limites[r["Propiedad"]]["min"] <= r["promedio"] <= limites[r["Propiedad"]]["max"]
                    ),
                    axis=1,
                )
            ]
            if not fuera_de_norma.empty:
                mallas_fuera = ", ".join(fuera_de_norma["Propiedad"].tolist())
                st.warning(f"⚠️ Mallas fuera de la banda de especificación en el promedio del periodo: {mallas_fuera}")
            else:
                st.success("✅ Todas las mallas dentro de la banda de especificación CEMEX en el promedio del periodo.")

    st.write("")
elif not es_granular:
    st.info("Este material no incluye curva granulométrica en el reporte a cliente.")
    st.write("")

# ============================================================
# Tabla de resultados
# ============================================================

with st.container(key="tabla"):
    st.subheader("📋 Resultados del periodo")

    tabla = propiedades_df.rename(columns={
        "promedio": "Promedio del periodo",
        "dias_con_dato": "Días con dato",
        "es_no_plastico": "No plástico (NP)",
    }).copy()

    tabla["Promedio del periodo"] = tabla.apply(
        lambda r: "NP" if r.get("No plástico (NP)", False) else round(r["Promedio del periodo"], 2),
        axis=1,
    )
    if "No plástico (NP)" in tabla.columns:
        tabla = tabla.drop(columns="No plástico (NP)")

    st.dataframe(tabla, hide_index=True, use_container_width=True)

st.write("")

# ============================================================
# Tendencia diaria de una propiedad (tarjeta roja)
# ============================================================

with st.container(key="tendencia"):
    st.subheader("📉 Tendencia diaria")

    propiedad_tendencia = st.selectbox(
        "Propiedad a graficar en el tiempo",
        propiedades_df["Propiedad"].tolist(),
    )

    serie = (
        df_long[
            (df_long["Material"] == material)
            & (df_long["Propiedad"] == propiedad_tendencia)
            & (df_long["Fecha"].dt.date >= fecha_inicio)
            & (df_long["Fecha"].dt.date <= fecha_fin)
        ]
        .groupby("Fecha", as_index=False)["Valor"]
        .mean()
    )

    if serie.empty:
        st.info("Sin datos diarios para esta propiedad en el periodo.")
    else:
        fig_tendencia = go.Figure()
        fig_tendencia.add_trace(go.Scatter(
            x=serie["Fecha"], y=serie["Valor"],
            mode="lines+markers",
            line=dict(color=AZUL, width=2),
            marker=dict(size=6, color=ROJO, line=dict(width=1, color=BLANCO)),
        ))
        promedio_periodo = serie["Valor"].mean()
        fig_tendencia.add_hline(
            y=promedio_periodo, line_dash="dash", line_color=ROJO,
            annotation_text=f"Promedio: {promedio_periodo:.2f}", annotation_position="top left",
        )
        fig_tendencia.update_layout(
            xaxis_title="Fecha", yaxis_title=propiedad_tendencia,
            plot_bgcolor=BLANCO, paper_bgcolor=ROJO_CLARO, font=dict(color=GRIS_TEXTO),
            margin=dict(t=20),
        )
        st.plotly_chart(fig_tendencia, use_container_width=True)

st.divider()
st.caption(
    "Nota: este reporte muestra únicamente propiedades de reporte a cliente. "
    "Los límites de consistencia y otras pruebas internas de laboratorio no "
    "se incluyen aquí."
)