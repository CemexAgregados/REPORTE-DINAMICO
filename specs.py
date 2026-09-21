# specs.py

# ============================================================
# Nombres amigables para el reporte
# ============================================================

NOMBRES_REPORTE = {

    "%H": "Contenido de Agua (%Humedad)",

    "%PXL": "Contenido de Finos",

    "M.F.": "Módulo de Finura",

    "Densidad": "Densidad Relativa",

    "Absorción": "Absorción",

    "Coef. De Forma": "Coeficiente de Forma",

    "Equivalente Arena": "Equivalente de Arena",

    "Suelto": "Masa Volumétrica Suelta",

    "Compacto": "Masa Volumétrica Compactada",
}


# ============================================================
# ARENAS
# ============================================================

ARENA_SPECS = {

    "M.F.": {
        "metodo": "NMX-C-111",
        "min": 2.3,
        "max": 3.1,
        "unidad": "%",
    },

    "%H": {
        "metodo": "NMX-C-166",
        "min": "---",
        "max": "---",
        "unidad": "%",
    },

    "Suelto": {
        "metodo": "NMX-C-073",
        "min": "---",
        "max": "---",
        "unidad": "kg/m3",
    },

    "Compacto": {
        "metodo": "NMX-C-073",
        "min": "---",
        "max": "---",
        "unidad": "kg/m3",
    },

    "Densidad": {
        "metodo": "NMX-C-165",
        "min": "---",
        "max": "---",
        "unidad": "---",
    },

    "Absorción": {
        "metodo": "NMX-C-165",
        "min": "---",
        "max": "---",
        "unidad": "%",
    },

    "%PXL": {
        "metodo": "NMX-C-084",
        "min": "---",
        "max": 15,
        "unidad": "%",
    },
}


# ============================================================
# GRAVAS
# ============================================================

GRAVA_SPECS = {

    "%H": {
        "metodo": "NMX-C-166",
        "min": "---",
        "max": "---",
        "unidad": "%",
    },

    "%PXL": {
        "metodo": "NMX-C-084",
        "min": "---",
        "max": 2,
        "unidad": "%",
    },

    "Suelto": {
        "metodo": "NMX-C-073",
        "min": "---",
        "max": "---",
        "unidad": "kg/m3",
    },

    "Compacto": {
        "metodo": "NMX-C-073",
        "min": "---",
        "max": "---",
        "unidad": "kg/m3",
    },

    "Densidad": {
        "metodo": "NMX-C-164",
        "min": "---",
        "max": "---",
        "unidad": "---",
    },

    "Absorción": {
        "metodo": "NMX-C-164",
        "min": "---",
        "max": "---",
        "unidad": "%",
    },

    "Coef. De Forma": {
        "metodo": "ASTM D4791",
        "min": "---",
        "max": "---",
        "unidad": "%",
    },
}


# ============================================================
# MEZCLAS / BASE HIDRÁULICA
# ============================================================

MEZCLA_SPECS = {

    "Equivalente Arena": {
        "metodo": "M-MMP-4-04-004-16",
        "min": "---",
        "max": "---",
        "unidad": "%",
    },
}


# ============================================================
# ESPECIFICACIONES POR MATERIAL
# ============================================================

ESPECIFICACIONES = {

    # --------------------------
    # Arena
    # --------------------------

    "Arena No. 4": ARENA_SPECS,

    # --------------------------
    # Gravas
    # --------------------------

    "Grava 10 mm": GRAVA_SPECS,

    "Grava 20 mm": GRAVA_SPECS,

    "Grava 40 mm": GRAVA_SPECS,

    # --------------------------
    # Mezclas
    # --------------------------

    "Mezcla 60% finos + 40% gruesos": MEZCLA_SPECS,

    "Mezcla 80% finos + 20% gruesos": MEZCLA_SPECS,

}

