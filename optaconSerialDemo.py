import serial
from psychopy import data, visual, event, core

# serial port name depends on the computer 
# To check for serial ports available on Mac OS, in Terminal app, type "ls /dev/tty.*"
# make sure driver is installed (http://www.tripplite.com/high-speed-usb-to-serial-adapter-keyspan~USA19HS/)
optaconSerialPortName = "/dev/tty.KeySerial1"

# define serial port to optacon computer
optacon=serial.Serial(optaconSerialPortName,9600,timeout=1)
optacon.read(100) #clear any existing messages

# set up stimuli
blocksToUse = range(2,5) # start at 2 because the first block should be blank (it is always played at the beginning)
nRepeats = 2
stimList = [{'blockNo':blockNo} for blockNo in blocksToUse] 
trials = data.TrialHandler(stimList, nRepeats)
trials.data.addDataType('repsonse')

pedal = ['a','c']
response = ['left','right']
quitkeys = ['escape','esc']

# define window that everything appears in
win = visual.Window(size=(1152, 870), fullscr=True, screen=0, allowGUI=False, allowStencil=False,
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
    
msg = visual.TextStim(win, text='Make sure you have loaded an Optacon protocol with at least %i blocks.\n\nThen click \"Go" on the Optacon protocol...\n\n<esc> to quit'%(max(blocksToUse)))
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
            
for thisTrial in trials:
    keyPressed = ['']
    
    # tell optacon what the next stimulus is
    msg = visual.TextStim(win, text='Loading next stimulus...\n<esc> to quit')
    msg.draw()
    win.flip()
    optacon.write("b"+str(thisTrial['blockNo']))
    print thisTrial['blockNo']
    
    # wait until optacon confirms next stimulus was received
    while not any(keyPressed) and not optaconStatus == "OK":
        optaconStatus = optacon.read(size=2)
        print optaconStatus
        keyPressed = event.getKeys(keyList=quitkeys)
    if any(keyPressed):
        print 'user aborted'
        core.quit()
        
    # use light to trigger stimulus presentation
    core.wait(1.2)
    msg = visual.TextStim(win, text='\n<esc> to quit')
    msg.draw()
    triggerSensorOn.setAutoDraw(True)
    triggerClockOn = core.Clock()
    while triggerClockOn.getTime()<0.01:
        win.flip()
    print triggerClockOn.getTime()
    triggerSensorOn.setAutoDraw(False)
    win.flip()
    
    # wait until optacon has finished presenting the stimulus
    while not optaconStatus == 'READY':
        optaconStatus = optacon.read(size=5)
        print optaconStatus
        keyPressed = event.getKeys(keyList=quitkeys)
        if any(keyPressed):
            print 'user aborted'
            core.quit()
    
    # prompt user to make a response
    msg = visual.TextStim(win, text='Which stimulus ...? (L/R)\n<esc> to quit')
    msg.draw()
    win.flip()
    while not any(keyPressed):
        keyPressed = event.waitKeys(keyList=pedal+quitkeys)
    if keyPressed[0] in quitkeys:
        print 'user aborted'
        core.quit()
    msg = visual.TextStim(win, text='\n<esc> to quit')
    msg.draw()
    win.flip()
    
    thisResp = response[pedal.index(keyPressed[0])]
    print thisResp
    trials.data.add('response', thisResp)
    
    
print '\n'
trials.printAsText(stimOut=['blockNo'], #write summary data to screen 
                  dataOut=['response_raw'])
trials.saveAsText(fileName='serialDemoData', # also write summary data to a text file
                  stimOut=['blockNo'], 
                  dataOut=['response_raw'])

msg = visual.TextStim(win, text='Click \"Stop" on the Optacon protocol...\n<esc> to quit')
msg.draw()
win.flip()
while keyPressed[0] not in quitkeys:
    keyPressed = event.waitKeys()
win.close()
