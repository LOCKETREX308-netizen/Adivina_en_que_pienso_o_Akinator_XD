
'''
La parte de la jugabilidad del akinator/Adivina en qué estoy pensando
'''
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import Proyecto_Adivina as PA  

#Permite guardar el árbol en un archivo .json
def guardar_arbol_archivo(tree:PA.Arbol):
    filepath = filedialog.asksaveasfilename(
        title=f"Guardar árbol",
        defaultextension=".json",
        filetypes=[("JSON files", "*.json")]
    )
    if filepath:
        try:
            tree.guardar_json(filepath)
            messagebox.showinfo("GUARDADO", f"Árbol guardado correctamente en:\n{filepath}")
        except Exception as e:
            messagebox.showerror("ERROR", f"No se pudo guardar el árbol: {e}")



def jugar_arbol(tree:PA.Arbol, ventana, source_path=None):
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

    def actualizar_vista():
        nodo = state["nodo_actual"]
        if nodo is None:
            pregunta_var.set("Árbol vacío.")
            b_sí.config(state=tk.DISABLED)
            b_no.config(state=tk.DISABLED)
            return

        if nodo.es_hoja():
            # Mostrar la respuesta propuesta
            pregunta_var.set(f"¿Estás pensando en: {nodo.value}?")
        else:
            pregunta_var.set(nodo.value)

    def accion_sí():
        nodo = state["nodo_actual"]
        if nodo is None:
            return
        if nodo.es_hoja():
            # Si la suposición fue correcta
            messagebox.showinfo("¡Le he atinado!", "¡Genial! Adiviné correctamente :D.")
            preguntar_reiniciar()
        else:
            if nodo.sí is None:
                messagebox.showwarning("Datos incompletos", "La rama 'sí' no está definida en este nodo.")
                return
            state["nodo_actual"] = nodo.sí
            actualizar_vista()

    def accion_no():
        nodo = state["nodo_actual"]
        if nodo is None:
            return
        if nodo.es_hoja():
            # Suposición incorrecta: aprender
            aprender(nodo)
        else:
            if nodo.no is None:
                messagebox.showwarning("Datos incompletos", "La rama 'no' no está definida en este nodo.")
                return
            state["nodo_actual"] = nodo.no
            actualizar_vista()

    def preguntar_reiniciar():
        # Preguntar si quiere jugar otra vez (volviendo a la raíz)
        if messagebox.askyesno("Jugar otra vez", "¿Quieres jugar otra partida?"):
            state["nodo_actual"] = tree.raiz
            actualizar_vista()
        else:
            juego.destroy()
    
    def intentar_guardado_automatico():
        #Si se conoce la ruta source_path, le daremos uso para sobrescribir en el archivo del árbol
        if source_path:
            try:
                tree.guardar_json(source_path)
                #No mostramos popup (guardado silencioso)
            except Exception:
                #Si no se logra guardar
                pass
    
    def aprender(nodo_hoja):
        # Pedir respuesta correcta y pregunta que distinga
        respuesta_correcta = simpledialog.askstring("Enseñar", "No adiviné D,: ¿En qué pensabas?")
        if not respuesta_correcta:
            return
        pregunta_dist = simpledialog.askstring("Enseñar", f"Proporcione una pregunta de sí/no que permita distinguir '{respuesta_correcta}' de '{nodo_hoja.value}':")
        if not pregunta_dist:
            return
        # Preguntar si la respuesta correcta corresponde a 'sí' ante la nueva pregunta
        si_es_nuevo = messagebox.askyesno("Enseñar", f"Para la pregunta:\n'{pregunta_dist}'\n¿la respuesta 'sí' corresponde a '{respuesta_correcta}'? (Sí -> {respuesta_correcta})")

        # Crear nuevos nodos
        nuevo_nodo_respuesta = PA.Nodo_desicion(respuesta_correcta, es_pregunta=False)
        viejo_nodo_respuesta = PA.Nodo_desicion(nodo_hoja.value, es_pregunta=False)

        # Actualizar el nodo actual in-place (reemplaza hoja por pregunta)
        nodo_hoja.es_pregunta = True
        nodo_hoja.value = pregunta_dist
        if si_es_nuevo:
            nodo_hoja.si = nuevo_nodo_respuesta
            nodo_hoja.no = viejo_nodo_respuesta
        else:
            nodo_hoja.si = viejo_nodo_respuesta
            nodo_hoja.no = nuevo_nodo_respuesta
        
        #intentamos guardar automáticamente en source_path si está definido
        if source_path:
            try:
                tree.guardar_json(source_path)
            except Exception:
                # Ignorar fallos de escritura; continuar sin molestar al usuario
                pass
        
        messagebox.showinfo("Aprendido", "Gracias — he aprendido algo nuevo.")
        # Reiniciar a la raíz para jugar de nuevo
        state["nodo_actual"] = tree.raiz
        actualizar_vista()

    # Botones Sí / No
    b_sí= tk.Button(botones_frame, text="Sí", width=12, bg="#11DB18", font=("Times New Roman", 14, "bold"), command=accion_sí)
    b_sí.grid(row=0, column=0, padx=20)
    b_no=tk.Button(botones_frame, text="No", width=12, bg="#f73434", font=("Times New Roman", 14, "bold"), command=accion_no)
    b_no.grid(row=0, column=1, padx=20)

    # Botones extra: Guardar y Reiniciar
    extras_frame = tk.Frame(frame, bg="#1ac6b8")
    extras_frame.pack(pady=8)

    tk.Button(extras_frame, text="Volver al inicio", command=lambda: [state.update({"nodo_actual": tree.raiz}), actualizar_vista()], bg="#E61F93").pack(side=tk.LEFT, padx=6)

    # Handler para cerrar la ventana (guardar automáticamente si se puede)
    def on_close():
        intentar_guardado_automatico()
        juego.destroy()
    
    #por si se cierra la ventana con la equis que viene por default, también se actualice
    juego.protocol("WM_DELETE_WINDOW", on_close)

    # Inicializar vista con la raíz
    state["nodo_actual"] = tree.raiz
    actualizar_vista()
