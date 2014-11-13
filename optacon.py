# -*- coding: utf-8 -*-
"""
Created on Tue Nov  4 16:26:33 2014

@author: sarahmcintyre
"""
import numpy
import sys
import math
import random

zeros = numpy.zeros
ceil = math.ceil
repeat = numpy.repeat
sample = random.sample


def write_protocol_file(fileName,stimList,stimRep=[1],blockList=[2],dwellTime=[4.35],leadTime=2000,stimName=[' '],
        readPins=['A1','B1','C1','D1','E1','F1']):
    """This function writes your stimulus list to a text file that can be loaded by the optacon controller software
    Block" and "Stimulus" are terms used by the optacon software. Stimuli are nested within Blocks.
        fileName:                 Name of file to save.
        stimList*:                 List of 24x6 arrays indicating state of each pin for each Stimulus.
        stimRep*:                List giving the number of times each Stimulus is to be repeated;
                                        if dwellTime is default, presentation duration = stimRep x 4.35ms.
        dwellTime*:             List giving the dwell time in ms; it's better to leave this as default and use stimRep to determine time.
                                       Default value of 4.35 will give one frame of approx 4.35ms.
       leadTime:                Use this to set the duration (in ms) of a blank stimulus presentation inserted at the start of the protocol.
        stimName*:             List giving the name of each Stimulus (optional).
        readPins:                List of optacon pins to be read by LabChart.
        *these variables should have the same length (if left at default it will be made to match length of other variables)
        """
     
    # quality control
    if 1 in blockList:
        sys.exit('blockList must not contain block number "1". It is reserved for the lead time inserted at the start of the protocol.')
    if len(stimRep)==1:
        stimRep = stimRep*len(stimList)
    if len(blockList)==1:
        blockList = blockList*len(stimList)
    if len(dwellTime)==1:
        dwellTime = dwellTime*len(stimList)
    if len(stimName)==1:
        stimName = stimName*len(stimList)
    if (not len(stimList)==len(stimRep)==len(blockList)==len(dwellTime)==len(stimName)):
        sys.exit('stimulus lists must have equal length')

    # add blank stim to start of protocol
    stimList.insert(0,zeros([24,6],int))
    stimRep.insert(0,int(ceil(leadTime/dwellTime[0])))
    blockList.insert(0,1)
    dwellTime.insert(0,4.35)    
    stimName.insert(0,'lead time')
    # ----------------
    
    # combine all lists into master list
    masterStimList=[]
    for i in range(len(stimList)):
        masterStimList.append({'stim':stimList[i], 'blockNo':blockList[i], 'stimNo':i+1, 
                                    'dwellTime':dwellTime[i],'stimRep':stimRep[i], 'stimName':stimName[i]})
    #-----------------
    
    # write header
    dataFile = open(fileName+'.txt', 'w')
    dataFile.write('This is an "Optacon Stimulator" Data File.\nFile Format\t1\n' 
                                        'nBlocks\t%i\n' %len(set(blockList)))
    dataFile.write('Spare Line\nSpare Line\nSpare Line\nSpare Line\nSpare Line\n')
    dataFile.write('Pin Sync\t'+"\t".join("%s" %pin for pin in readPins)+'\n\n')
    # ------------
        
    # write blocks
    dataFile.write('Block No\t nStimuli\t nPresentations\n')
    for b in set(blockList):
        dataFile.write('%i\t%i\t%i\n'%(b,blockList.count(b),1))
    dataFile.write('\n') ## blank line between block description and stimuli
    # ------
            
    # write stimuli
    for n in range(len(masterStimList)):
        thisStim = masterStimList[n]
        dataFile.write('Row No\tBlock No\tStim No\tnRows\tDwell ms\tType\tnPresentations\tName\n')
        dataFile.write('\t%i\t%i\t%i\t%f\t%i\t%i\t%s\n' %(thisStim['blockNo'],thisStim['stimNo'],
                                    24,thisStim['dwellTime'],0,thisStim['stimRep'],thisStim['stimName']))
        for row in range(0,24):
            dataFile.write('%i' %((row+1))) ## write row number at start of row
            for col in range(0,6):
                dataFile.write('\t%i' %(thisStim['stim'][row][col]))
            dataFile.write('\n') ## new line at end of row
        dataFile.write('\n') ##blank line between stimuli
    # -------
    
    dataFile.close

def time_to_frames(t):
    """ Convert time in milliseconds ("t") to number of 4.35ms frames of the 
    Optacon. If t is not divisible by 4.35, this function includes the last 
    frame to ensure that the actual running time is at least as long as t.
    Maximum actual running time is up to t + 4.35ms.
    """
    return int(ceil(t/4.35))

def map_apparent_motion(presDur=1000,stepDur=50,isoi=82):
    """ This functions makes an temporal "map" of the timing of apparent motion steps, 
        in the form of an array. Rows are frames, columns are step numbers. 
        
        presDur:    total presentation time for a single apparent motion stimulus trial
        stepDur:    the duration of each step of apparent motion
        isoi:        the time from the start of one step to the start of the next
        
        The array returned provides information about which step is "on" at any given frame (4.35ms).
        For example, at the start, the first step should be on, so stimMap[0,0] = 1. After a number 
        of frames determined by the isoi, the second step should be on, stimMap[isoiFrames,1] = 1.
        
        Note that this map does not provide any information about which pins in the array are on.
        The first step represents whichever optacon configuration is determined to be the starting
        configuration by the functions get_start_rows() and the input parameters for 
        apparent_motion_stim_sideways().
    """
    trialFrames = time_to_frames(presDur)
    onFrames = time_to_frames(stepDur)
    isoiFrames = time_to_frames(isoi)
    # number of steps that will start - if not enough time in presDur, last one won't be as long
    if isoiFrames == 0:
        sys.exit('cannot create stimulus with isoi = 0')
    else:
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