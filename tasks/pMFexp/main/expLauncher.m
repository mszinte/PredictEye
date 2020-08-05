%% General experimenter launcher
%  =============================
% By :      Martin SZINTE
% Projet :  pMFexp
% With :    Vanessa Morita, Anna MONTAGNINI & Guillaume MASSON
% Version:  1.0

% Version description
% ===================
% Experiment in which we try to adapt pRF methods to eye movement task.
% To do so, participants are invited to prepare sequences of smooth pursuit
% and saccadic eye movements across the screen

% pRF adaptation to do
% --------------------
% kick out mention of 2 acquisitions, keep 1.2 mm
% const.run_txt in sbjConfig.m instead of dirSaveFile

% design idea
% -----------
% 1.0 s of smooth pursuit followed by 200 ms of fixation
% 1.2 s to do return saccade
% 16 directions clockwise spread by 22.5 deg or pi/8 of smooth pursuit
% 16 directions clockwise spread by 22.5 deg or pi/8 of saccade
% 4 amplitudes 2.5, 5, 7.5, 10 dva giving 2.5, 5, 7.5, 10 dva/s smooth pursuit
% 9 sequences, sequence no 1, 3, 5, 7 and 9 are fixation periods
%              sequence no 2, 4, 6 and 8 are eye movement sequences
% randomize order of amplitude per subjects

% To do
% -----
% 1. make eye movement analysis

% First settings
% --------------
Screen('CloseAll');clear all;clear mex;clear functions;close all;home;AssertOpenGL;

% General settings
% ----------------
const.expName           =   'pMFexp';       % experiment name
const.expStart          =   1;              % Start of a recording exp                          0 = NO  , 1 = YES
const.checkTrial        =   0;              % Print trial conditions (for debugging)            0 = NO  , 1 = YES
const.writeLogTxt       =   0;              % write a log file in addition to eyelink file      0 = NO  , 1 = YES
const.mkVideo           =   0;              % Make a video of a run                             0 = NO  , 1 = YES

% External controls
% -----------------
const.tracker           =   1;              % run with eye tracker                              0 = NO  , 1 = YES
const.scanner           =   1;              % run in MRI scanner                                0 = NO  , 1 = YES
const.scannerTest       =   0;              % run with T returned at TR time                    0 = NO  , 1 = YES
const.room              =   1;              % run in MRI or eye-tracking room                   1 = MRI , 2 = eye-tracking

% Run order and number per condition
% ----------------------------------
const.cond_run_order    =   [01;01;01;01;01];
const.cond_run_num      =   [01;02;03;04;05];

% Desired screen setting
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
