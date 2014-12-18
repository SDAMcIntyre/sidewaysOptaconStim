from noiseStaircaseHelpers import printStaircase, toStaircase
import serial
from psychopy import data, visual, event, core
import csv
import numpy
from math import ceil
import random
print('after import')

exptFolder = r'./questDemo/'

stim_set(presentationTime = 3000, stepDuration = [50,50], pauseTime = 1000, responseTime = 1000, nReps =1, 
                        standard = 82, comparison = [-104,-82,-60,-39,-17,17,39,60,82,104], exptFolder = r'./questDemo')

stimFile = '/Users/sarahmcintyre/ownCloud/Optacon Expts Sarah/Expt4_OptaconFingerTransferTMAE/sidewaysOptaconStim/questDemo/questDemo_stimList.dlm'
with open(stimFile) as file_object:
    stimList = list(csv.DictReader(file_object, dialect='excel-tab'))

isoiValues = []
blockNs = []
for stim in stimList:
    isoiValues += [float(stim['isoi'])]
    blockNs += [float(stim['blockNo_raw'])]
isoiValues = numpy.array(isoiValues)
blockNs = numpy.array(blockNs)
prefaceValues = [-104,-82,-60,-39,-17,17,39,60,82,104]

optacon=serial.Serial("/dev/tty.KeySerial1",9600,timeout=1)
optacon.read(100) #check if there's a better way to clear optacon.read

pedal = ['a','c']
response = ['left','right']
quitkeys = ['escape','esc']
comparisonLocation = 'right'
threshCriterion = 0.5

staircase = data.QuestHandler(startVal = 82, 
                      startValSd = 150,
                      stopInterval= None, #6, #sd of posterior has to be this small or smaller for staircase to stop, unless nTrials reached
                      nTrials=20,
                      #extraInfo = thisInfo,
                      pThreshold = threshCriterion,
                      gamma = 0, #y value at floor of the function, 0 for PSE type experiment
                      delta=0.01, #lapse rate, I suppose for Weibull function fit
                      method = 'quantile', #uses the median of the posterior as the final answer
                      stepType = 'lin',  #will home in on the 80% threshold. But stepType = 'log' doesn't usually work
                      minVal=min(isoiValues), maxVal = max(isoiValues)
                      )

expStop = False
doingStaircasePhase = False #First phase of experiment is method of constant stimuli. If use naked QUEST, might converge too soon
prefaceStaircaseTrialsN = 5
prefaceStaircaseTrials = random.sample(prefaceValues, len(prefaceValues))
respEachTrial = list() #only needed for initialNonstaircaseTrials
overallTrialN = -1

if prefaceStaircaseTrialsN > len(prefaceStaircaseTrials): #repeat array to accommodate desired number of easyStarterTrials
    prefaceStaircaseTrials = numpy.tile( prefaceStaircaseTrials, ceil( prefaceStaircaseTrialsN/len(prefaceStaircaseTrials) ) )
prefaceStaircaseTrials = prefaceStaircaseTrials[0:prefaceStaircaseTrialsN]

staircaseTrialN = -1; mainStaircaseGoing = False

win = visual.Window([1366, 768],fullscr=True) #[1680, 1050]
msg = visual.TextStim(win, text='Start the Optacon protocol...\n<esc> to quit')
msg.draw()
win.flip()
optaconStatus = ''

while (not staircase.finished) and expStop==False:
    
    # first select the comparison ISOI for this trial, either from preface values or staircase
    if overallTrialN+1 < len(prefaceStaircaseTrials): #still doing prefaceStaircaseTrials
        overallTrialN += 1
        comparisonISOI = prefaceStaircaseTrials[overallTrialN]
        blockNo = int(blockNs[isoiValues == comparisonISOI][0])
    else:
        if overallTrialN+1 == len(prefaceStaircaseTrials): #add these non-staircase trials so QUEST knows about them
            print('Importing ',respEachTrial,' and intensities ',repr(prefaceStaircaseTrials))
            staircase.importData( prefaceStaircaseTrials, numpy.array(respEachTrial)) 
        try: #advance the staircase
            suggested = staircase.next() #staircase suggests the next value
            comparisonISOI = isoiValues[min(abs(suggested - isoiValues)) == abs(suggested - isoiValues)][0] #closest value to the suggested one that we have
            blockNo = int(blockNs[min(abs(suggested - isoiValues)) == abs(suggested - isoiValues)][0])
            overallTrialN += 1
        except StopIteration: #Need this here, even though test for finished above. I can't understand why finished test doesn't accomplish this.
            print('stopping because staircase.next() returned a StopIteration, which it does when it is finished')
            staircase.finished = True
            break #break out of the trials loop
    print('overallTrialN=',overallTrialN, '   comparison ISOI for this trial = ', round(comparisonISOI,2)) #debugON
    
    # next, present the stimulus and get a response
    keyPressed = ['']
    while not any(keyPressed) and not optaconStatus == 'READY':
        optaconStatus = optacon.read(size=5)
        keyPressed = event.getKeys(keyList=quitkeys)
    
    optacon.write("b"+str(blockNo))
    print("Block number: ",blockNo)
    msg = visual.TextStim(win, text='Sending next stimulus to Optacon\n<esc> to quit')
    msg.draw()
    win.flip()
    while not any(keyPressed) and not optaconStatus == "OK":
        optaconStatus = optacon.read(size=2)
        keyPressed = event.getKeys(keyList=quitkeys)
    
    # ###
    # trigger optacon with light #
    # ###
    core.wait(0.5)
    msg = visual.TextStim(win, text='Press button for tactile stimulus...\n<esc> to quit')
    msg.draw()
    win.flip()
    
    core.wait(2)
    msg = visual.TextStim(win, text='Which stimulus feels more proximal (less distal)? (L/R)\n<esc> to quit')
    msg.draw()
    win.flip()
    while not any(keyPressed):
        keyPressed = event.waitKeys(keyList=pedal+quitkeys)
        
    if keyPressed[0] in quitkeys:
        print('user aborted')
        expStop = True
    else:
        thisPedal = response[pedal.index(keyPressed[0])]
        print thisPedal
        if thisPedal == comparisonLocation:
            thisResp = 1
        else:
            thisResp = 0
    
        # finally, record the response and the ISOI used
        respEachTrial.append(thisResp)
        if overallTrialN >= len(prefaceStaircaseTrials): #doing staircase trials now
            staircase.addResponse(thisResp, intensity = comparisonISOI)
            print('Have added an intensity of ',comparisonISOI)

if overallTrialN+1 < len(prefaceStaircaseTrials) and (overallTrialN>=0): #exp stopped before got through staircase preface trials
    #add these non-staircase trials so QUEST knows about them
    print('Importing ',respEachTrial,' and intensities ',prefaceStaircaseTrials)
    staircase.importData( toStaircase(prefaceStaircaseTrials[0:overallTrialN+1],False), numpy.array(respEachTrial)) 
print('Finished experiment.')

if staircase.finished:
    print('Staircase was finished')
    msg = visual.TextStim(win, text='Stop the Optacon protocol...\n<esc> to quit')
    msg.draw()
    win.flip()
    while keyPressed[0] not in quitkeys:
        keyPressed = event.waitKeys()
else:
    print('Staircase was not finished')

print('Median of posterior distribution according to QUEST, ISOI= {:.4f}'.format(staircase.quantile())) 

win.close()
staircase.saveAsText(exptFolder+'/questDemo_data')
printStaircase(staircase, False, briefTrialUpdate=True, printInternalVal=True,  alsoLog=False)
