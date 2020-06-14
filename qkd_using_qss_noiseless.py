# -*- coding: utf-8 -*-
"""
Created on Wed Sep 25 08:53:39 2019

@author: DHRUV BHATNAGAR
"""

import qkd_using_qss_base as qq
import qkd_using_qss_experiment as expt
import numpy as np
np.set_printoptions(precision=3)

def main():
 
    # A "Small" experiment runs for 1 iteration and prints out a lot of
    # debugging information in the transcript. The total number of nodes 
    # and the number of qubits transmitted by Alice are small as well,
    # as compared to the "Big" experiment, which runs for 10 iterations.
    # The small experiment can be used for detailed analysis.
    # SIZE_TX represents the number of qubits prepared by Alice.
    # SYSTEM_SIZE is the number of intermediate nodes apart from Alice and Bob.
    # IS_QUIET is used to control the number of debug messages, with 2 settings.
    
    EXPT_TYPE = "Small"
    
    if(EXPT_TYPE == "Small"):
        N = 1
        IS_QUIET = False
        
    elif(EXPT_TYPE == "Big"):
        N = 10
        IS_QUIET = True 
    
    for m in range(N):
        if(EXPT_TYPE == "Small"):
            SYSTEM_SIZE = np.random.randint(4,8)
            SIZE_TX = np.random.randint(20,30)
        
        elif(EXPT_TYPE == "Big"):
            SYSTEM_SIZE = np.random.randint(200,500)
            SIZE_TX = np.random.randint(50,100)
            
        e1 = expt.qkd_using_qss_experiment(SYSTEM_SIZE, SIZE_TX, IS_QUIET)
        print("Run: ", m+1, " SYSTEM_SIZE: ", SYSTEM_SIZE, " SIZE_TX: ", SIZE_TX)
        e1.execute()

if __name__ == '__main__':
    main()