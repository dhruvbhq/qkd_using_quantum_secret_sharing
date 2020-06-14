# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 20:10:41 2019

@author: DHRUV BHATNAGAR

qkd using qss experiment class
"""
import qkd_using_qss_base as qq
import numpy as np
np.set_printoptions(precision=3)

class qkd_using_qss_experiment:
    
    def __init__(self, system_size, size_tx, is_quiet):
        #SIZE_TX represents size of sequences taken by Alice (a.k.a. s_length)        
        self.system_size = system_size        
        self.size_tx = size_tx
        self.is_quiet = is_quiet
        
    def build_phase(self):
        
        self.a0 = qq.qkd_alice_node(self.system_size, 2, self.size_tx, self.is_quiet)
        self.b0 = qq.qkd_bob_node(self.system_size, self.system_size - 1, self.size_tx, self.is_quiet)
        self.n0 = []
        self.q_c = []
        self.c_c = qq.c_channel()
        
        for i in range(2, self.system_size):
            self.n0.append(qq.qkd_node(self.system_size, i, i-1, i+1, self.size_tx, self.is_quiet))
        
        for i in range(1,self.system_size):
            self.q_c.append(qq.q_channel(self.is_quiet))
    
        
    def run_phase(self):
        self.a0.prep_init_state()
        #print("Alice's initial state")
        #print(np.array_str(self.a0.return_state_for_print(), precision=2))
        #print(np.linalg.norm(self.a0.return_state_for_print()))
        self.a0.modify_state() # The modify state function of parent class gets called.
        #print("Alice's modified state")
        #print(np.array_str(self.a0.return_state_for_print(), precision=2))
        #print(np.linalg.norm(self.a0.return_state_for_print()))
        self.q_c[0].get_state(self.a0.put_state_on_qc())
        self.q_c[0].corrupt_state()
        
        for i in range(2, self.system_size):
            self.n0[i-2].get_state_from_qc(self.q_c[i-2].put_state())
            self.n0[i-2].modify_state()
            #print(np.array_str(self.n0[i-2].return_state_for_print(), precision=2))
            self.q_c[i-1].get_state(self.n0[i-2].put_state_on_qc())
            self.q_c[i-1].corrupt_state()
        
        self.q_c[self.system_size-2].corrupt_state()
        self.b0.get_state_from_qc(self.q_c[self.system_size-2].put_state())
        #print(np.array_str(self.b0.return_state_for_print(), precision=2))
        self.b0.modify_state()
        self.b0.meas_qubit_stream_bob()
        
        
    def phase_declaration_phase(self):
        for j in range(2, self.system_size):
            self.c_c.get_phase_info(self.n0[j-2].put_phase_on_cc())
            self.register_phase_a_b()
            self.c_c.ch_reset()
            
        self.c_c.get_phase_info(self.a0.put_phase_on_cc())
        self.register_phase_a_b()
        self.c_c.ch_reset()
        
        self.c_c.get_phase_info(self.b0.put_phase_on_cc())
        self.register_phase_a_b()
        self.c_c.ch_reset()
        
    def register_phase_a_b(self):
        self.a0.get_phase_info_from_cc(self.c_c.put_phase_info())
        self.a0.process_phase_info()
        self.b0.get_phase_info_from_cc(self.c_c.put_phase_info())
        self.b0.process_phase_info()
        
    def key_generation_phase(self):
        self.a0.key_gen_alice()
        #self.a0.print_key_alice()
        #print("Size of Alice's key: ", np.size(self.a0.return_key()))
        self.b0.key_gen_bob()
        #self.b0.print_key_bob()
        #print("Size of Bob's key: ", np.size(self.b0.return_key()))
        
    def scoreboard_phase(self):
        # should only be run to debug the noiseless simulation,
        # where the expected QBER is 0.00%
        self.error_count = 0
        a_k = self.a0.return_key()
        b_k = self.b0.return_key()
        if(np.size(a_k) != np.size(b_k)):
            print("Error - key sizes don't match")
            assert(0)
        for j in range(np.size(a_k)):
            if(a_k[j] != b_k[j]):
                self.error_count += 1
                assert(0)
                
    def validation_phase(self):
    
        # key validation phase
        self.c_c.get_check_bits(self.b0.pre_key_check())
        self.key_efficiency, self.calc_perc_error = self.a0.key_check(self.c_c.put_check_bits())        
        #self.c_c.ch_reset()
        
    def results_phase(self):
        print("===============================================================================")
        self.a0.print_key_alice()
        self.b0.print_key_bob()
        self.a0.print_rem_key_alice()
        self.b0.print_rem_key_bob()
        print("Key efficiency obtained is ", self.key_efficiency, "%")
        print("Qubit error-rate calculated by Alice is ", self.calc_perc_error, "%")
        print("Run completed.")
        print("===============================================================================")
                
    ###
    # Alice and Bob have to decide which bits to keep (only those ones which have deterministic measurement outcomes!)
    # Alice has to infer the total phase
    # and flip some bits depending on overall phase
    # The secret key would have been shared.        
    ###
    
    def execute(self):
        self.build_phase()
        self.run_phase()
        self.phase_declaration_phase()
        self.key_generation_phase()
        self.scoreboard_phase()
        self.validation_phase()
        self.results_phase()