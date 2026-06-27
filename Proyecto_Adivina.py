
'''
Proyecto III de Taller a la programación
"Adivina en qué estoy pensando"
José Antonio Azofeifa Ugalde
2026083609
'''

import tkinter as tk
from tkinter import messagebox, filedialog
import json
import os

'''
Clases
'''
#Clase para los nodos
class Nodo_desicion:
    def __init__(self, value="", es_pregunta=True, sí=None, no=None):
        self.value=value     #para la pregunta o la respuesta
        self.es_pregunta=es_pregunta
        self.sí=sí
        self.no=no
    
    def es_hoja(self):  #Verifica si es hoja o nodo
        return not self.es_pregunta
    
    def para_diccio(self):   #Transforma el nodo en un diccionario para .json
        if self.es_pregunta:
            return {"Pregunta": self.value,
                    "sí": self.sí.para_diccio() if self.sí else None,
                    "no": self.no.pra_diccio() if self.no else None}
        else:
            return {"Respuesta": self.value}
    
    @classmethod
    def from_diccio(cls,diccio):   #pasa de diccionario a un Nodo_desicion
        if diccio is None:
            return None
        if "Respuesta" in diccio:
            return cls(diccio["Respuesta"], es_pregunta=False)
        elif "Pregunta" in diccio:
            nodo_sí=cls.from_diccio(diccio.get("sí"))
            nodo_no=cls.from_diccio(diccio.get("no"))
            return cls(diccio["Pregunta"], es_pregunta=True, sí=nodo_sí, no=nodo_no)
        else:
            # Lanzar excepción para que el cargador lo detecte
            raise ValueError("Formato de nodo desconocido: " + repr(diccio))

#Clase para los árboles como tal
class Arbol:
    def __init__(self, raiz: Nodo_desicion):
        self.raiz=raiz
    
    @staticmethod
    def arbol_default():
        #Carga arbol_default.json si existe; si no, crea un árbol mínimo y lo guarda
        default_path = "arbol_default.json"
        # Intentar cargar el archivo por defecto si existe
        if os.path.exists(default_path):
            try:
                return Arbol.cargar_json(default_path)
            except Exception:
                # Si falla la carga (formato inválido, json corrupto...), seguimos al fallback.
                pass

        # Fallback: crear un árbol mínimo en memoria
        sí = Nodo_desicion("perro", es_pregunta=False)
        no = Nodo_desicion("piedra", es_pregunta=False)
        raiz = Nodo_desicion("¿Es un animal?", es_pregunta=True, sí=sí, no=no)
        arbol = Arbol(raiz)

        # Intentar guardar el fallback como arbol_default.json para próximas ejecuciones
        try:
            arbol.guardar_json(default_path)
        except Exception:
            # Si no puede escribir, simplemente seguimos adelante con el programa
            pass
        return arbol

    @classmethod
    def cargar_json(cls, filepath):
        #carga el árbol como diccionario de .json y lo transforma en un arbol que el resto del código puede manejar
        with open(filepath, "r", encoding="utf-8") as f:
            datos = json.load(f)
        root = Nodo_desicion.from_diccio(datos)
        if root==None:
            raise ValueError("El JSON no contiene un nodo raíz válido.")
        return cls(root)

    def guardar_json(self, filepath):        #guarda la última versión del árbol en un archivo .json
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.raiz.para_diccio(), f, ensure_ascii=False, indent=4)
    

