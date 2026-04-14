import os
import sys
import hashlib
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
try:
    from send2trash import send2trash
except ImportError:
    messagebox.showerror("Error", "La librería 'send2trash' no está instalada.\nEjecute: pip install send2trash")
    sys.exit(1)

class DuplicateFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Eliminador de Duplicados - Estilo Explorador")
        self.root.geometry("800x600")

        # Configuración de estilos
        style = ttk.Style()
        style.theme_use('clam')

        # Marco Principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Marco para controles superiores
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        self.btn_select = ttk.Button(control_frame, text="Seleccionar Carpeta", command=self.select_folder)
        self.btn_select.pack(side=tk.LEFT)

        self.lbl_status = ttk.Label(control_frame, text="Esperando selección...")
        self.lbl_status.pack(side=tk.LEFT, padx=10)

        self.btn_delete = ttk.Button(control_frame, text="Eliminar Seleccionados", command=self.delete_selected, state=tk.DISABLED)
        self.btn_delete.pack(side=tk.RIGHT)

        # Árbol de visualización (Treeview)
        # Columnas: Archivo, Ruta, Tamaño
        self.tree = ttk.Treeview(main_frame, columns=("path", "size"), selectmode="extended")
        self.tree.heading("#0", text="Nombre / Grupo", anchor=tk.W)
        self.tree.heading("path", text="Ruta Completa", anchor=tk.W)
        self.tree.heading("size", text="Tamaño", anchor=tk.W)
        
        self.tree.column("#0", width=200, minwidth=100)
        self.tree.column("path", width=400, minwidth=200)
        self.tree.column("size", width=100, minwidth=50)

        # Scrollbars para el Treeview
        vsb = ttk.Scrollbar(main_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(main_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)

        self.duplicates_data = {}

    def select_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.lbl_status.config(text=f"Escaneando: {folder_selected}...")
            self.root.update()
            self.scan_folder(folder_selected)

    def get_file_hash(self, filepath, block_size=65536):
        """Calcula el hash MD5 de un archivo."""
        hasher = hashlib.md5()
        try:
            with open(filepath, "rb") as f:
                buf = f.read(block_size)
                while len(buf) > 0:
                    hasher.update(buf)
                    buf = f.read(block_size)
            return hasher.hexdigest()
        except OSError:
            return None

    def format_size(self, size):
        # Convertir bytes a formato legible
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} PB"

    def scan_folder(self, folder):
        # Limpiar árbol previo
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        files_by_size = {}
        
        # Paso 1: Agrupar por tamaño (rápido)
        for dirpath, _, filenames in os.walk(folder):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    size = os.path.getsize(filepath)
                    if size in files_by_size:
                        files_by_size[size].append(filepath)
                    else:
                        files_by_size[size] = [filepath]
                except OSError:
                    continue

        # Paso 2: Calcular hash solo para archivos con el mismo tamaño
        self.duplicates_data = {}
        total_groups = 0
        
        for size, files in files_by_size.items():
            if len(files) < 2:
                continue
            
            hashes = {}
            for filepath in files:
                file_hash = self.get_file_hash(filepath)
                if file_hash:
                    if file_hash in hashes:
                        hashes[file_hash].append(filepath)
                    else:
                        hashes[file_hash] = [filepath]
            
            # Filtrar los que tienen duplicados reales (hash colisión)
            for h, paths in hashes.items():
                if len(paths) > 1:
                    self.duplicates_data[h] = {"size": size, "paths": paths}
                    total_groups += 1

        self.populate_tree()
        self.lbl_status.config(text=f"Escaneo completado. Se encontraron {total_groups} grupos de duplicados.")
        
        if total_groups > 0:
            self.btn_delete.config(state=tk.NORMAL)
        else:
            self.btn_delete.config(state=tk.DISABLED)

    def populate_tree(self):
        for h, data in self.duplicates_data.items():
            size_str = self.format_size(data["size"])
            # Nodo padre (Grupo)
            group_id = self.tree.insert("", "end", text=f"Grupo {h[:8]} ({len(data['paths'])} archivos)", values=("", size_str))
            
            # Nodos hijos (Archivos)
            for path in data["paths"]:
                filename = os.path.basename(path)
                self.tree.insert(group_id, "end", text=filename, values=(path, size_str))
        
        # Expandir todos los grupos para verlos fácilmente
        # for item in self.tree.get_children():
        #     self.tree.item(item, open=True) 

    def delete_selected(self):
        selected_items = self.tree.selection()
        
        if not selected_items:
            messagebox.showwarning("Advertencia", "Por favor seleccione archivos para eliminar.")
            return

        files_to_delete = []
        for item in selected_items:
            # Verificar si es un archivo (tiene padre)
            if self.tree.parent(item):
                file_path = self.tree.item(item, "values")[0]
                files_to_delete.append((item, file_path))
        
        if not files_to_delete:
             messagebox.showwarning("Advertencia", "Seleccione los archivos individuales dentro de los grupos, no el grupo entero.")
             return

        confirm = messagebox.askyesno("Confirmar Eliminación", f"¿Está seguro de que desea eliminar {len(files_to_delete)} archivos permanentemente?")
        
        if confirm:
            deleted_count = 0
            for item, file_path in files_to_delete:
                try:
                    # Normalizar la ruta para Windows (corrige mezclas de / y \)
                    path_normalized = os.path.normpath(os.path.abspath(file_path))
                    send2trash(path_normalized) 
                    # self.tree.delete(item) # Solo eliminar del árbol si fue exitoso (send2trash lanza error si falla)
                    self.tree.delete(item)
                    deleted_count += 1
                except Exception as e:
                    print(f"Error enviando a papelera {file_path}: {e}")
            
            messagebox.showinfo("Éxito", f"Se enviaron {deleted_count} archivos a la Papelera de Reciclaje.")
            
            # Opcional: Limpiar grupos vacíos o con solo 1 elemento
            # (Se requeriría re-escanear o lógica compleja de actualización del árbol)

if __name__ == "__main__":
    root = tk.Tk()
    app = DuplicateFinderApp(root)
    root.mainloop()
