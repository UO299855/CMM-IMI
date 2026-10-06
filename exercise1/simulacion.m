function quemados = simulacion(A,p_i,s)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Función que simula un incendio en el grafo con matriz de probabilidades A
% y vector de probabilidades iniciales p_i. Devuelve un vector con un 1 en
% la posición i si el nodo si el nodo i se ha quemado en la etapa s y 0 en
% caso contrario
%
% A: matriz de probabilidades
% p_i: vector con las probabilidades de que el fuego se inicie en cada nodo
% s: número de etapas a simular
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Inicializamos
n = length(p_i) ;
quemados = zeros(1,n);

% Arranca el fuego
start = randsample(length(p_i), 1,true,p_i);
quemados(start) = 1;

% Aristas por las que se puede pasar
edgeTry = rand(n) <= A;

% Propagación del fuego
for i = 1:s
    quemados = quemados + quemados*edgeTry;
end

% Acotamos los que se pasaron 
quemados = ones(n,1) <= quemados';
end