function [prob_cortafuegos,A] = lugar_cortafuegos(idx_k,filas,columnas,datos,p_i,s,N) 
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Función que devuelve la esperanza de nodos quemados tras poner ciertos
% cortafuegos y la matriz de probabilidades A transformada tras poner los
% cortafuegos. Utilizará la función exacta si s = 2 y la aproximación de
% montecarlo en caso contrario
%
% idx_k: lista de cortafuegos que se colocan
% filas, columnas, datos: la posición y el valor de los elementos no nulos
% en la matriz de probabilidades A
% p_i: vector con las probabilidades de que el fuego se inicie en cada nodo
% s: número de etapas a simular
% N: número de repeticiones de la simulación
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

n = length(p_i); 

% Ponemos los cortafuegos
indices = unique([2*idx_k, 2*idx_k-1]);
A = sparse(filas,columnas,datos,n,n) - sparse(filas(indices),columnas(indices),datos(indices),n,n);

% Teórico
if s~=2
    prob_cortafuegos = probabilidad_quemado_montecarlo(A,p_i,s,N);
else
    prob_cortafuegos = sum(probabilidad_quemado_nodo(A,p_i));
    %prob_cortafuegos = probabilidad_quemado_montecarlo(A,p_i,s,N);
end
end