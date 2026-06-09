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

col1, col2 = st.columns([1, 2.5]) 

with col1:
    st.subheader("📦 Top Búsquedas (ML)")
    tendencias = obtener_tendencias_ml()
    df_ml = pd.DataFrame({"Tendencia": tendencias})
    st.dataframe(df_ml, use_container_width=True, hide_index=True)

with col2:
    st.subheader("💰 Oportunidades de Arbitraje (Spread)")
    posts = obtener_posts_monterrey()
    df_oportunidades = analizar_demanda_y_marcas(posts)
    
    lista_precios_ml = []
    lista_enlaces = []
    lista_margenes = []
    
    for index, row in df_oportunidades.iterrows():
        termino_busqueda = f"{row['Producto']} {row['Marca']}" if row['Marca'] != "Genérica" else row['Producto']
        
        # 1. Obtenemos los datos crudos
        precio_ml = buscar_precio_promedio_ml(termino_busqueda)
        presupuesto_fb = row.get('Presupuesto_FB')
        
        # 2. Conversión segura (Blindaje matemático)
        try:
            p_fb = float(presupuesto_fb) if pd.notna(presupuesto_fb) else 0.0
        except:
            p_fb = 0.0
            
        try:
            p_ml = float(precio_ml) if precio_ml is not None else 0.0
        except:
            p_ml = 0.0
        
        # 3. Calculamos la Ganancia exacta
        if p_fb > 0 and p_ml > 0:
            ganancia = float(p_fb - p_ml)
            lista_margenes.append(ganancia)
            lista_precios_ml.append(p_ml)
        else:
            lista_margenes.append(None)
            lista_precios_ml.append(p_ml if p_ml > 0 else None)
        
        # 4. Creamos el enlace
        termino_url = urllib.parse.quote(termino_busqueda)
        lista_enlaces.append(f"https://listado.mercadolibre.com.mx/{termino_url}")
        
    # Asignamos las listas a la tabla
    df_oportunidades["Costo Proveedor (ML)"] = lista_precios_ml
    df_oportunidades["Margen Estimado"] = lista_margenes
    df_oportunidades["Enlace Directo"] = lista_enlaces
    
    # Renderizamos la tabla financiera
    st.dataframe(
        df_oportunidades, 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "Presupuesto_FB": st.column_config.NumberColumn("Oferta Cliente (FB)", format="$%d MXN"),
            "Costo Proveedor (ML)": st.column_config.NumberColumn("Costo Proveedor (ML)", format="$%d MXN"),
            "Margen Estimado": st.column_config.NumberColumn("Tu Margen Neto", format="$%d MXN"),
            "Enlace Directo": st.column_config.LinkColumn("Comprar", display_text="Ver ML 🔗")
        }
    )
