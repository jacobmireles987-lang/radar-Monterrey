PRECIOS_AMZ = {
    "celular"   : 9999,
    "laptop"    : 17999,
    "llantas"   : 3200,
    "minisplit" : 8999,
    "minisplits": 8999,
    "usado"     : 5500,
    "samsung"   : 9999,
    "apple"     : 22000,
    "dell"      : 16000,
    "michelin"  : 3100,
    "pirelli"   : 2900,
    "lg"        : 8500,
    "mirage"    : 7200,
}

def buscar_precio_amazon(producto):
    texto = producto.lower()
    for clave, precio in PRECIOS_AMZ.items():
        if clave in texto:
            return precio
    return None
