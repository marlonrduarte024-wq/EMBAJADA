import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image
import requests
from io import BytesIO

# ✅ IMPORTAMOS TUS FUNCIONES ORIGINALES
from supabase_utils import descargar_archivo, SUPABASE_URL, SUPABASE_KEY

# =====================================================
# CREDENCIALES DIRECTAS DE TU SUPABASE_UTILS
# =====================================================
BUCKET_IMAGENES = "menu" # El bucket nuevo que creaste para las fotos
URL_BASE_PUBLICA = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_IMAGENES}"

# 🔥 MODO OSCURO
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# =====================================================
# RUTAS LOCALES
# =====================================================
BASE_DIR = "c:/posred/bot/web"
MENU_JSON = "c:/posred/bot/menu.json"
CONFIG_JSON = os.path.join(BASE_DIR, "menu_config.json")

# =====================================================
# CARGA DE DATOS
# =====================================================
def cargar_menu_keys():
    try:
        with open(MENU_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
        return list(data["menu"].keys())
    except:
        return []

def cargar_config():
    if os.path.exists(CONFIG_JSON):
        with open(CONFIG_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "horarios" not in data:
                data["horarios"] = {
                    dia: {
                        "cerrado": False,
                        "rangos": [{"inicio": "18:00", "fin": "23:00"}]
                    }
                    for dia in ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]
                }
            return data
    return {
        "portada": {"banner": "", "logo": ""},
        "banners_categoria": {},
        "recomendados": [],
        "orden_categorias": [],
        "horarios": {
            dia: {
                "cerrado": False,
                "rangos": [{"inicio": "18:00", "fin": "23:00"}]
            }
            for dia in ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]
        }
    }

# Sincronización inicial al abrir el panel
try:
    descargar_archivo("menu.json", MENU_JSON)
except: pass
try:
    descargar_archivo("menu_config.json", CONFIG_JSON)
except: pass

categorias = cargar_menu_keys()
config = cargar_config()

# =====================================================
# FUNCIONES DE PREVIEW
# =====================================================
def mostrar_preview(label_widget, url, size):
    if not url or not url.startswith("http"):
        label_widget.configure(text="Sin imagen", image=None)
        return
    try:
        response = requests.get(url)
        img_data = BytesIO(response.content)
        img = Image.open(img_data)
        ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=size)
        label_widget.configure(image=ctk_img, text="")
        label_widget.image = ctk_img
    except:
        label_widget.configure(text="Error al cargar preview")

# =====================================================
# SUBIDA AL BUCKET CORRESPONDIENTE DE IMÁGENES ("menu")
# =====================================================
def subir_imagen_menu(tipo, prefijo="portada"):
    ruta_local = filedialog.askopenfilename(filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.webp")])
    if ruta_local:
        try:
            _, ext = os.path.splitext(ruta_local)
            if not ext: ext = ".jpg"
                
            nombre_archivo = f"{prefijo}_{tipo}{ext}".replace(" ", "_").lower()
            
            # Leemos el archivo binario local de forma correcta usando tu orden original
            with open(ruta_local, "rb") as f:
                archivo_binario = f.read()

            # Forzamos la subida apuntando específicamente al bucket de fotos ("menu")
            url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET_IMAGENES}/{nombre_archivo}"

            headers = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "x-upsert": "true", 
                "Content-Type": "image/png" if ext.lower() == ".png" else "image/jpeg"
            }

            response = requests.post(url, headers=headers, data=archivo_binario)
            if response.status_code not in [200, 201]:
                response = requests.put(url, headers=headers, data=archivo_binario)

            if response.status_code in [200, 201]:
                url_final = f"{URL_BASE_PUBLICA}/{nombre_archivo}"
                return url_final
            else:
                raise Exception(f"Supabase Error: {response.text}")
            
        except Exception as e:
            messagebox.showerror("Error Supabase", f"No se pudo subir la imagen:\n{str(e)}")
    return None

