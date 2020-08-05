function [expDes] = runTrials(scr,const,expDes,my_key)
% ----------------------------------------------------------------------
% [expDes]=runTrials(scr,const,expDes,my_key)
% ----------------------------------------------------------------------
% Goal of the function :
% Draw stimuli of each indivual trial and waiting for inputs
% ----------------------------------------------------------------------
% Input(s) :
% scr : struct containing screen configurations
% const : struct containing constant configurations
% expDes : struct containg experimental design
% my_key : structure containing keyboard configurations
% ----------------------------------------------------------------------
% Output(s):
% resMat : experimental results (see below)
% expDes : struct containing all the variable design configurations.
% ----------------------------------------------------------------------
% Function created by Martin SZINTE (martin.szinte@gmail.com)
% Last update : 20 / 06 / 2020
% Project :     RSexp
% Version :     1.0
% ----------------------------------------------------------------------

for t = 1:const.blk_step
    
    % Write in log/edf
    log_txt                     =   sprintf('TR num %i started at %f\n',t,GetSecs);
    if const.writeLogTxt
        fprintf(const.log_file_fid,log_txt);
    end
    if const.tracker
        Eyelink('message','%s',log_txt);
    end
    
    % wait first trigger in trial beginning
    if t == 1
        % show the iti image
        Screen('FillRect',scr.main,const.background_color);
        drawTarget(scr,const,scr.x_mid,scr.y_mid);
        Screen('Flip',scr.main);
        
        first_trigger           =   0;
        expDes.mri_band_val     =   my_key.first_val(3);
        while ~first_trigger
            if const.scanner == 0 || const.scannerTest
                first_trigger           =   1;
                mri_band_val            =   -8;
            else
                keyPressed              =   0;
                keyCode                 =   zeros(1,my_key.keyCodeNum);
                for keyb = 1:size(my_key.keyboard_idx,2)
                    [keyP, keyC]            =   KbQueueCheck(my_key.keyboard_idx(keyb));
                    keyPressed              =   keyPressed+keyP;
                    keyCode                 =   keyCode+keyC;
                end
                if const.room == 1
                    input_return = my_key.ni_session.inputSingleScan;

                    if input_return(my_key.idx_mri_bands) == ~expDes.mri_band_val
                        keyPressed              = 1;
                        keyCode(my_key.mri_tr)  = 1;
                        expDes.mri_band_val     = ~expDes.mri_band_val;
                        mri_band_val            = input_return(my_key.idx_mri_bands);
                    end
                end

                if keyPressed
                    if keyCode(my_key.escape) && const.expStart == 0
                        overDone(const,my_key)
                    elseif keyCode(my_key.mri_tr)
                        first_trigger          =   1;
                    end
                end
            end
        end

        % write in log/edf
        log_txt                 =   sprintf('TR num %i event mri_trigger val = %i at %f',t,mri_band_val,GetSecs);
        if const.writeLogTxt
            fprintf(const.log_file_fid,'%s\n',log_txt);
        end
        if const.tracker
            Eyelink('message','%s',log_txt);
        end
    end

    nbf = 0;
    missed_all = [];
    while nbf < const.TR_num

        % flip count
        nbf = nbf + 1;

        % Draw background
        Screen('FillRect',scr.main,const.background_color);
        
        % Draw target
        drawTarget(scr,const,scr.x_mid,scr.y_mid);
        
        % Screen flip
        [~,~,~,missed]    =   Screen('Flip',scr.main);
            
        if sign(missed) == 1
            missed_val              =   1;
            missed_all              =   [missed_all;missed,missed_val];
        else
            missed_val              =   0;
            missed_all              =   [missed_all;missed,missed_val];
        end

        % Save trials times
        if nbf == 1
            % TR onset
            log_txt                 =   sprintf('TR num %i onset at %f',t,GetSecs);
            if const.writeLogTxt
                fprintf(const.log_file_fid,'%s\n',log_txt);
            end
            if const.tracker
                Eyelink('message','%s',log_txt);
            end
        end
        
        if nbf == const.TR_num
            % TR offset
            log_txt                 =   sprintf('TR num %i offset at %f',t,GetSecs);
            if const.writeLogTxt
                fprintf(const.log_file_fid,'%s\n',log_txt);
            end
            if const.tracker
                Eyelink('message','%s',log_txt);
            end
        end
        
        % Check keyboard
        % --------------
        keyPressed              =   0;
        keyCode                 =   zeros(1,my_key.keyCodeNum);
        for keyb = 1:size(my_key.keyboard_idx,2)
            [keyP, keyC]            =   KbQueueCheck(my_key.keyboard_idx(keyb));
            keyPressed              =   keyPressed+keyP;
            keyCode                 =   keyCode+keyC;
        end
        
        if const.room == 1
            input_return = my_key.ni_session.inputSingleScan;
            
            % mri trigger
            if input_return(my_key.idx_mri_bands) == ~expDes.mri_band_val
                keyPressed              = 1;
                keyCode(my_key.mri_tr)  = 1;
                expDes.mri_band_val     = ~expDes.mri_band_val;
                mri_band_val            = input_return(my_key.idx_mri_bands);
            end
        end
        
        if keyPressed
            if keyCode(my_key.mri_tr)
                % write in log/edf
                log_txt                 =   sprintf('TR num %i event mri_trigger val = %i at %f',t,mri_band_val,GetSecs);
                if const.writeLogTxt
                    fprintf(const.log_file_fid,'%s\n',log_txt);
                end
                if const.tracker
                    Eyelink('message','%s',log_txt);
                end
            elseif keyCode(my_key.escape)
                if const.expStart == 0
                    overDone(const,my_key)
                end
            end
        end
    end

    % Get number of stim and probe played
    %  -----------------------------------
    % write in log/edf
    log_txt                 =   sprintf('TR num %i - %i missed sync on %i frames, %1.1f%% (mean/median delay = %1.1f/%1.1f ms)',...
                                                t,sum(missed_all(:,2)>0),size(missed_all,1),sum(missed_all(:,2)>0)/size(missed_all,1)*100,...
                                                mean(missed_all(missed_all(:,2)==1))*1000,median(missed_all(missed_all(:,2)==1))*1000);
    if const.writeLogTxt
        fprintf(const.log_file_fid,'%s\n',log_txt);
    end
    if const.tracker
        Eyelink('message','%s',log_txt);
    end
    
    % write in log/edf
    log_txt                     =   sprintf('TR num %i stopped at %f',t,GetSecs);
    if const.writeLogTxt
        fprintf(const.log_file_fid,'%s\n',log_txt);
    end
    if const.tracker
        Eyelink('message', '%s',log_txt);
    end
end

end