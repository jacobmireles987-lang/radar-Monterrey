import pandas as pd

def analizar_demanda_y_marcas(posts):
    palabras_clave = ["busco", "ocupo", "compro", "dónde consigo", "alguien vende"]
    # Diccionario de marcas a detectar (puedes agregar las que quieras en el futuro)
    marcas_conocidas = ["mirage", "samsung", "apple", "dell", "michelin", "pirelli", "lg", "hp", "nissan", "iphone"]
    
    resultados = []
    
    for post in posts:
        post_lower = post.lower()
        if any(kw in post_lower for kw in palabras_clave):
            # 1. Detectar la marca
            marca_detectada = "Genérica"
            for marca in marcas_conocidas:
                if marca in post_lower:
                    marca_detectada = marca.title()
                    break
            
            # 2. Limpiar para encontrar el producto base
            texto_limpio = post_lower
            basura = palabras_clave + marcas_conocidas + [" para ", " en ", " por ", " urge ", " urgente ", " barato ", " económico ", " rin ", " usado ", " usadas "]
            for b in basura:
                texto_limpio = texto_limpio.replace(b, " ")
            
            # Tomamos la palabra más significativa como el "Producto"
            palabras = [p.strip() for p in texto_limpio.split() if len(p) > 4]
            if palabras:
                producto = palabras[0].title()
                resultados.append({"Producto": producto, "Marca": marca_detectada})
                
    # Contamos y agrupamos usando Pandas
    if resultados:
        df = pd.DataFrame(resultados)
        resumen = df.groupby(['Producto', 'Marca']).size().reset_index(name='Menciones')
        return resumen.sort_values(by='Menciones', ascending=False)
    
    return pd.DataFrame(columns=["Producto", "Marca", "Menciones"])