def cargar_portada_action(tipo):
    url = subir_imagen_menu(tipo)
    if url:
        config["portada"][tipo] = url
        if tipo == "banner":
            mostrar_preview(preview_banner, url, (400, 150))
        else:
            mostrar_preview(preview_logo, url, (150, 150))
        messagebox.showinfo("Éxito", f"{tipo.capitalize()} actualizado en Supabase.")

def asignar_banner_categoria():
    cat = categoria_var.get()
    url = subir_imagen_menu(cat, prefijo="cat")
    if url:
        config["banners_categoria"][cat] = url
        mostrar_preview(preview_categoria, url, (400, 150))
        messagebox.showinfo("OK", f"Banner para {cat} asignado en Supabase.")

def actualizar_preview_categoria(choice):
    url = config["banners_categoria"].get(choice, "")
    mostrar_preview(preview_categoria, url, (400, 150))

# =====================================================
# GUARDAR CONFIGURACIONES (JSON AL BUCKET "conf_pagina")
# =====================================================
def guardar_con_horarios():
    for dia, vars in horario_vars.items():
        rangos = []
        for r in vars["rangos"]:
            inicio = r["inicio"].get().strip()
            fin = r["fin"].get().strip()
            if inicio and fin:
                rangos.append({"inicio": inicio, "fin": fin})

        config["horarios"][dia] = {
            "cerrado": vars["cerrado"].get(),
            "rangos": rangos
        }

    with open(CONFIG_JSON, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    try:
        # Aquí reusamos tu función original de supabase_utils importada arriba
        # Respetando el orden exacto que definiste: subir_archivo(nombre_remoto, ruta_local)
        
        url = f"{SUPABASE_URL}/storage/v1/object/conf_pagina/menu_config.json"
        with open(CONFIG_JSON, "rb") as f:
            archivo = f.read()

        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "x-upsert": "true", 
            "Content-Type": "application/json"
        }

        response = requests.post(url, headers=headers, data=archivo)
        if response.status_code not in [200, 201]:
            response = requests.put(url, headers=headers, data=archivo)

        if response.status_code in [200, 201]:
            messagebox.showinfo("Guardado", "Configuración guardada en Local y Supabase ☁️")
        else:
            raise Exception(response.text)

    except Exception as e:
        messagebox.showerror("Error Supabase", f"No se pudo subir el archivo de configuración: {e}")

# =====================================================
# INTERFAZ GRÁFICA (CustomTkinter)
# =====================================================
root = ctk.CTk()
root.title("Configurador MenWapp - Portada & Horarios")
root.geometry("1000x900")

scroll = ctk.CTkScrollableFrame(root)
scroll.pack(fill="both", expand=True, padx=10, pady=10)

# --- SECCIÓN PORTADA ---
frame_portada = ctk.CTkFrame(scroll)
frame_portada.pack(fill="x", padx=10, pady=10)
ctk.CTkLabel(frame_portada, text="🖼️ CONFIGURACIÓN DE PORTADA (SUPABASE)", font=("Arial", 16, "bold")).pack(pady=10)

col_portada = ctk.CTkFrame(frame_portada, fg_color="transparent")
col_portada.pack(fill="x", padx=20, pady=10)

f_banner = ctk.CTkFrame(col_portada)
f_banner.pack(side="left", expand=True, fill="both", padx=5)
ctk.CTkButton(f_banner, text="Subir Banner Principal", command=lambda: cargar_portada_action("banner")).pack(pady=5)
preview_banner = ctk.CTkLabel(f_banner, text="...")
preview_banner.pack(pady=5)

f_logo = ctk.CTkFrame(col_portada)
f_logo.pack(side="left", expand=True, fill="both", padx=5)
ctk.CTkButton(f_logo, text="Subir Logo", command=lambda: cargar_portada_action("logo")).pack(pady=5)
preview_logo = ctk.CTkLabel(f_logo, text="...")
preview_logo.pack(pady=5)

