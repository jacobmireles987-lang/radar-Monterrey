def buscar_precio_amazon(producto):
    texto = producto.lower()
    precios = {
        "celular"   : 9999,
        "samsung"   : 9999,
        "laptop"    : 17999,
        "apple"     : 22000,
        "dell"      : 16000,
        "llantas"   : 3200,
        "michelin"  : 3100,
        "pirelli"   : 2900,
        "minisplit" : 8999,
        "minisplits": 8999,
        "lg"        : 8500,
        "mirage"    : 7200,
        "usado"     : 5500,
    }
    for clave, precio in precios.items():
        if clave in texto:
            return precio
    return None
