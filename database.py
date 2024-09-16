import sqlite3
import pandas as pd
from sqlalchemy import create_engine
import os

DB_NAME = 'supervisiones.db'
LOCALES_DB_NAME = 'locales_db.db'

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    
    # Crear tablas si no existen
    cur.execute('''CREATE TABLE IF NOT EXISTS main_database
                   (Fecha TEXT, Codigo_Interno TEXT, Region TEXT, 
                    Nombre_Supervisor TEXT, Estado_Supervision TEXT, 
                    Mes TEXT, Tipo_Fiscalizacion TEXT, Aprobado INTEGER)''')
    
    cur.execute('''CREATE TABLE IF NOT EXISTS temp_database
                   (Fecha TEXT, Codigo_Interno TEXT, Region TEXT, 
                    Nombre_Supervisor TEXT, Estado_Supervision TEXT, 
                    Mes TEXT, Tipo_Fiscalizacion TEXT)''')
    
    cur.execute('''CREATE TABLE IF NOT EXISTS inconsistencias
                   (Fecha TEXT, Codigo_Interno TEXT, Region TEXT, 
                    Nombre_Supervisor TEXT, Estado_Supervision TEXT, 
                    Mes TEXT, Tipo_Fiscalizacion TEXT)''')
    
    conn.commit()
    conn.close()

    # Copiar datos de main_database.xlsx a la base de datos SQL si existe
    if os.path.exists("main_database.xlsx"):
        df = pd.read_excel("main_database.xlsx")
        engine = create_engine(f'sqlite:///{DB_NAME}')
        df.to_sql('main_database', engine, if_exists='replace', index=False)
        print("Datos de main_database.xlsx copiados a la base de datos SQL.")

    init_locales_db()

def init_locales_db():
    engine = create_engine(f'sqlite:///{LOCALES_DB_NAME}')
    if os.path.exists("locales_por_supervisar.xlsx"):
        df = pd.read_excel("locales_por_supervisar.xlsx")
        df['Código interno'] = df['Código interno'].astype(str)
        df.to_sql('locales', engine, if_exists='replace', index=False)
        print("Datos de locales_por_supervisar.xlsx copiados a la base de datos locales_db.")

def load_main_database():
    engine = create_engine(f'sqlite:///{DB_NAME}')
    df = pd.read_sql_table('main_database', engine)
    df["Fecha"] = pd.to_datetime(df["Fecha"])
    df["Codigo_Interno"] = df["Codigo_Interno"].astype(str)
    return df

def load_temp_database():
    engine = create_engine(f'sqlite:///{DB_NAME}')
    df = pd.read_sql_table('temp_database', engine)
    df["Fecha"] = pd.to_datetime(df["Fecha"])
    df["Codigo_Interno"] = df["Codigo_Interno"].astype(str)
    return df

def save_temp_database(df):
    engine = create_engine(f'sqlite:///{DB_NAME}')
    df["Fecha"] = df["Fecha"].dt.strftime('%Y-%m-%d')
    df["Codigo_Interno"] = df["Codigo_Interno"].astype(str)
    df.to_sql('temp_database', engine, if_exists='replace', index=False)

def save_main_database(df):
    engine = create_engine(f'sqlite:///{DB_NAME}')
    df["Fecha"] = df["Fecha"].dt.strftime('%Y-%m-%d')
    df["Codigo_Interno"] = df["Codigo_Interno"].astype(str)
    df.to_sql('main_database', engine, if_exists='replace', index=False)

def load_locales_db():
    engine = create_engine(f'sqlite:///{LOCALES_DB_NAME}')
    df = pd.read_sql_table('locales', engine)
    df['Código interno'] = df['Código interno'].astype(str)
    return df

def save_locales_db(df):
    engine = create_engine(f'sqlite:///{LOCALES_DB_NAME}')
    df['Código interno'] = df['Código interno'].astype(str)
    df.to_sql('locales', engine, if_exists='replace', index=False)

def load_locations_to_supervise(main_db):
    locales_db = load_locales_db()
    
    # Ordenar main_db por fecha y obtener el último estado para cada Codigo_Interno
    latest_status = main_db.sort_values('Fecha').groupby('Codigo_Interno').last()
    
    # Mapear el estado de supervisión más reciente a los locales
    locales_db['Estado_Supervision'] = locales_db['Código interno'].map(latest_status['Estado_Supervision'])
    locales_db['Estado_Supervision'] = locales_db['Estado_Supervision'].fillna('Disponible')
    
    return locales_db

def load_inconsistencias():
    engine = create_engine(f'sqlite:///{DB_NAME}')
    df = pd.read_sql_table('inconsistencias', engine)
    df["Fecha"] = pd.to_datetime(df["Fecha"])
    df["Codigo_Interno"] = df["Codigo_Interno"].astype(str)
    return df

def save_inconsistencias(df):
    engine = create_engine(f'sqlite:///{DB_NAME}')
    df["Fecha"] = df["Fecha"].dt.strftime('%Y-%m-%d')
    df["Codigo_Interno"] = df["Codigo_Interno"].astype(str)
    df.to_sql('inconsistencias', engine, if_exists='replace', index=False)

def load_all_data():
    main_db = load_main_database()
    temp_db = load_temp_database()
    inconsistencias_db = load_inconsistencias()
    return pd.concat([main_db, temp_db, inconsistencias_db]).drop_duplicates(subset=["Codigo_Interno", "Fecha"], keep="last")

# Inicializar la base de datos
init_db()