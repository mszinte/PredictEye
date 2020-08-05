function [expDes]=designConfig(const)
% ----------------------------------------------------------------------
% [expDes]=designConfig(const)
% ----------------------------------------------------------------------
% Goal of the function :
% Define experimental design
% ----------------------------------------------------------------------
% Input(s) :
% const : struct containing constant configurations
% ----------------------------------------------------------------------
% Output(s):
% expDes : struct containg experimental design
% ----------------------------------------------------------------------
% Function created by Martin SZINTE (martin.szinte@gmail.com)
% Last update : 17 / 06 / 2020
% Project :     pRFexp
% Version :     1.0
% ----------------------------------------------------------------------

%% Experimental random variables

% Cond 1 : task (1 modality)
% =======
expDes.oneC             =   [1];
expDes.txt_cond1        =   {'bar'};
% 01 = task on bar

% Var 1 : bar direction (9 modalities)
% ======
expDes.oneV             =   [1;3;5;7];
expDes.txt_var1         =   {'180 deg','225 deg','270 deg','315 deg','0 deg','45 deg','90 deg','135 deg','none'};
% value defined as const.subdirection in constConfig.m
% 01 = 180 deg
% 02 = 225 deg
% 03 = 270 deg
% 04 = 315 deg
% 05 =   0 deg
% 06 =  45 deg
% 07 =  90 deg
% 08 = 135 deg
% 09 = none

% Rand 1: stim orientation (2 modalities)
% =======
expDes.oneR             =   [1;2];
expDes.txt_rand1        =   {'cw','ccw','none'};
% 01 = tilt cw
% 02 = tilt ccw
% 03 = none

% Staircase
% ---------
if const.runNum == 1
    % create staircase starting value
    expDes.stim_stair_val   =   const.stim_stair_val;
    expDes.cor_count_stim   =   0;
    expDes.incor_count_stim =   0;
else
    % load staircase of previous blocks
    load(const.staircase_file);
    expDes.stim_stair_val   =   staircase.stim_stair_val;
    expDes.cor_count_stim   =   staircase.cor_count_stim;
    expDes.incor_count_stim =   staircase.incor_count_stim;
end

%% Experimental configuration :
expDes.nb_cond          =   2;
expDes.nb_var           =   1;
expDes.nb_rand          =   1;
expDes.nb_list          =   0;

%% Experimental loop
rng('default');rng('shuffle');
runT                    =   const.runNum;

t_trial = 0;
for t_bar_pass = 1:size(const.bar_dir_run,2)
    cond1                       =   const.cond1;
    rand_var1                   =   const.bar_dir_run(t_bar_pass);
    
    if rand_var1 == 9
        bar_pos_per_pass  =   const.blk_step;
    else
        if rand_var1 == 1 || rand_var1 == 5
            bar_pos_per_pass     =   const.bar_step_hor;
        elseif rand_var1 == 3 || rand_var1 == 7
            bar_pos_per_pass     =   const.bar_step_ver;
        end
    end
    
    for bar_step = 1:bar_pos_per_pass
    
        rand_rand1                  =   expDes.oneR(randperm(numel(expDes.oneR),1));

        % no bar
        if rand_var1 == 9
            rand_var1                   =   9;
            rand_rand1                  =   3;
        end
    
        t_trial     =   t_trial + 1;
        
        expDes.expMat(t_trial,:)=   [   runT,           t_trial,        cond1,          rand_var1,      t_bar_pass, ...
                                        bar_step,       rand_rand1,     NaN,            NaN,            NaN, ...
                                        NaN,            NaN,            NaN];
        % col 01:   Run number
        % col 02:   Trial number
        % col 03:   Attention task
        % col 04:   Bar direction
        % col 05:   Bar pass period
        % col 06:   Bar step
        % col 07:   Stimulus noise orientation
        % col 08:   Trial onset time
        % col 09:   Trial offset time
        % col 10:   Stimulus noise staircase value
        % col 11:   Reponse value (correct/incorrect)
        % col 12:   Probe time
        % col 13:   Response time
    end
end

expDes.nb_trials = size(expDes.expMat,1);

end