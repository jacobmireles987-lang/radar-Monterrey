import streamlit as st
import pandas as pd
from ml_extractor import obtener_tendencias_ml, buscar_precio_promedio_ml
from fb_extractor import obtener_posts_monterrey
from processor import analizar_demanda_y_marcas

st.set_page_config(page_title="Radar Monterrey 2.0", page_icon="📡", layout="wide")

st.title("📡 Radar de Intención de Compra 2.0 - Monterrey")
st.markdown("Ahora con **Detección de Marcas** y **Comparativa de Precios en Vivo** vs Mercado Libre.")
st.divider()

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📦 Top Búsquedas (ML)")
    st.caption("Tendencias en Nuevo León hoy:")
    tendencias = obtener_tendencias_ml()
    df_ml = pd.DataFrame({"Tendencia": tendencias})
    st.dataframe(df_ml, use_container_width=True, hide_index=True)

with col2:
    st.subheader("💬 Oportunidades de Venta Local")
    posts = obtener_posts_monterrey()
    st.caption("Extrayendo productos, marcas y cotizando en tiempo real...")
    
    # Analizamos los textos
    df_oportunidades = analizar_demanda_y_marcas(posts)
    
    # Agregamos la columna de precios conectando a la API
    precios_ml = []
    for index, row in df_oportunidades.iterrows():
        termino_busqueda = f"{row['Producto']} {row['Marca']}" if row['Marca'] != "Genérica" else row['Producto']
        precio = buscar_precio_promedio_ml(termino_busqueda)
        precios_ml.append(precio)
        
    # Esta es la línea clave que dibuja la columna de precios:
    df_oportunidades["Precio Promedio (MercadoLibre)"] = precios_ml
    
    st.dataframe(df_oportunidades, use_container_width=True, hide_index=True)
