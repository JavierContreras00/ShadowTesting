import time
import random
import os
import requests

def calcular_descuento(precio):
    time.sleep(random.uniform(0.3, 0.6))
    return round(precio * 0.9, 2)
def comparar(valor1, valor2):
    if valor1 == valor2:
        return "✅ Coinciden"
    else:
        return "❌ No coinciden"



def log_accion(usuario, version, accion):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    os.makedirs("logs", exist_ok=True)
    with open("logs/acciones.csv", "a") as f:
        f.write(f"{timestamp},{usuario},{version},{accion}\n")

    try:
        requests.post("http://localhost:8000/shadow/log", json={
            "usuario": usuario,
            "version": version,
            "accion": accion,
            "timestamp": timestamp
        })
    except:
        pass
