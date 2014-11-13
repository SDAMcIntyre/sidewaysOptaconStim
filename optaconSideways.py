# -*- coding: utf-8 -*-
"""
Created on Tue Nov  4 15:20:27 2014

@author: sarahmcintyre
"""

from optacon import map_apparent_motion
from optacon import get_start_rows
import numpy
import random

zeros = numpy.zeros
sample = random.sample

def make_image_list(mapList):
    repList=[]
    imageList=[]
    def is_prev_same(a,b,i):
        return all(a[i]==a[i-1]) and all(b[i]==b[i-1])
    for frameNo in range(len(mapList[0])):
        if frameNo!=0 and is_prev_same(mapList[0],mapList[1],frameNo):
            repList[len(repList)-1] +=1
        else:
            imageList.append({'left':mapList[0][frameNo], 'right':mapList[1][frameNo]})
            repList.append(1)
    return imageList, repList

def populate_one_step(imageToWrite,stepNo,colsToUse,randomPos,startRows,stepVector,rowsToUse):
    for iCol in range(len(colsToUse)): 
        col=colsToUse[iCol]
        if randomPos == False: ## if coherent motion, motion goes with direction
            row = (startRows[iCol] + stepNo*stepVector) % len(rowsToUse)
        elif iCol % 2 ==0: ## if stim is a random test stimulus and column is even (starts with 0)
            row = sample(rowsToUse,1)[0] ##choose a new random row
            ## otherwise, row will stay the same as last time, i.e. they will clump in twos
        imageToWrite[col][row] = 1 ## inverted because the Optacon is sideways
    return imageToWrite

def create_one_image(stepsToUse,colsToUse,randomPos,startRows,stepVector,rowsToUse):
    image = zeros([24,6],int)
    for thisFinger in ['left','right']:
        for stepNo in range(len(stepsToUse[thisFinger])):
            if stepsToUse[thisFinger][stepNo]:
                image = populate_one_step(imageToWrite=image,stepNo=stepNo,colsToUse=colsToUse[thisFinger],randomPos=randomPos[thisFinger],startRows=startRows[thisFinger],stepVector=stepVector[thisFinger],rowsToUse=rowsToUse)
    return image

def single_presentation(presDur=3000, stepDur=[50,50], isoi=[82,82], 
                                  rowsToUse=range(0,6), colsToUse=[range(0,6),range(18,24)],
                                  stepVector=[1,1], randomPos=[False,False], spread=[True,True]):
    """This function creates an apparent motion stimulus for the Optacon, in a sideways configuration
    It returns a list of optacon array configurations, one for each step of the apparent motion, in order.
    
        rowsToUse:        List of rows to use. Default is maximum, as the Optacon has 
                            6 rows. Must start at row 0.
                                
        colsToUse:        List of columns to use. Default is maximum for 
                            'spread' = True to work. The Optacon has 24 columns. 
                                
        stepVector:        Number of pins to advance, e.g. value of 1 will activate every pin, value 
                            of 2 will activate every second pin.Positive values move down/proximal; 
                            negative values move up/distal.
                                
        randomPos:        If True, will use a random position on each step instead of motion. This is 
                            designed to be used as a test stimulus. If False, will use single-component 
                            motion (all columns move in the same direction). This is designed to be 
                            used as an adapting stimulus.
        spread:            If True, each active column will activate a different row on a given step, 
                            pseudo-randomly. If False, each column will initially activate the same 
                            (random) row. This only applies when randomPos is False. If randomPos is 
                            True, then spread = True.
                            
        For parameters with two values, these are for programming two independent stimuli to be presented 
            to two fingers [Left, Right]
    """    
    # respTime = 500,
    
    #convert lists to dictionaries
    lab = ['left','right']
    stepDur = dict(zip(lab,stepDur))
    isoi = dict(zip(lab,isoi))
    colsToUse = dict(zip(lab,colsToUse))
    stepVector = dict(zip(lab,stepVector))
    randomPos = dict(zip(lab,randomPos))
    spread = dict(zip(lab,spread))
    
    mapList=[]
    motionStim=[]
    
    for finger in ['left','right']:
        # enforce spread for either of the two stimuli if they use random positions instead of apparent motion
        if randomPos[finger]:
            spread[finger] = True        
        # create a stim map for each stim (left and right finger)    
        mapList.append(map_apparent_motion(presDur=presDur,stepDur=stepDur[finger],isoi=isoi[finger]))
    
    # set starting optacon images for each stim (left and right finger)
    startRows = {'left':get_start_rows(colsToUse=colsToUse['left'],spread=spread['left'],rowsToUse=rowsToUse),
                      'right':get_start_rows(colsToUse=colsToUse['right'],spread=spread['right'],rowsToUse=rowsToUse)}
    
    # create a list of unique optacon "images" and accompanying number of repeats based on stim maps  
    imageList, repList = make_image_list(mapList=mapList)
             
    # create each optacon image based on starting image and stim maps
    for imgNo in range(len(imageList)):
        thisImage = create_one_image(stepsToUse=imageList[imgNo],colsToUse=colsToUse,randomPos=randomPos,startRows=startRows,stepVector=stepVector,rowsToUse=rowsToUse)
        motionStim.append(thisImage)
    
    return motionStim, repList
