from noiseStaircaseHelpers import printStaircase, toStaircase, outOfStaircase, plotDataAndPsychometricCurve
from fingerTransferTMAEfunctions import stim_set
from psychopy import data, visual, event, core
from math import ceil
import serial, csv, numpy, random, pylab, time

setup = False

# serial port name depends on the computer 
# To check for serial ports available on Mac OS, in Terminal app, type "ls /dev/tty.*"
# make sure driver is installed (http://www.tripplite.com/high-speed-usb-to-serial-adapter-keyspan~USA19HS/)
optaconSerialPortName = "/dev/tty.KeySerial1"

# create/locate stimulus files
exptFolder = r'./fingerTransferTest/'
exptName = 'pilot'
condition = 'unadapted'
participant = 'sarah'
threshCriterion = 0.5
standardValue = 82 # should be a positive value; direction is randomised
prefaceValues = [21,47,126,152] #comparison ISOIs that will be presented before the staircase
prefaceStaircaseTrialsN = 16
staircaseTrialsN=34
jitter = 22 #amount by which to jitter staircase suggestions
comparisonValues = [17,21,26,30,34,39,43,47,52,56,60,65,69,73,78,82,87,91,95,100,104,108,113,117,
                                121,126,130,134,139,143,147,152,156,160,165,169,174,178,182,187,191,195,200,204] 
                                #all possible ISOIs available to the staircase; be generous
                                # both directions for each ISOI are automatically created in the stim_set() function
if setup == True:
    stim_set(presentationTime = 3000, stepDuration = [50,50],
                        standard = standardValue, comparison = comparisonValues,
                        exptFolder = exptFolder, exptName = exptName, nReps =1)
    core.quit()

# read in stimulus file information
stimFile = exptFolder+exptName+'_stimList.dlm'
with open(stimFile) as file_object:
    stimList = list(csv.DictReader(file_object, dialect='excel-tab'))
isoiValues = []
blockNs = []
standardPositionValues = []
standardISOIvalues = []
for stim in stimList:
    isoiValues += [float(stim['compISOI'])]
    standardPositionValues += [stim['standardPosition']]
    standardISOIvalues += [float(stim['stndISOI'])]
    blockNs += [float(stim['blockNo_raw'])]
isoiValues = numpy.array(isoiValues)
standardPositionValues = numpy.array(standardPositionValues)
standardISOIvalues = numpy.array(standardISOIvalues)
blockNs = numpy.array(blockNs)

# set up staircase
staircase = data.QuestHandler(startVal = 82, 
                      startValSd = 40,
                      stopInterval= None, #6, #sd of posterior has to be this small or smaller for staircase to stop, unless nTrials reached
                      nTrials=staircaseTrialsN,
                      #extraInfo = thisInfo,
                      pThreshold = threshCriterion,
                      gamma = 0, #y value at floor of the function, 0 for PSE type experiment
                      delta=0.01, #lapse rate, I suppose for Weibull function fit
                      grain = 4,
                      range = 400, # if left at "None", seems to be set to 5, which is too small
                      method = 'quantile', #uses the median of the posterior as the final answer
                      stepType = 'lin',  #will home in on the 80% threshold. But stepType = 'log' doesn't usually work
                      minVal=min(comparisonValues), maxVal = max(comparisonValues)
                      )

expStop = False
doingStaircasePhase = False #First phase of experiment is method of constant stimuli. If use naked QUEST, might converge too soon
#prefaceStaircaseTrials = random.sample(prefaceValues, len(prefaceValues))
respEachTrial = list() #only needed for initialNonstaircaseTrials
overallTrialN = -1

prefaceStaircaseTrials = []
prefaceTrials = data.TrialHandler( prefaceValues, nReps = ceil(prefaceStaircaseTrialsN/float(len(prefaceValues))) )
for thisTrial in prefaceTrials:
    prefaceStaircaseTrials += [thisTrial]
prefaceStaircaseTrials = prefaceStaircaseTrials[0:prefaceStaircaseTrialsN]

staircaseTrialN = -1; mainStaircaseGoing = False

# define serial port to optacon computer
optacon=serial.Serial(optaconSerialPortName,9600,timeout=1)
optacon.read(100) #clear any existing messages

# keypress labels
pedal = ['a','c']
response = ['left','right']
quitkeys = ['escape','esc']

# define window that messages and light trigger appear in
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
            

#data file
dataFileName = exptName+'_'+participant+'_'+condition+'_data_'+time.strftime('%Y-%m-%d_%H%M%S')
dataFile = open(exptFolder+'rawData/'+dataFileName+'.txt', 'w')
dataFile.write('ISOI\tresponse\tthreshold\tdirection\tstndPosition\n')

