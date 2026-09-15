import json
import os
import customtkinter as ctk
from tkinter import messagebox, filedialog
import requests  # Manejo de descargas y subidas HTTP directas

# Supabase se queda solo para el backup silencioso de los JSON
from supabase_utils import subir_archivo

# ==========================================
# 🚀 CONFIGURACIÓN DE TU PROPIO SERVIDOR
# ==========================================
URL_SERVIDO_UPLOAD = "https://nube.menwapp.com/upload/embajada/json"
URL_IMAGENES_UPLOAD = "https://nube.menwapp.com/upload/embajada/imagenes"
URL_BASE_PUBLICA_IMG = "https://nube.menwapp.com/embajada/imagenes"

# ===============================
# ARCHIVOS LOCALES WINDOWS
# ===============================
MENU_FILE = "c:/posred/bot/menu.json"
DESC_FILE = "c:/posred/bot/web/descripciones.json"
IMG_FILE = "c:/posred/bot/web/imagenes.json"

# Asegurar que las carpetas locales existan para evitar errores
os.makedirs(os.path.dirname(MENU_FILE), exist_ok=True)
os.makedirs(os.path.dirname(DESC_FILE), exist_ok=True)

# ==========================================
# 🚀 SINCRONIZAR DESDE TU PROPIO SERVIDOR
# ==========================================
try:
    print("⏳ Actualizando menu.json...")
    res = requests.get("https://nube.menwapp.com/embajada/json/menu.json", timeout=10)
    if res.status_code == 200:
        with open(MENU_FILE, "w", encoding="utf-8") as f:
            json.dump(res.json(), f, indent=4, ensure_ascii=False)
        print("✅ menu.json actualizado desde servidor propio")
except Exception as e:
    print("⚠️ No se pudo descargar menu.json del server propio, usando local:", e)

try:
    print("⏳ Actualizando descripciones.json...")
    res = requests.get("https://nube.menwapp.com/embajada/json/descripciones.json", timeout=10)
    if res.status_code == 200:
        with open(DESC_FILE, "w", encoding="utf-8") as f:
            json.dump(res.json(), f, indent=4, ensure_ascii=False)
        print("✅ descripciones.json actualizado desde servidor propio")
except Exception as e:
    print("⚠️ No se pudo descargar descripciones.json del server propio, usando local:", e)

try:
    print("⏳ Actualizando imagenes.json...")
    res = requests.get("https://nube.menwapp.com/embajada/json/imagenes.json", timeout=10)
    if res.status_code == 200:
        with open(IMG_FILE, "w", encoding="utf-8") as f:
            json.dump(res.json(), f, indent=4, ensure_ascii=False)
        print("✅ imagenes.json actualizado desde servidor propio")
except Exception as e:
    print("⚠️ No se pudo descargar imagenes.json del server propio, usando local:", e)


