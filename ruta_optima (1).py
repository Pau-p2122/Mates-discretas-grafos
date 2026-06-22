#  CALCULADORA DE RUTA ÓPTIMA ENTRE CIUDADES
#  Matematica Discreta, Teoria de Grafos
#  Integrantes:
#  Paula Pasten, Asher Galvan, Tomas Mardones

#LIBRERIAS
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os

# FUNCIÓN 1: Cargar datos desde el archivo Excel
def cargar_datos(ruta_excel):
      
    df = pd.read_excel(ruta_excel) #PANDAS lee excel con los datos de las ciudades y distancias

    G = nx.Graph()  # Grafo no dirigido (se puede ir y volver)

    for _, fila in df.iterrows():
        origen  = fila["ciudad de origen"]
        destino = fila["ciudad de destino"]
        peso    = fila["distancia (km)"]
        # Agrega la conexión (arista) con su distancia como peso
        G.add_edge(origen, destino, weight=peso)

    ciudades = sorted(G.nodes())  # Lista de ciudades en orden alfabético
    return G, ciudades

# FUNCIÓN 2: Calcular la ruta óptima (Dijkstra manual)
def calcular_ruta_optima(G, origen, destino):
 
    # ── Inicialización ──
    distancias   = {nodo: float("inf") for nodo in G.nodes()}
    predecesores = {nodo: None        for nodo in G.nodes()}
    distancias[origen] = 0
    no_visitados = set(G.nodes())

    while no_visitados:
        # Seleccionar el nodo no visitado con menor distancia acumulada
        nodo_actual = min(no_visitados, key=lambda n: distancias[n])

        # Si la distancia mínima es infinita, los nodos restantes son inalcanzables
        if distancias[nodo_actual] == float("inf"):
            break

        # Si llegamos al destino, no es necesario seguir explorando
        if nodo_actual == destino:
            break

        no_visitados.remove(nodo_actual)

        # Revisar cada vecino del nodo actual
        for vecino, atributos in G[nodo_actual].items():
            if vecino not in no_visitados:
                continue  # Ya fue visitado, saltar

            peso = atributos.get("weight", 1)
            distancia_tentativa = distancias[nodo_actual] + peso

            # Si encontramos un camino más corto hacia este vecino, actualizarlo
            if distancia_tentativa < distancias[vecino]:
                distancias[vecino]   = distancia_tentativa
                predecesores[vecino] = nodo_actual

    # ── Verificar si el destino es alcanzable ──
    if distancias[destino] == float("inf"):
        return None, None

    # ── Reconstruir la ruta siguiendo predecesores (de destino a origen) ──
    ruta = []
    nodo = destino
    while nodo is not None:
        ruta.append(nodo)
        nodo = predecesores[nodo]

    ruta.reverse()  # Invertir para obtener el orden origen - destino

    # Verificar que la ruta realmente parte desde el origen
    if ruta[0] != origen:
        return None, None

    return ruta, distancias[destino]


