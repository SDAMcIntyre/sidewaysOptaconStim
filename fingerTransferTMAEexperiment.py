from noiseStaircaseHelpers import printStaircase, toStaircase, outOfStaircase, plotDataAndPsychometricCurve
from fingerTransferTMAEfunctions import stim_set
from psychopy import data, visual, event, core
from math import ceil
import serial, csv, numpy, random, pylab

setup = True

# create/locate stimulus files
exptFolder = r'./fingerTransferTest/'
exptName = 'unadapted'
threshCriterion = 0.5
standardValue = 82
prefaceValues = [60,69,78,87,95,104] #comparison ISOIs that will be presented before the staircase
prefaceStaircaseTrialsN = 2
staircaseTrialsN=10
comparisonValues = [17,21,26,30,34,39,43,47,52,56,60,65,69,73,78,82,87,91,95,100,104,108,113,117,
                                121,126,130,134,139,143,147,152,156,160,165,169,174,178,182,187,191,195,200,204,
                                -17,-21,-26,-30,-34,-39,-43,-47,-52,-56,-60,-65,-69,-73,-78,-82,-87,-91,-95,-100,-104,
                                -108,-113,-117,-121,-126,-130,-134,-139,-143,-147,-152,-156,-160,-165,-169,-174,-178,
                                -182,-187,-191,-195,-200,-204]
if setup == True:
    stim_set(presentationTime = 3000, stepDuration = [50,50], 
                        standard = -standardValue, comparison = comparisonValues, #negative standard so positive means proximal motion and negative means distal (not the reverse)
                        exptFolder = exptFolder, exptName = exptName, nReps =1) #pauseTime = 1000, 
    print 'created files in folder \"'+exptFolder+'\":\n'+exptName+'_stimList.dlm\n'+exptName+'_protocol.txt'
    core.quit()

# read in stimulus file information
stimFile = exptFolder+exptName+'_stimList.dlm'
with open(stimFile) as file_object:
    stimList = list(csv.DictReader(file_object, dialect='excel-tab'))
isoiValues = []
blockNs = []
for stim in stimList:
    isoiValues += [-float(stim['isoi'])] #take the negative so positive means proximal motion and negative means distal (not the reverse)
    blockNs += [float(stim['blockNo_raw'])]
isoiValues = numpy.array(isoiValues)
blockNs = numpy.array(blockNs)

# set up staircase
staircase = data.QuestHandler(startVal = 82, 
                      startValSd = 12,
                      stopInterval= None, #6, #sd of posterior has to be this small or smaller for staircase to stop, unless nTrials reached
                      nTrials=staircaseTrialsN,
                      #extraInfo = thisInfo,
                      pThreshold = threshCriterion,
                      gamma = 0, #y value at floor of the function, 0 for PSE type experiment
                      delta=0.01, #lapse rate, I suppose for Weibull function fit
                      grain = 4,
                      range = 286, # if left at "None", seems to be set to 5, which is too small
                      method = 'quantile', #uses the median of the posterior as the final answer
                      stepType = 'lin',  #will home in on the 80% threshold. But stepType = 'log' doesn't usually work
                      minVal=min(comparisonValues), maxVal = max(comparisonValues)
                      )

expStop = False
doingStaircasePhase = False #First phase of experiment is method of constant stimuli. If use naked QUEST, might converge too soon
prefaceStaircaseTrials = random.sample(prefaceValues, len(prefaceValues))
respEachTrial = list() #only needed for initialNonstaircaseTrials
overallTrialN = -1

if prefaceStaircaseTrialsN > len(prefaceStaircaseTrials): #repeat array to accommodate desired number of easyStarterTrials
    prefaceStaircaseTrials = numpy.tile( prefaceStaircaseTrials, ceil( prefaceStaircaseTrialsN/len(prefaceStaircaseTrials) ) )
prefaceStaircaseTrials = prefaceStaircaseTrials[0:prefaceStaircaseTrialsN]

staircaseTrialN = -1; mainStaircaseGoing = False

# define serial port to optacon computer
optacon=serial.Serial("/dev/tty.KeySerial1",9600,timeout=1)
optacon.read(100) #clear any existing messages

# keypress labels
pedal = ['a','c']
response = ['left','right']
quitkeys = ['escape','esc']

# define window that everything appears in
win = visual.Window(size=(1152, 870), fullscr=True, screen=1, allowGUI=False, allowStencil=False,
    monitor='testMonitor', color=[-1,-1,-1], colorSpace='rgb',
    blendMode='avg', useFBO=True,
    )

# define the patch of white screen to trigger the light sensor
triggerPosition = [-11, 8]
triggerSensorOn = visual.Rect(win=win, name='polygon',units='cm', 
    width=[1, 1][0], height=[1, 1][1],
    ori=0, pos=triggerPosition,
    lineWidth=1, lineColor=[1,1,1], lineColorSpace='rgb',
    fillColor=[1,1,1], fillColorSpace='rgb',
    opacity=1,interpolate=True)
    
