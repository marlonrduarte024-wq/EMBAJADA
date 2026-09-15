import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
from supabase_utils import subir_archivo, descargar_archivo

# Archivos de referencia
MENU_FILE = "menu.json"
OUTPUT_FILE = "web/custom/adicionales.json"
# ===============================
# SINCRONIZAR DESDE SUPABASE
# ===============================

try:
    descargar_archivo("menu.json", MENU_FILE)
    print("✅ menu.json actualizado desde Supabase")
except Exception as e:
    print("⚠️ No se pudo descargar menu.json:", e)

try:
    descargar_archivo("adicionales.json", OUTPUT_FILE)
    print("✅ adicionales.json actualizado desde Supabase")
except Exception as e:
    print("⚠️ No se pudo descargar adicionales.json:", e)

# Estructuras de datos
# grupos: { "NombreGrupo": [{"nombre": "Extra Queso", "codigo": "AD01"}, ...] }
grupos = {}
# productos_que_muestran: { "NombreGrupo": ["COD_PLATO1", "COD_PLATO2"] }
productos_que_muestran = {}

def cargar_menu():
    try:
        with open(MENU_FILE, encoding="utf-8") as f:
            return json.load(f)["menu"]
    except Exception as e:
        print(f"Error al cargar menú: {e}")
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

# --- COL 2: PRODUCTOS QUE SON ADICIONALES (Para sacar el código) ---
frame_son_adicionales = crear_lista_scroll(col2)
checks_son_adicionales = {}

# --- COL 4: PRODUCTOS DONDE SE MUESTRAN (Lógica original) ---
frame_donde_se_muestran = crear_lista_scroll(col4)
checks_donde_se_muestran = {}

def renderizar_listas():
    for f, d in [(frame_son_adicionales, checks_son_adicionales), (frame_donde_se_muestran, checks_donde_se_muestran)]:
        for cat, items in menu.items():
            ttk.Label(f, text=cat, font=("Arial", 9, "bold")).pack(anchor="w", pady=(5,0))
            for it in items:
                var = tk.BooleanVar()
                # Guardamos nombre y codigo para la Columna 2
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
    
    # Marcar Columna 2 (Cuáles de este grupo ya están seleccionados)
    codigos_en_grupo = [item['codigo'] for item in grupos[g]]
    for cod, info in checks_son_adicionales.items():
        info["var"].set(cod in codigos_en_grupo)
        
    # Marcar Columna 4 (Dónde se muestra este grupo)
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

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data_final, f, indent=2, ensure_ascii=False)

    subir_archivo("adicionales.json", OUTPUT_FILE)
    actualizar_columna_3(g)
    messagebox.showinfo("Éxito", "Configuración guardada")

ttk.Button(main_frame, text="GUARDAR CAMBIOS DEL GRUPO", command=guardar).pack(side="bottom", fill="x", pady=10)

def actualizar_lista_grupos():
    lista_grupos_ui.delete(0, tk.END)
    for g in grupos: lista_grupos_ui.insert(tk.END, g)

cargar_config_previa()
actualizar_lista_grupos()
renderizar_listas()
app.mainloop()