'''
GUI
'''
class Ventana:
    def __init__(self):
        self.Menu=tk.Tk()
        #mantiene la ruta del archivo actual del árbol (puede ser arbol_default.json u otro seleccionado)
        self.current_filepath = None
        #intentar cargar el archivo por defecto si existe, sino crear uno en memoria.
        default_path = "arbol_default.json"
        if os.path.exists(default_path):
            try:
                self.tree = Arbol.cargar_json(default_path)
                self.current_filepath = default_path
            except Exception:
                self.tree = Arbol.arbol_default()
                #se intentará guardar fallback y asignar current_filepath si tiene éxito
                try:
                    self.tree.guardar_json(default_path)
                    self.current_filepath = default_path
                except Exception:
                    self.current_filepath = None
        else:
            # Guardar el default en disco para futuras ejecuciones
            self.tree = Arbol.arbol_default()
            #si arbol_default se logró guardar, asignamos path
            if os.path.exists(default_path):
                self.current_filepath = default_path
            else:
                self.current_filepath = None
    
        self.Menu.title("Menú Adivina en qué estoy pensando_Akinator")
        self.Menu.geometry("500x500")
    
        tk.Label(self.Menu, text=f"Adivina en qué estoy pensando\n😎 >:D 😎", font=("Times New Roman", 24, "bold"), bg="#D1CD12").pack(pady=10, fill=tk.X)

        #Frame para los labels instructivos
        frame_ins=tk.Frame(self.Menu, bg="#15CEE6")
        frame_ins.pack(padx=10, pady=10, fill=tk.BOTH, expand=False)
    
        tk.Label(frame_ins, text="Instrucciones básicas para jugar: ", font=("Times New Roman", 14, "bold"), bg="#25C6DB").pack(padx=2,pady=2)
        tk.Label(frame_ins, text=f"1. Cargue el árbol que desea jugar\n(o juega el de defecto) ", font=("Times New Roman", 14, "bold"), bg="#25C6DB").pack(padx=2,pady=2)
        tk.Label(frame_ins, text="2. Piense en el objeto o ser\nque quiere que le adivinen", font=("Times New Roman", 14, "bold"), bg="#25C6DB").pack(padx=2,pady=2)
        tk.Label(frame_ins, text=f"3. Responda sí o no ante cada pregunta,\nrecuerde ser sincero para que el sistema atine", font=("Times New Roman", 14, "bold"), bg="#25C6DB").pack(padx=2,pady=2)
        tk.Label(frame_ins, text="4. Si al final nunca le atina,\nentonces agregue una pregunta de sí o no\nque le permita al sistema atinarle", font=("Times New Roman", 14, "bold"), bg="#25C6DB").pack(padx=2,pady=2)

        # Botones en la parte inferior
        frame_botones = tk.Frame(self.Menu)
        frame_botones.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        tk.Button(frame_botones, text="Cargar", command=self.cargar_arbol_archivo,
                  font=("Times New Roman", 12, "bold"), bg="#d0820d", width=15).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_botones, text="Empezar el juego", command=self.empezar_juego,
                  font=("Times New Roman", 11, "bold"), bg="#11DB9B", width=15).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_botones, text="Salir", command=self.Menu.destroy,
                  font=("Times New Roman", 12, "bold"), bg="#ce0a1a", width=15).pack(side=tk.RIGHT, padx=10)
    
    def cargar_arbol_archivo(self):
        filepath = filedialog.askopenfilename(
            title="Seleccionar árbol",
            filetypes=[("JSON files", "*.json")]
        )
        if not filepath:
            return
        try:
            tree = Arbol.cargar_json(filepath)
            if tree is None or tree.raiz is None:
                messagebox.showerror("ERROR","El archivo no contiene un árbol válido.")
                return
            self.tree = tree
            messagebox.showinfo("CARGADO", f"Árbol cargado correctamente desde:\n{filepath}")
        except Exception as e:
            # En caso de fallo, mostrar mensaje y ofrecer seguir con árbol por defecto
            messagebox.showerror("ERROR", f"No se pudo cargar: {e}\nSe usará el árbol por defecto.")
            self.tree = Arbol.arbol_default()
    
    def empezar_juego(self):
        try:
            import Akinator_jugar
            # Pasamos el árbol (objeto Arbol), la ventana y la ruta actual del archivo (puede ser None)
            if hasattr(Akinator_jugar, "jugar_arbol"):
                Akinator_jugar.jugar_arbol(self.tree, self.Menu, self.current_filepath)
            else:
                messagebox.showerror("ERROR", "El módulo Akinator_jugar no tiene la función 'jugar_arbol'.")
        except ModuleNotFoundError:
            messagebox.showinfo("NO IMPLEMENTADO",
                                "No se encontró el módulo 'Akinator_jugar'.\nAsegúrate de que está en el mismo directorio y contiene jugar_arbol(tree, ventana, filepath).")
        except Exception as e:
            messagebox.showerror("ERROR", f"Ocurrió un error al intentar iniciar el juego: {e}")


#para abrir la ventana desde la clase
def main():
    app = Ventana()
    app.Menu.mainloop()

if __name__ == "__main__":
    main()
