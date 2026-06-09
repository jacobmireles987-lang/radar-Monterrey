import streamlit as st
import pandas as pd
from ml_extractor import obtener_tendencias_ml, buscar_precio_promedio_ml
from fb_extractor import obtener_posts_monterrey
from processor import analizar_demanda_y_marcas
import urllib.parse

st.set_page_config(page_title="Radar Arbitraje", page_icon="📡", layout="wide")

st.title("📡 Radar de Arbitraje Comercial")
st.markdown("Compara cuánto ofrece pagar el cliente en **Facebook** vs cuánto te cuesta a ti en **Mercado Libre**.")
st.divider()

col1, col2 = st.columns([1, 2.5]) # Damos más espacio a la tabla grande

with col1:
    st.subheader("📦 Top Búsquedas (ML)")
    tendencias = obtener_tendencias_ml()
    df_ml = pd.DataFrame({"Tendencia": tendencias})
    st.dataframe(df_ml, use_container_width=True, hide_index=True)

with col2:
    st.subheader("💰 Oportunidades de Arbitraje (Spread)")
    posts = obtener_posts_monterrey()
    df_oportunidades = analizar_demanda_y_marcas(posts)
    
    precios_ml = []
    enlaces_ml = []
    margen = []
    
    for index, row in df_oportunidades.iterrows():
        termino_busqueda = f"{row['Producto']} {row['Marca']}" if row['Marca'] != "Genérica" else row['Producto']
        
        # 1. Obtenemos ambos precios (ML y FB)
        precio_ml = buscar_precio_promedio_ml(termino_busqueda)
        presupuesto_fb = row['Presupuesto_FB']
        
        # 2. Calculamos la Ganancia (Oferta del cliente - Tu costo de compra)
        if pd.notna(presupuesto_fb) and precio_ml is not None:
            ganancia = presupuesto_fb - precio_ml
            margen.append(ganancia)
            precios_ml.append(precio_ml)
        else:
            margen.append(None)
            precios_ml.append(precio_ml if precio_ml is not None else None)
        
        # 3. Creamos el enlace
        termino_url = urllib.parse.quote(termino_busqueda)
        enlaces_ml.append(f"https://listado.mercadolibre.com.mx/{termino_url}")
        
    df_oportunidades["Costo Proveedor (ML)"] = precios_ml
    df_oportunidades["Margen Estimado"] = margen
    df_oportunidades["Enlace Directo"] = enlaces_ml
    
    # Renderizamos la tabla como una hoja financiera
    st.dataframe(
        df_oportunidades, 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "Presupuesto_FB": st.column_config.NumberColumn("Oferta del Cliente (FB)", format="$%d MXN"),
            "Costo Proveedor (ML)": st.column_config.NumberColumn("Costo Proveedor (ML)", format="$%d MXN"),
            "Margen Estimado": st.column_config.NumberColumn("Tu Margen Neto", format="$%d MXN"),
            "Enlace Directo": st.column_config.LinkColumn("Comprar", display_text="Ver ML 🔗")
        }
    )