# FUNCIÓN 3: Dibujar el grafo en pantalla
def dibujar_grafo(G, ruta_optima, ax):
   
    ax.clear()  # Limpia el dibujo anterior

    pos = nx.circular_layout(G)  # la forma en que muestra los nodos y sus aristas

    # ── Determinar qué aristas pertenecen a la ruta óptima ──
    aristas_ruta = []
    aristas_normales = []

    if ruta_optima:
        # Convertir la ruta (lista de ciudades) en pares de aristas
        for i in range(len(ruta_optima) - 1):
            aristas_ruta.append((ruta_optima[i], ruta_optima[i + 1]))

    for arista in G.edges():
        par  = (arista[0], arista[1])
        par2 = (arista[1], arista[0])
        if par in aristas_ruta or par2 in aristas_ruta:
            pass 
        else:
            aristas_normales.append(arista)

    # ── Dibujar aristas normales
    nx.draw_networkx_edges(
        G, pos, edgelist=aristas_normales,
        edge_color="#AAAAAA", width=1.2, alpha=0.5, ax=ax
    )

    # ── Dibujar aristas de la ruta óptima
    if aristas_ruta:
        nx.draw_networkx_edges(
            G, pos, edgelist=aristas_ruta,
            edge_color="#E63946", width=4.5, alpha=0.95, ax=ax
        )

    # ── Color de los nodos: destacar origen, destino y ruta 
    colores_nodos = []
    for nodo in G.nodes():
        if ruta_optima and nodo == ruta_optima[0]:
            colores_nodos.append("#2DC653")   # Verde - origen
        elif ruta_optima and nodo == ruta_optima[-1]:
            colores_nodos.append("#E63946")   # Rojo - destino
        elif ruta_optima and nodo in ruta_optima:
            colores_nodos.append("#F4A261")   # Naranja - ciudad intermedia
        else:
            colores_nodos.append("#4895EF")   # Azul - ciudad normal"""

    nx.draw_networkx_nodes(
        G, pos, node_color=colores_nodos,
        node_size=500, ax=ax
    )

    # ── Etiquetas de ciudades ──
    nx.draw_networkx_labels(
        G, pos, font_size=7.5, font_color="white",
        font_weight="bold", ax=ax
    )

    # ── Etiquetas de distancias en las aristas ──
    etiquetas_peso = nx.get_edge_attributes(G, "weight")
    etiquetas_peso = {k: f"{v} km" for k, v in etiquetas_peso.items()}
    nx.draw_networkx_edge_labels(
        G, pos, edge_labels=etiquetas_peso,
        font_size=6, font_color="#333333", ax=ax
    )

    # ── Leyenda ──
    from matplotlib.patches import Patch, FancyArrow
    from matplotlib.lines import Line2D
    leyenda = [
        Patch(color="#2DC653", label="Ciudad Origen"),
        Patch(color="#E63946", label="Ciudad Destino"),
        Patch(color="#F4A261", label="Ciudad Intermedia"),
        Patch(color="#4895EF", label="Otras Ciudades"),
        Line2D([0], [0], color="#E63946", linewidth=3, label="Ruta Óptima"),
        Line2D([0], [0], color="#AAAAAA", linewidth=1.5, label="Otras Conexiones"),
    ]
    ax.legend(handles=leyenda, loc="lower right", fontsize=7, framealpha=0.85)

    ax.set_title("Ruta Optima  -  Grafo Ciudades", fontsize=16, color="#FFFFFF", fontweight="bold", pad=20)
    ax.axis("off")


# FUNCIÓN 4: Construir la interfaz gráfica principal

