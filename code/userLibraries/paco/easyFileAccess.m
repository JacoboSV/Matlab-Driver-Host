function dataout = easyFileAccess(pathin,sep)
    global user__Data__Path;
    if nargin < 2
        sep = ' ';
    end 
    realpath = strcat(user__Data__Path, pathin);

    %disp(realpath)
    datatable = readtable(realpath, 'Delimiter',{sep});
    dataout = datatable{:,:};
end
