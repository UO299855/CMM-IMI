function E = probabilidad_quemado_montecarlo(A,p_i,s,N)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Función que devuelve la esperanza de nodos quemados en un grafo tras s
% etapas de tiempo mediante un método de Montecarlo
% 
% Parámtros de entrada:
% A: matriz de probabilidades
% p_i: vector con las probabilidades de que el fuego se inicie en cada nodo
% s: número de etapas a simular
% N: número de repeticiones de la simulación
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Inicializamos
n = length(p_i);
E_sim = zeros(n,1);

% Hacemos tantas simulaciones como indique N
for i = 1:N
    E_sim = E_sim + simulacion(A,p_i,s);
end

% Calculamos la media final
E = sum(E_sim/N);
end