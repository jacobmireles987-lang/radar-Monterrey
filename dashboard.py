# ... al principio de tus imports agrega:
from amazon_extractor import buscar_precio_amazon

# ... dentro del bucle for index, row in df_oportunidades.iterrows():
    # 1. Obtenemos precios de ML y AMZ
    precio_ml = buscar_precio_promedio_ml(termino_busqueda)
    precio_amz = buscar_precio_amazon(termino_busqueda)
    
    # 2. Lógica de comparación: ¿Cuál es más barato?
    # Usamos el menor de los dos proveedores
    precios_proveedores = [p for p in [precio_ml, precio_amz] if p is not None and p > 0]
    mejor_costo = min(precios_proveedores) if precios_proveedores else 0.0
    
    # 3. Calculamos la Ganancia contra el mejor precio
    if row['Precio_Promedio_FB'] > 0 and mejor_costo > 0:
        ganancia = row['Precio_Promedio_FB'] - mejor_costo
    else:
        ganancia = 0.0
