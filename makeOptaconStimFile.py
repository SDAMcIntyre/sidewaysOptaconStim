# -*- coding: utf-8 -*-
"""
Created on Tue Nov  4 16:29:29 2014

# To do:
    ## fix overlapping steps
    ## new function to generate full experiment set of motion stimuli:
            # assigning blockNo
            # assigning signal pin code
            # assigning stimulus name?
    ##

@author: sarahmcintyre
"""

from optacon import *
from optaconSideways import *

#def apparent_motion_stim_sideways(prestim = 500, trialDur=600, stepDur={'left':350,'right':200}, isoi={'left':80,'right':100}, 
#                                  rowsToUse=range(0,6), colsToUse={'left':range(0,6),'right':range(18,24)},
#                                  stepVector={'left':1,'right':1}, randomPos={'left':False,'right':False}, spread={'left':True,'right':True}):
#    """This function creates an apparent motion stimulus for the Optacon, in a sideways configuration
#    It returns a list of optacon array configurations, one for each step of the apparent motion, in order.
#    
#        rowsToUse:        List of rows to use. Default is maximum, as the Optacon has 
#                            6 rows. Must start at row 0.
#                                
#        colsToUse:        List of columns to use. Default is maximum for 
#                            'spread' = True to work. The Optacon has 24 columns. 
#                                
#        stepVector:        Number of pins to advance, e.g. value of 1 will activate every pin, value 
#                            of 2 will activate every second pin.Positive values move down/proximal; 
#                            negative values move up/distal.
#                                
#        randomPos:        If True, will use a random position on each step instead of motion. This is 
#                            designed to be used as a test stimulus. If False, will use single-component 
#                            motion (all columns move in the same direction). This is designed to be 
#                            used as an adapting stimulus.
#        spread:            If True, each active column will activate a different row on a given step, 
#                            pseudo-randomly. If False, each column will initially activate the same 
#                            (random) row. This only applies when randomPos is False. If randomPos is 
#                            True, then spread = True.
#                            
#        For parameters with two values, these are for programming two independent stimuli to be presented 
#            to two fingers [Left, Right]
#    """    
#    return motionStim, repList

#### parameters
trialDur=600
stepDur={'left':350,'right':200}
isoi={'left':80,'right':100}
rowsToUse=range(0,6)
colsToUse={'left':range(0,6),'right':range(18,24)}
stepVector={'left':1,'right':1}
randomPos={'left':False,'right':False}
spread={'left':True,'right':True}

###############
mapList=[]
motionStim=[]

for finger in ['left','right']:
    # enforce spread for either of the two stimuli if they use random positions instead of apparent motion
    if randomPos[finger]:
        spread[finger] = True        
    # create a stim map for each stim (left and right finger)    
    mapList.append(make_stim_map(trialDur=trialDur,stepDur=stepDur[finger],isoi=isoi[finger]))

# set starting optacon images for each stim (left and right finger)
startRows = {'left':get_start_rows(colsToUse=colsToUse['left'],spread=spread['left'],rowsToUse=rowsToUse),
                  'right':get_start_rows(colsToUse=colsToUse['right'],spread=spread['right'],rowsToUse=rowsToUse)}

# create a list of unique optacon "images" and accompanying number of repeats based on stim maps  
imageList, repList = make_image_list(mapList=mapList)
         
# create each optacon image based on starting image and stim maps
for imgNo in range(len(imageList)):
    thisImage = create_one_image(stepsToUse=imageList[imgNo])
    motionStim.append(thisImage)


