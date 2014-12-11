# -*- coding: utf-8 -*-
"""
Created on Wed Nov  12 14:33:59 2014

@author: sarahmcintyre
"""

import optacon
import optaconSideways
from psychopy import data
import numpy
import os

single_presentation = optaconSideways.single_presentation
zeros = numpy.zeros
sign = numpy.sign

presentationTime = 3000
stepDuration = [50,50]
pauseTime = 1000
responseTime = 1000
nReps =1
standard = 82

exptFolder = r'./questDemo' 
if not os.path.exists(exptFolder): 
    os.makedirs(exptFolder)

stimCombinations = [{'isoi':isoi} for isoi in [-104,-82,-60,-39,-17,17,39,60,82,104]]

trials = data.TrialHandler(stimCombinations,nReps=nReps,method='sequential')
trials.data.addDataType('blockNo')

stimList = []
repList = []
nameList = []
blockList = []

blockNo = 1
for thisTrial in trials:
    
    blockNo += 1 #starts at 2 because 1 is reserved for lead time
    trials.data.add('blockNo', blockNo)
    
    stim, rep = single_presentation(presDur=presentationTime,
                                                                        stepDur=stepDuration,
                                                                        isoi = [ abs(standard), abs(thisTrial['isoi']) ],
                                                                        stepVector = [ sign(standard), sign(thisTrial['isoi']) ]
                                                                        )
    name = ['STDISOI'+str(standard)+'_CMPISOI'+str(thisTrial['isoi'])]
    name = name*len(stim)
    
    stimList += stim
    repList += rep
    nameList += name
    blockList += [blockNo] * (len(stim))
    
trials.saveAsText(fileName=exptFolder+'/questDemo_stimList', 
                                stimOut=['isoi'], 
                                dataOut=['blockNo_raw'],
                                appendFile=False)

optacon.write_protocol_file(fileName=exptFolder+'/questDemo_protocol',
                                stimList=stimList,
                                stimRep=repList,
                                blockList=blockList,
                                stimName=nameList)
