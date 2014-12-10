# -*- coding: utf-8 -*-
"""
Created on Tue Nov  4 16:29:29 2014

# New in this version:
    ## make lead time in write_optacon_protocol_file() a separate block
    ## put stim file in a specified folder
    
@author: sarahmcintyre
"""

from optacon import *
from optaconSideways import *

motionStim, repList = single_presentation()

exptPath = r'./example' 
if not os.path.exists(exptPath): os.makedirs(exptPath)

write_protocol_file(fileName='%s/sidewaysExample' %(exptPath),stimList=motionStim,stimRep=repList)
