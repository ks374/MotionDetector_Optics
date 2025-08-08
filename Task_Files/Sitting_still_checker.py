import sys, types,os
from pype import *
import pygame as pg
import numpy as np
import random

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
        
        ##########################SSTOPPEDHERE
        stim_ids = range(100)
        stim_ids = np.unique(stim_filenames)
        self.numStim = 100
        con(app,f"Found {self.numStim} stimulus")
        
        #For N stimulus, we will have 5 sprites for each, the first one will be the 
        #top location and the other 4 will be listed from left to right in the bottom. 
        #Currently all positions are hardcoded. 
        Cur_id = 0
        Top_pos = [(0,180)]
        Bot_pos = [(-470,-180),(-170,-180),(170,-180),(470,-180)]
        Pos_list = Top_pos + Bot_pos
        for i in range(self.numStim):
            for j in range(len(Pos_list)):
                img = Sprite(1,1,Pos_list[j][0],Pos_list[j][1],fb=app.fb,depth=1,on=0,centerorigin=1,fname=stim_filenames[i])
                self.mySprites.append(img)
                self.stimid.append(Cur_id)
                Cur_id += 1
        con(app,f"Final Sprite list len is {len(self.mySprites)}")
            
        
    def createParamTable(self,app):
        P = app.getcommon()
        self.myTaskButton = app.taskbutton(text=__name__, check = 1)
        self.myTaskNotebook = DockWindow(title=__name__, checkbutton=self.myTaskButton)
        parfile = "%s.%s" % (app.taskname(), P['subject'])
        
        if parfile:
            parfile = parfile + '.par'
        
        self.myTaskParams = ParamTable(self.myTaskNotebook, (        
            ("Stim Presentation Params", None, None), 
            ("bg_before", "(10, 10, 10)", is_color, "The background color before stimulus presentation"),            
            ("bg_during", "(10, 10, 10)", is_color, "The background color during stimulus presentation"),
            ("stim_path", "/home/shapelab/.pyperc/Tasks/Kiani_Stimuli/300/", is_any, "Directory where stimuli are stored"),           

            
            ("Task Params", None, None),
            ("iti", "1500", is_int, "Inter-trial interval"),
            #"stim_duration", "300", is_int, "Stimulus presentation time"),
            
            ("Reward Params", None, None),
            ("numdrops", "8", is_int, "Number of juice drops")
            ), file=parfile)

    def cleanup(self):
        #delete parameter table and anything else we created
        self.myTaskParams.save()
        self.myTaskButton.destroy()
        self.myTaskNotebook.destroy()
        self.myTaskParams.destroy()
        del self.mySprites
    
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
        
        while 1:
            result,t = self._RunTrial(app,t)
        
        return 1,t
        
    def _RunTrial(self,app,t):
        P = self.myTaskParams.check(mergewith=app.getcommon())
        params = self.myTaskParams.check()
        
        con(app,">------------------------------")
        con(app,"Next trial",'blue')
        
        app.udpy.display(None)
        
        app.globals.dlist = DisplayList(app.fb) #dlist manage all elements that will be shown on the screen. 
        
        app.globals.dlist.bg = self.params['bg_before']
        app.globals.dlist.update()
        app.fb.flip()
        
        #Then start the trial. 
        app.globals.dlist.bg = self.params['bg_during']
        app.globals.dlist.update()
        
        t.reset()
        app.idlefn(self.params['iti']-t.ms())
        app.fb.flip()
            
        #Fetch a random stimulus. 
        rand_pos_id = random.randint(1,4)
        sprite_id = 5*(random.randint(1,10)-1)+rand_pos_id
        self.mySprites[sprite_id].on()
        app.globals.dlist.add(self.mySprites[sprite_id])
        app.globals.dlist.update()
        app.fb.flip()
        #app.udpy.display(app.globals.dlist)
            
        touch_x,touch_y = gettouch(wait=1)
        self.mySprites[sprite_id].off()
        app.globals.dlist.update()
        app.fb.flip()
        result = touch_check(touch_x,touch_y,rand_pos_id)
        if result == 1:
            con(app,"Giving reward...")
            clk_num = self.params['numdrops']
            while clk_num > 0:
                app.reward(multiplier = 1)
                app.idlefn(150)
                clk_num -= 1
        else:
            con(app,"Wrong, not giving reward")
        return result,t
