function [prob_cortafuegos,A] = lugar_cortafuegosYagua(idx,filas,columnas,datos,p_i,k,r_a,s,N) 
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Función que devuelve la esperanza de nodos quemados tras poner ciertos
% cortafuegos y mojar ciertas aristas y la matriz de probabilidades A 
% transformada tras poner los cortafuegos. Utilizará la función exacta si 
% s = 2 y la aproximación de Montecarlo en caso contrario.
%
% idx_k: lista de cortafuegos y zonas mojadas que se colocan
% filas, columnas, datos: la posición y el valor de los elementos no nulos
% en la matriz de probabilidades A
% p_i: vector con las probabilidades de que el fuego se inicie en cada nodo
% k: número de cortafuegos que se pueden colocar
% r_a: coeficiente de reducción del agua
% s: número de etapas a simular
% N: número de repeticiones de la simulación
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

n = length(p_i); 
% Separamos los cortafuegos de las zonas a mojar
idx = unique(idx); % Eliminamos las zonas repetidas
l = numel(idx);
idx_agua = idx(min(l,k)+1:l);

% Ponemos los cortafuegos y el agua
indices = [2*idx, 2*idx-1];
indices_agua = [2*idx_agua, 2*idx_agua-1];
A = sparse(filas,columnas,datos,n,n) - sparse(filas(indices),columnas(indices),datos(indices),n,n) + sparse(filas(indices_agua),columnas(indices_agua),(1-r_a).*datos(indices_agua),n,n);

% Teórico
if s~=2
    prob_cortafuegos = probabilidad_quemado_montecarlo(A,p_i,s,N);
else
    prob_cortafuegos = sum(probabilidad_quemado_nodo(A,p_i));
    %prob_cortafuegos = probabilidad_quemado_montecarlo(A,p_i,s,N);
end
end