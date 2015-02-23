from psychopy import gui, misc, core, misc, data
import os, pylab
import numpy as np
from noiseStaircaseHelpers import toStaircase, printStaircase, outOfStaircase
from pandas import DataFrame

datFile = misc.fromFile(r'./fingerTransferTest/rawData/pilot_sarah_unadapted_data_2015-02-11_184932.psydat')
#print datFile.otherData
#print datFile.intensities
#print datFile.data
print datFile.quantile()

#fit curve
fit = None
try: 
    fit = data.FitLogistic(datFile.intensities, datFile.data, expectedMin=0,  sems = 1.0/len(datFile.intensities))
    print fit.params
except:
    print('Fit failed.')
    

def plotDataAndPsychometricCurve(staircase,fit,descendingPsycho,threshVal):
    #Expects staircase, which has intensities and responses in it
    #May or may not be log steps staircase internals
    #Plotting with linear axes
    #Fit is a psychopy data fit object. Assuming that it couldn't handle descendingPsycho so have to invert the values from it
    intensLinear= outOfStaircase(staircase.intensities, staircase, descendingPsycho)
    print 'intensLinear', intensLinear
    if fit is not None:
        #generate psychometric curve
        intensitiesForCurve = pylab.arange(min(intensLinear), max(intensLinear), 0.01)
        print 'intensitiesForCurve', intensitiesForCurve
        thresh = fit.inverse(threshVal)
        print 'thresh', thresh
        if descendingPsycho:
            print 'descendingPsycho'
            intensitiesForFit = 100-intensitiesForCurve
            thresh = 100 - thresh
        else:
            intensitiesForFit = intensitiesForCurve
        ysForCurve = fit.eval(intensitiesForFit)
        #print('intensitiesForCurve=',intensitiesForCurve)
        #print('ysForCurve=',ysForCurve) #debug
    else: #post-staircase function fitting failed, but can fall back on what staircase returned
        thresh = staircase.quantile()
        if descendingPsycho:
            thresh = 100-thresh
    #plot staircase in left hand panel
    pylab.subplot(121)
    pylab.plot(intensLinear)
    pylab.xlabel('staircase trial')
    pylab.ylabel('comparison ISOI (ms)')
    #plot psychometric function on the right.
    ax1 = pylab.subplot(122)
    if fit is not None:
        pylab.plot(intensitiesForCurve, ysForCurve, 'k-') #fitted curve
    pylab.plot([thresh, thresh],[0,threshVal],'k--') #vertical dashed line
    pylab.plot([0, thresh],[threshVal,threshVal],'k--') #horizontal dashed line
    figure_title = 'threshold (%.2f) = %0.2f' %(threshVal, thresh) + 'ms'
    #print thresh proportion top of plot
    pylab.text(0, 1.11, figure_title, horizontalalignment='center', fontsize=12)
    if fit is None:
        pylab.title('Fit failed')
    
    #Use pandas to calculate proportion correct at each level
    df= DataFrame({'intensity': intensLinear, 'response': staircase.data})
    #print('df='); print(df) #debug
    grouped = df.groupby('intensity')
    groupMeans= grouped.mean() #a groupBy object, kind of like a DataFrame but without column names, only an index?
    intensitiesTested = list(groupMeans.index)
    pCorrect = list(groupMeans['response'])  #x.iloc[:]
    ns = grouped.sum() #want n per trial to scale data point size
    ns = list(ns['response'])
    print('df mean at each intensity\n'); print(  DataFrame({'intensity': intensitiesTested, 'pCorr': pCorrect, 'n': ns })   )
    #data point sizes. One entry in array for each datapoint

    pointSizes = 5+ 40 * np.array(ns) / max(ns) #the more trials, the bigger the datapoint size for maximum of 6
    #print('pointSizes = ',pointSizes)
    points = pylab.scatter(intensitiesTested, pCorrect, s=pointSizes, 
        edgecolors=(0,0,0), facecolors= 'none', linewidths=1,
        zorder=10, #make sure the points plot on top of the line
        )
    pylab.ylim([-0.01,1.01])
    pylab.xlim([-20,180])
    pylab.xlabel('comparison ISOI (ms)')
    pylab.ylabel('proportion comparison clearer direction')
    #save a vector-graphics format for future
    #outputFile = os.path.join(dataFolder, 'last.pdf')
    #pylab.savefig(outputFile)
    createSecondAxis = False
#    if createSecondAxis: #presently not used, if fit to log would need this to also show linear scale
#        #create second x-axis to show linear percentNoise instead of log
#        ax2 = ax1.twiny()
#        ax2.set(xlabel='comparison ISOI (ms)', xlim=[-20,180]) #not quite right but if go to 0, end up with -infinity? and have error
#        #ax2.axis.set_major_formatter(ScalarFormatter()) #Show linear labels, not scientific notation
#        #ax2 seems to be the wrong object. Why am I using pylab anyway? Matplotlib documentation seems more clear
#        #for programming it is recommended that the namespaces be kept separate, http://matplotlib.org/api/pyplot_api.html
#        #http://stackoverflow.com/questions/21920233/matplotlib-log-scale-tick-label-number-formatting
#        ax2.set_xscale('log')
#        ax2.tick_params(axis='x',which='minor',bottom='off')

#    #save figure to file
#    outputFile = os.path.join(dataDir, 'test.pdf')
#    pylab.savefig(outputFile)

plotDataAndPsychometricCurve(datFile,fit,False,0.5)
# save figure to file
#outputFile =  exptFolder+exptName+'_plot'
#pylab.savefig(outputFile + '.pdf')
#pylab.savefig(outputFile + '.jpg')
pylab.show() #must call this to actually show plot