def construir_interfaz(G, ciudades):
    # ── Configuración visual de CustomTkinter ──
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    ventana = ctk.CTk()
    ventana.title("Calculadora de Ruta Óptima entre Ciudades")
    ventana.geometry("1200x750")
    ventana.resizable(True, True)

    # ── Panel izquierdo: controles ──
    panel_izq = ctk.CTkFrame(ventana, width=260, corner_radius=0)
    panel_izq.pack(side="left", fill="y", padx=12, pady=12)
    panel_izq.pack_propagate(False)

    ctk.CTkLabel(
        panel_izq, text="Ruta Óptima",
        font=ctk.CTkFont(size=20, weight="bold")
    ).pack(pady=(20, 5))

    # ── Selector de Ciudad Origen ──
    ctk.CTkLabel(
        panel_izq, text=" Ciudad de Origen:",
        font=ctk.CTkFont(size=13, weight="bold")
    ).pack(anchor="w", padx=15, pady=(15, 3))

    combo_origen = ctk.CTkComboBox(
        panel_izq, values=ciudades, width=230,
        font=ctk.CTkFont(size=12), state="readonly"
    )
    combo_origen.set(ciudades[0])
    combo_origen.pack(padx=15, pady=(0, 10))

    # ── Selector de Ciudad Destino ──
    ctk.CTkLabel(
        panel_izq, text=" Ciudad de Destino:",
        font=ctk.CTkFont(size=13, weight="bold")
    ).pack(anchor="w", padx=15, pady=(5, 3))

    combo_destino = ctk.CTkComboBox(
        panel_izq, values=ciudades, width=230,
        font=ctk.CTkFont(size=12), state="readonly"
    )
    combo_destino.set(ciudades[2])  # Empieza seleccionado en otra ciudad
    combo_destino.pack(padx=15, pady=(0, 20))

    # ── Botón Calcular Ruta ──
    def al_calcular():
      
        origen  = combo_origen.get()
        destino = combo_destino.get()

        if origen == destino:
            lbl_resultado.configure(
                text=" Origen y destino\nno pueden ser iguales.",
                text_color="#F4A261"
            )
            return

        ruta, distancia = calcular_ruta_optima(G, origen, destino)

        if ruta is None:
            lbl_resultado.configure(
                text=" No existe ruta\nentre esas ciudades.",
                text_color="#E63946"
            )
            dibujar_grafo(G, None, ax)
        else:
            # Construir texto de la secuencia de ciudades
            secuencia = " ➜ ".join(ruta)
            lbl_resultado.configure(
                text=f"✅ Ruta encontrada:\n\n{secuencia}\n\n Distancia total:\n{distancia:,.0f} km",
                text_color="#2DC653"
            )
            dibujar_grafo(G, ruta, ax)

        canvas.draw()  # Actualizar el gráfico en pantalla

    btn_calcular = ctk.CTkButton(
        panel_izq, text=" Calcular Ruta Óptima",
        command=al_calcular, height=42,
        font=ctk.CTkFont(size=13, weight="bold"),
        fg_color="#1d6fa4", hover_color="#2980b9"
    )
    btn_calcular.pack(padx=15, pady=5)

    # ── Botón Limpiar / Reset ──
    def limpiar():
        lbl_resultado.configure(text="Selecciona origen\ny destino, luego\npresiona Calcular.", text_color="gray")
        dibujar_grafo(G, None, ax)
        canvas.draw()

    btn_limpiar = ctk.CTkButton(
        panel_izq, text="Limpiar",
        command=limpiar, height=36,
        font=ctk.CTkFont(size=12),
        fg_color="#3a3a3a", hover_color="#555555"
    )
    btn_limpiar.pack(padx=15, pady=(5, 20))


    # ── Área de resultado ──
    ctk.CTkLabel(
        panel_izq, text=" Resultado:",
        font=ctk.CTkFont(size=13, weight="bold")
    ).pack(anchor="w", padx=15, pady=(15, 5))

    lbl_resultado = ctk.CTkLabel(
        panel_izq,
        text="Selecciona origen\ny destino, luego\npresiona Calcular.",
        font=ctk.CTkFont(size=11),
        text_color="gray",
        wraplength=220,
        justify="left"
    )
    lbl_resultado.pack(padx=15, anchor="w")

    # ── Panel derecho: gráfico matplotlib ──
    panel_der = ctk.CTkFrame(ventana, corner_radius=0)
    panel_der.pack(side="right", fill="both", expand=True, padx=(0, 12), pady=12)

    fig, ax = plt.subplots(figsize=(9, 6.5))
    fig.patch.set_facecolor("#1a1a2e")
    ax.set_facecolor("#1a1a2e")

    # Dibuja el grafo inicial (sin ruta seleccionada)
    dibujar_grafo(G, None, ax)

    # Embeber el gráfico de matplotlib dentro de customtkinter
    canvas = FigureCanvasTkAgg(fig, master=panel_der)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)

    ventana.mainloop()

# FUNCIÓN PRINCIPAL: Punto de entrada de la aplicación

def main():
    # Busca el archivo Excel en la misma carpeta que este script
    ruta_excel = os.path.join(os.path.dirname(os.path.abspath(__file__)), "distancias.xlsx")

    if not os.path.exists(ruta_excel):
        print(f"ERROR: No se encontró el archivo '{ruta_excel}'")
        print("Asegúrate de que 'distancias.xlsx' esté en la misma carpeta que este script.")
        return

    print("Cargando datos del archivo Excel...")
    G, ciudades = cargar_datos(ruta_excel)
    print(f"✅ Grafo cargado: {len(ciudades)} ciudades, {G.number_of_edges()} conexiones.")

    print("Iniciando interfaz gráfica...")
    construir_interfaz(G, ciudades)


# ── Ejecutar la aplicación ──
if __name__ == "__main__":
    main()
