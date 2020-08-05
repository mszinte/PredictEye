function [const]=constConfig(scr,const)
% ----------------------------------------------------------------------
% [const]=constConfig(scr,const)
% ----------------------------------------------------------------------
% Goal of the function :
% Define all constant configurations
% ----------------------------------------------------------------------
% Input(s) :
% scr : struct containing screen configurations
% const : struct containing constant configurations
% ----------------------------------------------------------------------
% Output(s):
% const : struct containing constant configurations
% ----------------------------------------------------------------------
% Function created by Martin SZINTE (martin.szinte@gmail.com)
% Last update : 17 / 01 / 2020
% Project :     pMFexp
% Version :     1.0
% ----------------------------------------------------------------------

% Randomization
rng('default');
rng('shuffle');

%% Colors
const.white             =   [255,255,255];                                                      % white color
const.black             =   [0,0,0];                                                            % black color
const.gray              =   [128,128,128];                                                      % gray color
const.red               =   [200,0,0];                                                          % red
const.background_color  =   const.black;                                                        % background color
const.dot_color         =   const.white;                                                        % define fixation dot color

% Fixation circular aperture
const.fix_out_rim_radVal=   0.3;                                                                % radius of outer circle of fixation bull's eye
const.fix_rim_radVal    =   0.75*const.fix_out_rim_radVal;                                      % radius of intermediate circle of fixation bull's eye in degree
const.fix_radVal        =   0.25*const.fix_out_rim_radVal;                                      % radius of inner circle of fixation bull's eye in degrees
const.fix_out_rim_rad   =   vaDeg2pix(const.fix_out_rim_radVal,scr);                            % radius of outer circle of fixation bull's eye in pixels
const.fix_rim_rad       =   vaDeg2pix(const.fix_rim_radVal,scr);                                % radius of intermediate circle of fixation bull's eye in pixels
const.fix_rad           =   vaDeg2pix(const.fix_radVal,scr);                                    % radius of inner circle of fixation bull's eye in pixels


%% Time parameters
const.TR_dur            =   1.2;                                                                % repetition time
const.TR_num            =   (round(const.TR_dur/scr.frame_duration));                           % repetition time in screen frames
const.seq_num           =   9;                                                                  % number of sequences per run
const.eyemov_seq        =   [1,2,1,2,1,2,1,2,1];                                                % 1 = blank, 2 = eye movement

const.eyemov_step       =   32;                                                                 % eye movement steps (16 smooth pursuit and 16 saccade trials)
const.blk_step          =   16;                                                                 % blank period step
const.eyemov_step_dur   =   const.TR_dur;                                                       % eye movement steps in seconds
const.eyemov_step_num   =   (round(const.eyemov_step_dur/scr.frame_duration));                  % eye movement step duration in screen frames
const.blk_step_dur      =   const.TR_dur;                                                       % blank step duration in seconds
const.blk_step_num      =   (round(const.blk_step_dur/scr.frame_duration));                     % blank step duration in screen frames


const.eyemov_ampVal     =   [2.5, 5,  7.5,  10];                                                % eye movement amplitude in degrees
const.eyemov_amp        =   vaDeg2pix(const.eyemov_ampVal,scr);                                 % eye movement amplitude in pixel
const.eyemov_dir_step   =   22.5;                                                               % eye movement direction steps
const.eyemov_dir        =   0:const.eyemov_dir_step:360-const.eyemov_dir_step;                  % eye movement diection

const.pursuit_tot_dur   =   1.100;                                                              % eye movement total duration in seconds
const.pursuit_tot_num   =   (round(const.pursuit_tot_dur/scr.frame_duration));                  % eye movement total duration in screen frames
const.pursuit_ramp_dur  =   0.100;                                                              % eye movement ramp duration in seconds
const.pursuit_ramp_num  =   (round(const.pursuit_ramp_dur/scr.frame_duration));                 % eye movement ramp duration in screen frames
const.pursuit_dur       =   const.pursuit_tot_dur - const.pursuit_ramp_dur;                     % eye movement duration after ramp
const.pursuit_speed_pps =   const.eyemov_amp/const.pursuit_dur;                                 % eye movement speed in pixel per second
const.pursuit_speed_ppf =   const.pursuit_speed_pps/scr.hz;                                     % eye movement speed in degree per screen frame
const.end_dur           =   0.100;                                                              % return saccade duration in seconds
const.end_num           =   (round(const.end_dur/scr.frame_duration));                          % return saccade duration in screen frames

const.trial_dur         =   const.pursuit_tot_dur + const.end_dur;                              % trial duration in seconds
const.trial_num         =   (round(const.trial_dur/scr.frame_duration));                        % trial duration in screen frames

