from collections import Counter

def extraer_intencion_compra(posts):
    palabras_clave = ["busco", "ocupo", "compro", "dónde consigo", "necesito", "alguien vende"]
    productos_detectados = []
    
    for post in posts:
        post_lower = post.lower()
        if any(kw in post_lower for kw in palabras_clave):
            texto_limpio = post_lower
            basura = palabras_clave + [" para ", " en ", " por ", " urge ", " urgente ", " barato ", " económico "]
            for b in basura:
                texto_limpio = texto_limpio.replace(b, " ")
            
            palabras = [p.strip() for p in texto_limpio.split() if len(p) > 4]
            productos_detectados.extend(palabras)
            
    return Counter(productos_detectados)
