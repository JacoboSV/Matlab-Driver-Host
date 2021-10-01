function output=maximo(input_file)

% Ejemplo de llamada de la función en matlab:
%        [valormax,tiempo_valormax]=maximo('input_file')

%PARÁMETROS DE ENTRADA:
%     - input_file: Nombre del fichero que contiene los argumentos de entrada 

%PARÁMETROS DE SALIDA:
%     - valormax: Valor máximo de una señal de una determinada descarga
%     - tiempo_valormax: Tiempo donde se alcanza el valor máximo
% Se crea un fichero grafico.jpg en el directorio desde donde se ejecutando la función


load(input_file,'-mat')

%Cálculo del valor máximo de una señal de una descarga

%Genero el path/nombre del fichero de donde tengo que obtener el valor máximo y
%el instante de tiempo 
file_valormax = strcat (d_r,'DES_',num2str(numdescarga),'_0',num2str(numsignal),'_r.txt');       

%Cargo el fichero de la señal que quiero pintar y donde quiero calcular el valor máximo 
signal=load([file_valormax]);

valormax=max(signal(:,2));
indiceaux=find(signal(:,2)==valormax);
tiempo_valormax=signal(indiceaux,1);

jsonsignal(1,:,:) = signal;
jsonmaximum(1,1,:) = [tiempo_valormax, valormax];
%jsonmaximum(1,2,:) = [];


outStruct.signal = jsonsignal;
outStruct.features = jsonmaximum;

output = jsonencode(outStruct);

 

