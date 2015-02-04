# -*- coding: utf-8 -*-
"""
Created on Tue Nov  4 16:29:29 2014

@author: sarahmcintyre
"""

from optacon import *
from optaconSideways import *

motionStim, repList = single_presentation(presDur=3000, stepDur=[50,50], isoi=[82,82], 
                                  rowsToUse=range(0,6), colsToUse=[range(0,6),range(18,24)],
                                  stepVector=[1,1], randomPos=[False,False], spread=[True,True])

exptPath = r'./example' 
if not os.path.exists(exptPath): os.makedirs(exptPath)

write_protocol_file(fileName='%s/sidewaysExample' %(exptPath), stimList=motionStim,
                                stimRep=repList, blockList=[2], dwellTime=[4.35], leadTime=2000,
                                stimName=[' '], readPins=['A1','B1','C1','D1','E1','F1'])

