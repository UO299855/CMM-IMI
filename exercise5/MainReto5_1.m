clear
%% Inicializamos las variables generales del problema
% Leemos el vector de probabilidades iniciales
p_i = readmatrix("inicio.txt"); p_i = p_i(:,2);
n = length(p_i);

% Condiciones generales del problemadel problema
s = 2;      % Número de etapas
k = 4;      % Número de cortafuegos
a = 3;      % Número de aristas mojadas
r_a = 0.6;  % Coeficiente de reducción del agua

%% Optimización para s=2 exacta
% Opciones de optimización
e = ones(k+a,1);
optionsga = optimoptions("ga","Display","off");

% Optimizamos para cada grafo
rng(1)

for j = [3,4,5,7,8,10]
    % Leemos los datos del grafo j
    filename = sprintf("graph_%03i_probs.txt",j);
    datos = readmatrix(filename);
    filas = datos(:,1) + 1; columnas = datos(:,2) + 1; n = max([filas;columnas]);
    probabilidades = datos(:,3);

    m = length(filas)/2; % Número máximo de zonas a afectar con cortafuegos o agua
    
    % Función a minimizar
    fun_min = @(idx)lugar_cortafuegosYagua(idx,filas,columnas,probabilidades,p_i,k,r_a,s,0);
    
    % Optimización
    [idx_Medidas, Esperanza_CortafuegosYAgua] = ga(fun_min,k+a,[],[],[],[],1*e,m*e,[],1:k+a,optionsga);
    
    % Imprimimos el resultado por pantalla
    filas_Medidas = filas(2*idx_Medidas)-1;
    columnas_Medidas = columnas(2*idx_Medidas)-1;
    fprintf("%2i &",j)
    fprintf(" (%2i, %2i) &", [filas_Medidas';columnas_Medidas'])
    fprintf("%.2f \\\\ \\hline \n", n- Esperanza_CortafuegosYAgua)
end

