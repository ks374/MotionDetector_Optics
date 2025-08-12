import sys, types,os
from pype import *
import pygame as pg
import numpy as np
import random
from collections import deque
from MotionDetector import MotionDetector
import datetime
import csv

def RunSet(app):
    app.taskObject.RunSet(app)

def cleanup(app):
    app.taskObject.cleanup(app)
    
def main(app):
    app.taskObject = TouchTask(app)
    app.globals = Holder() #A dummy object to hold parameters. 
    app.idlefb()
    app.startfn = RunSet

class TouchTask:
    def __init__(self,app):
        self.createParamTable(app)
        self.app = app
        self.trial_num = 0
        self.success_rate = 0.0
        self.trial_outcomes = []
        self.csv_file = None
        self.csv_writer = None
        self.mySprites = list()
        self.stimid = list()
        self.numStim = 0
        self.sound_cue = None # Initialize sound cue object

    def createStimuli(self,app):
        # gParam = app.getcommon()
        self.params = self.myTaskParams.check()
        
        # --- SOUND CUE IMPLEMENTATION ---
        # Initialize pygame mixer and load sound file
        pg.mixer.init()
        # Replace 'path/to/your/sound_cue.wav' with the actual path to your sound file
        self.sound_cue = pg.mixer.Sound('/home/lab/.pyperc/Tasks/Sound/mixkit-morning-clock-alarm-1003.wav')
        con(app, "Sound cue loaded.")

        self.numStim = 100
        stim_ids = range(self.numStim)
        con(app,f"Created {self.numStim} stimuli. ")
        
        #For N stimulus, we will have 5 sprites for each, the first one will be the 
        #top location and the other 4 will be listed from left to right in the bottom. 
        #Currently all positions are hardcoded. 
        Cur_id = 0
        Pos_list = [(0,y) for y in range(-500,540,int(1080/self.numStim))]
        Stim_size = self.params['Stim_size']
        for i in range(len(Pos_list)):
            img = Sprite(Stim_size,Stim_size,Pos_list[i][0],Pos_list[i][1],fb=app.fb,depth=1,on=0,centerorigin=1)
            img.fill((255,255,254))
            self.mySprites.append(img)
            self.stimid.append(Cur_id)
            Cur_id += 1
        con(app,f"Final Sprite list len is {len(self.mySprites)}")

        # The rest of the visual stimuli creation is now removed or commented out.
        # The MotionDetector and other visual elements remain.
        self.MT = MotionDetector(0,640,480,30,10)
        self.reward_flag = deque(maxlen=self.params['Reward_delay_length'])
        for _ in range(self.params['Reward_delay_length']):
            self.reward_flag.append(0)

    def createParamTable(self,app):
        P = app.getcommon()
        self.myTaskButton = app.taskbutton(text=__name__, check = 1)
        self.myTaskNotebook = DockWindow(title=__name__, checkbutton=self.myTaskButton)
        parfile = "%s.%s" % (app.taskname(), P['subject'])
        
        if parfile:
            parfile = parfile + '.par'
        
        self.myTaskParams = ParamTable(self.myTaskNotebook, (        
            ("Stim Presentation Params", None, None),
            ("bg_during", "(10, 10, 10)", is_color, "The background color during stimulus presentation"),
            ("Stim_size","10",is_int,"the size of the jumping fixation point"),
            ("Reward_delay_length","2",is_int,"The monkey have to sit still for this many rounds to get reward"),
            ("log_path","/home/lab/temp_Chenghang/",is_any,"path to save the log file"),
            
            ("Task Params", None, None),
            ("Mapping_scale","25000",is_int,"The scale from motion_index to upward acceleration. "),
            ("iti", "200", is_int, "Inter-trial interval"),
            ("Downward_acc","1",is_float,"Downward accelleration of the object"),
            #"stim_duration", "300", is_int, "Stimulus presentation time"),
            
            ("Reward Params", None, None),
            ("numdrops", "2", is_int, "Number of juice drops")
            ), file=parfile)

    def cleanup(self):
        self.MT.release()
        self.myTaskParams.save()
        self.myTaskButton.destroy()
        self.myTaskNotebook.destroy()
        #self.myTaskParams.destroy()
        del self.mySprites
        del self.SpriteLine
        del self.SpriteBlock
        if self.csv_file:
            self.csv_file.close()

    def toggle_photo_diode(self,app):
        app.globals.dlist.update()
        app.fb.sync_toggle()

    def turn_off_photo_diode(self,app):
        app.fb.sync(0)
    
    def RunSet(self,app):
        app.tally(clear=1)
        P = self.myTaskParams.check(mergewith=app.getcommon())
        parames = self.myTaskParams.check()
    
        self.createStimuli(app)
        self.setup_csv_file(app,self.params['log_path'])
        
        app.paused = 0
        app.running = 1
        app.led(1)
        
        app.globals.repnum = -1
        app.globals.ncorrect = 0
        app.globals.ntrials = 0
        app.globals.seqcorrect = 0
        
        t = Timer()
        result,t = self.RunTrial(app,t)
        return 1
    
    def setup_csv_file(self, app,log_path):
        filename = f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_touch_task.csv"
        filename = log_path + filename
        try:
            self.csv_file = open(filename, 'w', newline='')
            self.csv_writer = csv.writer(self.csv_file)
            self.csv_writer.writerow(['Index', 'Time', 'Reward', 'MD', 'Cur_obj_speed', 'Cur_obj_pos'])
            con(app, f"CSV file created: {filename}")
        except IOError as e:
            con(app, f"Error creating CSV file: {e}", 'red')
    
    def RunTrial(self,app,t):
        P = self.myTaskParams.check(mergewith=app.getcommon())
        params = self.myTaskParams.check()
        
        app.globals.dlist = DisplayList(app.fb) #dlist manage all elements that will be shown on the screen. 
        app.globals.dlist.bg = self.params['bg_during']
        # Visual sprite lines for the screen are kept, but the moving sprite is removed
        self.SpriteLine = Sprite(1000,10,0,-270,fb=app.fb,depth=1,on=1,centerorigin=1)
        self.SpriteLine.fill((255,0,0))
        self.SpriteBlock = Sprite(1000,250,0,-402,fb=app.fb,depth=1,on=1,centerorigin=1)
        self.SpriteBlock.fill((40,120,40))
        app.globals.dlist.add(self.SpriteLine)
        app.globals.dlist.add(self.SpriteBlock)
        app.globals.dlist.update()
        app.fb.flip()
        
        self.show_id = 0
        self.show_id_speed = 0
        while app.running == 1:
            while app.paused == 1:
                app.idlefn(1000)
            result,t = self._RunTrial(app,t)
        self.cleanup()
        return 1,t
        
    def _RunTrial(self,app,t):
        P = self.myTaskParams.check(mergewith=app.getcommon())
        self.params = self.myTaskParams.check()
        
        con(app,">------------------------------")
        con(app,"Next trial",'blue')
        
        app.udpy.display(None)
        
        t.reset()
        flag_reward_updated = 0
        while t.ms()<self.params['iti']:
            _ = self.MT.update_frame_buffer()
            MD,_ = self.MT.get_motion_index(2) #Repead it to avoid sudden motion after reward. 
            Mapping_scale = self.params['Mapping_scale']
            total_a = MD/Mapping_scale-self.params['Downward_acc']
            self.show_id_speed = self.show_id_speed + total_a
            if self.show_id_speed > 10:
                self.show_id_speed = 10
            elif self.show_id_speed < -30:
                self.show_id_speed = -10
            self.show_id = round(self.show_id + self.show_id_speed)
            if self.show_id >= self.numStim:
                self.show_id = self.numStim-1
            elif self.show_id <= 1:
                self.show_id = 1
            
            self.mySprites[self.show_id].on()
            app.globals.dlist.add(self.mySprites[self.show_id])
            app.globals.dlist.update()
            app.fb.flip()
            self.mySprites[self.show_id].off()
            app.globals.dlist.delete(self.mySprites[self.show_id])
        
            # --- SOUND CUE IMPLEMENTATION ---
            # Play sound cue when a certain condition is met
            if flag_reward_updated == 0:
                if self.show_id > 25:
                    self.reward_flag.append(0)
                    if not pg.mixer.get_busy(): # Check if sound is not already playing
                        self.sound_cue.play()
                    flag_reward_updated = 1
        if flag_reward_updated == 0:
            self.reward_flag.append(1)
            if pg.mixer.get_busy():
                self.sound_cue.stop()
            
        if flag_reward_updated == 0:
            self.reward_flag.append(1)

        reward_given = False
        if sum(self.reward_flag) >= self.params['Reward_delay_length']: #threshold is drawn at (Mapping_scale * 25):
            con(app,"Giving reward...")
            clk_num = self.params['numdrops']
            while clk_num > 0:
                app.reward(multiplier = 1)
                app.idlefn(150)
                clk_num -= 1
            result = 1
            reward_given = True
        else:
            con(app,"Wrong, not giving reward")
            result = 0
            reward_given = False

        # Update trial counts and success rate
        self.trial_num += 1
        self.trial_outcomes.append(reward_given)
        success_count = sum(self.trial_outcomes)
        self.success_rate = (success_count / self.trial_num) * 100
        con(app, f"Trial {self.trial_num}: Reward given: {reward_given}. Current success rate: {self.success_rate:.2f}%")

        # Write final reward status to the CSV file
        if self.csv_writer:
            # The last row written had None for reward. We need to go back and update it.
            # A better way would be to write all the data for a trial at the end of the trial.
            # However, to minimally change the code, we can append a final row for the trial result.
            self.csv_writer.writerow([self.trial_num, datetime.datetime.now().isoformat(), reward_given, None, None, None])

        return result,t
