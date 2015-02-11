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

def stim_set(presentationTime, stepDuration, standard, comparison, exptFolder, exptName, nReps=1):
    
    standard = [standard, -standard]
    comparison+=[x*-1 for x in comparison]
    
    if not os.path.exists(exptFolder): 
        os.makedirs(exptFolder)
    
    stimCombinations = [{'compISOI':compISOI, 'stndISOI':stndISOI, 'standardPosition':standardPosition} for 
                                        compISOI in comparison for stndISOI in standard for standardPosition in ['left','right']]
    
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
        
        stndName = 'STNDISOI_'+str(thisTrial['stndISOI'])
        compName = 'COMPISOI_'+str(thisTrial['compISOI'])
        
        isoiLR = [0,0]
        stepVectorLR = [0,0]
        if thisTrial['standardPosition'] == 'left':
            stndPos = 0
            compPos = 1
            name = [stndName+'_'+compName]
        else:
            stndPos = 1
            compPos = 0
            name = [compName+'_'+stndName]
            
        isoiLR[stndPos] = abs(thisTrial['stndISOI'])
        isoiLR[compPos] = abs(thisTrial['compISOI'])
        stepVectorLR[stndPos] = sign(thisTrial['stndISOI'])
        stepVectorLR[compPos] = sign(thisTrial['compISOI'])
        
        stim, rep = single_presentation(presDur=presentationTime,
                                                                            stepDur=stepDuration,
                                                                            isoi = isoiLR,
                                                                            rowsToUse=range(0,6), #assumes Optacon is sideways
                                                                            colsToUse=[range(18,24),range(0,6)], #first is left, second is right; depends on Optacon orientation in eperiment
                                                                            stepVector = stepVectorLR, 
                                                                            randomPos=[False,False], spread=[True,True]
                                                                            )
        
        name = name*len(stim)
        
        stimList += stim
        repList += rep
        nameList += name
        blockList += [blockNo] * (len(stim))
        
    trials.saveAsText(fileName=exptFolder+exptName+'_stimList', 
                                    stimOut=['compISOI','stndISOI','standardPosition'], 
                                    dataOut=['blockNo_raw'],
                                    appendFile=False)

    optacon.write_protocol_file(fileName=exptFolder+exptName+'_protocol',
                                    stimList=stimList,
                                    stimRep=repList,
                                    blockList=blockList,
                                    stimName=nameList)

    print 'created files in folder \"'+exptFolder+'\":\n'+exptName+'_stimList.dlm\n'+exptName+'_protocol.txt'