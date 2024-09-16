import pandas as pd

def load_and_process_data(file, data_type):
    df = pd.read_excel(file)
    
    if data_type == "Fiscalizados":
        df = df.rename(columns={
            "Fecha": "Fecha",
            "Código interno": "Codigo_Interno",
            "Región": "Region",
            "Nombre supervisor": "Nombre_Supervisor",
            "Estado supervisión": "Estado_Supervision"
        })
        df["Estado_Supervision"] = "Fiscalizado"
        df["Tipo_Fiscalizacion"] = "Normal"
    elif data_type == "Prefiscalizados":
        df = df.rename(columns={
            "Fecha": "Fecha",
            "Numero Comercio": "Codigo_Interno",
            "Region": "Region",
            "Nombre Fiscalizador": "Nombre_Supervisor"
        })
        df["Estado_Supervision"] = "Prefiscalizado"
        df["Tipo_Fiscalizacion"] = "Normal"
    elif data_type == "Fiscalizados CMC":
        df = df.rename(columns={
            "Fecha": "Fecha",
            "Numero Comercio": "Codigo_Interno",
            "Region": "Region",
            "Nombre": "Nombre_Supervisor"
        })
        df["Estado_Supervision"] = "Fiscalizado"
        df["Tipo_Fiscalizacion"] = "CMC"
    
    if "Región" in df.columns:
        df = df.rename(columns={"Región": "Region"})
    
    # Convertir fecha al formato correcto (día/mes/año)
    df["Fecha"] = pd.to_datetime(df["Fecha"], dayfirst=True, errors='coerce')
    df["Mes"] = df["Fecha"].dt.strftime('%B').map({
        'January': 'Enero', 'February': 'Febrero', 'March': 'Marzo', 'April': 'Abril', 
        'May': 'Mayo', 'June': 'Junio', 'July': 'Julio', 'August': 'Agosto', 
        'September': 'Septiembre', 'October': 'Octubre', 'November': 'Noviembre', 'December': 'Diciembre'
    })
    
    # Asegurar que Codigo_Interno sea tipo string
    df["Codigo_Interno"] = df["Codigo_Interno"].astype(str)
    
    # Unificar nombres de regiones
    region_mapping = {
        "Antofagasta": "ANTOFAGASTA",
        "Arica y Parinacota": "ARICA Y PARINACOTA",
        "Atacama": "ATACAMA",
        "Aysén": "AISÉN DEL GRAL. CARLOS IBAÑEZ DEL CAMPO",
        "Biobío": "DEL BIOBÍO",
        "Coquimbo": "COQUIMBO",
        "La Araucanía": "DE LA ARAUCANÍA",
        "Los Lagos": "DE LOS LAGOS",
        "Los Ríos": "DE LOS RÍOS",
        "Magallanes": "MAGALLANES Y DE LA ANTÁRTICA CHILENA",
        "Maule": "DEL MAULE",
        "Metropolitana": "METROPOLITANA DE SANTIAGO",
        "Ñuble": "DE ÑUBLE",
        "O'Higgins": "DEL LIBERTADOR GRAL. BERNARDO O´HIGGINS",
        "Tarapacá": "TARAPACÁ",
        "Valparaíso": "VALPARAISO"
    }
    df["Region"] = df["Region"].replace(region_mapping)
    
    # Unificar nombres de supervisores
    supervisor_mapping = {
        "Alejandra Ibarra": "EUGENIA IBARRA",
        "Angela Vidal": "ANGELA VIDAL",
        "Barbara Alvarado  (EDENRED)": "BÁRBARA  ALVARADO",
        "Camila Lopez": "CAMILA LOPEZ",
        "Camila Sierra": "CAMILA SIERRA",
        "Catherine Espinoza": "CATHERINE  ESPINOZA",
        "Ceci Zapata": "CECILIA  ZAPATA CONTRERAS",
        "Claudia Vera": "CLAUDIA  VERA",
        "Claudio Vergara": "CLAUDIO VERGARA",
        "Daniela Sanmartin": "DANIELA SAN MARTIN",
        "Deissy Pinochet": "DEISSY  PINOCHET",
        "Diego Scheel": "DIEGO  SCHEEL",
        "Dominique Constenla": "DOMINIQUE CONSTENLA",
        "Francisca Contreras": "FRANCISCA CONTRERAS",
        "Ignacio Barros": "IGNACIO  BARRIOS",
        "Isabel Diaz": "ISABEL DIAZ",
        "Karen Barboza": "KAREN BARBOZA",
        "Kathi Olivares": "KATHERIN  OLIVARES",
        "Maria Jose Hermosilla": "MARIAJOSE  HERMOSILLA",
        "Maria Oyarzun": "MARIA  OYARZUN",
        "Martin Ibañez": "MARTIN  IBAÑEZ",
        "Melisa Marin": "MELISA  MARIN",
        "Nicole Aravena": "NICOLE ARAVENA",
        "Nicole Toledo": "NICOLE  TOLEDO",
        "Paulina Alvarez": "PAULINA ALVAREZ",
        "Sebastian Cornejo": "SEBASTIÁN IGNACIO CORNEJO LEPPE",
        "Sofia Aranguiz": "SOFIA  ARANGUIZ",
        "Tamara Ortega": "TAMARA ORTEGA",
        "Tania Tapia": "TANIA TAPIA ARAYA",
        "Tomas Guzman": "TOMÁS  GUZMÁN",
        "Valentia Elia": "VALENTINA  ELIA",
        "Veronica Cordova": "VERÓNICA CÓRDOVA",
        "Victoria Landeros": "VICTORIA LANDEROS"
    }
    df["Nombre_Supervisor"] = df["Nombre_Supervisor"].replace(supervisor_mapping)
    
    return df[["Fecha", "Codigo_Interno", "Region", "Nombre_Supervisor", "Estado_Supervision", "Mes", "Tipo_Fiscalizacion"]].dropna(subset=["Fecha"])