# ===============================
# CARGAR MENÚS LOCALES
# ===============================
def cargar_menu():
    with open(MENU_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["menu"]

def cargar_descripciones():
    if not os.path.exists(DESC_FILE): return {}
    with open(DESC_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def cargar_imagenes():
    if not os.path.exists(IMG_FILE): return {}
    with open(IMG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# ===============================
# GUARDAR DESCRIPCIÓN
# ===============================
def guardar_descripcion(codigo, entry):
    descripcion = entry.get().strip()

    if descripcion:
        descripciones[codigo] = descripcion
    else:
        if codigo in descripciones: del descripciones[codigo]

    with open(DESC_FILE, "w", encoding="utf-8") as f:
        json.dump(descripciones, f, indent=4, ensure_ascii=False)

    # 🚀 SUBIR A TU PROPIO SERVIDOR DEBIAN
    try:
        with open(DESC_FILE, 'rb') as f:
            payload = {'file': ('descripciones.json', f, 'application/json')}
            requests.post(URL_SERVIDO_UPLOAD, files=payload, timeout=10)
        print("✅ descripciones.json subido a tu servidor")
    except Exception as e:
        print("⚠️ Falló subida de descripciones a tu servidor:", e)

    # 🔥 BACKUP SILENCIOSO SUPABASE
    try: subir_archivo("descripciones.json", DESC_FILE)
    except: pass

    messagebox.showinfo("Guardado", "Descripción guardada correctamente")


# ===============================
# GUARDAR IMAGEN (URL MANUAL)
# ===============================
def guardar_imagen(codigo, entry):
    url = entry.get().strip()

    if url:
        imagenes[codigo] = url
    else:
        if codigo in imagenes: del imagenes[codigo]

    with open(IMG_FILE, "w", encoding="utf-8") as f:
        json.dump(imagenes, f, indent=4, ensure_ascii=False)

    # 🚀 SUBIR A TU PROPIO SERVIDOR DEBIAN
    try:
        with open(IMG_FILE, 'rb') as f:
            payload = {'file': ('imagenes.json', f, 'application/json')}
            requests.post(URL_SERVIDO_UPLOAD, files=payload, timeout=10)
        print("✅ imagenes.json subido a tu servidor")
    except Exception as e:
        print("⚠️ Falló subida de imagenes.json a tu servidor:", e)

    # 🔥 BACKUP SILENCIOSO SUPABASE
    try: subir_archivo("imagenes.json", IMG_FILE)
    except: pass

    messagebox.showinfo("Guardado", "Imagen guardada correctamente")


# ==========================================
# 🚀 SUBIR IMAGEN FÍSICA DIRECTA A TU TORRE
# ==========================================
def subir_imagen(codigo, entry):
    file_path = filedialog.askopenfilename(
        filetypes=[("Imagenes", "*.jpg *.jpeg *.png *.webp")]
    )

    if not file_path: return

    try:
        # Extraemos la extensión original de la foto (.png, .jpg, etc)
        _, ext = os.path.splitext(file_path)
        if not ext: ext = ".jpg"

        # El nombre final en tu Debian será el código único del ítem (ej: "101.png")
        nombre_archivo_remoto = f"{codigo}{ext}".lower()

        # Subida directa a la carpeta 
        with open(file_path, "rb") as f:
            payload = {'file': (nombre_archivo_remoto, f, f"image/{ext.replace('.','')}")}
            response = requests.post(URL_IMAGENES_UPLOAD, files=payload, timeout=15)

        if response.status_code == 200:
            # Construimos la URL pública de tu Nginx propio
            url_final_propia = f"{URL_BASE_PUBLICA_IMG}/{nombre_archivo_remoto}"

            # Limpiamos e insertamos la nueva URL en el input de la UI
            entry.delete(0, "end")
            entry.insert(0, url_final_propia)

            # Sincronizamos en caliente el diccionario local
            imagenes[codigo] = url_final_propia

            # Guardamos localmente el archivo imagenes.json
            with open(IMG_FILE, "w", encoding="utf-8") as f:
                json.dump(imagenes, f, indent=4, ensure_ascii=False)

            # Subimos el imagenes.json actualizado a tu servidor
            with open(IMG_FILE, 'rb') as f:
                json_payload = {'file': ('imagenes.json', f, 'application/json')}
                requests.post(URL_SERVIDO_UPLOAD, files=json_payload, timeout=10)

            # 🔥 BACKUP SILENCIOSO DE RESPALDO EN SUPABASE (Solo el archivo JSON)
            try: subir_archivo("imagenes.json", IMG_FILE)
            except: pass

            messagebox.showinfo("Éxito", "Imagen subida físicamente a tu torre Debian con éxito")
        else:
            raise Exception(f"Error del servidor propio: Código {response.status_code}")

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo subir la imagen a tu servidor:\n{e}")


# ===============================
# TOGGLE CATEGORIA
# ===============================
def toggle(frame):
    if frame.winfo_viewable():
        frame.pack_forget()
    else:
        frame.pack(fill="x", padx=20)

def cerrar_app():
    root.destroy()

# ===============================
# INTERFAZ CUSTOMTKINTER
# ===============================
ctk.set_appearance_mode("dark")

root = ctk.CTk()
root.title("Editor de Menú")
root.attributes("-fullscreen", True)

menu = cargar_menu()
descripciones = cargar_descripciones()
imagenes = cargar_imagenes()

# --- BARRA SUPERIOR ---
topbar = ctk.CTkFrame(root, height=50)
topbar.pack(fill="x")

titulo = ctk.CTkLabel(
    topbar,
    text="Editor de Menú (Descripciones + Imágenes en Servidor Propio)",
    font=("Arial", 18, "bold")
)
titulo.pack(side="left", padx=20)

btn_cerrar = ctk.CTkButton(topbar, text="Cerrar", width=120, command=cerrar_app)
btn_cerrar.pack(side="right", padx=20, pady=10)

# --- SCROLL PRINCIPAL ---
scroll = ctk.CTkScrollableFrame(root)
scroll.pack(fill="both", expand=True, padx=20, pady=20)

# --- RENDERIZADO DINÁMICO ---
for categoria, items in menu.items():

    btn_categoria = ctk.CTkButton(scroll, text=f"▼ {categoria}", anchor="w", height=40)
    btn_categoria.pack(fill="x", pady=5)

    frame_items = ctk.CTkFrame(scroll)
    btn_categoria.configure(command=lambda f=frame_items: toggle(f))

    for item in items:
        codigo = item["codigo"]
        articulo = item["articulo"]

        frame_item = ctk.CTkFrame(frame_items)
        frame_item.pack(fill="x", pady=5, padx=10)

        label = ctk.CTkLabel(frame_item, text=articulo, width=300, anchor="w")
        label.pack(side="left", padx=10)

        # --- SECCIÓN DESCRIPCIÓN ---
        entry_desc = ctk.CTkEntry(frame_item, width=350)
        entry_desc.pack(side="left", padx=10, pady=10)
        if codigo in descripciones:
            entry_desc.insert(0, descripciones[codigo])

        btn_desc = ctk.CTkButton(
            frame_item, text="Guardar Desc", width=120,
            command=lambda c=codigo, e=entry_desc: guardar_descripcion(c, e)
        )
        btn_desc.pack(side="left", padx=10)

        # --- SECCIÓN IMAGEN ---
        entry_img = ctk.CTkEntry(frame_item, width=350, placeholder_text="URL imagen")
        entry_img.pack(side="left", padx=10)
        if codigo in imagenes:
            entry_img.insert(0, imagenes[codigo])

        btn_subir = ctk.CTkButton(
            frame_item, text="Subir Img", width=120,
            command=lambda c=codigo, e=entry_img: subir_imagen(c, e)
        )
        btn_subir.pack(side="left", padx=10)

        btn_guardar_img = ctk.CTkButton(
            frame_item, text="Guardar URL", width=120,
            command=lambda c=codigo, e=entry_img: guardar_imagen(c, e)
        )
        btn_guardar_img.pack(side="left", padx=10)

def salir_fullscreen(event=None):
    root.attributes("-fullscreen", False)

root.bind("<Escape>", salir_fullscreen)
root.mainloop()