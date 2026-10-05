import pulp
from graph import Graph

def resolver_exacto_ilp(graph, q, k):
    n = len(graph.vertices)
    T = n - 1  # El fuego se extingue como máximo en n-1 etapas
    
    # Declaración del modelo de minimización
    prob = pulp.LpProblem("Reto2_Bomberos", pulp.LpMinimize)
    
    # --- VARIABLES DE DECISIÓN ---
    # x[i, t]: 1 si la zona i está quemada en la etapa t o antes, 0 en caso contrario
    x = {}
    for i in range(n):
        for t in range(T + 1):
            x[(i, t)] = pulp.LpVariable(f"x_{i}_{t}", cat='Binary')
    
    # y[u, v, t]: 1 si el arco (u, v) ha sido cortado por los bomberos en la etapa t o antes
    arcos = [(u, v) for u in range(n) for v in range(n) if graph.adj_matrix[u][v]]
    y = {}
    for (u, v) in arcos:
        for t in range(T + 1):
            y[(u, v, t)] = pulp.LpVariable(f"y_{u}_{v}_{t}", cat='Binary')
    
    # --- FUNCIÓN OBJETIVO ---
    # Minimizar el total de zonas quemadas al final del horizonte temporal
    prob += pulp.lpSum([x[(i, T)] for i in range(n)]), "zonas_quemadas"
    
    # --- RESTRICCIONES ---
    # 1. Condición inicial: El fuego se inicia únicamente en la zona q en t=0
    prob += x[(q, 0)] == 1, "inicio_fuego"
    for i in range(n):
        if i != q:
            prob += x[(i, 0)] == 0, f"no_inicio_{i}"
            
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
            prob += x[(i, t)] >= x[(i, t-1)], f"irreversible_quema_{i}_{t}"
            
            for j in range(n):
                if graph.adj_matrix[i][j]:
                    # Irreversibilidad del cortafuego: un corte permanece en el tiempo
                    prob += y[(i, j, t)] >= y[(i, j, t-1)], f"irreversible_corte_{i}_{j}_{t}"
                    
                    # Propagación: Si 'i' arde en t-1 y el arco (i, j) NO está cortado en t, 'j' arde en t
                    prob += x[(j, t)] >= x[(i, t-1)] - y[(i, j, t)], f"propagacion_{i}_{j}_{t}"
    
    # --- RESOLUCIÓN ---
    # Se desactiva la salida de mensajes del solver
    prob.solve(pulp.PULP_CBC_CMD(msg=0))
    
    # --- VERIFICACIÓN DE FACTIBILIDAD ---
    if prob.status != pulp.LpStatusOptimal:
        print(f"⚠️  Solver no encontró óptimo. Status: {pulp.LpStatus[prob.status]}")
        return None, None
    
    # --- EXTRACCIÓN DE RESULTADOS ---
    zonas_quemadas = sum(1 for i in range(n) if pulp.value(x[(i, T)]) > 0.5)
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

    resultado = resolver_exacto_ilp(graph, q=1, k=2)
    
    if resultado[0] is not None:
        zonas_salvadas, estrategia = resultado
        print(f"✓ Zonas salvadas: {zonas_salvadas}")
        print(f"✓ Estrategia por etapas:")
        for t, cortes in estrategia.items():
            print(f"  Etapa {t}: {cortes}")
    else:
        print("✗ No se pudo resolver el problema.")


if __name__ == "__main__":
    for i in [3,4,5,7,8,10]:
        print(f"\n Grafo {i:03d}:")
        main(f"graph_{i:03d}_probs.txt")
        print()