
'''
La parte de la jugabilidad del akinator/Adivina en qué estoy pensando
'''
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
from typing import Optional
import os
import Proyecto_Adivina as PA  

#Permite guardar el árbol en un archivo .json
def guardar_arbol_archivo(tree:PA.Arbol):
    filepath = filedialog.asksaveasfilename(
        title="Guardar árbol",
        defaultextension=".json",
        filetypes=[("JSON files", "*.json")]
    )
    if filepath:
        try:
            tree.guardar_json(filepath)
            messagebox.showinfo("GUARDADO", f"Árbol guardado correctamente en:\n{filepath}")
        except Exception as e:
            messagebox.showerror("ERROR", f"No se pudo guardar el árbol: {e}")



def jugar_arbol(tree:PA.Arbol, ventana, source_path: Optional[str] =None):
    #Source_path es para tener un acceso directo al archivo para sobrescribirlo, en caso de que este no sea None
    #Verificar que el tree sea una instancia de PA:Arbol 
    if tree is None or tree.raiz is None:
        messagebox.showerror("ERROR", "Árbol inválido.")
        return
    
    # Estado mutable para la función interna
    state = {"nodo_actual": tree.raiz}

    juego=tk.Toplevel(ventana)
    juego.title("Ventana de juego Adivina en qué estoy pensando_Akinator")
    juego.geometry("700x400")

    tk.Label(juego, text=f"Adivina en qué estoy pensando\n😎 >:D 😎", font=("Times New Roman", 24, "bold"), bg="#D1CD12").pack(pady=10, fill=tk.X)

    #frame para las preguntas y para el sí o no
    frame = tk.Frame(juego, bg="#1ac6b8")
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)


    pregunta_var = tk.StringVar()
    tk.Label(frame, textvariable=pregunta_var, font=("Times New Roman", 16, "bold"),
                              bg="#1ac6b8", wraplength=650, justify="center").pack(pady=20)

    botones_frame = tk.Frame(frame, bg="#1ac6b8")
    botones_frame.pack(pady=10)

    def intentar_guardado_automatico():
        #Si se conoce la ruta source_path, le daremos uso para sobrescribir en el archivo del árbol
        if source_path:
            try:
                tree.guardar_json(source_path)
                #No mostramos popup (guardado silencioso)
            except Exception:
                #Si no se logra guardar
                pass

    def actualizar_vista():
        nodo: Optional[PA.Nodo_desicion] = state["nodo_actual"]
        if nodo is None:
            pregunta_var.set("Árbol vacío.")
            b_si.config(state=tk.DISABLED)
            b_no.config(state=tk.DISABLED)
            return

        if nodo.es_hoja():
            # Mostrar la respuesta propuesta
            pregunta_var.set(f"¿Estás pensando en: {nodo.value}?")
        else:
            pregunta_var.set(nodo.value)
    
    def definir_rama_vacía(nodo: PA.Nodo_desicion, branch="sí"):
        #Por si un nodo se queda sin respuesta o info en general, entonces permitir definir la respuesta del nodo
        texto = simpledialog.askstring("Definir rama", f"Ingrese la respuesta (texto) para la rama '{branch}':")
        if not texto or not texto.strip():
            messagebox.showwarning("Entrada vacía", "Debe ingresar texto no vacío para crear la rama.")
            return
        nuevo_nodo = PA.Nodo_desicion(texto, es_pregunta=False)
        if branch == "sí":
            nodo.si = nuevo_nodo
        else:
            nodo.no = nuevo_nodo
        # intentar guardar automáticamente
        intentar_guardado_automatico()
        messagebox.showinfo("Definido", f"Se creó la rama '{branch}' con '{texto}'.")
        # no cambiamos nodo actual; el usuario puede seguir desde aquí

    def accion_sí():
        nodo: Optional[PA.Nodo_desicion] = state["nodo_actual"]
        if nodo is None:
            return
        if nodo.es_hoja():
            # Si la suposición fue correcta
            messagebox.showinfo("¡Le he atinado!", "¡Genial! Adiviné correctamente :D.")
            preguntar_reiniciar()
        # Comprobación explícita antes de asignar
        if nodo.si is None:
            # Ofrecer crear la rama en ese momento (evita None assignment)
            if messagebox.askyesno("Rama faltante", "La rama 'si' no está definida. ¿Deseas crearla ahora?"):
                definir_rama_vacía(nodo, "si")
            return
        state["nodo_actual"] = nodo.si
        actualizar_vista()
    

    def accion_no():
        nodo: Optional[PA.Nodo_desicion] = state["nodo_actual"]
        if nodo is None:
            return
        if nodo.es_hoja():
            # Suposición incorrecta: aprender
            aprender(nodo)
        if nodo.no is None:
            if messagebox.askyesno("Rama faltante", "La rama 'no' no está definida. ¿Deseas crearla ahora?"):
                definir_rama_vacía(nodo, "no")
            return
        state["nodo_actual"] = nodo.no
        actualizar_vista()

    def preguntar_reiniciar():
        # Preguntar si quiere jugar otra vez (volviendo a la raíz)
        if messagebox.askyesno("Jugar otra vez", "¿Quieres jugar otra partida?"):
            state["nodo_actual"] = tree.raiz
            actualizar_vista()
        else:
            intentar_guardado_automatico()
            juego.destroy()
    
    def aprender(nodo_hoja: PA.Nodo_desicion):
        # Pedir respuesta correcta y pregunta que distinga
        respuesta_correcta = simpledialog.askstring("Enseñar", "No adiviné D,: ¿En qué pensabas?")
        if not respuesta_correcta or not respuesta_correcta.strip():
            messagebox.showwarning("Entrada vacía", "Debe escribir la respuesta correcta para que aprenda.")
            return
        pregunta_dist = simpledialog.askstring("Enseñar", f"Proporcione una pregunta de sí/no que permita distinguir '{respuesta_correcta}' de '{nodo_hoja.value}':")
        if not pregunta_dist or not pregunta_dist.strip():
            messagebox.showwarning("Entrada vacía", "Debe escribir una pregunta válida para que el sistema aprenda.")
            return
        # Preguntar si la respuesta correcta corresponde a 'sí' ante la nueva pregunta
        si_es_nuevo = messagebox.askyesno("Enseñar", f"Para la pregunta:\n'{pregunta_dist}'\n¿la respuesta 'sí' corresponde a '{respuesta_correcta}'? (Sí -> {respuesta_correcta})")

        # Crear nuevos nodos
        nuevo_nodo_respuesta = PA.Nodo_desicion(respuesta_correcta.strip(), es_pregunta=False)
        viejo_nodo_respuesta = PA.Nodo_desicion(nodo_hoja.value, es_pregunta=False)

        # Actualizar el nodo actual in-place (reemplaza hoja por pregunta)
        nodo_hoja.es_pregunta = True
        nodo_hoja.value = pregunta_dist.strip()
        if si_es_nuevo:
            nodo_hoja.si = nuevo_nodo_respuesta
            nodo_hoja.no = viejo_nodo_respuesta
        else:
            nodo_hoja.si = viejo_nodo_respuesta
            nodo_hoja.no = nuevo_nodo_respuesta
        
        # Guardado automático silencioso
        intentar_guardado_automatico()
        messagebox.showinfo("Aprendido", "¡Gracias! — he aprendido algo nuevo :D")
        state["nodo_actual"] = tree.raiz
        actualizar_vista()

    # Botones Sí / No
    b_si =tk.Button(botones_frame, text="Sí", width=12, bg="#11DB18", font=("Times New Roman", 14, "bold"), command=accion_sí)
    b_si.grid(row=0, column=0, padx=20)
    b_no=tk.Button(botones_frame, text="No", width=12, bg="#f73434", font=("Times New Roman", 14, "bold"), command=accion_no)
    b_no.grid(row=0, column=1, padx=20)

    # Botones extra: Guardar y Reiniciar
    extras_frame = tk.Frame(frame, bg="#1ac6b8")
    extras_frame.pack(pady=8)

    tk.Button(extras_frame, text="Volver al inicio", command=lambda: [state.update({"nodo_actual": tree.raiz}), actualizar_vista()]).pack(side=tk.LEFT, padx=6)
    tk.Button(extras_frame, text="Guardar como...", command=lambda: guardar_arbol_archivo(tree)).pack(side=tk.LEFT, padx=6)

    # Handler para cerrar la ventana (guardar automáticamente si se puede)
    def on_close():
        intentar_guardado_automatico()
        juego.destroy()
    
    #por si se cierra la ventana con la equis que viene por default, también se actualice
    juego.protocol("WM_DELETE_WINDOW", on_close)

    # Inicializar vista con la raíz
    state["nodo_actual"] = tree.raiz
    actualizar_vista()
