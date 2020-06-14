# -*- coding: utf-8 -*-
"""
Created on Wed Sep 25 08:56:15 2019

@author: DHRUV BHATNAGAR
"""


import qkd_using_qss_base as qq
import qkd_using_qss_experiment as expt
import numpy as np
import random
np.set_printoptions(precision=3)

class eve_q_channel(qq.q_channel):
    
    def corrupt_state(self):
        self.temp_st_mtx = self.st_mtx_in
        self.length = np.shape(self.temp_st_mtx[0])[0] 
        # Eve generates a random binary sequence
        # and according to the result, measures
        # the incoming qubits in the standard or 
        # the Hadamard basis, and returns the 
        # collapsed state
        
        self.basis_seq_e = np.random.randint(2, size=self.length)
        
        for i in range(self.length):
            st = self.temp_st_mtx[:,i]
            if(self.is_quiet == False):
                print("In Eve: input state: ", st)
                if(self.basis_seq_e[1] == 0):
                    print("Measurement basis: 0/1")
                else:
                    print("Measurement basis: +/-")
            if(self.basis_seq_e[1] == 0):
                res = self.meas_single_qubit_e(st)
                if(res==0):
                    self.temp_st_mtx[:,i] = np.array([1,0])
                    if(self.is_quiet == False):
                        print("Returned state: ", self.temp_st_mtx[:,i])
                        print("---------------------------------------")
                else:
                    self.temp_st_mtx[:,i] = np.array([0,1])
                    if(self.is_quiet == False):                    
                        print("Returned state: ", self.temp_st_mtx[:,i])
                        print("---------------------------------------")
               
            else:
                st = self.hadamard_e(st)
                res = self.meas_single_qubit_e(st)
                if(res==0):
                    self.temp_st_mtx[:,i] = self.hadamard_e(np.array([1,0]))
                    if(self.is_quiet == False):
                        print("Returned state: ", self.temp_st_mtx[:,i])
                        print("---------------------------------------")

                else:
                    self.temp_st_mtx[:,i] = self.hadamard_e(np.array([0,1]))
                    if(self.is_quiet == False):
                        print("Returned state: ", self.temp_st_mtx[:,i])
                        print("---------------------------------------")

        self.out_st_mtx = self.temp_st_mtx
                   
    def meas_single_qubit_e(self, state_vec):
        a = np.square(np.absolute(state_vec[0]))
        if(self.is_quiet == False):
            print("In Eve: probability of |0> or |+>", a)
        thres = 10**(-3)
        if(np.absolute(a-0) < thres):
            res = 1
        elif(np.absolute(a-1) < thres):
            res = 0
        elif(random.random() < a):
            res = 0
        else:
            res = 1
        return res        
            
    def hadamard_e(self, state_vec):
        k = 1.0/np.sqrt(2.0)
        H = np.array([[k,k],[k,(-1*k)]])
        return np.matmul(H, state_vec)
                     
class eve_qkd_using_qss_experiment(expt.qkd_using_qss_experiment):
    
    def build_phase(self):
        super().build_phase()
        if(self.is_quiet == False):
            print(self.system_size)
            print(np.size(self.q_c))
        q_c_e = []
        
        for i in range(1,self.system_size):
            q_c_e.append(eve_q_channel(self.is_quiet))
        if(self.is_quiet == False):
            print(np.size(q_c_e))
        
            
        for i in range(0,self.system_size-1):            
            # Polymorphism!
            self.q_c[i] = q_c_e[i]
    
    def scoreboard_phase(self):
        pass

def main():
        
    EXPT_TYPE = "Big"
    
    if(EXPT_TYPE == "Small"):
        N = 1
        IS_QUIET = False
        SYSTEM_SIZE = np.random.randint(4,8)
        SIZE_TX = np.random.randint(20,30)
        
    elif(EXPT_TYPE == "Big"):
        N = 10
        IS_QUIET = True
        SYSTEM_SIZE = np.random.randint(200,500)
        SIZE_TX = np.random.randint(50,100) 
    
    for m in range(N):
        e1 = eve_qkd_using_qss_experiment(SYSTEM_SIZE, SIZE_TX, IS_QUIET)
        print("Run: ", m+1, " SYSTEM_SIZE: ", SYSTEM_SIZE, " SIZE_TX: ", SIZE_TX)
        e1.execute()

if __name__ == '__main__':
    main()