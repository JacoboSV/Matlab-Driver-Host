function procesado(campaign,periodoremuestreo,numdescarga,numsignal)

% Ejemplo de llamada de la función en matlab:
%        procesado('C15a',0.001,65988,6)

%PARÁMETROS DE ENTRADA:
%     - campaign: Nombre de la campaña de las descargas a procesar (de momento introducir C15a)
%     - periodoremuestreo: periodo para remuestrear en segundos (para remuestrear a 1 ms introducir 0.001)
%     - numdescarga: numero de descarga que la que se desea pintar una señal obteniendo su valor 
%                    máximo y el tiempo donde se alcanza ese valor máximo (de momento como 
%                    numdescarga se pueden introducir 65988 y 66027)
%     - numsignal: número de la señal que se desea pintar y calcular su valor máximo y el 
%                  tiempo donde se alcanza ese valor máximo  (un número del 1 al 9)

%PARÁMETROS DE SALIDA:
% Se crea un fichero output_file.mat donde se almacenan las siguientes
% variables:
%     d_r, numdescarga, numsignal, namesignal


%Este programa procesa las señales de las descargas de una determinada carpeta.
%Todas las señales de una misma carpeta deben tener mismo t0 y el mismo tmax.
%El t0 para una descarga se corresponde con el valor mayor de los tiempos iniciales
%de las señales que componen la descarga. 
%El tiempo tmax para una descarga se correspondecon el valor mínimo de los tiempos finales 
%de las señales que componen la descarga.

%A continuación se remuestrean con el periodo de muestreo especificado todas las señales de
%todas las descargas

if numsignal==1
    namesignal='Current Plasma';
elseif numsignal==2
    namesignal='Locked Mode';
elseif numsignal==3
    namesignal='Inductance';
elseif numsignal==4
    namesignal='Density';
elseif numsignal==5
    namesignal='Diamagnetic energy';
elseif numsignal==6
    namesignal='Radiated power';
elseif numsignal==7
    namesignal='Total power';
elseif numsignal==8
    namesignal='Poloidal Beta';
elseif numsignal==9
    namesignal='Vertical position of centroid';
end


%En d se almacena la lista de ficheros .txt que hay en el directorio Datos_brutos
aux=strcat(userpath,'/Datos_brutos/',campaign,'/*.txt');
d=dir(aux);

dd=strcat(userpath,'/Datos_brutos/',campaign,'/');

%d_r es el directorio donde se van a ir almacenando las señales
%recortadas y remuestreadas teniendo en cuenta t0 y tmax
d_r=strcat(userpath,'/Datos_remuestreados/',campaign,'/');

%En f se almacena la lista de señales que se encuentran en el directorio d
f=[];
 for i=1:length(d)
     f=[f;d(i).name];
 end;

 
 %En descargas se almacena la lista de descargas que hay en el directorio d
 descargas=unique(f(:,1:9),'rows');

for i=1:size(descargas,1)
    
    disp(['DESCARGA:  ' descargas(i,:)])
        
    dAux=dir([dd,descargas(i,:),'*.txt']);
    
    % en f se almacena la lista de señales que se encuentran en el
    % directorio dAux para una descarga determinada (i)
    f=[];
    for i=1:size(dAux,1)
        f=[f;dAux(i).name];
    end;
   
    t0=-1;
    tmax=inf;
    %Este for busca el t0 máximo de todas las señales de una descarga y el
    %tfinal mínimo de todas las señales de una descarga
    for j=1:size(f,1)
         dato=load([dd,f(j,:)]);
         datoAux_t0=dato(1,1);       %el primer valor de tiempo
         datoAux_tmax=dato(end,1);   %el último valor de tiempo 
         
                  
         if datoAux_t0 > t0          
             t0=datoAux_t0;
         end
         if datoAux_tmax < tmax
             tmax=datoAux_tmax;
         end         
    end
  
    
    %Este for recorta teniendo en cuenta t0 y tmax y remuestrea.
    %Permite introducir alguna condición de saturación en alguna de las
    %señales
    for j=1:size(f,1) %Para todas las señales de la descarga i
         dato=load([dd,f(j,:)]);
              
         disp(['Signal:  ' f(j,:)])
         
         time=t0:periodoremuestreo:tmax;
     
         dato_remuestreado = interp1(dato(:,1),dato(:,2),time); 
         dato_remuestreado = [time',dato_remuestreado'];
         filename = strcat (d_r,f(j,1:end-4),'_r','.txt'); %_r significa remuestreo 
         
         if j==1    %Corriente de plasma  (tomo como valor máximo de la corriente el valor 0)
             
             dato_remuestreado(find(dato_remuestreado(:,2)>=0),2)=0;
           
         elseif j==2  %Locked Mode (tomo como valor mínimo del mode lock el valor 0)
                 
             dato_remuestreado(find(dato_remuestreado(:,2)<=0),2)=0;
               
         elseif j==3  %Inductancia
          
            %Las señales de inductancia que superen un cierto umbral se truncan
            %a un determinado valor, en principio este tratamiento se les
            %hará a las descargas disruptivas pero como normalmente será
            %después del instante de la disrupción cuando se procesen no
            %tendrá efecto
                umbral=13;  %umbral=10;
                truncar=1;  %valor bajo que no influirá en el procesamiento final
                dato_remuestreado(find(dato_remuestreado(:,2)>umbral),2)=truncar;
             
         elseif j==4  %Densidad (tomo como valor mínimo de la densidad el valor 0)
                 
             dato_remuestreado(find(dato_remuestreado(:,2)<=0),2)=0;
             
                   
         elseif j==6  %Potencia radiada (tomo como valor mínimo de la potencia radiada 1000 W)
             
            %los valores de la potencia radiada que estén por debajo de
            %1000W se fijan a 1000 W
             dato_remuestreado(find(dato_remuestreado(:,2)<=1000),2)=1000; 
         
         elseif j==7  %Potencia de entrada (tomo como valor mínimo de la potencia de entrada 1 W)
             
            %los valores de la potencia radiada que estén por debajo de
            %1W se fijan a 1 W
             dato_remuestreado(find(dato_remuestreado(:,2)<=1),2)=1;    
                  
        end
          
          save (filename, 'dato_remuestreado', '-ascii');
         
     end
 
end
 
savepath = strcat(userpath,'/output_file');
save(savepath,"d_r","numdescarga","numsignal","namesignal")


