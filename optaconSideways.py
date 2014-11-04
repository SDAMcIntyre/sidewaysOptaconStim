# -*- coding: utf-8 -*-
"""
Created on Tue Nov  4 15:20:27 2014

@author: sarahmcintyre
"""

import numpy
import random
import math

zeros = numpy.zeros
repeat = numpy.repeat
sample = random.sample
ceil = math.ceil

def time_to_frames(t):
    return int(ceil(t/4.35))

def make_stim_map(trialDur,stepDur,isoi):
    """ This functions makes an temporal "map" of the timing of apparent motion steps, 
        in the form of an array. Rows are frames, columns are step numbers. 
        
        trialDur:    total presentation time for a single apparent motion stimulus trial
        stepDur:    the duration of each step of apparent motion
        isoi:        the time from the start of one step to the start of the next
        
        The array returned provides information about which step is "on" at any given frame (4.35ms).
        For example, at the start, the first step should be on, so stimMap[0,0] = 1. After a number 
        of frames determined by the isoi, the second step should be on, stimMap[isoiFrames,1] = 1.
        
        Note that this map does not provide any information about which pins in the array are on.
        The first step represents whichever optacon configuration is determined to be the starting
        configuration by the functions get_start_rows and the input parameters for 
        apparent_motion_stim_sidways().
    """
    trialFrames = time_to_frames(trialDur)
    onFrames = time_to_frames(stepDur)
    isoiFrames = time_to_frames(isoi)
    # number of steps that will start - if not enough time in trialDur, last one won't be as long
    nSteps = int(ceil(1 + (trialFrames - onFrames)/float(isoiFrames)))
    stimMap = zeros([trialFrames,nSteps,],int)
    
    for thisStep in range(nSteps):
        startFrame = thisStep*isoiFrames
        if startFrame + onFrames > len(stimMap):
            onRange = range(startFrame,len(stimMap))
        else:
            onRange = range(startFrame,startFrame + onFrames)
        stimMap[onRange,thisStep] = 1
    return stimMap
    
def get_start_rows(colsToUse=range(0,6),spread=True,rowsToUse=range(0,6)):
    startRows = zeros([1,len(colsToUse)],int)
    if spread:
        nSpreadSections = len(colsToUse)/2
        nSpreadSectionRows = len(rowsToUse)/nSpreadSections
        spreadSectionList=repeat(sample(range(nSpreadSections),len(colsToUse)/2),2) ## list of equal sections, number according to rows/cols being used
        for thisCol in range(len(colsToUse)): ## randomise where in the section each pin starts
            if thisCol % 2 == 0:
                thisRow = spreadSectionList[thisCol]*nSpreadSectionRows + sample(range(nSpreadSectionRows),1)[0]
            startRows[0][thisCol] = thisRow
    else:
        startRow=sample(rowsToUse,1)[0]
        for iCol in range(len(colsToUse)):
            startRows[0][iCol] = startRow
    return startRows[0]

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

def populate_one_step(imageToWrite,stepNo=stepNo,colsToUse=colsToUse[thisFinger],randomPos=randomPos[thisFinger],startRows=startRows[thisFinger],stepVector=stepVector[thisFinger],rowsToUse=rowsToUse):
    for iCol in range(len(colsToUse[i])): 
        col=colsToUse[i][iCol]
        if randomPos[i] == False: ## if coherent motion, motion goes with direction
            row = (startRows[i][iCol] + stepNo*stepVector[i]) % len(rowsToUse)
        elif iCol % 2 ==0: ## if stim is a random test stimulus and column is even (starts with 0)
            row = random.sample(rowsToUse,1)[0] ##choose a new random row
            ## otherwise, row will stay the same as last time, i.e. they will clump in twos
        imageToWrite[col][row] = 1 ## inverted because the Optacon is sideways
    return imageToWrite

def create_one_image(stepsToUse,colsToUse=colsToUse,randomPos=randomPos,startRows=startRows,stepVector=stepVector,rowsToUse=rowsToUse):
    image = zeros([24,6],int)
    for thisFinger in ['left','right']:
        for stepNo in range(len(stepsToUse[thisFinger])):
            if stepsToUse[thisFinger][stepNo]:
                image = populate_one_step(imageToWrite=image)
    return image
