clear
%% Inicializamos las variables generales del problema
% Leemos el vector de probabilidades iniciales
p_i = readmatrix("inicio.txt"); p_i = p_i(:,2);
n = length(p_i);

% Condiciones generales del problemadel problema
s = 2; % Número de etapas
k = 4; % Número de cortafuegos

%% Optimización exacta para s=2 exacta
% Opciones de optimización
e = ones(k,1);
optionsga = optimoptions("ga","Display","off");

rng(1)
% Optimizamos para cada grafo
for j = [3,4,5,7,8,10]
    % Leemos los datos del grafo j
    filename = sprintf("graph_%03i_probs.txt",j);
    datos = readmatrix(filename);
    filas = datos(:,1) + 1; columnas = datos(:,2) + 1; n = max([filas;columnas]);
    probabilidades = datos(:,3);

    m = length(filas)/2; % Número máximo de cortafuegos
    
    % Función a minimizar
    fun_min = @(idx_k)lugar_cortafuegos(idx_k,filas,columnas,probabilidades,p_i,s,0);
    
    % Optimización
    [idx_Cortafuegos, Esperanza_Cortafuegos] = ga(fun_min,k,[],[],[],[],1*e,m*e,[],1:k,optionsga);
    
    % Imprimimos el resultado por pantalla
    filas_cortafuegos = filas(2*idx_Cortafuegos)-1;
    columnas_cortafuegos = columnas(2*idx_Cortafuegos)-1;
    fprintf("%2i &",j)
    fprintf(" (%2i, %2i) &", [filas_cortafuegos';columnas_cortafuegos'])
    fprintf("%.2f \\\\ \\hline \n", n- Esperanza_Cortafuegos)
end

%% Comparación Montecarlo y método exacto para s = 2
% Fijamos la semilla
rng(1)

% Comparamos para cada grafo
for j = [3,4,5,7,8,10]
    % Leemos los datos del grafo j
    filename = sprintf("graph_%03i_probs.txt",j);
    datos = readmatrix(filename);
    filas = datos(:,1) + 1; columnas = datos(:,2) + 1; n = max([filas;columnas]);
    probabilidades = datos(:,3);

    % Creamos la matriz de probabilidades
    A = sparse(filas,columnas,probabilidades,n,n);

    % Cálculo de la esperanza exacta
    Esperanza_exacta = n- sum(probabilidad_quemado_nodo(A,p_i));

    % Cálculo de la esperanza con el método de Montecarlo
    N = 1000; s = 2;
    Esperanza_montecarlo = n- probabilidad_quemado_montecarlo(A,p_i,s,N);

    % Imprimimos el resultado por pantalla
    fprintf("%i \t & %.2f & %.2f \\\\ \\hline \n", j, Esperanza_exacta, Esperanza_montecarlo)
end

%% Optimización con Montecarlo para s = 2
% Hay que realizar un pequeño ajuste en la función lugar_cortafuegos para
% que cuando s=2 use la funcion de montecarlo, luego se quita ya que no
% interesa que funcione de esa forma

% Fijamos la semilla 
rng(1)

% Opciones de optimización
% Hay que acotar el número de pasos para que no tarde demasiado (aún así tarda más que los ejemplos anteriores)
optionsga = optimoptions("ga","Display","off","MaxGenerations",50);

% Optimizamos para cada grafo
for j = [3,4,5,7,8,10]
    % Leemos los datos del grafo j
    filename = sprintf("graph_%03i_probs.txt",j);
    datos = readmatrix(filename);
    filas = datos(:,1) + 1; columnas = datos(:,2) + 1; n = max([filas;columnas]);
    probabilidades = datos(:,3);

    m = length(filas)/2; % Número máximo de cortafuegos
    
    % Función a minimizar
    N = 1000;
    fun_min = @(idx_k)lugar_cortafuegos(idx_k,filas,columnas,probabilidades,p_i,s,N);
    
    % Optimización
    [~, Esperanza_Cortafuegos] = ga(fun_min,4,[],[],[],[],1*e,m*e,[],1:k,optionsga);
    
    % Imprimimos el resultado por pantalla
    fprintf("%i \t &  &  %.2f \\\\ \\hline \n", j, n- Esperanza_Cortafuegos)
end

%% Optimización con Montecarlo para s = 3,4
% Fijamos la semilla 
rng(1)

% Opciones de optimización
% Hay que acotar el número de pasos para que no tarde demasiado
optionsga = optimoptions("ga","Display","off","MaxGenerations",50);

% Optimizamos para cada grafo con s = 3
fprintf("s = 3\n")
s = 3;
for j = [3,4,5,7,8,10]
    % Leemos los datos del grafo j
    filename = sprintf("graph_%03i_probs.txt",j);
    datos = readmatrix(filename);
    filas = datos(:,1) + 1; columnas = datos(:,2) + 1; n = max([filas;columnas]);
    probabilidades = datos(:,3);

    m = length(filas)/2; % Número máximo de cortafuegos
    
    % Función a minimizar
    N = 1000;
    fun_min = @(idx_k)lugar_cortafuegos(idx_k,filas,columnas,probabilidades,p_i,s,N);
    
    % Optimización
    [idx_Cortafuegos, Esperanza_Cortafuegos] = ga(fun_min,4,[],[],[],[],1*e,m*e,[],1:k,optionsga);
    
    % Imprimimos el resultado por pantalla
    fprintf("%i \t & (%i, %i) \t &  (%i, %i) \t &  (%i, %i) \t &  (%i, %i) \t &  %.2f \\\\ \\hline \n", j, filas(2*idx_Cortafuegos(1))-1, columnas(2*idx_Cortafuegos(1))-1, filas(2*idx_Cortafuegos(2))-1, columnas(2*idx_Cortafuegos(2))-1, filas(2*idx_Cortafuegos(3))-1, columnas(2*idx_Cortafuegos(3))-1, filas(2*idx_Cortafuegos(4))-1, columnas(2*idx_Cortafuegos(4))-1, n- Esperanza_Cortafuegos)
end

% Optimizamos para cada grafo con s = 3
fprintf("s = 4\n")
s = 4;
for j = [3,4,5,7,8,10]
    % Leemos los datos del grafo j
    filename = sprintf("graph_%03i_probs.txt",j);
    datos = readmatrix(filename);
    filas = datos(:,1) + 1; columnas = datos(:,2) + 1; n = max([filas;columnas]);
    probabilidades = datos(:,3);

    m = length(filas)/2; % Número máximo de cortafuegos
    
    % Función a minimizar
    N = 1000;
    fun_min = @(idx_k)lugar_cortafuegos(idx_k,filas,columnas,probabilidades,p_i,s,N);
    
    % Optimización
    [idx_Cortafuegos, Esperanza_Cortafuegos] = ga(fun_min,4,[],[],[],[],1*e,m*e,[],1:k,optionsga);
    
    % Imprimimos el resultado por pantalla
    filas_cortafuegos = filas(2*idx_Cortafuegos)-1;
    columnas_cortafuegos = columnas(2*idx_Cortafuegos)-1;
    fprintf("%2i &",j)
    fprintf(" (%2i, %2i) &", [filas_cortafuegos';columnas_cortafuegos'])
    fprintf("%.2f \\\\ \\hline \n", n- Esperanza_Cortafuegos)
end