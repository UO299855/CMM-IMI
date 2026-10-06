function prob_quem_cum = probabilidad_quemado_nodo(A,p_i)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Función que devuelve la esperanza de nodos quemados de un grafo tras 2
% etapas de tiempo.
% 
% Parámetros de entrada:
% A: matriz de probabilidades
% p_i: vector con las probabilidades de que el fuego se inicie en cada nodo
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Inicializamos variables
n = length(p_i);
prob_quem_cum = zeros(n,1);

% Etapas 1 y 2
A = A + eye(n);
for i=1:n                           % Para cada nodo de llegada
    for j=cat(2, 1:i-1, i+1:n)      % Nodos de origen, distintos del de llegada
        producto = 1;
        for k=cat(2, 1:j-1, j+1:n)  % Nodos intermedios, distinto al de salida
            % En un momento dado vas a tener k = 1, en ese paso sumaras
            % todos los caminos de longitud 1
            producto = producto * (1-A(j, k)*A(k, i));
        end
        prob_quem_cum(i) = prob_quem_cum(i) + p_i(j) * (1 - producto);
    end
end

% Etapa 0
prob_quem_cum = prob_quem_cum + p_i;
end