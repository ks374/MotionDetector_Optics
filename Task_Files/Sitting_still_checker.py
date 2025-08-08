import sys, types,os
from pype import *
import pygame as pg
import numpy as np
import random
from collections import deque
from MotionDetector import MotionDetector

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
        self.mySprites = list()
        self.stimid = list() 
        self.numStim = 0
        
    def createStimuli(self,app):
        gParam = app.getcommon() 
        self.params = self.myTaskParams.check()
        #A list of stimuli will be created, so that motion_index will correspond to object 
        #at different heights. 
        
        self.numStim = 100
        stim_ids = range(self.numStim)
        con(app,f"Created {self.numStim} stimuli. ")
        
        #For N stimulus, we will have 5 sprites for each, the first one will be the 
        #top location and the other 4 will be listed from left to right in the bottom. 
        #Currently all positions are hardcoded. 
        Cur_id = 0
        Start_pos = (0,-540)
        End_pos = (0,540)
        Pos_list = [(0,y) for y in range(-540,540,int(1080/self.numStim))]
        Stim_size = self.params['Stim_size']
        for i in range(len(Pos_list)):
            img = Sprite(Stim_size,Stim_size,Pos_list[i][0],Pos_list[i][1],fb=app.fb,depth=1,on=0,centerorigin=1)
            img.fill((255,255,254))
            self.mySprites.append(img)
            self.stimid.append(Cur_id)
            Cur_id += 1
        con(app,f"Final Sprite list len is {len(self.mySprites)}")
        self.SpriteLine = Sprite(1000,10,0,-270,fb=app.fb,depth=1,on=1,centerorigin=1)
        self.SpriteLine.fill((255,0,0))
        self.SpriteBlock = Sprite(1000,250,0,-402,fb=app.fb,depth=1,on=1,centerorigin=1)
        self.SpriteBlock.fill((40,120,40))
        
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
            
            ("Task Params", None, None),
            ("Mapping_scale","2500",is_int,"The scale from motion_index to pixels on the screen. "),
            ("iti", "200", is_int, "Inter-trial interval"),
            ("Reward_delay_length","2",is_int,"The monkey have to sit still for this many rounds to get reward"),
            #"stim_duration", "300", is_int, "Stimulus presentation time"),
            
            ("Reward Params", None, None),
            ("numdrops", "2", is_int, "Number of juice drops")
            ), file=parfile)

    def cleanup(self):
        #delete parameter table and anything else we created
        self.MT.release()
        self.myTaskParams.save()
        self.myTaskButton.destroy()
        self.myTaskNotebook.destroy()
        self.myTaskParams.destroy()
        del self.mySprites
        del self.SpriteLine
        del Self.SpriteBlock
    
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
        
        app.paused = 0
        app.running = 1
        app.led(1)
        
        app.globals.repnum = -1
        app.globals.ncorrect = 0
        app.globals.ntrials = 0
        app.globals.seqcorrect = 0
        #app.globals.uicount = 0
        #app.globals.stimCorrect = 0
        #app.globals.stimSeen = 0
        #pp.globals.yOffset = 600
        
        t = Timer()
        
            #Save recent success rate. 
        result,t = self.RunTrial(app,t)
        return 1
    
    def RunTrial(self,app,t):
        P = self.myTaskParams.check(mergewith=app.getcommon())
        params = self.myTaskParams.check()
        
        app.globals.dlist = DisplayList(app.fb) #dlist manage all elements that will be shown on the screen. 
        app.globals.dlist.bg = self.params['bg_during']
        app.globals.dlist.add(self.SpriteLine)
        app.globals.dlist.add(self.SpriteBlock)
        app.globals.dlist.update()
        app.fb.flip()
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
        
        
        #app.fb.flip()
        
        t.reset()
        #con(app,f"len of mySpirtes = {len(self.mySprites)}")
        flag_reward_updated = 0
        while t.ms()<self.params['iti']:
            MD,_ = self.MT.get_motion_index()
            Mapping_scale = self.params['Mapping_scale']
            show_id = round(MD/Mapping_scale)
            if show_id >= self.numStim:
                show_id = self.numStim-1
            elif show_id <= 1:
                show_id = 1
        
            self.mySprites[show_id].on()
            app.globals.dlist.add(self.mySprites[show_id])
            app.globals.dlist.update()
            app.fb.flip()
            self.mySprites[show_id].off()
            app.globals.dlist.delete(self.mySprites[show_id])
            
            if flag_reward_updated == 0:
                if show_id > 25:
                    self.reward_flag.append(0)
                    flag_reward_updated = 1
        if flag_reward_updated == 0:
            self.reward_flag.append(1)

        if sum(self.reward_flag) == self.params['Reward_delay_length']: #threshold is drawn at (Mapping_scale * 25):
            con(app,"Giving reward...")
            clk_num = self.params['numdrops']
            while clk_num > 0:
                app.reward(multiplier = 1)
                app.idlefn(150)
                clk_num -= 1
            result = 1
        else:
            con(app,"Wrong, not giving reward")
            result = 0

        return result,t