# --- SECCIÓN CATEGORÍAS ---
frame_cats = ctk.CTkFrame(scroll)
frame_cats.pack(fill="x", padx=10, pady=10)
ctk.CTkLabel(frame_cats, text="📂 BANNERS DE CATEGORÍAS", font=("Arial", 16, "bold")).pack(pady=10)
categoria_var = ctk.StringVar(value=categorias[0] if categorias else "")

f_cat_content = ctk.CTkFrame(frame_cats, fg_color="transparent")
f_cat_content.pack(pady=10)

dropdown = ctk.CTkOptionMenu(f_cat_content, values=categorias, variable=categoria_var, command=actualizar_preview_categoria, width=250)
dropdown.pack(side="left", padx=20)
ctk.CTkButton(f_cat_content, text="Cargar Banner para esta Categoría", command=asignar_banner_categoria).pack(side="left")

preview_categoria = ctk.CTkLabel(frame_cats, text="...")
preview_categoria.pack(pady=10)

# --- SECCIÓN HORARIOS ---
frame_horarios = ctk.CTkFrame(scroll)
frame_horarios.pack(fill="x", padx=10, pady=10)
ctk.CTkLabel(frame_horarios, text="🕒 HORARIOS DE ATENCIÓN", font=("Arial", 16, "bold")).pack(pady=10)

header = ctk.CTkFrame(frame_horarios, fg_color="#333")
header.pack(fill="x", padx=10, pady=2)
ctk.CTkLabel(header, text="Día", width=120, font=("Arial", 12, "bold")).pack(side="left", padx=10)
ctk.CTkLabel(header, text="Apertura", width=100, font=("Arial", 12, "bold")).pack(side="left", padx=30)
ctk.CTkLabel(header, text="Cierre", width=100, font=("Arial", 12, "bold")).pack(side="left", padx=10)
ctk.CTkLabel(header, text="Estado", width=100, font=("Arial", 12, "bold")).pack(side="right", padx=20)

horario_vars = {}
dias = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]

for dia in dias:
    row = ctk.CTkFrame(frame_horarios)
    row.pack(fill="x", padx=10, pady=2)
    ctk.CTkLabel(row, text=dia, width=120, anchor="w").pack(side="left", padx=10)

    datos = config["horarios"][dia]
    v_cerrado = tk.BooleanVar(value=datos["cerrado"])
    rangos_vars = []
    rangos = datos.get("rangos", [])
    while len(rangos) < 2: rangos.append({"inicio": "", "fin": ""})

    for idx, rango in enumerate(rangos[:2]):
        v_inicio = ctk.StringVar(value=rango["inicio"])
        v_fin = ctk.StringVar(value=rango["fin"])
        rangos_vars.append({"inicio": v_inicio, "fin": v_fin})

        ctk.CTkEntry(row, textvariable=v_inicio, width=70, justify="center").pack(side="left", padx=(10 if idx == 0 else 20, 5))
        ctk.CTkLabel(row, text="a").pack(side="left")
        ctk.CTkEntry(row, textvariable=v_fin, width=70, justify="center").pack(side="left", padx=5)

    horario_vars[dia] = {"rangos": rangos_vars, "cerrado": v_cerrado}
    ctk.CTkCheckBox(row, text="Cerrado hoy", variable=v_cerrado, fg_color="#e74c3c", hover_color="#c0392b").pack(side="right", padx=10)

# BOTÓN GUARDAR FINAL
ctk.CTkButton(root, text="💾 GUARDAR TODO Y ACTUALIZAR WEB", command=guardar_con_horarios, height=60, font=("Arial", 18, "bold"), fg_color="#27ae60", hover_color="#219150").pack(fill="x", padx=20, pady=20)

# Cargar previews de arranque
try:
    mostrar_preview(preview_banner, config["portada"]["banner"], (400, 150))
    mostrar_preview(preview_logo, config["portada"]["logo"], (150, 150))
    if categorias: actualizar_preview_categoria(categorias[0])
except: pass

root.mainloop()