function slowtasktest(fileIn)

fileID = fopen(fileIn,'r');
formatSpec = '%f %f';
sizeA = [2 Inf];
A = fscanf(fileID,formatSpec,sizeA);
fclose(fileID);
vectorIn = A';

pause(20)

valormax=max(vectorIn(:,2));
indiceaux=find(vectorIn(:,2)==valormax);
tiempo_valormax=vectorIn(indiceaux,1);

fprintf('Time of maximum: %0.5f Maximum value %0.5f \n',tiempo_valormax(1), valormax(1))