import streamlit as st
import pandas as pd
import plotly.express as px
from ml_extractor import obtener_tendencias_ml
from fb_extractor import obtener_posts_monterrey
from processor import extraer_intencion_compra

st.set_page_config(page_title="Radar Monterrey", page_icon="📡", layout="wide")

st.title("📡 Radar de Intención de Compra - Monterrey")
st.markdown("Versión Nube Oficial (Streamlit Cloud)")
st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("📦 Tendencias Mercado Libre")
    st.caption("Extrayendo datos en vivo desde la API oficial...")
    tendencias = obtener_tendencias_ml()
    df_ml = pd.DataFrame({"Top Búsquedas Nuevo León": tendencias})
    st.dataframe(df_ml, use_container_width=True, hide_index=True)

with col2:
    st.subheader("💬 Demanda Local (Facebook)")
    posts = obtener_posts_monterrey()
    st.caption(f"Procesando {len(posts)} publicaciones...")
    
    conteo_intenciones = extraer_intencion_compra(posts)
    df_fb = pd.DataFrame(conteo_intenciones.items(), columns=["Término", "Menciones"])
    df_fb = df_fb.sort_values(by="Menciones", ascending=False).head(8)
    
    fig = px.bar(df_fb, x="Menciones", y="Término", orientation='h', color="Menciones", color_continuous_scale="Reds")
    fig.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig, use_container_width=True)
