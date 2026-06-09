def obtener_tendencias_ml():
    return ["Minisplit", "Llantas", "Celular", "Laptop", "iPhone"]

def buscar_precio_promedio_ml(producto_o_marca):
    texto = producto_o_marca.lower()
    precios = {
        "celular"   : 8500,
        "samsung"   : 8500,
        "laptop"    : 15000,
        "apple"     : 18000,
        "dell"      : 14000,
        "llantas"   : 2800,
        "michelin"  : 2800,
        "pirelli"   : 2600,
        "minisplit" : 7200,
        "minisplits": 7200,
        "lg"        : 7000,
        "mirage"    : 6500,
        "usado"     : 4500,
    }
    for clave, precio in precios.items():
        if clave in texto:
            return precio
    return 6000
