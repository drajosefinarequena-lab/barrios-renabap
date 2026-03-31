# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Visor Barrios RENABAP", page_icon="🏘️", layout="wide")

# Estilo para mejorar la visualización de las métricas
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e1e4e8; }
    </style>
    """, unsafe_allow_html=True)

# 2. CARGA DE DATOS CON MANEJO DE ERRORES
@st.cache_data
def cargar_datos_renabap():
    file_path = '20231205_info_publica_datos_barrios (2).csv'
    if not os.path.exists(file_path):
        return None
    try:
        # Cargamos el CSV ignorando líneas con errores (como la 173)
        df = pd.read_csv(file_path, encoding='utf-8', on_bad_lines='skip', engine='python')
        df.columns = [c.strip() for c in df.columns]
        return df
    except:
        return None

df = cargar_datos_renabap()

if df is not None:
    st.title("🏘️ Monitor Nacional de Barrios Populares")
    
    # --- FILTROS LATERALES ---
    st.sidebar.header("Filtros Territoriales")
    provincias_sel = st.sidebar.multiselect("Seleccionar Provincia/s:", sorted(df['provincia'].unique()))
    
    df_filtrado = df.copy()
    if provincias_sel:
        df_filtrado = df_filtrado[df_filtrado['provincia'].isin(provincias_sel)]
        
    localidades_sel = st.sidebar.multiselect("Seleccionar Localidad/es:", sorted(df_filtrado['localidad'].unique()))
    if localidades_sel:
        df_filtrado = df_filtrado[df_filtrado['localidad'].isin(localidades_sel)]

    # --- MÉTRICAS DE RESUMEN ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total de Barrios", f"{len(df_filtrado):,}")
    c2.metric("Familias (Aprox.)", f"{int(df_filtrado['cantidad_familias_aproximada'].sum()):,}")
    c3.metric("Viviendas (Aprox.)", f"{int(df_filtrado['cantidad_viviendas_aproximadas'].sum()):,}")
    c4.metric("Superficie Total", f"{df_filtrado['superficie_m2'].sum() / 1_000_000:.2f} km²")

    st.markdown("---")

    # --- ANÁLISIS DE INFRAESTRUCTURA ---
    col_a, col_b = st.columns(2)
    with col_a:
        fig_agua = px.pie(df_filtrado, names='agua_corriente', title="Acceso a Agua Corriente")
        st.plotly_chart(fig_agua, use_container_width=True)
    with col_b:
        fig_elec = px.pie(df_filtrado, names='energia_electrica', title="Conexión Eléctrica", hole=0.4)
        st.plotly_chart(fig_elec, use_container_width=True)

    # --- SECCIÓN DE TIPOLOGÍA (AQUÍ ESTABA EL ERROR) ---
    st.subheader("📈 Tipología y Antigüedad")
    col_c, col_d = st.columns(2)

    with col_c:
        # CORRECCIÓN: Renombramos las columnas manualmente para evitar el ValueError
        df_tipo = df_filtrado['clasificacion_barrio'].value_counts().reset_index()
        df_tipo.columns = ['Tipo', 'Cantidad'] # Forzamos nombres claros que Plotly entienda
        
        fig_tipo = px.bar(df_tipo, x='Tipo', y='Cantidad', color='Tipo',
                          title="Clasificación de los Barrios")
        st.plotly_chart(fig_tipo, use_container_width=True)

    with col_d:
        df_decada = df_filtrado['decada_de_creacion'].value_counts().reset_index()
        df_decada.columns = ['Década', 'Barrios']
        df_decada = df_decada.sort_values('Década')
        
        fig_time = px.line(df_decada, x='Década', y='Barrios', markers=True, 
                           title="Evolución: Década de Creación")
        st.plotly_chart(fig_time, use_container_width=True)

    # --- TABLA DE DATOS ---
    with st.expander("📄 Ver listado detallado"):
        st.dataframe(df_filtrado[['nombre_barrio', 'provincia', 'localidad', 'cantidad_familias_aproximada']], 
                     use_container_width=True)
else:
    st.error("Asegúrate de que el archivo CSV esté en el repositorio con el nombre exacto.")
