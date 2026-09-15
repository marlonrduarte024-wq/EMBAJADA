import os

# Configuración de URLs
BUSCAR_URL = "https://nube.menwapp.com/distrito"
REEMPLAZAR_URL = "https://apidistrito.menwapp.com/web/"

# Lista de archivos JSON a modificar sobre el mismo archivo
ARCHIVOS = ["imagenes.json", "menu_config.json"]


def actualizar_archivos_json():
  for nombre_archivo in ARCHIVOS:
    if not os.path.exists(nombre_archivo):
      print(f"⚠️ El archivo '{nombre_archivo}' no se encontró, omitiendo...")
      continue

    # 1. Leer el contenido del archivo original
    with open(nombre_archivo, "r", encoding="utf-8") as f:
      contenido = f.read()

    # 2. Contar y reemplazar todas las coincidencias
    coincidencias = contenido.count(BUSCAR_URL)

    if coincidencias > 0:
      nuevo_contenido = contenido.replace(BUSCAR_URL, REEMPLAZAR_URL)

      # 3. Sobreescribir exactamente el mismo archivo
      with open(nombre_archivo, "w", encoding="utf-8") as f:
        f.write(nuevo_contenido)

      print(
          f"✅ '{nombre_archivo}' actualizado correctamente ({coincidencias}"
          " rutas modificadas)."
      )
    else:
      print(
          f"ℹ️ '{nombre_archivo}' no tenía ninguna ruta con '{BUSCAR_URL}'."
      )


if __name__ == "__main__":
  actualizar_archivos_json()