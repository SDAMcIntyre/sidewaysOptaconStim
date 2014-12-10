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

exptFolder = r'./pilot1' 
if not os.path.exists(exptFolder): 
    os.makedirs(exptFolder)

stimCombinations = [{'standardLocation':standardLocation,
    'adaptStandard':adaptStandard, 
    'adaptComparison':adaptComparison,
    'testStandard':testStandard,
    'testComparison':testComparison} for 
    standardLocation in ['left','right'] for 
    adaptStandard in [-82,82] for 
    adaptComparison in [-82,82] for 
    testStandard in [-82,82] for 
    testComparison in [-104,-82,-60,-39,-17,17,39,60,82,104] 
    if adaptStandard != adaptComparison]
stimCombinations.append({'standardLocation':'none', 'adaptStandard':'none', 'adaptComparison':'none', 'testStandard':'random', 'testComparison':'random'})

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
    
    #pause
    pauseStim = [zeros([24,6],int)]
    pauseRep = [optacon.time_to_frames(pauseTime)]
    pauseName = ['pause']
    
    if thisTrial['testStandard'] == 'random':
        testStim, testRep = single_presentation(presDur=presentationTime,
                                                                            stepDur=stepDuration,
                                                                            isoi=[82,82],
                                                                            randomPos=[True,True])
        testName = ['random']*len(testStim)
        
        stimList += testStim
        repList += testRep
        nameList += testName
        blockList += [blockNo] * (len(testStim))
        
    else:
        
        if thisTrial['standardLocation'] == 'left':
            adaptLeft = thisTrial['adaptStandard']
            adaptRight = thisTrial['adaptComparison']
            testLeft = thisTrial['testStandard']
            testRight = thisTrial['testComparison']
        else:
            adaptLeft = thisTrial['adaptComparison']
            adaptRight = thisTrial['adaptStandard']
            testLeft = thisTrial['testComparison']
            testRight = thisTrial['testStandard']
            
        #adapting stimulus
        adaptStim, adaptRep = single_presentation(presDur=presentationTime,
                                                                            stepDur=stepDuration,
                                                                            isoi=[abs(adaptLeft),abs(adaptRight)],
                                                                            stepVector=[sign(adaptLeft),sign(adaptRight)])
        adaptName = ['adapt_STDLOC'+str(thisTrial['standardLocation'])+'_STDISOI'+str(thisTrial['adaptStandard'])+'_CMPISOI'+str(thisTrial['adaptComparison'])]
        adaptName = adaptName*len(adaptStim)
        
        #test stimulus
        testStim, testRep = single_presentation(presDur=presentationTime,
                                                                            stepDur=stepDuration,
                                                                            isoi=[abs(testLeft),abs(testRight)],
                                                                            stepVector=[sign(testLeft),sign(testRight)])
        testName = ['test_STDLOC'+str(thisTrial['standardLocation'])+'_STDISOI'+str(thisTrial['testStandard'])+'_CMPISOI'+str(thisTrial['testComparison'])]
        testName = testName*len(testStim)
        
        stimList += adaptStim + pauseStim + testStim
        repList += adaptRep + pauseRep + testRep
        nameList += adaptName + pauseName + testName
        blockList += [blockNo] * (len(adaptStim) + len(pauseStim) + len(testStim))
    
trials.saveAsText(fileName=exptFolder+'/pilot1_stimList', 
                                stimOut=['adaptStandard','adaptComparison','testStandard','testComparison','standardLocation'], 
                                dataOut=['blockNo_raw'],
                                appendFile=False)

optacon.write_protocol_file(fileName=exptFolder+'/pilot1_protocol',
                                stimList=stimList,
                                stimRep=repList,
                                blockList=blockList,
                                stimName=nameList)
