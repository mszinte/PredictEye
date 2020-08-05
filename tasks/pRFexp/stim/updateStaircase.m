function [expDes] = updateStaircase(cond1,const,expDes,response,current_time)
% ----------------------------------------------------------------------
% [expDes] = updateStaircase(cond1,const,expDes,response,current_time)
% ----------------------------------------------------------------------
% Goal of the function :
% Update the staircase value in function of the response
% ----------------------------------------------------------------------
% Input(s) :
% cond1 : fixation of stimulus task
% const : struct containing constant configurations
% expDes : struct containg experimental design
% response: response returned by participant
% current_time : last GetSecs (clock)
% ----------------------------------------------------------------------
% Output(s):
% expDes : experimental trial config
% ----------------------------------------------------------------------
% Function created by Martin SZINTE (martin.szinte@gmail.com)
% Last update : 17 / 06 / 2020
% Project :     pRFexp
% Version :     1.0
% ----------------------------------------------------------------------

% update counters
if response == 1
    expDes.cor_count_stim   =   expDes.cor_count_stim + 1;
elseif response == 0
    expDes.incor_count_stim =   expDes.incor_count_stim + 1;
end

if cond1 == 1
    % stimuli staircase: update difficulty and set counter to zero
    if expDes.cor_count_stim == const.good_4_harder
        expDes.stim_stair_val   =   expDes.stim_stair_val - 1;
        expDes.cor_count_stim   =   0;
        expDes.incor_count_stim =   0;
        update_stim             =   1;
    elseif expDes.incor_count_stim == const.bad_4_easier
        expDes.stim_stair_val   =   expDes.stim_stair_val + 1;
        expDes.cor_count_stim   =   0;
        expDes.incor_count_stim =   0;
        update_stim             =   1;
    else
        update_stim             =   0;
    end
    
    if expDes.stim_stair_val > const.num_steps_kappa
        expDes.stim_stair_val   =   const.num_steps_kappa;
    elseif expDes.stim_stair_val < 2
        expDes.stim_stair_val  =   2;
    end
    
    if update_stim
        log_txt                 =   sprintf('stimulus staircase updated to %1.2f at %f',expDes.stim_stair_val,current_time);
        if const.writeLogTxt
            fprintf(const.log_file_fid,'%s\n',log_txt);
        end
        if const.tracker
            Eyelink('message','%s',log_txt);
        end
    end
end

end