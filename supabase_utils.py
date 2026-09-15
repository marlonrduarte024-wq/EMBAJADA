# -*- coding: utf-8 -*-
import requests
import json

# URL de tu API en tu servidor propio
API_URL = "https://nube.menwapp.com/api/registrar_pedido"

def subir_archivo(nombre_archivo, ruta_local):
    try:
        with open(ruta_local, "rb") as f:
            archivo = f.read()

        url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET}/{nombre_archivo}"

        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            # "x-upsert": "true" le dice a Supabase: "Si ya existe, reemplázalo"
            "x-upsert": "true", 
            "Content-Type": "application/json"
        }

        # Intentamos subirlo directamente con x-upsert
        response = requests.post(url, headers=headers, data=archivo)

        if response.status_code in [200, 201]:
            print(f"☁️ Subido y actualizado en Supabase: {nombre_archivo}")
        else:
            # Si el POST falla aun con x-upsert, intentamos el PUT tradicional
            response = requests.put(url, headers=headers, data=archivo)
            
            if response.status_code in [200, 201]:
                print(f"☁️ Reemplazado vía PUT en Supabase: {nombre_archivo}")
            else:
                print(f"❌ Error Supabase ({nombre_archivo}): {response.text}")

    except Exception as e:
        print(f"❌ Error subiendo {nombre_archivo}:", e)

def registrar_pedido_local(data):
    """Envía el pedido a tu API central en lugar de conectar a Postgres."""
    try:
        # Nota: Enviamos el diccionario 'data' tal cual lo recibe el bot.
        # La API en el servidor se encargará de insertarlo en la base de datos.
        response = requests.post(API_URL, json=data, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Pedido enviado exitosamente a la nube.")
        else:
            print(f"❌ Error en API (Código {response.status_code}): {response.text}")
            
    except Exception as e:
        print(f"❌ Error crítico al conectar con la API: {e}")

def actualizar_pedido_local(id_pedido_local, nuevos_datos):
    """Envía la actualización a tu API central."""
    # 1. Limpieza de datos ANTES de cualquier intento de proceso
    datos_limpios = {}
    for k, v in nuevos_datos.items():
        if isinstance(v, str):
            # Forzamos la limpieza eliminando caracteres no UTF-8
            datos_limpios[k] = v.encode('utf-8', 'ignore').decode('utf-8')
        else:
            datos_limpios[k] = v
            
    # 2. Envío a la API (NADA DE PSYCOPG2 AQUÍ)
    try:
        url = "https://nube.menwapp.com/api/actualizar_pedido"
        payload = {"id": id_pedido_local, "data": datos_limpios}
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Pedido #{id_pedido_local} actualizado en el servidor.")
        else:
            print(f"❌ Error al actualizar: {response.text}")
            
    except Exception as e:
        print(f"❌ Error al conectar con la API: {e}")