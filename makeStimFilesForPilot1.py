# -*- coding: utf-8 -*-
"""
Created on Wed Nov  12 14:33:59 2014

# To do:
    ## in progress function to generate full experiment set of motion stimuli:
            # assigning blockNo
            # assigning signal pin code
            # account for trials with no adapting stimulus
    
# New in this version:
    ## script almost generates full experiment set of motion stimuli:
            # assigns stimulus name
            # pairs adapting and test stimuli
            # includes pause and response period
    ## make lead time in write_optacon_protocol_file() a separate block

@author: sarahmcintyre
"""

from optacon import *
from optaconSideways import *
from psychopy import data
import numpy

zeros = numpy.zeros

presentationTime = 3000
pauseTime = 500
responseTime = 2000

exptFolder = r'./pilot1' 
if not os.path.exists(exptFolder): 
    os.makedirs(exptFolder)

stimCombinations = []
for standardLocation in ['left','right']:        
    for adaptStndComp in [[-82,82],[82,-82]]:
        for testStandard in [-82,82]:
            for testComparison in [-104,-82,-60,-39,-17,0,17,39,60,82,104]:
                stimCombinations.append(
                {'adaptStandard':adaptStndComp[0], 
                 'adaptComparison':adaptStndComp[1],
                'testStandard':testStandard,
                'testComparison':testComparison,
                'standardLocation':standardLocation}
                )

trials = data.TrialHandler(stimCombinations,nReps=1)

stimList = []
repList = []
nameList = []
blockList = []

blockNo = 1
for thisTrial in trials:
    
    blockNo += 1 #starts at 2 because 1 is reserved for lead time
    
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
    adaptStim, adaptRep = single_optacon_presentation(presDur=presentationTime,isoi=[abs(adaptLeft),abs(adaptRight)],stepVector=[sign(adaptLeft),sign(adaptRight)])
    adaptName = ['adapt_STDLOC'+str(thisTrial['standardLocation'])+'_STDISOI'+str(thisTrial['adaptStandard'])+'_CMPISOI'+str(thisTrial['adaptComparison'])]
    adaptName = adaptName*len(adaptStim)
    
    #pause
    pauseStim = zeros([24,6],int)
    pauseRep = [time_to_frames(pauseTime)]
    pauseName = ['pause']
    
    #test stimulus
    testStim, testRep = single_optacon_presentation(presDur=presentationTime,isoi=[abs(testLeft),abs(testRight)],stepVector=[sign(testLeft),sign(testRight)])
    testName = ['test_STDLOC'+str(thisTrial['standardLocation'])+'_STDISOI'+str(thisTrial['testStandard'])+'_CMPISOI'+str(thisTrial['testComparison'])]
    testName = testName*len(testStim)
    
    #response
    respStim = zeros([24,6],int)
    respRep = [time_to_frames(responseTime)]
    respName = ['response']
    
    stimList.append(adaptStim)
    stimList.append(pauseStim)
    stimList.append(testStim)
    stimList.append(respStim)
    
    repList.append(adaptRep)
    repList.append(pauseRep)
    repList.append(testRep)
    repList.append(respRep)

    nameList.append(adaptName)
    nameList.append(pauseName)
    nameList.append(testName)
    nameList.append(respName)
    
    #BLOCK LIST IS NOT LONG ENOUGH, SO CALL TO write_optacon_protocol_file() FAILS
    blockList.append([blockNo] * (len(adaptStim) + len(pauseStim) + len(testStim) + len(respStim)) )
    

write_optacon_protocol_file(fileName=exptFolder+'/pilot1_protocols_SM',stimList=stimList,stimRep=repList,blockList=blockList,stimName=nameList)
