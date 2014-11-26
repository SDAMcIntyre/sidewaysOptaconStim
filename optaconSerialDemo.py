import serial
from psychopy import data, visual, event, core

optacon=serial.Serial("/dev/tty.KeySerial1",9600,timeout=1)
optacon.read(100) #check if there's a better way to clear optacon.read

stimList = [{'blockNo':blockNo} for blockNo in range(2,5)] 
trials = data.TrialHandler(stimList,2)
trials.data.addDataType('repsonse')

pedal = ['a','c']
response = ['left','right']
quitkeys = ['escape','esc']

win = visual.Window([1366, 768],fullscr=True) #[600,400]
msg = visual.TextStim(win, text='Start the Optacon protocol...\n<esc> to quit')
msg.draw()
win.flip()

nDone = 0
optaconStatus = ''
for thisTrial in trials:
    keyPressed = ['']
    while not any(keyPressed) and not optaconStatus == 'READY':
        optaconStatus = optacon.read(size=5)
        keyPressed = event.getKeys(keyList=quitkeys)
    print optaconStatus
    
    optacon.write("b"+str(thisTrial['blockNo']))
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
    msg = visual.TextStim(win, text='Presenting stimulus...\n<esc> to quit')
    msg.draw()
    win.flip()
    
    core.wait(2)
    msg = visual.TextStim(win, text='Which stimulus ...? (L/R)\n<esc> to quit')
    msg.draw()
    win.flip()
    while not any(keyPressed):
        keyPressed = event.waitKeys(keyList=pedal+quitkeys)
        
    if keyPressed[0] in quitkeys:
        core.quit('user aborted')
    
    thisResp = response[pedal.index(keyPressed[0])]
    print thisResp
    trials.data.add('response', thisResp)
    nDone +=1
    
    
print '\n'
trials.printAsText(stimOut=['blockNo'], #write summary data to screen 
                  dataOut=['response_raw'])
trials.saveAsText(fileName='serialDemoData', # also write summary data to a text file
                  stimOut=['blockNo'], 
                  dataOut=['response_raw'])

msg = visual.TextStim(win, text='Stop the Optacon protocol...\n<esc> to quit')
msg.draw()
win.flip()
while keyPressed[0] not in quitkeys:
    keyPressed = event.waitKeys()
