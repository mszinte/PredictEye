function [const] = dirSaveFile(const)
% ----------------------------------------------------------------------
% [const] = dirSaveFile(const)
% ----------------------------------------------------------------------
% Goal of the function :
% Make directory and saving files name and fid.
% ----------------------------------------------------------------------
% Input(s) :
% const : struct containing constant configurations
% ----------------------------------------------------------------------
% Output(s):
% const : struct containing constant configurations
% ----------------------------------------------------------------------
% Function created by Martin SZINTE (martin.szinte@gmail.com)
% Last update : 20 / 06 / 2020
% Project :     RSexp
% Version :     1.0
% ----------------------------------------------------------------------

% Create data directory 
if ~isdir(sprintf('data/%s/func/',const.sjct))
    mkdir(sprintf('data/%s/func/',const.sjct))
end

% Define directory
const.dat_output_file   =   sprintf('data/%s/func/%s_task-%s_%s',const.sjct,const.sjct,const.cond1_txt,const.run_txt);

% Eye data
const.eyelink_temp_file =   'XX.edf';
const.eyelink_local_file=   sprintf('%s_eyeData.edf',const.dat_output_file);

% Create additional info directory
if ~isdir(sprintf('data/%s/add/',const.sjct))
    mkdir(sprintf('data/%s/add/',const.sjct))
end

% Define directory
const.add_output_file   =   sprintf('data/%s/add/%s_task-%s_%s',const.sjct,const.sjct,const.cond1_txt,const.run_txt);

% Define .mat saving file
const.mat_file          =   sprintf('%s_matFile.mat',const.add_output_file);

% Log file
if const.writeLogTxt
    const.log_file          =   sprintf('%s_logData.txt',const.add_output_file);
    const.log_file_fid      =   fopen(const.log_file,'w');
end

end