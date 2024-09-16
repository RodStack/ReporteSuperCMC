from PIL import Image

# Definir las regiones
REGIONS = [
    "AISÉN DEL GRAL. CARLOS IBAÑEZ DEL CAMPO",
    "ANTOFAGASTA",
    "ARICA Y PARINACOTA",
    "ATACAMA",
    "COQUIMBO",
    "DE LA ARAUCANÍA",
    "DE LOS LAGOS",
    "DE LOS RÍOS",
    "DE ÑUBLE",
    "DEL BIOBÍO",
    "DEL LIBERTADOR GRAL. BERNARDO O´HIGGINS",
    "DEL MAULE",
    "MAGALLANES Y DE LA ANTÁRTICA CHILENA",
    "METROPOLITANA DE SANTIAGO",
    "TARAPACÁ",
    "VALPARAISO"
]

# Definir las metas mensuales
MONTHLY_GOALS = {
    "Julio": [9, 20, 15, 11, 31, 53, 31, 43, 36, 113, 24, 42, 10, 551, 12, 78],
    "Agosto": [9, 20, 15, 11, 31, 53, 31, 43, 36, 113, 24, 42, 10, 551, 12, 78],
    "Septiembre": [6, 13, 10, 7, 21, 36, 21, 29, 24, 75, 16, 28, 7, 367, 8, 52],
    "Octubre": [9, 20, 15, 11, 31, 53, 31, 43, 36, 113, 24, 42, 10, 551, 12, 78],
    "Noviembre": [6, 13, 10, 7, 21, 36, 21, 29, 24, 75, 16, 28, 7, 367, 8, 52],
    "Diciembre": [3, 7, 5, 4, 10, 18, 10, 14, 12, 38, 8, 14, 3, 184, 4, 26]
}

# Lista de meses
MESES = ["Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

# Page icon
logo = Image.open('CMC360 Isotípo.png')