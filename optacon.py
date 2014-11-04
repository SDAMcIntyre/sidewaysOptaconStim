# -*- coding: utf-8 -*-
"""
Created on Tue Nov  4 16:26:33 2014

@author: sarahmcintyre
"""
import numpy
import sys
import math

zeros = numpy.zeros
ceil = math.ceil


def write_optacon_protocol_file(fileName,stimList,stimRep=[1],dwellTime=[4.35],leadTime=2000,stimName=[],
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
     
    # add blank stim to start of stim list
    stimListPlusLead = []
    stimListPlusLead += [zeros([24,6],int)]
    stimListPlusLead += stimList
    
    # quality control
    if len(stimRep)==1:
        stimRep = stimRep*len(stimList)
    # add rep for blank stim at start of stim list
    stimRepPlusLead =[]
    stimRepPlusLead += [int(ceil(leadTime/dwellTime[0]))]
    stimRepPlusLead += stimRep
    if len(dwellTime)==1:
        dwellTime = dwellTime*len(stimListPlusLead)
    if len(stimName)==0:
        stimName = [' ']*len(stimListPlusLead)
    stimName[0] = 'lead time'
    if (len(stimListPlusLead)==len(dwellTime)==len(stimRepPlusLead)==len(stimName)) == False: #currently if user provides their own list this won't work because of the blank stim added at the start
        sys.exit('stimulus lists must have equal length')
    # ----------------
    
    # combine all lists into master list
    masterStimList=[]
    for i in range(len(stimListPlusLead)):
        masterStimList.append({'stim':stimListPlusLead[i], 'stimNo':i+1, 
                                    'dwellTime':dwellTime[i],'stimRep':stimRepPlusLead[i], 'stimName':stimName[i]})
    #-----------------
    
    # write header
    dataFile = open(fileName+'.txt', 'w')
    dataFile.write('This is an "Optacon Stimulator" Data File.\nFile Format\t1\n' 
                                        'nBlocks\t1\n')
    dataFile.write('Spare Line\nSpare Line\nSpare Line\nSpare Line\nSpare Line\n')
    dataFile.write('Pin Sync\t'+"\t".join("%s" %pin for pin in readPins)+'\n\n')
    # ------------
    
    # write blocks
    dataFile.write('Block No\t nStimuli\t nPresentations\n')
    dataFile.write('%i\t%i\t%i\n'%(1,len(stimListPlusLead),1))
    dataFile.write('\n') ## blank line between block description and stimuli
    # ------
    
    # stimuli
    for thisStim in masterStimList:
        dataFile.write('Row No\tBlock No\tStim No\tnRows\tDwell ms\tType\tnPresentations\tName\n')
        dataFile.write('\t%i\t%i\t%i\t%f\t%i\t%i\t%s\n' %(1,thisStim['stimNo'],
                                    24,thisStim['dwellTime'],0,thisStim['stimRep'],thisStim['stimName']))
        for row in range(0,24):
            dataFile.write('%i' %((row+1))) ## write row number at start of row
            for col in range(0,6):
                dataFile.write('\t%i' %(thisStim['stim'][row][col]))
            dataFile.write('\n') ## new line at end of row
        dataFile.write('\n') ##blank line between stimuli
    # -------
    
    dataFile.close