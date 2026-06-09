import streamlit as st
import pandas as pd
from ml_extractor import obtener_tendencias_ml, buscar_precio_promedio_ml
from fb_extractor import obtener_posts_monterrey
from processor import analizar_demanda_y_marcas
import urllib.parse

st.set_page_config(page_title="Radar Monterrey 2.0", page_icon="📡", layout="wide")

st.title("📡 Radar de Intención de Compra 2.0 - Monterrey")
st.markdown("Ahora con **Detección de Marcas**, **Precios en Vivo** y **Enlaces Directos**.")
st.divider()

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📦 Top Búsquedas (ML)")
    tendencias = obtener_tendencias_ml()
    df_ml = pd.DataFrame({"Tendencia": tendencias})
    st.dataframe(df_ml, use_container_width=True, hide_index=True)

with col2:
    st.subheader("💬 Oportunidades de Venta Local")
    posts = obtener_posts_monterrey()
    
    df_oportunidades = analizar_demanda_y_marcas(posts)
    
    precios_ml = []
    enlaces_ml = []
    
    for index, row in df_oportunidades.iterrows():
        termino_busqueda = f"{row['Producto']} {row['Marca']}" if row['Marca'] != "Genérica" else row['Producto']
        
        # 1. Buscamos el precio
        precio = buscar_precio_promedio_ml(termino_busqueda)
        precios_ml.append(precio)
        
        # 2. Generamos el enlace directo a Mercado Libre
        termino_url = urllib.parse.quote(termino_busqueda)
        enlace = f"https://listado.mercadolibre.com.mx/{termino_url}"
        enlaces_ml.append(enlace)
        
    df_oportunidades["Precio Promedio"] = precios_ml
    df_oportunidades["Enlace Directo"] = enlaces_ml
    
    # Configuramos la tabla para que el enlace sea un botón azul clickeable
    st.dataframe(
        df_oportunidades, 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "Enlace Directo": st.column_config.LinkColumn("Comprar / Ver Ofertas", display_text="Ver productos 🔗")
        }
    )
