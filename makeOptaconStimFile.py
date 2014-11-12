# -*- coding: utf-8 -*-
"""
Created on Tue Nov  4 16:29:29 2014

# To do:
    ## new function to generate full experiment set of motion stimuli:
            # assigning blockNo
            # assigning signal pin code
            # assigning stimulus name?
            # include response period
    
# New in this version:
    ## make lead time in write_optacon_protocol_file() a separate block
    ## put stim file in a specified folder
    
@author: sarahmcintyre
"""

from optacon import *
from optaconSideways import *

motionStim, repList = single_optacon_presentation()

exptPath = r'./pilot' 
if not os.path.exists(exptPath): os.makedirs(exptPath)

write_optacon_protocol_file(fileName='%s/sidewaysOverlap' %(exptPath),stimList=motionStim,stimRep=repList)
