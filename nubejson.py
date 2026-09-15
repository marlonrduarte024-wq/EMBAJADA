import os
import requests
import mimetypes  # 🚀 NUEVO: Para detectar automáticamente el tipo de archivo (.txt, .json, etc.)
import customtkinter as ctk
from tkinter import filedialog, messagebox

# Configuración de tu API local
URL_BASE_UPLOAD = "https://nube.menwapp.com/upload/distrito"

def seleccionar_archivo():
    # 🚀 MODIFICADO: Ahora permite seleccionar cualquier tipo de archivo
    ruta = filedialog.askopenfilename(filetypes=[("Todos los archivos", "*.*"), ("Archivos JSON", "*.json"), ("Archivos de Texto", "*.txt")])
    if ruta:
        entry_ruta.delete(0, "end")
        entry_ruta.insert(0, ruta)

def ejecutar_subida():
    ruta_local = entry_ruta.get().strip()
    carpeta_destino = combo_destino.get().lower() # 'json' o 'imagenes'
    
    if not ruta_local or not os.path.exists(ruta_local):
        messagebox.showwarning("Aviso", "Por favor selecciona un archivo válido.")
        return
        
    nombre_archivo = os.path.basename(ruta_local)
    url_final = f"{URL_BASE_UPLOAD}/{carpeta_destino}"
    
    # 🚀 NUEVO: Detectar el tipo MIME real (ej: 'text/plain', 'application/json', etc.)
    # Si no logra adivinarlo, le asignamos uno genérico por defecto
    tipo_mime, _ = mimetypes.guess_type(ruta_local)
    if not tipo_mime:
        tipo_mime = 'application/octet-stream'
    
    try:
        btn_subir.configure(state="disabled", text="Subiendo...")
        root.update()
        
        with open(ruta_local, 'rb') as f:
            # 🚀 MODIFICADO: Se inyecta la variable tipo_mime dinámica en vez de 'application/json' fijo
            payload = {'file': (nombre_archivo, f, tipo_mime)}
            response = requests.post(url_final, files=payload, timeout=15)
            
        if response.status_code == 200:
            messagebox.showinfo("Éxito", f"¡{nombre_archivo} subido correctamente a /distrito/{carpeta_destino}!")
            entry_ruta.delete(0, "end")
        else:
            messagebox.showerror("Error", f"El servidor respondió con código: {response.status_code}\n{response.text}")
            
    except Exception as e:
        messagebox.showerror("Error de red", f"No se pudo conectar con la torre:\n{e}")
    finally:
        btn_subir.configure(state="normal", text="Subir Archivo")

# --- INTERFAZ GRÁFICA ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("Subidor Multipropósito - Menwapp")
root.geometry("550x280")
root.resizable(False, False)

# Título
ctk.CTkLabel(root, text="Carga Masiva de Archivos a la Torre", font=("Arial", 18, "bold")).pack(pady=15)

# Frame Selección de Archivo
frame_archivo = ctk.CTkFrame(root)
frame_archivo.pack(fill="x", padx=20, pady=10)

# 🚀 MODIFICADO: Ajustado el placeholder
entry_ruta = ctk.CTkEntry(frame_archivo, placeholder_text="Selecciona cualquier tipo de archivo...", width=360)
entry_ruta.pack(side="left", padx=10, pady=10)

btn_buscar = ctk.CTkButton(frame_archivo, text="Buscar", width=90, command=seleccionar_archivo)
btn_buscar.pack(side="left", padx=5)

# Frame Destino
frame_destino = ctk.CTkFrame(root)
frame_destino.pack(fill="x", padx=20, pady=10)

ctk.CTkLabel(frame_destino, text="Carpeta de destino:", font=("Arial", 13)).pack(side="left", padx=15, pady=10)

combo_destino = ctk.CTkComboBox(frame_destino, values=["json", "imagenes"], width=150)
combo_destino.pack(side="left", padx=5)
combo_destino.set("json") # Destino por defecto

# Botón Acción
btn_subir = ctk.CTkButton(root, text="Subir Archivo", font=("Arial", 14, "bold"), height=40, command=ejecutar_subida)
btn_subir.pack(fill="x", padx=20, pady=20)

root.mainloop()