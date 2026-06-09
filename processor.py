import pandas as pd
import re

def analizar_demanda_y_marcas(posts):
    palabras_clave = ["busco", "ocupo", "compro", "dónde consigo", "alguien vende"]
    marcas_conocidas = ["mirage", "samsung", "apple", "dell", "michelin", "pirelli", "lg"]
    
    resultados = []
    for post in posts:
        post_lower = post.lower()
        if any(kw in post_lower for kw in palabras_clave):
            marca_detectada = "Genérica"
            for marca in marcas_conocidas:
                if marca in post_lower:
                    marca_detectada = marca.title()
                    break
            
            # Buscamos el presupuesto con el símbolo $
            presupuesto = 0.0
            match = re.search(r'\$(\d+[,.]?\d*)', post_lower)
            if match:
                presupuesto = float(match.group(1).replace(',', ''))
            
            texto_limpio = re.sub(r'\$\d+[,.]?\d*', ' ', post_lower)
            basura = palabras_clave + marcas_conocidas + [" para ", " en ", " por ", " pago ", " doy ", " ofrezco ", " presupuesto ", " maximo ", " efectivo ", " hoy ", " traigo ", " tengo "]
            for b in basura:
                texto_limpio = texto_limpio.replace(b, " ")
                
            palabras = [p.strip() for p in texto_limpio.split() if len(p) > 3]
            if palabras:
                producto = palabras[0].title()
                resultados.append({"Producto": producto, "Marca": marca_detectada, "Oferta_FB": presupuesto})
                
    if resultados:
        df = pd.DataFrame(resultados)
        # FIX: Reemplazamos 0.0 con None, que es 100% seguro para matemáticas
        df['Oferta_FB'] = df['Oferta_FB'].apply(lambda x: None if x == 0.0 else x)
        
        resumen = df.groupby(['Producto', 'Marca']).agg(
            Menciones=('Producto', 'size'),
            Presupuesto_FB=('Oferta_FB', 'mean')
        ).reset_index()
        return resumen.sort_values(by='Menciones', ascending=False)
    
    return pd.DataFrame(columns=["Producto", "Marca", "Menciones", "Presupuesto_FB"])
