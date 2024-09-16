import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import base64
from config import REGIONS, MONTHLY_GOALS, MESES, logo
from data_processing import load_and_process_data
from database import (load_main_database, load_temp_database, save_temp_database, 
                      save_main_database, load_locales_db, save_locales_db, init_db, 
                      load_locations_to_supervise, load_inconsistencias, save_inconsistencias,
                      load_all_data)
from visualization import create_heatmap
from utils import compare_with_client_list

# Inicializar la base de datos
init_db()

st.set_page_config(page_title="Supervisores CMC360 Dashboard", page_icon=logo, layout="wide")

# Agregar estilos personalizados
st.markdown("""
<style>
.stButton>button {
    background-color: #201E43;
    color: #EEEEEE;
}
.stTextInput>div>div>input {
    background-color: #EEEEEE;
}
.stSelectbox>div>div>div {
    background-color: #134B70;
    color: #EEEEEE;
}
.stDataFrame {
    border: 1px solid #508C9B;
}
.stProgress > div > div > div > div {
    background-color: #7A1CAC;
}
</style>
""", unsafe_allow_html=True)

def main():
    
    def load_css(file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    load_css('style.css')
    
    st.title("Reporte de Supervisión de Locales")

    # Cargar todos los datos
    all_data = load_all_data()

    # Sidebar
    st.sidebar.image(logo, width=90)
    st.sidebar.header("Filtros")
    
    # Mover la selección de mes al sidebar
    selected_month = st.sidebar.selectbox("Seleccionar mes para las metas y visualización", ["Total"] + MESES)
    
    supervisors = all_data["Nombre_Supervisor"].unique()
    selected_supervisor = st.sidebar.multiselect("Supervisor", supervisors)
    
    regions = all_data["Region"].unique()
    selected_region = st.sidebar.multiselect("Región", regions)
    
    if not all_data.empty and "Fecha" in all_data.columns:
        min_date = all_data["Fecha"].min().date()
        max_date = all_data["Fecha"].max().date()
        if pd.notnull(min_date) and pd.notnull(max_date):
            start_date = st.sidebar.date_input("Fecha de inicio", min_date)
            end_date = st.sidebar.date_input("Fecha de fin", max_date)
        else:
            start_date = st.sidebar.date_input("Fecha de inicio")
            end_date = st.sidebar.date_input("Fecha de fin")
    else:
        start_date = st.sidebar.date_input("Fecha de inicio")
        end_date = st.sidebar.date_input("Fecha de fin")

    # Subir archivo
    uploaded_file = st.file_uploader("Cargar archivo de supervisión", type=["xls", "xlsx"])
    if uploaded_file is not None:
        data_type = st.radio("Tipo de datos", ["Fiscalizados", "Prefiscalizados", "Fiscalizados CMC"])
        
        df = load_and_process_data(uploaded_file, data_type)
        
        # Verificar duplicados en all_data
        existing_codes = set(all_data["Codigo_Interno"])
        new_records = df[~df["Codigo_Interno"].isin(existing_codes)]
        duplicates = df[df["Codigo_Interno"].isin(existing_codes)]
        
        # Eliminar duplicados dentro del nuevo archivo
        new_records = new_records.drop_duplicates(subset=["Codigo_Interno"], keep="last")
        
        if len(new_records) == 0 and len(duplicates) == 0:
            st.warning("Todos los registros ya existen en la base de datos.")
        else:
            # Agregar nuevos registros a temp_db
            temp_db = load_temp_database()
            temp_db = pd.concat([temp_db, new_records])
            save_temp_database(temp_db)
            
            # Guardar duplicados
            inconsistencias_db = load_inconsistencias()
            inconsistencias_db = pd.concat([inconsistencias_db, duplicates])
            save_inconsistencias(inconsistencias_db)
            
            st.success(f"Se agregaron {len(new_records)} nuevos registros a la base de datos temporal.")
            st.warning(f"Se encontraron {len(duplicates)} registros duplicados.")

    # Aplicar filtros
    filtered_data = all_data
    if selected_supervisor:
        filtered_data = filtered_data[filtered_data["Nombre_Supervisor"].isin(selected_supervisor)]
    if selected_region:
        filtered_data = filtered_data[filtered_data["Region"].isin(selected_region)]
    
    filtered_data = filtered_data[
        (filtered_data["Fecha"].dt.date >= start_date) & 
        (filtered_data["Fecha"].dt.date <= end_date)
    ]

    # Métricas principales
    st.header(f"Métricas Principales - {selected_month}")
    col1, col2, col3, col4 = st.columns(4)

    if selected_month != "Total":
        month_data = filtered_data[filtered_data['Mes'] == selected_month]
    else:
        month_data = filtered_data

    col1.metric("Total Supervisiones", len(month_data))
    col2.metric("Fiscalizados", len(month_data[month_data["Estado_Supervision"] == "Fiscalizado"]))
    col3.metric("Prefiscalizados", len(month_data[month_data["Estado_Supervision"] == "Prefiscalizado"]))
    col4.metric("Fiscalizados CMC", len(month_data[month_data["Tipo_Fiscalizacion"] == "CMC"]))

    # Progreso de metas
    if selected_month in MONTHLY_GOALS or selected_month == "Total":
        st.header(f"Progreso de Metas para {selected_month}")
        
        if selected_month != "Total":
            current_goals = dict(zip(REGIONS, MONTHLY_GOALS[selected_month]))
            total_goal = sum(current_goals.values())
            total_progress = len(month_data[month_data["Estado_Supervision"] == "Fiscalizado"])
        else:
            current_goals = {region: sum(MONTHLY_GOALS[month][i] for month in MESES) for i, region in enumerate(REGIONS)}
            total_goal = sum(current_goals.values())
            total_progress = len(filtered_data[filtered_data["Estado_Supervision"] == "Fiscalizado"])
        
        total_progress_percentage = min((total_progress / total_goal) * 100 if total_goal > 0 else 0, 100)

        st.write(f"Progreso total: {total_progress} de {total_goal} ({total_progress_percentage:.2f}%)")
        st.progress(min(total_progress_percentage / 100, 1.0))

        st.subheader("Progreso por Región")
        
        # Preparar datos para los gráficos
        regions = list(current_goals.keys())
        goals = list(current_goals.values())
        progress = [len(month_data[(month_data["Region"] == region) & (month_data["Estado_Supervision"] == "Fiscalizado")]) for region in regions]
        percentages = [min((p / g) * 100 if g > 0 else 0, 100) for p, g in zip(progress, goals)]

        # Opción de tipo de gráfico
        chart_type = st.selectbox("Seleccionar tipo de gráfico", ["Barras de progreso", "Gráfico de barras", "Gráfico de pie"])

        if chart_type == "Barras de progreso":
            for region, goal, prog, perc in zip(regions, goals, progress, percentages):
                st.write(f"{region}: {prog} de {goal} ({perc:.2f}%)")
                st.progress(min(perc / 100, 1.0))

        elif chart_type == "Gráfico de barras":
            fig = go.Figure(data=[
                go.Bar(name='Meta', x=regions, y=goals, marker_color='#201E43'),
                go.Bar(name='Progreso', x=regions, y=progress, marker_color='#508C9B')
            ])
            fig.update_layout(barmode='group', height=600, title="Progreso vs Meta por Región")
            st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Gráfico de pie":
            st.subheader("Progreso por Región")
            cols = st.columns(4)  # Ajusta este número según el diseño que prefieras
            
            for i, (region, goal, prog) in enumerate(zip(regions, goals, progress)):
                with cols[i % 4]:  # Esto distribuirá los gráficos en las columnas
                    remaining = max(goal - prog, 0)  # Aseguramos que el valor no sea negativo
                    pie_data = pd.DataFrame({
                        'Categoría': ['Fiscalizados', 'Faltantes'],
                        'Cantidad': [prog, remaining]
                    })
                    fig = px.pie(pie_data, values='Cantidad', names='Categoría',
                                 title=f'{region}',
                                 color_discrete_map={'Fiscalizados': '#508C9B', 'Faltantes': '#201E43'})
                    fig.update_traces(textposition='inside', textinfo='percent+value')
                    fig.update_layout(showlegend=False, height=300, width=300)
                    st.plotly_chart(fig, use_container_width=True)
                    st.write(f"Meta: {goal}")
                    st.write(f"Progreso: {prog} ({(prog/goal*100):.2f}%)")
                    st.write(f"Faltante: {remaining}")

            # Gráfico de pie para el total
            st.subheader("Progreso Total")
            total_remaining = max(total_goal - total_progress, 0)
            total_pie_data = pd.DataFrame({
                'Categoría': ['Fiscalizados', 'Faltantes'],
                'Cantidad': [total_progress, total_remaining]
            })
            fig_total = px.pie(total_pie_data, values='Cantidad', names='Categoría',
                               title='Progreso Total',
                               color_discrete_map={'Fiscalizados': '#508C9B', 'Faltantes': '#201E43'})
            fig_total.update_traces(textposition='inside', textinfo='percent+value')
            fig_total.update_layout(height=400, width=400)
            st.plotly_chart(fig_total, use_container_width=True)
            st.write(f"Meta total: {total_goal}")
            st.write(f"Progreso total: {total_progress} ({(total_progress/total_goal*100):.2f}%)")
            st.write(f"Faltante total: {total_remaining}")

        # Tabla de progreso
        progress_df = pd.DataFrame({
            "Región": regions,
            "Meta": goals,
            "Progreso": progress,
            "Porcentaje": [f"{p:.2f}%" for p in percentages]
        })
        st.dataframe(progress_df)

    # Estado de Locales
    st.header("Estado de Locales")

    locations_to_supervise = load_locations_to_supervise(all_data)

    total_locales = len(locations_to_supervise)
    fiscalizados = len(locations_to_supervise[locations_to_supervise['Estado_Supervision'] == 'Fiscalizado'])
    prefiscalizados = len(locations_to_supervise[locations_to_supervise['Estado_Supervision'] == 'Prefiscalizado'])
    disponibles = len(locations_to_supervise[locations_to_supervise['Estado_Supervision'] == 'Disponible'])

    pie_data = {
        'Categoría': ['Fiscalizados', 'Prefiscalizados', 'Disponibles'],
        'Cantidad': [fiscalizados, prefiscalizados, disponibles]
    }
    
    fig = px.pie(pie_data, values='Cantidad', names='Categoría', 
                 title='Estado de Locales',
                 color_discrete_sequence=['#201E43', '#134B70', '#508C9B'])
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    
    st.plotly_chart(fig)
    
    st.write(f"Total de locales: {total_locales}")
    st.write(f"Fiscalizados: {fiscalizados}")
    st.write(f"Prefiscalizados: {prefiscalizados}")
    st.write(f"Disponibles: {disponibles}")

    # Botón para descargar locales disponibles
    if st.button("Descargar Locales Disponibles"):
        locales_disponibles = locations_to_supervise[locations_to_supervise['Estado_Supervision'] == 'Disponible']
        csv = locales_disponibles.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="locales_disponibles.csv">Descargar CSV</a>'
        st.markdown(href, unsafe_allow_html=True)

    # Mapa de calor
    st.header("Mapa de Calor - Metas de Fiscalización")
    
    # Calcular los datos de fiscalización real
    fiscalized_data = {}
    for region in REGIONS:
        for month in MESES:
            fiscalized_count = len(filtered_data[(filtered_data['Region'] == region) & 
                                               (filtered_data['Mes'] == month) & 
                                               (filtered_data['Estado_Supervision'] == 'Fiscalizado')])
            fiscalized_data[(region, month)] = fiscalized_count
    
    fig_heatmap = create_heatmap(MONTHLY_GOALS, fiscalized_data)
    st.plotly_chart(fig_heatmap, use_container_width=True)

    # Mostrar datos
    st.header("Datos")
    st.dataframe(month_data)

    # Mostrar datos duplicados
    st.header("Datos Duplicados")
    duplicates_data = load_inconsistencias()
    st.dataframe(duplicates_data)

    # Comparación con lista del cliente
    st.header("Comparación con Lista del Cliente")
    client_list_file = st.file_uploader("Cargar lista de aprobados del cliente", type=["xls", "xlsx"])
    if client_list_file is not None:
        client_list = pd.read_excel(client_list_file)
        client_list['Codigo_Interno'] = client_list['Codigo_Interno'].astype(str)
        discrepancies = compare_with_client_list(load_temp_database(), client_list)
        for key, value in discrepancies.items():
            st.subheader(key)
            st.write(value)

        # Opción para aprobar y mover a la base de datos principal
        if st.button("Aprobar y Mover a Base de Datos Principal"):
            temp_db = load_temp_database()
            approved_records = temp_db[temp_db['Codigo_Interno'].isin(client_list['Codigo_Interno'])]
            approved_records['Aprobado'] = True
            main_db = load_main_database()
            main_db = pd.concat([main_db, approved_records])
            save_main_database(main_db)
            
            # Eliminar registros aprobados de la base de datos temporal
            temp_db = temp_db[~temp_db['Codigo_Interno'].isin(client_list['Codigo_Interno'])]
            save_temp_database(temp_db)
            
            st.success("Registros aprobados movidos a la base de datos principal")

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .st-emotion-cache-1v0mbdj{
                margin: 0px 0px 10px 80px;
            }
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

if __name__ == "__main__":
    main()