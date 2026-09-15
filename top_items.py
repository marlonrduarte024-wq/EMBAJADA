import json
import os
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import requests  # 🚀 NUEVO: Para la conexión directa con tu torre

# ✅ IMPORTACIÓN PARA EL RESPALDO SILENCIOSO
from supabase_utils import subir_archivo

# ======================
# CONFIG VISUAL Y RUTAS
# ======================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

RUTA_MENU = "c:/posred/bot/menu.json"
RUTA_CONFIG = "c:/posred/bot/web/menu_config.json"

DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

# Asegurar que las carpetas locales existan para evitar errores al volcar data
os.makedirs(os.path.dirname(RUTA_MENU), exist_ok=True)
os.makedirs(os.path.dirname(RUTA_CONFIG), exist_ok=True)

# ==========================================
# 🚀 SINCRONIZAR DESDE TU PROPIO SERVIDOR
# ==========================================

# 1. Descargar menu.json desde tu torre
try:
    print("⏳ Actualizando menu.json desde tu torre...")
    res = requests.get("https://nube.menwapp.com/embajada/json/menu.json", timeout=10)
    if res.status_code == 200:
        with open(RUTA_MENU, "w", encoding="utf-8") as f:
            json.dump(res.json(), f, indent=4, ensure_ascii=False)
        print("✅ menu.json actualizado desde el servidor propio")
except Exception as e:
    print("⚠️ No se pudo descargar menu.json del server propio, usando local:", e)

# 2. Descargar menu_config.json desde tu torre
try:
    print("⏳ Actualizando menu_config.json desde tu torre...")
    res = requests.get("https://nube.menwapp.com/embajada/json/menu_config.json", timeout=10)
    if res.status_code == 200:
        with open(RUTA_CONFIG, "w", encoding="utf-8") as f:
            json.dump(res.json(), f, indent=2, ensure_ascii=False)
        print("✅ menu_config.json actualizado desde el servidor propio")
except Exception as e:
    print("⚠️ No se pudo descargar menu_config.json del server propio, usando local:", e)


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
        messagebox.showerror("Error", f"No se pudo cargar menu.json local: {e}")
        return []

def cargar_recomendados_actuales():
    if os.path.exists(RUTA_CONFIG):
        with open(RUTA_CONFIG, "r", encoding="utf-8") as f:
            data = json.load(f)
            rec = data.get("recomendados", {})
            if isinstance(rec, list):
                return {cod: DIAS_SEMANA.copy() for cod in rec}
            return rec
    return {}

def guardar_recomendados():
    if os.path.exists(RUTA_CONFIG):
        try:
            with open(RUTA_CONFIG, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            data["recomendados"] = top_items_dict
            
            # Guardamos local en Windows primero
            with open(RUTA_CONFIG, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # ==========================================
            # 🚀 SUBIR A TU PROPIO SERVIDOR DEBIAN
            # ==========================================
            print("⏳ Subiendo menu_config.json a tu servidor local...")
            url_servidor = "https://nube.menwapp.com/upload/embajada/json"
            
            try:
                with open(RUTA_CONFIG, 'rb') as f:
                    payload = {'file': ('menu_config.json', f, 'application/json')}
                    response = requests.post(url_servidor, files=payload, timeout=10)
                
                if response.status_code == 200:
                    print("✅ ¡Subido con éxito a tu propio servidor!")
                else:
                    print(f"⚠️ Error en tu servidor, código: {response.status_code}")
            except Exception as server_error:
                print(f"⚠️ Falló la conexión con tu servidor: {server_error}")

            # ==========================================
            # SUBIR A SUPABASE (RESPALDO SILENCIOSO)
            # ==========================================
            try:
                subir_archivo("menu_config.json", RUTA_CONFIG)
            except Exception as sb_error:
                print(f"⚠️ Respaldo Supabase falló: {sb_error}")

            messagebox.showinfo("Listo", "Promos por día guardadas y sincronizadas ☁️")
        
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo procesar el guardado: {e}")

# ======================
# UI LOGIC
# ======================

menu_productos = cargar_menu()
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