# start message
msg = visual.TextStim(win, text='Waiting for the experiment to start...\n<esc> to quit')
msg.draw()
win.flip()
optaconStatus = ''
# wait until optacon protocol has been started
while not optaconStatus == 'READY':
    optaconStatus = optacon.read(size=5)
    print optaconStatus
    keyPressed = event.getKeys(keyList=quitkeys)
    if any(keyPressed):
        print 'user aborted'
        core.quit()
            

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
            print '\nSuggested value = '+str(suggested)
            comparisonISOI = isoiValues[min(abs(suggested - isoiValues)) == abs(suggested - isoiValues)][0] #closest value to the suggested one that we have
            blockNo = int(blockNs[min(abs(suggested - isoiValues)) == abs(suggested - isoiValues)][0])
            overallTrialN += 1
        except StopIteration: #Need this here, even though test for finished above. I can't understand why finished test doesn't accomplish this.
            print('\n\nStopping because staircase.next() returned a StopIteration, which it does when it is finished')
            staircase.finished = True
            break #break out of the trials loop
    print '\noverallTrialN='+str(overallTrialN)+ '   comparison ISOI for this trial = '+ str(round(comparisonISOI,2))+"    Block number: "+str(blockNo)
    
    keyPressed = ['']
    
    # tell optacon what the next stimulus is
    msg = visual.TextStim(win, text='Loading next stimulus...')
    msg.draw()
    win.flip()
    optacon.write("b"+str(blockNo))
    
    # wait until optacon confirms next stimulus was received
    while not any(keyPressed) and not optaconStatus == "OK":
        optaconStatus = optacon.read(size=2)
        print optaconStatus
        keyPressed = event.getKeys(keyList=quitkeys)
    if any(keyPressed):
        print 'user aborted'
        expStop=True
        break
        
    if expStop == False:
        # use light to trigger stimulus presentation
        core.wait(1.2)
        msg = visual.TextStim(win, text='\n<esc> to quit')
        msg.draw()
        triggerSensorOn.setAutoDraw(True)
        triggerClockOn = core.Clock()
        while triggerClockOn.getTime()<0.01:
            win.flip()
        print 'stimulus triggered'
        triggerSensorOn.setAutoDraw(False)
        win.flip()
        
        # wait until optacon has finished presenting the stimulus
        while not optaconStatus == 'READY':
            optaconStatus = optacon.read(size=5)
            print optaconStatus
            keyPressed = event.getKeys(keyList=quitkeys)
            if any(keyPressed):
                print 'user aborted'
                expStop=True
                break
        
    if expStop == False:
        # prompt user to make a response
        msg = visual.TextStim(win, text='Which stimulus feels more proximal (less distal)?\n( LEFT / RIGHT )')
        msg.draw()
        win.flip()
        while not any(keyPressed):
            keyPressed = event.waitKeys(keyList=pedal+quitkeys)
        if keyPressed[0] in quitkeys:
            print 'user aborted'
            expStop = True
        msg = visual.TextStim(win, text='\n<esc> to quit')
        msg.draw()
        win.flip()
        
    if expStop == False:
        # label the response
        thisPedal = response[pedal.index(keyPressed[0])]
        if thisPedal == comparisonLocation:
            thisResp = 1
        else:
            thisResp = 0
        print 'pedal pressed: '+str(thisPedal)+', comparison location: '+str(comparisonLocation)
    
        # record the response and the ISOI used
        respEachTrial.append(thisResp)
        if overallTrialN >= len(prefaceStaircaseTrials): #if doing staircase trials now
            staircase.addResponse(thisResp, intensity = comparisonISOI)
            print 'Have added an intensity of ' + str(comparisonISOI)

if overallTrialN+1 < len(prefaceStaircaseTrials) and (overallTrialN>=0): #exp stopped before got through staircase preface trials
    #add these non-staircase trials so QUEST knows about them
    print 'Importing '+str(respEachTrial)+' and intensities '+str(prefaceStaircaseTrials[0:len(respEachTrial)])+'\n\n'
    staircase.importData( toStaircase(prefaceStaircaseTrials[0:len(respEachTrial)],False), numpy.array(respEachTrial)) 
print 'Finished experiment.'

if staircase.finished:
    print 'Staircase completed.'
else:
    print 'Staircase did not complete.'

print('Median of posterior distribution according to QUEST, ISOI= {:.4f}'.format(staircase.quantile())) 

#fit curve
fit = None
try: 
    fit = data.FitWeibull(staircase.intensities, staircase.data, expectedMin=0,  sems = 1.0/len(staircase.intensities))
except:
    print("Fit failed.")
plotDataAndPsychometricCurve(staircase,fit,False,threshCriterion)
#save figure to file
outputFile =  exptFolder+exptName+'_plot'
pylab.savefig(outputFile + '.pdf')
pylab.savefig(outputFile + '.jpg')
pylab.show() #must call this to actually show plot

# save data
staircase.saveAsText(exptFolder+exptName+'_data')
print 'created file in folder \"'+exptFolder+'\":\n'+exptName+'_data.dlm\n'
printStaircase(staircase, False, briefTrialUpdate=False, printInternalVal=False,  alsoLog=False)

msg = visual.TextStim(win, text='The experiment is finished.\nPress <esc> to quit.')
msg.draw()
win.flip()
while keyPressed[0] not in quitkeys:
    keyPressed = event.waitKeys()
win.close()
