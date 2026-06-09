import requests
import urllib.parse

def buscar_precio_promedio_ml(producto_o_marca):
    headers = {"User-Agent": "Mozilla/5.0"}
    termino_codificado = urllib.parse.quote(producto_o_marca)
    url = f"https://api.mercadolibre.com/sites/MLM/search?q={termino_codificado}&limit=10"

    res = requests.get(url, headers=headers, timeout=10)
    print(f"Status: {res.status_code}")
    datos = res.json()
    resultados = datos.get("results", [])
    print(f"Resultados encontrados: {len(resultados)}")
    for item in resultados[:3]:
        print(f"  - {item.get('title')} → ${item.get('price')}")
    precios = [item["price"] for item in resultados if item.get("price")]
    if precios:
        return sum(precios) / len(precios)
    return None

# Prueba directa
resultado = buscar_precio_promedio_ml("Celular Samsung")
print(f"\nPrecio promedio: {resultado}")
