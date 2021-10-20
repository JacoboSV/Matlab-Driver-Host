function []=visualizar(signals)

	%load(input_file,'-mat')
	points = jsondecode(signals)
	
	features = points.features
	signal = points.signal
	try 
		titlePlot = points.features.name
	catch exception
		titlePlot = 'Plot of series and feature'
	end
	%Cálculo del valor máximo de una señal de una descarga

	%Genero el path/nombre del fichero de donde tengo que obtener el valor máximo y
	%el instante de tiempo 
	%file_valormax = strcat (d_r,'DES_',num2str(numdescarga),'_0',num2str(numsignal),'_r.txt');       

	%Cargo el fichero de la señal que quiero pintar y donde quiero calcular el valor máximo 
	%signal=load([file_valormax]);

	
	graficoaux=plot(signal(:,:,1),signal(:,:,2))
	hold on
	tiempo_feature = features(1)
	value_feature = features(2)
	plot(tiempo_feature,value_feature,'ro','MarkerFaceColor','r');
	%viscircles([tiempo_feature tiempo_feature],2)
	plot(tiempo_feature,tiempo_feature,'bo','MarkerFaceColor','b')
	title(titlePlot)
	
	savepath = strcat(userpath,'\grafico.jpg');
	saveas(graficoaux,savepath)


