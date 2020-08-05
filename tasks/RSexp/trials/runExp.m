function [const] = runExp(scr,const,el,my_key)
% ----------------------------------------------------------------------
% [const] = runExp(scr,const,el,my_key)
% ----------------------------------------------------------------------
% Goal of the function :
% Launch experiement instructions and connection with eyelink
% ----------------------------------------------------------------------
% Input(s) :
% scr : struct containing screen configurations
% const : struct containing constant configurations
% my_key : structure containing keyboard configurations
% ----------------------------------------------------------------------
% Output(s):
% const : struct containing constant configurations
% ----------------------------------------------------------------------
% Function created by Martin SZINTE (martin.szinte@gmail.com)
% Last update : 20 / 06 / 2020
% Project :     RSexp
% Version :     1.0
% ----------------------------------------------------------------------

% Special instruction for scanner
% -------------------------------
if const.scanner && ~const.scannerTest
    scanTxt                 =   '_Scanner';
else
    scanTxt                 =   '';
end

% Save all config at start of the block
% -------------------------------------
config.scr              =   scr;
config.const            =   const;
config.my_key           =   my_key;
save(const.mat_file,'config');

% First mouse config
% ------------------
if const.expStart
    HideCursor;
    for keyb = 1:size(my_key.keyboard_idx,2)
        KbQueueFlush(my_key.keyboard_idx(keyb));
    end
end

% Initial calibrations
% --------------------
if const.tracker
    fprintf(1,'\tEye tracking instructions - press space or right button-\n');
    eyeLinkClearScreen(el.bgCol);
    eyeLinkDrawText(scr.x_mid,scr.y_mid,el.txtCol,'CALIBRATION INSTRUCTION - PRESS SPACE');
    instructionsIm(scr,const,my_key,sprintf('Calibration%s',scanTxt),0);
    calibresult             =   EyelinkDoTrackerSetup(el);
    if calibresult == el.TERMINATE_KEY
        return
    end
end

for keyb = 1:size(my_key.keyboard_idx,2)
    KbQueueFlush(my_key.keyboard_idx(keyb));
end

% Start Eyelink
% -------------
record                  =   0;
while ~record
    if const.tracker
        if ~record
            Eyelink('startrecording');
            key                     =   1;
            while key ~=  0
                key                     =   EyelinkGetKey(el);
            end
            error                   =   Eyelink('checkrecording');
            if error==0
                record                  =   1;
                Eyelink('message', 'RECORD_START');
            else
                record                  =   0;
                Eyelink('message', 'RECORD_FAILURE');
            end
        end
    else
        record                  =   1;
    end
end

% Task instructions 
fprintf(1,'\n\tTask instructions -press space or left button-');
if const.tracker
    eyeLinkClearScreen(el.bgCol);
    eyeLinkDrawText(scr.x_mid,scr.y_mid,el.txtCol,'TASK INSTRUCTIONS - PRESS SPACE')
end
instructionsIm(scr,const,my_key,sprintf('%s%s',const.cond1_txt,scanTxt),0);
for keyb = 1:size(my_key.keyboard_idx,2)
    KbQueueFlush(my_key.keyboard_idx(keyb));
end
fprintf(1,'\n\n\tBUTTON PRESSED BY SUBJECT\n');

% Write on eyelink screen
if const.tracker
    drawTrialInfoEL(scr,const)
end

% Main trial loop
% ---------------
expDes = [];
[expDes] = runTrials(scr,const,expDes,my_key);

% End messages
% ------------
if const.runNum == size(const.cond_run_order,1)
    instructionsIm(scr,const,my_key,'End',1);
else
    instructionsIm(scr,const,my_key,'End_block',1);
end

% Save all config at the end of the block (overwrite start made at start)
% ---------------------------------------
config.scr = scr; config.const = const; config.my_key = my_key;
save(const.mat_file,'config');

% Stop Eyelink
% ------------
if const.tracker
    Eyelink('command','clear_screen');
    Eyelink('command', 'record_status_message ''END''');
    WaitSecs(1);
    Eyelink('stoprecording');
    Eyelink('message', 'RECORD_STOP');
    eyeLinkClearScreen(el.bgCol);eyeLinkDrawText(scr.x_mid,scr.y_mid,el.txtCol,'THE END - PRESS SPACE OR WAIT');
end

end