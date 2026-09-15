import json
import os
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

# ✅ IMPORTACIÓN DE TU UTILIDAD
from supabase_utils import subir_archivo, descargar_archivo

# ======================
# CONFIG VISUAL Y RUTAS
# ======================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

RUTA_MENU = "c:/posred/bot/menu.json"
RUTA_CONFIG = "c:/posred/bot/web/menu_config.json"

DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

# ======================
# SINCRONIZAR DESDE SUPABASE
# ======================

try:
    descargar_archivo("menu.json", RUTA_MENU)
    print("✅ menu.json actualizado desde Supabase")
except Exception as e:
    print("⚠️ No se pudo descargar menu.json:", e)

try:
    descargar_archivo("menu_config.json", RUTA_CONFIG)
    print("✅ menu_config.json actualizado desde Supabase")
except Exception as e:
    print("⚠️ No se pudo descargar menu_config.json:", e)

# ======================
# CARGA / GUARDADO
# ======================

def cargar_menu():
    try:
        with open(RUTA_MENU, "r", encoding="utf-8") as f:
            data = json.load(f)
        productos = []
        menu = data.get("menu", {})
        for categoria, items in menu.items():
            for p in items:
                productos.append({
                    "codigo": str(p.get("codigo", "")).strip(),
                    "nombre": p.get("articulo", "").strip(),
                    "categoria": categoria
                })
        return productos
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo cargar menu.json: {e}")
        return []

def cargar_recomendados_actuales():
    """
    Ahora 'recomendados' será un diccionario: {"codigo": ["Lunes", "Martes"]}
    """
    if os.path.exists(RUTA_CONFIG):
        with open(RUTA_CONFIG, "r", encoding="utf-8") as f:
            data = json.load(f)
            rec = data.get("recomendados", {})
            # Si el archivo viejo tiene una lista [], la convertimos a {}
            if isinstance(rec, list):
                return {cod: DIAS_SEMANA.copy() for cod in rec}
            return rec
    return {}

def guardar_recomendados():
    if os.path.exists(RUTA_CONFIG):
        try:
            with open(RUTA_CONFIG, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Guardamos el diccionario de códigos con sus días
            data["recomendados"] = top_items_dict
            
            with open(RUTA_CONFIG, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            subir_archivo("menu_config.json", RUTA_CONFIG)
            messagebox.showinfo("Listo", "Promos por día guardadas y sincronizadas ☁️")
        
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {e}")

# ======================
# UI LOGIC
# ======================

menu_productos = cargar_menu()
# Diccionario: { "codigo": [dias...] }
top_items_dict = cargar_recomendados_actuales()

root = ctk.CTk()
root.title("Gestor de Promos por Día ⭐")
root.geometry("1100x750")

# Panel Izquierdo
panel_izq = ctk.CTkFrame(root, width=300)
panel_izq.pack(side="left", fill="y", padx=10, pady=10)

ctk.CTkLabel(panel_izq, text="🔍 Buscar Producto", font=("Arial", 14, "bold")).pack(pady=10)
buscar_var = tk.StringVar()
ctk.CTkEntry(panel_izq, textvariable=buscar_var, placeholder_text="Escribe nombre...").pack(fill="x", padx=15)

lista_busqueda = tk.Listbox(panel_izq, bg="#1a1a1a", fg="white", font=("Arial", 10), borderwidth=0)
lista_busqueda.pack(expand=True, fill="both", padx=15, pady=15)

# Panel Derecho
panel_der = ctk.CTkFrame(root)
panel_der.pack(side="right", expand=True, fill="both", padx=10, pady=10)
ctk.CTkLabel(panel_der, text="Configuración de Promos Diarias", font=("Arial", 16, "bold")).pack(pady=10)

frame_lista_top = ctk.CTkScrollableFrame(panel_der, fg_color="#1a1a1a")
frame_lista_top.pack(expand=True, fill="both", padx=10, pady=10)

def actualizar_dias(codigo, dia, estado):
    if estado:
        if dia not in top_items_dict[codigo]:
            top_items_dict[codigo].append(dia)
    else:
        if dia in top_items_dict[codigo]:
            top_items_dict[codigo].remove(dia)

def reconstruir_panel():
    for w in frame_lista_top.winfo_children():
        w.destroy()
    
    for cod, dias in top_items_dict.items():
        prod = next((p for p in menu_productos if p["codigo"] == cod), None)
        if not prod: continue

        f_master = ctk.CTkFrame(frame_lista_top, fg_color="#2a2a2a")
        f_master.pack(fill="x", pady=5, padx=5)

        # Info Producto
        f_info = ctk.CTkFrame(f_master, fg_color="transparent")
        f_info.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(f_info, text=f"⭐ {prod['nombre']}", font=("Arial", 13, "bold")).pack(side="left")
        ctk.CTkButton(f_info, text="Eliminar", width=70, height=20, fg_color="#c0392b", 
                      command=lambda c=cod: eliminar(c)).pack(side="right")

        # Selector de Días
        f_dias = ctk.CTkFrame(f_master, fg_color="transparent")
        f_dias.pack(fill="x", padx=10, pady=5)
        
        for dia in DIAS_SEMANA:
            is_checked = dia in dias
            cb = ctk.CTkCheckBox(f_dias, text=dia, font=("Arial", 10), width=80,
                                 command=lambda c=cod, d=dia: toggle_dia(c, d))
            if is_checked: cb.select()
            cb.pack(side="left", padx=5)

def toggle_dia(codigo, dia):
    if dia in top_items_dict[codigo]:
        top_items_dict[codigo].remove(dia)
    else:
        top_items_dict[codigo].append(dia)

def eliminar(cod):
    if cod in top_items_dict:
        del top_items_dict[cod]
        reconstruir_panel()

def filtrar(*args):
    texto = buscar_var.get().lower()
    lista_busqueda.delete(0, "end")
    for p in menu_productos:
        if texto in p["nombre"].lower():
            lista_busqueda.insert("end", p["nombre"])

def agregar(event):
    if not lista_busqueda.curselection(): return
    seleccion = lista_busqueda.get(lista_busqueda.curselection())
    prod = next(p for p in menu_productos if p["nombre"] == seleccion)
    if prod["codigo"] not in top_items_dict:
        # Por defecto se agrega para todos los días
        top_items_dict[prod["codigo"]] = DIAS_SEMANA.copy()
        reconstruir_panel()

buscar_var.trace_add("write", filtrar)
lista_busqueda.bind("<Double-Button-1>", agregar)

btn_guardar = ctk.CTkButton(root, text="💾 GUARDAR CONFIGURACIÓN DE PROMOS", 
                            command=guardar_recomendados, fg_color="#27ae60", height=50)
btn_guardar.pack(fill="x", padx=20, pady=15)

filtrar()
reconstruir_panel()
root.mainloop()