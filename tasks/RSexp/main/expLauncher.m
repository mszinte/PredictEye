%% General experimenter launcher
%  =============================
% By :      Martin SZINTE
% Projet :  RSexp
% With :    Vanessa Morita, Anna MONTAGNINI & Guillaume MASSON
% Version:  1.0

% Version description
% ===================
% Resting state experiment for Glasser parcellation

% To do
% -----

% Design idea
% -----------
% MB6 with 2mm isotropic voxels
% TR of 800 ms , 500 TRs in total
% simple fixation, eye tracking control

% To do
% -----
% test in the lab with eyelink

% First settings
% --------------
Screen('CloseAll');clear all;clear mex;clear functions;close all;home;AssertOpenGL;

% General settings
% ----------------
const.expName           =   'RSexp';        % experiment name
const.expStart          =   1;              % Start of a recording exp                          0 = NO  , 1 = YES
const.checkTrial        =   0;              % Print trial conditions (for debugging)            0 = NO  , 1 = YES
const.writeLogTxt       =   0;              % write a log file in addition to eyelink file      0 = NO  , 1 = YES

% External controls
% -----------------
const.tracker           =   1;              % run with eye tracker                              0 = NO  , 1 = YES
const.scanner           =   1;              % run in MRI scanner                                0 = NO  , 1 = YES
const.scannerTest       =   0;              % run with T returned at TR time                    0 = NO  , 1 = YES
const.room              =   1;              % run in MRI or eye-tracking room                   1 = MRI , 2 = eye-tracking

% Run order and number per condition
% ----------------------------------
const.cond_run_order    =   [01;01];
const.cond_run_num      =   [01;02];

% Desired screen setting1
% ----------------------
const.desiredFD         =   120;            % Desired refresh rate
%fprintf(1,'\n\n\tDon''t forget to change before testing\n');
const.desiredRes        =   [1920,1080];    % Desired resolution

% Path
% ----
dir                     =   (which('expLauncher'));
cd(dir(1:end-18));

% Add Matlab path
% ---------------
addpath('config','main','conversion','eyeTracking','instructions','trials','stim','stats');

% Subject configuration
% ---------------------
[const]                 =   sbjConfig(const);

% Main run
% --------
main(const);