% define TR for scanner
if const.scanner
    const.TRs = 0;
    for seq = const.eyemov_seq
        if seq == 1
            TR_seq = const.blk_step;
        elseif seq == 1
            TR_seq = const.eyemov_step;
        end
        const.TRs = const.TRs + TR_seq;
    end
    const.TRs = const.TRs;
    fprintf(1,'\n\tScanner parameters; %1.0f TRs, %1.2f seconds, %s\n',const.TRs,const.TR_dur,datestr(seconds((const.TRs*const.TR_dur)),'MM:SS'));
end

% compute pusuit coordinates
for pursuit_amp = 1:size(const.eyemov_amp,2)
    pix_ramp = (const.pursuit_ramp_num-1)*const.pursuit_speed_ppf(pursuit_amp);
    pix_step = const.pursuit_speed_ppf(pursuit_amp);
    for pursuit_dir = 1:size(const.eyemov_dir,2)
        for nbf = 1:const.pursuit_tot_num
            if nbf == 1
                % eye movement ramp
                const.pursuit_matX(nbf,pursuit_amp,pursuit_dir) = scr.x_mid + (cosd(const.eyemov_dir(pursuit_dir)-180) * pix_ramp);
                const.pursuit_matY(nbf,pursuit_amp,pursuit_dir) = scr.y_mid + (-sind(const.eyemov_dir(pursuit_dir)-180) * pix_ramp);
            else
                % eye movement step
                const.pursuit_matX(nbf,pursuit_amp,pursuit_dir) = const.pursuit_matX(nbf-1,pursuit_amp,pursuit_dir) + (cosd(const.eyemov_dir(pursuit_dir)) * pix_step);
                const.pursuit_matY(nbf,pursuit_amp,pursuit_dir) = const.pursuit_matY(nbf-1,pursuit_amp,pursuit_dir) + (-sind(const.eyemov_dir(pursuit_dir)) * pix_step);
            end
        end
    end
end

%% Eyelink calibration value
% Personal calibrations
rng('default');rng('shuffle');
angle = 0:pi/3:5/3*pi;
 
% compute calibration target locations
const.calib_amp_ratio  = 0.5;
[cx1,cy1] = pol2cart(angle,const.calib_amp_ratio);
[cx2,cy2] = pol2cart(angle+(pi/6),const.calib_amp_ratio*0.5);
cx = round(scr.x_mid + scr.x_mid*[0 cx1 cx2]);
cy = round(scr.y_mid + scr.x_mid*[0 cy1 cy2]);
 
% order for eyelink
const.calibCoord = round([  cx(1), cy(1),...   % 1.  center center
                            cx(9), cy(9),...   % 2.  center up
                            cx(13),cy(13),...  % 3.  center down
                            cx(5), cy(5),...   % 4.  left center
                            cx(2), cy(2),...   % 5.  right center
                            cx(4), cy(4),...   % 6.  left up
                            cx(3), cy(3),...   % 7.  right up
                            cx(6), cy(6),...   % 8.  left down
                            cx(7), cy(7),...   % 9.  right down
                            cx(10),cy(10),...  % 10. left up
                            cx(8), cy(8),...   % 11. right up
                            cx(11),cy(11),...  % 12. left down
                            cx(12),cy(12)]);    % 13. right down
      
% compute validation target locations (calibration targets smaller radius)
const.valid_amp_ratio = const.calib_amp_ratio*0.8;
[vx1,vy1] = pol2cart(angle,const.valid_amp_ratio);
[vx2,vy2] = pol2cart(angle+pi/6,const.valid_amp_ratio*0.5);
vx = round(scr.x_mid + scr.x_mid*[0 vx1 vx2]);
vy = round(scr.y_mid + scr.x_mid*[0 vy1 vy2]);
 
% order for eyelink
const.validCoord =round( [  vx(1), vy(1),...   % 1.  center center
                             vx(9), vy(9),...   % 2.  center up
                             vx(13),vy(13),...  % 3.  center down
                             vx(5), vy(5),...   % 4.  left center
                             vx(2), vy(2),...   % 5.  right center
                             vx(4), vy(4),...   % 6.  left up
                             vx(3), vy(3),...   % 7.  right up
                             vx(6), vy(6),...   % 8.  left down
                             vx(7), vy(7),...   % 9.  right down
                             vx(10),vy(10),...  % 10. left up
                             vx(8), vy(8),...   % 11. right up
                             vx(11),vy(11),...  % 12. left down
                             vx(12),vy(12)]);    % 13. right down

const.ppd               =   vaDeg2pix(1,scr);                                                  % get one pixel per degree

end