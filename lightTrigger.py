from psychopy import visual, core, event

win = visual.Window(size=(1152, 870), fullscr=True, screen=1, allowGUI=False, allowStencil=False,
    monitor='testMonitor', color=[-1,-1,-1], colorSpace='rgb',
    blendMode='avg', useFBO=True,
    )
triggerPosition = [-11, 8]

triggerSensorOn = visual.Rect(win=win, name='polygon',units='cm', 
    width=[8, 8][0], height=[8, 8][1],
    ori=0, pos=triggerPosition,
    lineWidth=1, lineColor=[1,1,1], lineColorSpace='rgb',
    fillColor=[1,1,1], fillColorSpace='rgb',
    opacity=1,interpolate=True)

lightkeys = ['l','L']
quitkeys = ['q','Q']
userQuit = False
while not userQuit:
    keyPressed = ['']
    msg = visual.TextStim(win, text='Press L key to trigger the light sensor. Press Q to escape')
    msg.draw()
    win.flip()
    while not any(keyPressed):
        keyPressed = event.getKeys(keyList=lightkeys+quitkeys)
    
    if keyPressed[0] in quitkeys:
        userQuit = True
    
    if keyPressed[0] in lightkeys:
        print 'trigger'
        triggerSensorOn.setAutoDraw(True)
        triggerClockOn = core.Clock()
        while triggerClockOn.getTime()<0.01:
            win.flip()
    triggerSensorOn.setAutoDraw(False)
    win.flip()

win.close()
core.quit()