# -*- coding: utf-8 -*-
"""
Created on Tue Nov  4 16:29:29 2014

# To do:
    ## new function to generate full experiment set of motion stimuli:
            # assigning blockNo
            # assigning signal pin code
            # assigning stimulus name?
            # include response period
    ## make lead time in write_optacon_protocol_file() a separate block
    
# New in this version:
    ## overlapping stim fixed

@author: sarahmcintyre
"""

from optacon import *
from optaconSideways import *

motionStim, repList = single_trial()

write_optacon_protocol_file(fileName='sidewaysOverlap',stimList=motionStim,stimRep=repList)
