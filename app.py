# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Visor Barrios RENABAP", page_icon="🏘️", layout="wide")

# Estilo personalizado para mejorar la visualización
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e1e4e8; }
    </style>
    """, unsafe_allow_html=True)

# 2. CARGA DE DATOS
@st.cache_data
def cargar_datos_renabap():
    file_path = '20231205_info_publica_datos_barrios (2).csv'
    if not os.path.exists(file_path):
        st.error(f"No se encontró el archivo {file_path} en el repositorio.")
        return None
    
    try:
        # Cargamos el CSV ignorando líneas con errores para evitar caídas
        df = pd.read_csv(file_path, encoding='utf-8', on_bad_lines='skip', engine='python')
        # Limpieza básica de nombres de columnas
        df.columns = [c.strip() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Error al procesar el CSV: {e}")
        return None

df = cargar_datos_renabap()

if df is not None:
    # --- TÍTULO Y BANNER ---
    st.title("🏘️ Monitor Nacional de Barrios Populares")
    st.markdown("Visualización de datos oficiales del Registro Nacional de Barrios Populares (RENABAP).")
    
    # --- FILTROS EN BARRA LATERAL ---
    st.sidebar.header("Filtros Territoriales")
    
    lista_provincias = sorted(df['provincia'].unique())
    provincias_sel = st.sidebar.multiselect("Seleccionar Provincia/s:", lista_provincias)
    
    # Filtrado dinámico
    df_filtrado = df.copy()
    if provincias_sel:
        df_filtrado = df_filtrado[df_filtrado['provincia'].isin(provincias_sel)]
        
    lista_localidades = sorted(df_filtrado['localidad'].unique())
    localidades_sel = st.sidebar.multiselect("Seleccionar Localidad/es:", lista_localidades)
    
    if localidades_sel:
        df_filtrado = df_filtrado[df_filtrado['localidad'].isin(localidades_sel)]

    # --- MÉTRICAS PRINCIPALES ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total de Barrios", f"{len(df_filtrado):,}")
    with col2:
        total_familias = df_filtrado['cantidad_familias_aproximada'].sum()
        st.metric("Familias (Aprox.)", f"{int(total_familias):,}")
    with col3:
        total_viviendas = df_filtrado['cantidad_viviendas_aproximadas'].sum()
        st.metric("Viviendas (Aprox.)", f"{int(total_viviendas):,}")
    with col4:
        sup_total = df_filtrado['superficie_m2'].sum() / 1_000_000
        st.metric("Superficie Total", f"{sup_total:.2f} km²")

    st.markdown("---")

    # --- ANÁLISIS DE INFRAESTRUCTURA ---
    st.subheader("📊 Acceso a Servicios Básicos")
    c1, c2 = st.columns(2)

    with c1:
        # Gráfico de Agua Corriente
        fig_agua = px.pie(df_filtrado, names='agua_corriente', title="Acceso a Agua Corriente",
                          color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_agua, use_container_width=True)

    with c2:
        # Gráfico de Energía Eléctrica
        fig_elec = px.pie(df_filtrado, names='energia_electrica', title="Conexión Eléctrica",
                          hole=0.4, color_discrete_sequence=px.colors.qualitative.Safe)
        st.plotly_chart(fig_elec, use_container_width=True)

    # --- CLASIFICACIÓN Y CREACIÓN ---
    st.subheader("📈 Tipología y Antigüedad")
    c3, c4 = st.columns(2)

    with c3:
        # Clasificación de barrios
        fig_tipo = px.bar(df_filtrado['clasificacion_barrio'].value_counts().reset_index(),
                          x='index', y='clasificacion_barrio', 
                          labels={'index': 'Tipo', 'clasificacion_barrio': 'Cantidad'},
                          title="Clasificación de los Barrios", color='index')
        st.plotly_chart(fig_tipo, use_container_width=True)

    with c4:
        # Década de creación
        decadas = df_filtrado['decada_de_creacion'].value_counts().sort_index()
        fig_time = px.line(decadas, title="Evolución: Década de Creación", 
                           markers=True, labels={'value': 'Barrios creados', 'index': 'Década'})
        st.plotly_chart(fig_time, use_container_width=True)

    # --- TABLA DE DATOS ---
    with st.expander("📄 Ver listado detallado de barrios"):
        st.dataframe(df_filtrado[['nombre_barrio', 'provincia', 'departamento', 'localidad', 
                                  'cantidad_familias_aproximada', 'clasificacion_barrio']], 
                     use_container_width=True)

    st.sidebar.markdown("---")
    st.sidebar.info(f"Visualizando {len(df_filtrado)} registros.")
