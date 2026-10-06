import numpy as np
import pulp
from graph import Graph

def resolver_exacto_ilp(graph, q, k, N):
    n = len(graph.vertices)
    T = n - 1  # El fuego se extingue como máximo en n-1 etapas

    # Generamos N configuraciones aleatorias del bosque
    A_0 = np.array(graph.weight_matrix, dtype=float)
    adj = np.array(graph.adj_matrix, dtype=bool)
    A = []

    for ite in range(N):
        U = np.random.rand(n, n)
        A.append((U <= A_0) & adj)
    
    # Declaración del modelo de minimización
    prob = pulp.LpProblem("Reto2_Bomberos", pulp.LpMinimize)
    
    # --- VARIABLES DE DECISIÓN ---
    # x[i, t, ite]: 1 si la zona i está quemada en la etapa t o antes en la muestra ite, 0 en caso contrario
    x = {}
    for ite in range(N):
        for i in range(n):
            for t in range(T + 1):
                x[(i, t, ite)] = pulp.LpVariable(f"x_{i}_{t}_{ite}", cat='Binary')
    
    # y[u, v, t]: 1 si el arco (u, v) ha sido cortado por los bomberos en la etapa t o antes
    arcos = [(u, v) for u in range(n) for v in range(n) if adj[u][v]]
    y = {}
    
    for (u, v) in arcos:
        for t in range(T + 1):
            y[(u, v, t)] = pulp.LpVariable(f"y_{u}_{v}_{t}", cat='Binary')
    
    # --- FUNCIÓN OBJETIVO ---
    # Minimizar el total medio de zonas quemadas al final del horizonte temporal
    prob += pulp.lpSum([x[(i, T, ite)] for i in range(n) for ite in range(N)]) / N, "zonas_quemadas"
    
    # --- RESTRICCIONES ---
    # 1. Condición inicial: El fuego se inicia únicamente en la zona q en t=0
    for ite in range(N):
        prob += x[(q, 0, ite)] == 1, f"inicio_fuego_{ite}"
        for i in range(n):
            if i != q:
                prob += x[(i, 0, ite)] == 0, f"no_inicio_{i}_{ite}"
            
    # 2. En t=0 no hay cortafuegos colocados
    for (u, v) in arcos:
        prob += y[(u, v, 0)] == 0, f"no_cortes_t0_{u}_{v}"

    # 3. Evolución del fuego y actuación por etapas
    for t in range(1, T + 1):
        
        # Límite de actuación: Se pueden poner como máximo k cortafuegos nuevos por etapa
        nuevos_cortafuegos = pulp.lpSum([
            y[(u, v, t)] - y[(u, v, t-1)] for (u, v) in arcos
        ])
        prob += nuevos_cortafuegos <= k, f"limite_cortes_t{t}"

        for i in range(n):
            # Irreversibilidad: Si una zona se quema en t-1, sigue quemada en t
            for ite in range(N):
                prob += x[(i, t, ite)] >= x[(i, t-1, ite)], f"irreversible_quema_{i}_{t}_{ite}"
            
            for j in range(n):
                if adj[i][j]:
                    # Irreversibilidad del cortafuego: un corte permanece en el tiempo
                    prob += y[(i, j, t)] >= y[(i, j, t-1)], f"irreversible_corte_{i}_{j}_{t}"

                    for ite in range(N):
                        if A[ite][i][j]:
                            # Propagación: Si 'i' arde en t-1 y el arco (i, j) NO está cortado en t, 'j' arde en t
                            prob += x[(j, t, ite)] >= x[(i, t-1, ite)] - y[(i, j, t)], f"propagacion_{i}_{j}_{t}_{ite}"

    # --- RESOLUCIÓN ---
    # Se desactiva la salida de mensajes del solver
    prob.solve(pulp.PULP_CBC_CMD(msg=False), threads=8)
    
    # --- VERIFICACIÓN DE FACTIBILIDAD ---
    if prob.status != pulp.LpStatusOptimal:
        print(f"⚠️  Solver no encontró óptimo. Status: {pulp.LpStatus[prob.status]}")
        return None, None
    
    # --- EXTRACCIÓN DE RESULTADOS ---
    zonas_quemadas = sum(1 for i in range(n) for ite in range(N) if pulp.value(x[(i, T, ite)]) > 0.5) / N
    zonas_salvadas = n - zonas_quemadas
    
    estrategia_bomberos = {}
    for t in range(1, T + 1):
        cortes_etapa = []
        for (u, v) in arcos:
            # Identificamos los cortes que pasaron de 0 a 1 justo en esta etapa
            val_actual = pulp.value(y[(u, v, t)])
            val_anterior = pulp.value(y[(u, v, t-1)])
            if val_actual > 0.5 and val_anterior < 0.5:
                cortes_etapa.append((u, v))
        if cortes_etapa:
            estrategia_bomberos[t] = cortes_etapa
    
    return zonas_salvadas, estrategia_bomberos

def main(filename):

    graph = Graph(directed=True)
    graph.load_from_file(filename)

    resultado = resolver_exacto_ilp(graph, q=1, k=1, N=50)
    
    if resultado[0] is not None:
        zonas_salvadas, estrategia = resultado
        print(f"✓ Zonas salvadas: {zonas_salvadas}")
        print(f"✓ Estrategia por etapas:")
        for t, cortes in estrategia.items():
            print(f"  Etapa {t}: {cortes}")
    else:
        print("✗ No se pudo resolver el problema.")


np.random.seed(1)
if __name__ == "__main__":
    # cwd = "C:/Users/diego/Documentos/CMM-IMI"
    # print(os.getcwd())
    for i in [3,4,5,10]:
        print(f"\n Grafo {i:03d}:")
        main(f"graph_{i:03d}_probs.txt")
        print()