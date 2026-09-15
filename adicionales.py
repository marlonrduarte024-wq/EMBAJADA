import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
import requests  # 🚀 NUEVO: Manejo de descargas y subidas HTTP directas

# Importamos supabase por si acaso lo necesitamos de backup silencioso
from supabase_utils import subir_archivo

# Archivos de referencia locales
MENU_FILE = "menu.json"
OUTPUT_FILE = "web/custom/adicionales.json"

# Asegurar que las carpetas locales existan para evitar errores al guardar
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

# ==========================================
# 🚀 SINCRONIZAR DESDE TU PROPIO SERVIDOR
# ==========================================

# 1. Descargar menu.json desde tu servidor propio
try:
    print("⏳ Actualizando menu.json desde tu torre...")
    response = requests.get("https://nube.menwapp.com/embajada/json/menu.json", timeout=10)
    if response.status_code == 200:
        with open(MENU_FILE, "w", encoding="utf-8") as f:
            json.dump(response.json(), f, indent=4, ensure_ascii=False)
        print("✅ menu.json actualizado desde el servidor propio")
    else:
        print(f"⚠️ Servidor respondió con código {response.status_code}, se usará el archivo local si existe.")
except Exception as e:
    print("⚠️ No se pudo descargar menu.json del servidor propio, usando copia local:", e)

# 2. Descargar adicionales.json desde tu servidor propio
try:
    print("⏳ Actualizando adicionales.json desde tu torre...")
    response = requests.get("https://nube.menwapp.com/embajada/json/adicionales.json", timeout=10)
    if response.status_code == 200:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(response.json(), f, indent=2, ensure_ascii=False)
        print("✅ adicionales.json actualizado desde el servidor propio")
    else:
        print(f"⚠️ Servidor respondió con código {response.status_code}, se usará el archivo local.")
except Exception as e:
    print("⚠️ No se pudo descargar adicionales.json del servidor propio, usando copia local:", e)


# Estructuras de datos
grupos = {}
productos_que_muestran = {}

def cargar_menu():
    try:
        with open(MENU_FILE, encoding="utf-8") as f:
            return json.load(f)["menu"]
    except Exception as e:
        print(f"Error al cargar menú local: {e}")
        return {}

menu = cargar_menu()

def cargar_config_previa():
    global grupos, productos_que_muestran
    if not os.path.exists(OUTPUT_FILE):
        return
    try:
        with open(OUTPUT_FILE, encoding="utf-8") as f:
            data = json.load(f)
        grupos = data.get("grupos", {})
        productos_data = data.get("productos", {})
        for cod_prod, lista_grupos in productos_data.items():
            for g in lista_grupos:
                if g not in productos_que_muestran:
                    productos_que_muestran[g] = []
                productos_que_muestran[g].append(cod_prod)
    except: pass

app = tk.Tk()
app.title("Configurador Maestro de Adicionales")
app.geometry("1400x700")

main_frame = ttk.Frame(app)
main_frame.pack(fill="both", expand=True, padx=10, pady=10)

# --- COLUMNAS ---
col1 = ttk.LabelFrame(main_frame, text="1. Grupos")
col1.pack(side="left", fill="y", padx=5)

col2 = ttk.LabelFrame(main_frame, text="2. ¿Qué productos SON adicionales?")
col2.pack(side="left", fill="both", expand=True, padx=5)

col3 = ttk.LabelFrame(main_frame, text="3. Items en el Grupo (Vista)")
col3.pack(side="left", fill="both", expand=True, padx=5)

col4 = ttk.LabelFrame(main_frame, text="4. ¿Dónde se muestran?")
col4.pack(side="left", fill="both", expand=True, padx=5)

# --- COL 1: GRUPOS ---
lista_grupos_ui = tk.Listbox(col1, height=25)
lista_grupos_ui.pack(padx=5, pady=5)
entry_nuevo_grupo = ttk.Entry(col1)
entry_nuevo_grupo.pack(fill="x", padx=5)

def cmd_crear_grupo():
    n = entry_nuevo_grupo.get().strip()
    if n and n not in grupos:
        grupos[n] = []
        productos_que_muestran[n] = []
        actualizar_lista_grupos()
        entry_nuevo_grupo.delete(0, tk.END)
ttk.Button(col1, text="Crear Grupo", command=cmd_crear_grupo).pack(pady=5)

# --- FUNCION GENÉRICA PARA LISTAR PRODUCTOS ---
def crear_lista_scroll(parent):
    canvas = tk.Canvas(parent)
    scroll = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    frame = ttk.Frame(canvas)
    frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=frame, anchor="nw")
    canvas.configure(yscrollcommand=scroll.set)
    canvas.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")
    return frame