while (not staircase.finished) and expStop==False:
    
    # first select the comparison ISOI for this trial, either from preface values or QUEST
    if overallTrialN+1 < len(prefaceStaircaseTrials): #if still doing prefaceStaircaseTrials
        overallTrialN += 1
        suggestedISOI = prefaceStaircaseTrials[overallTrialN]
    else: #QUEST trials
        if overallTrialN+1 == len(prefaceStaircaseTrials): 
            #add these preface trials so QUEST knows about them
            print('Importing ',respEachTrial,' and intensities ',repr(prefaceStaircaseTrials))
            staircase.importData(prefaceStaircaseTrials, 1-numpy.array(respEachTrial)) 
        try: #advance the staircase
            suggestedISOI = staircase.next() #staircase suggests the next value
            print '\nSuggested value = '+str(suggestedISOI)
            suggestedISOI = suggestedISOI + random.sample(range(jitter),1)[0]*random.sample([-1,1],1)[0]
            overallTrialN += 1
        except StopIteration: #Need this here, even though test for finished above. I can't understand why finished test doesn't accomplish this.
            print('\n\nStopping because staircase.next() returned a StopIteration, which it does when it is finished')
            staircase.finished = True
            break #break out of the trials loop
    
    direction = random.sample([-1,1],1)[0]
    staircase.addOtherData('direction', direction)
    
    #closest value to the suggested one that we have
    comparisonISOI = isoiValues[min(abs(suggestedISOI - isoiValues)) == abs(suggestedISOI - isoiValues)][0]
    
    standardISOI = standardValue*direction
    standardPosition = random.sample(['left','right'],1)[0]
    staircase.addOtherData('standardPosition', standardPosition)
    
    #find the block number for the stimulus
    iClosest = [i for i in range(len(isoiValues)) if 
            isoiValues[i] == comparisonISOI*direction and 
            standardISOIvalues[i] == standardISOI and
            standardPositionValues[i] == standardPosition]
    blockNo = int(blockNs[iClosest][0])
    print '\noverallTrialN='+str(overallTrialN)+ '   comparison ISOI for this trial = '+ str(round(comparisonISOI,2))+"    Block number: "+str(blockNo)
    
    keyPressed = ['']
    
    # tell optacon what the next stimulus is
    msg = visual.TextStim(win, text='Next stimulus...')
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
        triggerSensorOn.setAutoDraw(True)
        msg.draw()
        win.flip()
        print 'stimulus triggered'
        # wait until optacon has finished presenting the stimulus
        while not optaconStatus == 'READY':
            optaconStatus = optacon.read(size=5)
            print optaconStatus
            keyPressed = event.getKeys(keyList=quitkeys)
            if any(keyPressed):
                print 'user aborted'
                expStop=True
                break
        triggerSensorOn.setAutoDraw(False)
        win.flip()
        
    if expStop == False:
        # prompt user to make a response
        msg = visual.TextStim(win, text='Which stimulus feels more proximal (less distal)?\nLEFT / RIGHT\n\n\n'+
                                                                str(overallTrialN+1)+' of '+str(prefaceStaircaseTrialsN+staircaseTrialsN))
        msg.draw()
        win.flip()
        while not any(keyPressed):
            keyPressed = event.waitKeys(keyList=pedal+quitkeys)
        if keyPressed[0] in quitkeys:
            print 'user aborted'
            expStop = True
#        msg = visual.TextStim(win, text='')
#        msg.draw()
        win.flip()
        
    if expStop == False:
        # label the response
        thisPedal = response[pedal.index(keyPressed[0])]
        if (thisPedal == standardPosition and direction == 1) or (thisPedal != standardPosition and direction == -1):
            thisResp = 0
        else:
            thisResp = 1
        print 'pedal pressed: '+str(thisPedal)+', standard location: '+standardPosition+'; direction: '+str(direction)
    
        # record the response and the ISOI used
        respEachTrial.append(thisResp)
        if overallTrialN >= len(prefaceStaircaseTrials): #if doing staircase trials now
            staircase.addResponse(1-thisResp, intensity = comparisonISOI)
            print 'Have added an intensity of ' + str(comparisonISOI)

if overallTrialN+1 < len(prefaceStaircaseTrials) and (overallTrialN>=0): #exp stopped before got through staircase preface trials
    #add these non-staircase trials so QUEST knows about them
    print 'Importing '+str(respEachTrial)+' and intensities '+str(prefaceStaircaseTrials[0:len(respEachTrial)])+'\n\n'
    staircase.importData( toStaircase(prefaceStaircaseTrials[0:len(respEachTrial)],False), 1-numpy.array(respEachTrial)) 
print 'Finished experiment.'

if staircase.finished:
    print 'Staircase completed.'
else:
    print 'Staircase did not complete.'

print('Median of posterior distribution according to QUEST, ISOI= {:.4f}'.format(staircase.quantile())) 

# save data
staircase.saveAsPickle(exptFolder+'rawData/'+dataFileName)
for i in range(len(staircase.intensities)):
    dataFile.write( '%f\t%i\t%f\t%i\t%s\n' %(staircase.intensities[i], respEachTrial[i], staircase.quantile(), 
                                                        staircase.otherData['direction'][i], staircase.otherData['standardPosition'][i]) )
dataFile.write('\n')
dataFile.close()
print 'created file in folder \"'+exptFolder+'rawData/\":\n'+dataFileName+'.txt\n'

printStaircase(staircase, False, briefTrialUpdate=False, printInternalVal=False,  alsoLog=False)

msg = visual.TextStim(win, text='The experiment is finished.\nPress <esc> to quit.')
msg.draw()
win.flip()
while keyPressed[0] not in quitkeys:
    keyPressed = event.waitKeys()
win.close()

#fit curve
#fit = None
#try: 
#    fit = data.FitWeibull(staircase.intensities, staircase.data, expectedMin=0,  sems = 1.0/len(staircase.intensities))
#except:
#    print("Fit failed.")

#plotDataAndPsychometricCurve(staircase,fit,False,threshCriterion)
# save figure to file
#outputFile =  exptFolder+exptName+'_plot'
#pylab.savefig(outputFile + '.pdf')
#pylab.savefig(outputFile + '.jpg')
#pylab.show() #must call this to actually show plot
