import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image
import requests
from io import BytesIO

# El módulo de Supabase se queda quieto exclusivamente como backup silencioso del JSON
from supabase_utils import subir_archivo

# =====================================================
# 🚀 CONFIGURACIÓN DE TU PROPIO SERVIDOR DEBIAN
# =====================================================
URL_SERVIDO_UPLOAD = "https://nube.menwapp.com/upload/embajada/json"
URL_IMAGENES_UPLOAD = "https://nube.menwapp.com/upload/embajada/imagenes"
URL_BASE_PUBLICA_IMG = "https://nube.menwapp.com/embajada/imagenes"

# 🔥 MODO OSCURO UI
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# =====================================================
# RUTAS LOCALES WINDOWS
# =====================================================
BASE_DIR = "c:/posred/bot/web"
MENU_JSON = "c:/posred/bot/menu.json"
CONFIG_JSON = os.path.join(BASE_DIR, "menu_config.json")

# Asegurar la existencia de los directorios locales
os.makedirs(BASE_DIR, exist_ok=True)
os.makedirs(os.path.dirname(MENU_JSON), exist_ok=True)

# =====================================================
# 🚀 SINCRONIZAR DESDE TU PROPIO SERVIDOR
# =====================================================
try:
    print("⏳ Actualizando menu.json desde tu torre...")
    res = requests.get("https://nube.menwapp.com/embajada/json/menu.json", timeout=10)
    if res.status_code == 200:
        with open(MENU_JSON, "w", encoding="utf-8") as f:
            json.dump(res.json(), f, indent=4, ensure_ascii=False)
        print("✅ menu.json sincronizado.")
except Exception as e:
    print("⚠️ No se pudo bajar menu.json, se usará copia local si existe:", e)

try:
    print("⏳ Actualizando menu_config.json desde tu torre...")
    res = requests.get("https://nube.menwapp.com/embajada/json/menu_config.json", timeout=10)
    if res.status_code == 200:
        with open(CONFIG_JSON, "w", encoding="utf-8") as f:
            json.dump(res.json(), f, indent=2, ensure_ascii=False)
        print("✅ menu_config.json sincronizado.")
except Exception as e:
    print("⚠️ No se pudo bajar menu_config.json, se usará copia local si existe:", e)


# =====================================================
# CARGA DE DATOS LOCALES
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
        response = requests.get(url, timeout=5)
        img_data = BytesIO(response.content)
        img = Image.open(img_data)
        ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=size)
        label_widget.configure(image=ctk_img, text="")
        label_widget.image = ctk_img
    except:
        label_widget.configure(text="Error al cargar preview")

# =====================================================
# 🚀 SUBIDA FÍSICA DE IMÁGENES DIRECTO A TU TORRE
# =====================================================
def subir_imagen_menu(tipo, prefijo="portada"):
    ruta_local = filedialog.askopenfilename(filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.webp")])
    if ruta_local:
        try:
            _, ext = os.path.splitext(ruta_local)
            if not ext: ext = ".jpg"
                
            # Formateamos el nombre limpio para guardarlo en la torre
            nombre_archivo_remoto = f"{prefijo}_{tipo}{ext}".replace(" ", "_").lower()
            
            # Subida directa mediante multipart/form-data a tu backend FastAPI
            with open(ruta_local, "rb") as f:
                payload = {'file': (nombre_archivo_remoto, f, f"image/{ext.replace('.','')}")}
                response = requests.post(URL_IMAGENES_UPLOAD, files=payload, timeout=15)

            if response.status_code == 200:
                # Construimos el link público definitivo apuntando a tu Nginx local
                url_final_propia = f"{URL_BASE_PUBLICA_IMG}/{nombre_archivo_remoto}"
                return url_final_propia
            else:
                raise Exception(f"Error de tu servidor local: Código {response.status_code}")
            
        except Exception as e:
            messagebox.showerror("Error de red", f"No se pudo despachar la imagen a la torre:\n{str(e)}")
    return None

def cargar_portada_action(tipo):
    url = subir_imagen_menu(tipo)
    if url:
        config["portada"][tipo] = url
        if tipo == "banner":
            mostrar_preview(preview_banner, url, (400, 150))
        else:
            mostrar_preview(preview_logo, url, (150, 150))
        messagebox.showinfo("Éxito", f"{tipo.capitalize()} guardado físicamente en la torre.")

def asignar_banner_categoria():
    cat = categoria_var.get()
    if not cat:
        messagebox.showwarning("Aviso", "No hay una categoría seleccionada.")
        return
    url = subir_imagen_menu(cat, prefijo="cat")
    if url:
        config["banners_categoria"][cat] = url
        mostrar_preview(preview_categoria, url, (400, 150))
        messagebox.showinfo("OK", f"Banner para {cat} asignado correctamente en la torre.")

def actualizar_preview_categoria(choice):
    url = config["banners_categoria"].get(choice, "")
    mostrar_preview(preview_categoria, url, (400, 150))

# =====================================================
# 🚀 GUARDAR CONFIGURACIONES GENERALES Y HORARIOS
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

    # Guardar en local Windows
    with open(CONFIG_JSON, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    try:
        # Enviar el JSON actualizado a tu servidor Debian
        with open(CONFIG_JSON, "rb") as f:
            json_payload = {'file': ('menu_config.json', f, 'application/json')}
            response = requests.post(URL_SERVIDO_UPLOAD, files=json_payload, timeout=10)

        if response.status_code == 200:
            # 🔥 BACKUP SILENCIOSO EN SUPABASE (Solo por seguridad extra)
            try:
                subir_archivo("menu_config.json", CONFIG_JSON)
            except:
                pass
            messagebox.showinfo("Guardado", "Configuración y horarios guardados correctamente en tu Torre ☁️")
        else:
            raise Exception(f"Respuesta inesperada del servidor propio: {response.status_code}")

    except Exception as e:
        messagebox.showerror("Error Servidor", f"No se pudo sincronizar el archivo de configuración: {e}")

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
ctk.CTkLabel(frame_portada, text="🖼️ CONFIGURACIÓN DE PORTADA (SERVIDOR PROPIO)", font=("Arial", 16, "bold")).pack(pady=10)

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

dropdown = ctk.CTkOptionMenu(frame_cats, values=categorias, variable=categoria_var, command=actualizar_preview_categoria, width=250)
dropdown.pack(pady=5)
ctk.CTkButton(frame_cats, text="Cargar Banner para esta Categoría", command=asignar_banner_categoria).pack(pady=5)

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

# Cargar previews de arranque en la interfaz
try:
    mostrar_preview(preview_banner, config["portada"]["banner"], (400, 150))
    mostrar_preview(preview_logo, config["portada"]["logo"], (150, 150))
    if categorias: actualizar_preview_categoria(categorias[0])
except: pass

root.mainloop()