# --- COL 2: PRODUCTOS QUE SON ADICIONALES ---
frame_son_adicionales = crear_lista_scroll(col2)
checks_son_adicionales = {}

# --- COL 4: PRODUCTOS DONDE SE MUESTRAN ---
frame_donde_se_muestran = crear_lista_scroll(col4)
checks_donde_se_muestran = {}

def renderizar_listas():
    for f, d in [(frame_son_adicionales, checks_son_adicionales), (frame_donde_se_muestran, checks_donde_se_muestran)]:
        for cat, items in menu.items():
            ttk.Label(f, text=cat, font=("Arial", 9, "bold")).pack(anchor="w", pady=(5,0))
            for it in items:
                var = tk.BooleanVar()
                cb = ttk.Checkbutton(f, text=it["articulo"], variable=var)
                cb.pack(anchor="w", padx=10)
                d[it["codigo"]] = {"var": var, "nombre": it["articulo"]}

# --- COL 3: VISTA PREVIA DEL GRUPO ---
lista_items_ver = tk.Listbox(col3)
lista_items_ver.pack(fill="both", expand=True, padx=5, pady=5)

def actualizar_columna_3(g):
    lista_items_ver.delete(0, tk.END)
    for item in grupos[g]:
        lista_items_ver.insert(tk.END, f"{item['nombre']} ({item['codigo']})")

# --- LÓGICA DE SELECCIÓN ---
def on_select_grupo(event):
    selection = lista_grupos_ui.curselection()
    if not selection: return
    g = lista_grupos_ui.get(selection[0])
    
    actualizar_columna_3(g)
    
    codigos_en_grupo = [item['codigo'] for item in grupos[g]]
    for cod, info in checks_son_adicionales.items():
        info["var"].set(cod in codigos_en_grupo)
        
    for cod, info in checks_donde_se_muestran.items():
        info["var"].set(cod in productos_que_muestran.get(g, []))

lista_grupos_ui.bind("<<ListboxSelect>>", on_select_grupo)

# --- GUARDAR ---
def guardar():
    idx = lista_grupos_ui.curselection()
    if not idx:
        messagebox.showwarning("Aviso", "Selecciona un grupo")
        return
    g = lista_grupos_ui.get(idx[0])

    # 1. Actualizar los integrantes del grupo (Columna 2)
    grupos[g] = []
    for cod, info in checks_son_adicionales.items():
        if info["var"].get():
            grupos[g].append({"nombre": info["nombre"], "codigo": cod})

    # 2. Actualizar dónde se muestra (Columna 4)
    productos_que_muestran[g] = [cod for cod, info in checks_donde_se_muestran.items() if info["var"].get()]

    # 3. Preparar JSON final
    data_final = {"grupos": grupos, "productos": {}}
    for nom_g, lista_prods in productos_que_muestran.items():
        for p_cod in lista_prods:
            if p_cod not in data_final["productos"]:
                data_final["productos"][p_cod] = []
            data_final["productos"][p_cod].append(nom_g)

    # Guardar archivo de manera local
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data_final, f, indent=2, ensure_ascii=False)

    # ==========================================
    # 🚀 SUBIR A TU PROPIO SERVIDOR DEBIAN
    # ==========================================
    print("⏳ Subiendo adicionales.json a tu servidor local...")
    url_servidor = "https://nube.menwapp.com/upload/embajada/json"
    
    try:
        with open(OUTPUT_FILE, 'rb') as f:
            archivo_payload = {'file': ('adicionales.json', f, 'application/json')}
            response = requests.post(url_servidor, files=archivo_payload, timeout=10)
        
        if response.status_code == 200:
            print("✅ ¡Subido con éxito a tu propio servidor!")
        else:
            print(f"⚠️ Error en tu servidor, código: {response.status_code}")
    except Exception as server_error:
        print(f"⚠️ Falló la conexión con tu servidor: {server_error}")

    # ==========================================
    # SUBIR A SUPABASE (BACKUP DE RESPALDO)
    # ==========================================
    try:
        print("⏳ Guardando respaldo en Supabase...")
        subir_archivo("adicionales.json", OUTPUT_FILE)
    except Exception as supabase_error:
        print(f"⚠️ Error al guardar respaldo en Supabase: {supabase_error}")

    actualizar_columna_3(g)
    messagebox.showinfo("Éxito", "Configuración guardada en tu servidor y backup")

ttk.Button(main_frame, text="GUARDAR CAMBIOS DEL GRUPO", command=guardar).pack(side="bottom", fill="x", pady=10)

def actualizar_lista_grupos():
    lista_grupos_ui.delete(0, tk.END)
    for g in grupos: lista_grupos_ui.insert(tk.END, g)

cargar_config_previa()
actualizar_lista_grupos()
renderizar_listas()
app.mainloop()