from psychopy import visual, core, event

win = visual.Window(size=(1152, 870), fullscr=True, screen=0, allowGUI=False, allowStencil=False,
    monitor='testMonitor', color=[0,0,0], colorSpace='rgb',
    blendMode='avg', useFBO=True,
    )
triggerPosition = [-11, 8]

triggerSensorOn = visual.Rect(win=win, name='polygon',units='cm', 
    width=[8, 8][0], height=[8, 8][1],
    ori=0, pos=triggerPosition,
    lineWidth=1, lineColor=[1,1,1], lineColorSpace='rgb',
    fillColor=[1,1,1], fillColorSpace='rgb',
    opacity=1,interpolate=True)
    
triggerSensorOn.setAutoDraw(True)

triggerClockOn = core.Clock()
while triggerClockOn.getTime()<5:
    if event.getKeys(keyList=['escape','q']):
        myWin.close()
        core.quit()
    win.flip()
