"""
material_catalog.py — Catálogo canónico de materiales y esquema de columnas
de la bitácora.

Convenciones:
  * "tamices": mallas MEDIDAS en la bitácora, ya normalizadas por
    transform.py (sin el prefijo "Malla " y con "1½" escrito como "1 1/2"),
    en el mismo orden en que aparecen en el Excel.
  * "propiedades": propiedades client-facing, con el nombre EXACTO de la
    columna del Excel (incluyendo unidades).
  * "internas": columnas de laboratorio que NO se muestran al cliente.

Cualquier columna del Excel que no esté en ninguna de las tres listas hace
que transform.py falle a propósito (detecta cambios en la bitácora fuente).

Los límites normativos CEMEX (min/max por malla) viven en dashboard.py.
"""

# Columnas internas que se repiten en varios materiales
_CONSISTENCIA = ["Límite Líquido (%)", "Límite Plástico (%)", "Índice Plástico (%)"]

_PROPS_GRAVA = [
    "%PXL",
    "%H",
    "Densidad (g/cm3)",
    "Absorción (%)",
    "P.V. Suelto (kg/m3)",
    "P.V. Compacto (kg/m3)",
    "Coef. de Forma",
]

_INTERNAS_BASE = [
    "3/4", "3/8", "No.4", "No.10", "No.40", "No.200",  # mallas: sin curva a cliente
    "VRS/CBR (%)",
    "% Partículas Trituradas",
    "Desgaste Los Ángeles (%)",
] + _CONSISTENCIA

# ============================================================
# Esquema de columnas por material
# ============================================================

MATERIAL_SCHEMA = {
    "Arena No.4": {
        "tamices": ["No.4", "No.8", "No.16", "No.30", "No.50", "No.100"],
        "propiedades": [
            "Módulo de Finura",
            "%Humedad",
            "Masa Vol. Suelta (kg/m3)",
            "Masa Vol. Compactada (kg/m3)",
            "Densidad Relativa",
            "Absorción (%)",
            "Contenido de Finos (%)",
        ],
        "internas": _CONSISTENCIA + ["Azul de Metileno"],
    },
    "Grava 10mm-3/8": {
        "tamices": ["3/8", "No.4", "No.8", "No.16", "No.30", "No.50"],
        "propiedades": _PROPS_GRAVA,
        "internas": _CONSISTENCIA,
    },
    "Grava 20mm-3/4": {
        "tamices": ["3/4", "1/2", "3/8", "No.4", "No.8", "No.16"],
        "propiedades": _PROPS_GRAVA,
        "internas": _CONSISTENCIA,
    },
    "Grava 40mm-1½": {
        "tamices": ["1 1/2", "1", "3/4", "1/2", "3/8", "No.4"],
        "propiedades": _PROPS_GRAVA,
        "internas": _CONSISTENCIA,
    },
    "Base Hidráulica 60Finos/40Gruesos": {
        # Sin curva granulométrica en el reporte a cliente
        "tamices": [],
        "propiedades": ["Equivalente de Arena (%)"],
        "internas": _INTERNAS_BASE,
    },
    "Base Hidráulica 80/20": {
        "tamices": [],
        "propiedades": ["Equivalente de Arena (%)"],
        "internas": _INTERNAS_BASE,
    },
    # Grava 13mm intencionalmente excluida: no existe en producción
}

# ============================================================
# Orden global de mallas, de mayor a menor abertura, con la charola al
# final. Sirve para ordenar el eje X de la curva aunque las mallas medidas
# y las de los límites normativos no coincidan del todo.
# ============================================================

ORDEN_MALLAS = [
    "3", "2", "1 1/2", "1", "3/4", "1/2", "3/8",
    "No.4", "No.8", "No.10", "No.16", "No.30", "No.40", "No.50",
    "No.100", "No.200", "Ch",
]


def category_lookup():
    lookup = {}

    for mat, cfg in MATERIAL_SCHEMA.items():

        # Tamices (curva granulométrica)
        for prop in cfg["tamices"]:
            lookup[(mat, prop)] = "sieve"

        # Propiedades mostradas al cliente
        for prop in cfg["propiedades"]:
            lookup[(mat, prop)] = "client"

        # Columnas internas de laboratorio (nunca al cliente)
        for prop in cfg["internas"]:
            lookup[(mat, prop)] = "internal"

    return lookup