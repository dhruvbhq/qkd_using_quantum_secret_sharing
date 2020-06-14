"""
Created on Tue Sep  3 08:21:52 2019

@author_of_program: DHRUV BHATNAGAR

Program for the protocol in the paper:
Two-Party secret key distribution via a 
modified quantum secret sharing protocol

DOI: 10.1364/OE.23.007300 (OSA)

(link to paper in video description)

"""

import numpy as np
np.set_printoptions(precision=3)

class qkd_node:
    
    def __init__(self, system_size, self_id, left_neighbour_id, right_neighbour_id, size_tx, is_quiet):
        # node IDs start from 1 to N.
        self.self_id = self_id
        self.left_neighbour_id = left_neighbour_id
        self.right_neighbour_id = right_neighbour_id
        self.size_tx = size_tx
        self.state_matrix = np.zeros((2,self.size_tx)) + 1.00j*np.zeros((2,self.size_tx))
        self.phase_array = np.zeros(self.size_tx)
        self.phase_chooser_array = np.zeros(self.size_tx)
        self.is_quiet = is_quiet
        
    def get_state_from_qc(self, state_matrix):
        self.state_matrix = state_matrix
    
    def put_state_on_qc(self):
        return self.state_matrix

    def modify_state(self):
        for self.ind in range(self.size_tx):
            
            ket_st = self.state_matrix[:,self.ind]
            self.state_matrix[:,self.ind], self.phase_array[self.ind], self.phase_chooser_array[self.ind] = self.apply_random_phase(ket_st)                
        
    def apply_random_phase(self, state_vec):
        # according to a uniform distribution
        self.ph1 = 0.00
        self.ph2 = np.pi/2.00
        self.ph3 = np.pi
        self.ph4 = 3.00*np.pi/2.00
        self.phase_to_apply = 0.00
        
        self.p_c = np.random.uniform(0,1)
        self.phase_chooser = 0
        
        if(self.p_c <= 0.25):
            self.phase_to_apply = self.ph1
        elif(self.p_c > 0.25 and self.p_c <= 0.50):
            self.phase_to_apply = self.ph2
            self.phase_chooser = 1
        elif(self.p_c > 0.50 and self.p_c <= 0.75):
            self.phase_to_apply = self.ph3
        else:
            self.phase_to_apply = self.ph4
            self.phase_chooser = 1
        
        if(self.is_quiet == False):
            print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
            print("Node id: ", self.self_id, "| Qubit number: ", (self.ind + 1), "| random phase: %.3f" %self.phase_to_apply, "|")
        t_c = np.cos(self.phase_to_apply)
        t_s = np.sin(self.phase_to_apply)
        
        p = t_c + t_s*1j
        ph_gate = np.array([[1.00+0.00j,0.00+0.00j],[0.00+0.00j,p]])
        return np.matmul(ph_gate, state_vec), self.phase_to_apply, self.phase_chooser
        
    def put_phase_on_cc(self):
        # returns the exact phase applied
        if(self.is_quiet == False):
            print("Node Id: ", self.self_id, "Phase array forwarded to c_c: ", self.phase_array)        
        return self.phase_array
        
    def return_state_for_print(self):
        return self.state_matrix
        
##########################################################
    
class qkd_alice_node(qkd_node):
    
    def __init__(self, system_size, right_neighbour_id, size_tx, is_quiet):
        self.self_id = 1
        self.left_neighbour_id = -1
        self.right_neighbour_id = right_neighbour_id
        self.size_tx = size_tx
        self.state_matrix = np.zeros((2,self.size_tx)) + 1.00j*np.zeros((2,self.size_tx))
        self.phase_array = np.zeros(self.size_tx)
        self.phase_chooser_array = np.zeros(self.size_tx)
        self.temp_total_phase_track_arr = np.zeros(self.size_tx)
        self.total_phase_track_arr = np.zeros(self.size_tx)
        #self.is_meas_deterministic = np.zeros(self.size_tx) 
        self.key_arr = np.empty(0)
        self.size_of_key = 0
        self.is_quiet = is_quiet
        
    def apply_Hadamard(self, state_vec):
        k = 1.00/np.sqrt(2)        
        H = np.array([[k,k],[k,-1*k]])
        return np.matmul(H,state_vec)
        
    def prep_init_state(self):
        ket0 = np.array([1.00+0.00j, 0.00+0.00j])
        for i in range(self.size_tx):
            self.state_matrix[:,i] = self.apply_Hadamard(ket0)
        
    def return_state(self):
        return self.state_matrix
    
    def get_state_from_qc(self, state_vec):
        pass
    
    def put_phase_on_cc(self):
        # returns 0 if applied phase is 0 or pi
        # else returns 1
        if(self.is_quiet == False):
            print("Node Id: ", self.self_id, "Phase array forwarded to c_c: ", self.phase_chooser_array)
        return self.phase_chooser_array
        
    def get_phase_info_from_cc(self, phase_info_array):
        if(self.is_quiet == False):
            print("In Alice: phase_info_array received is: ", phase_info_array)
        self.temp_total_phase_track_arr = phase_info_array
        
        
    def process_phase_info(self):
        
        is_pi_array = False
        for i in self.temp_total_phase_track_arr:
            if((abs(i-(np.pi/2.00)) < 10**(-5)) or (abs(i-(np.pi)) < 10**(-5)) or (abs(i-(3*np.pi/2.00)) < 10**(-5))):
                is_pi_array = True
       
        if(is_pi_array):        
            k1 = np.pi/2.00
            self.temp_total_phase_track_arr = self.temp_total_phase_track_arr/k1
            self.temp_total_phase_track_arr = np.round(self.temp_total_phase_track_arr.astype(int))
            
        self.total_phase_track_arr += self.temp_total_phase_track_arr
        if(self.is_quiet == False):
            print("Alice's temp phase tracking array", self.temp_total_phase_track_arr)
            print("ALICE: total phase tracking array: ", self.total_phase_track_arr, "Shape of array", np.shape(self.total_phase_track_arr))
            
    def key_gen_alice(self):
        for i in range(self.size_tx):
            if(np.mod(self.total_phase_track_arr[i], 2) == 0):
                self.size_of_key += 1
                if(np.mod(self.total_phase_track_arr[i], 4) == 0):
                    if((np.absolute(self.phase_array[i] - np.pi) < 10**(-3))or ((np.absolute(self.phase_array[i] - (3.00*np.pi/2.00))) < 10**(-3))):
                        self.key_arr = np.append(self.key_arr, 1)
                    elif(((np.absolute(self.phase_array[i] - 0) < 10**(-3))) or ((np.absolute(self.phase_array[i] - (np.pi/2.00)) < 10**(-3)))):
                        self.key_arr = np.append(self.key_arr, 0)
                elif(np.mod(self.total_phase_track_arr[i], 4) == 2):
                    if(((np.absolute(self.phase_array[i] - (np.pi))) < 10**(-3)) or (np.absolute(self.phase_array[i] - (3.00*np.pi/2.00)) < 10**(-3))):
                        self.key_arr = np.append(self.key_arr, 0)
                    elif(((np.absolute(self.phase_array[i] - 0) < 10**(-3))) or ((np.absolute(self.phase_array[i] - (np.pi/2.00)) < 10**(-3)))):
                        self.key_arr = np.append(self.key_arr, 1)
                    
                
    def key_check(self, check_bits_bob):
        self.size_of_check_bits = np.size(check_bits_bob)
        self.check_bits_alice = self.key_arr[:self.size_of_check_bits].astype(int)
        self.rem_key_alice = self.key_arr[self.size_of_check_bits:].astype(int)
        self.errors = 0        
        for i in range(self.size_of_check_bits):
            if(check_bits_bob[i] != self.check_bits_alice[i]):
                self.errors += 1
        self.percent_error_rate = 100.00*(self.errors)/(self.size_of_check_bits)
        self.key_efficiency = 100.00*(self.size_of_key+1)/(self.size_tx)
        return self.key_efficiency, self.percent_error_rate
        
    def print_rem_key_alice(self):
        print("Alice's remaining key is: ")
        for i in range(np.size(self.rem_key_alice)):
            print(self.rem_key_alice[i], end='')
        print("\n Size of Alice's remaining key is: ", np.size(self.rem_key_alice))
        print("-------------------------------------------------------------------------------")
                                   
    def print_key_alice(self):
        print("Alice's generated key: ")
        for i in range(np.size(self.key_arr)):
            print(self.key_arr[i].astype(int), end='') 
        print()
        print("Size of Alice's key: ", self.size_of_key)
        print("-------------------------------------------------------------------------------")
        
    def return_key(self):
        return self.key_arr

        
class qkd_bob_node(qkd_node):
    
    def __init__(self, system_size, left_neighbour_id, size_tx, is_quiet):
        self.self_id = system_size
        self.left_neighbour_id = left_neighbour_id
        self.right_neighbour_id = -1
        self.curr_key_size = 0
        self.size_tx = size_tx
        self.state_matrix = np.zeros((2,self.size_tx)) + 1.00j*np.zeros((2,self.size_tx))
        self.phase_array = np.zeros(self.size_tx)
        self.phase_chooser_array = np.zeros(self.size_tx)
        self.meas_seq_b = np.zeros(self.size_tx)
        self.temp_meas_seq_b = np.zeros(self.size_tx)
        self.phase_info_array = np.zeros(self.size_tx)
        self.total_phase_track_arr = np.zeros(self.size_tx)
        self.key_arr = np.empty(0)
        self.size_of_key = 0
        #self.is_meas_deterministic = np.zeros(self.size_tx)
        self.is_quiet = is_quiet

    def get_curr_key_size(self):
        return self.curr_key_size
        
    def apply_random_phase(self, state_vec):        
        # according to a uniform distribution
        self.ph1 = 0.00
        self.ph2 = np.pi/2.00

        self.phase_to_apply = 0
        
        self.p_c = np.random.uniform()
        self.phase_chooser = 0
        
        if(self.p_c <= 0.50):
            self.phase_to_apply = self.ph1
        else:
            self.phase_to_apply = self.ph2
            self.phase_chooser = 1
        
        if(self.is_quiet == False):
            print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
            print("Node Id: ", self.self_id, "| Qubit number: ", (self.ind + 1), "| random phase: %.3f" %self.phase_to_apply, "|")
        t_c = np.cos(self.phase_to_apply)
        t_s = np.sin(self.phase_to_apply)
        
        p = t_c + t_s*1j
        ph_gate = np.array([[1.00+0.00j,0.00+0.00j],[0.00+0.00j,p]])
        return np.matmul(ph_gate, state_vec), self.phase_to_apply, self.phase_chooser
        
    def put_phase_on_cc(self):
        # returns 0 if applied phase is 0 or pi
        # else returns 1
        if(self.is_quiet == False):
            print("Node Id: ", self.self_id, "Phase array forwarded to c_c: ", self.phase_chooser_array)
        return self.phase_chooser_array
        
    def apply_Hadamard(self, state_vec):
        k = 1.00/np.sqrt(2)        
        H = np.array([[k,k],[k,-1*k]])
        return np.matmul(H,state_vec)
        
    def meas_qubit_stream_bob(self):
        for j in range(self.size_tx):
            st = self.state_matrix[:,j]
            st = self.apply_Hadamard(st)
            self.temp_meas_seq_b[j] = self.meas_single_qubit_bob(st)
        self.meas_seq_b = self.temp_meas_seq_b.astype(int)
        if(self.is_quiet != True):
            print("DEBUG BOB: STATE: \n", self.state_matrix, "\n BOB's MEASURED SEQ: ", self.meas_seq_b, "\n Shape of array", np.shape(self.total_phase_track_arr))
                
        #return self.meas_seq_b.astype(int)
    
    def meas_single_qubit_bob(self, state_vec):
        a = np.square(np.absolute(state_vec[0]))
        thres = 10**(-3)
        if(np.absolute(a-0) < thres):
            res = 1
        elif(np.absolute(a-1) < thres):
            res = 0
        elif(np.random.uniform() <= a):
            res = 0
        else:
            res = 1
        #print("values of a: ", a)
        return res
        
    def get_phase_info_from_cc(self, phase_info_array):
        if(self.is_quiet == False):
            print("In Bob: phase_info_array received is: ", phase_info_array)
        self.temp_total_phase_track_arr = phase_info_array
        
    def process_phase_info(self):
        
        is_pi_array = False
        for i in self.temp_total_phase_track_arr:
            if((abs(i-(np.pi/2.00)) < 10**(-5)) or (abs(i-(np.pi)) < 10**(-5)) or (abs(i-(3*np.pi/2.00)) < 10**(-5))):
                is_pi_array = True
       
        if(is_pi_array):        
            k1 = np.pi/2.00
            self.temp_total_phase_track_arr = self.temp_total_phase_track_arr/k1
            self.temp_total_phase_track_arr = np.round(self.temp_total_phase_track_arr.astype(int))
            
        self.total_phase_track_arr += self.temp_total_phase_track_arr
        if(self.is_quiet == False):
            print("Bob's temp phase tracking array", self.temp_total_phase_track_arr)
            print("BOB: total phase tracking array: ", self.total_phase_track_arr, "Shape of array", np.shape(self.total_phase_track_arr))
            
    def key_gen_bob(self):
        for i in range(self.size_tx):
            if(np.mod(self.total_phase_track_arr[i], 2) == 0):
                self.size_of_key += 1
                self.key_arr = np.append(self.key_arr, self.meas_seq_b[i])
                
    def pre_key_check(self):
        self.size_of_check_bits = np.ceil((self.size_of_key-1)/2).astype(int)
        self.check_bits = self.key_arr[:self.size_of_check_bits].astype(int)
        self.rem_key_bob = self.key_arr[self.size_of_check_bits:].astype(int)
        return self.check_bits
        
    def print_rem_key_bob(self):
        print("Bob's remaining key is: ")
        for i in range(np.size(self.rem_key_bob)):
            print(self.rem_key_bob[i], end='')
        print("\n Size of Bob's remaining key is: ", np.size(self.rem_key_bob))
        print("-------------------------------------------------------------------------------")
                                
    def print_key_bob(self):
        if(self.is_quiet != True):
            print("RE: Bob's measured seq: ", self.meas_seq_b)
        print("Bob's generated key: ")
        for i in range(np.size(self.key_arr)):
            print(self.key_arr[i].astype(int), end='')
        print()
        print("Size of Bob's key: ", self.size_of_key)
        print("-------------------------------------------------------------------------------")
        
    def return_key(self):
        return self.key_arr
        
##################################################
   
class q_channel:
    
    def __init__(self, is_quiet = True):
        self.is_quiet = is_quiet
    
    def get_state(self, st_mtx):
        self.st_mtx_in = st_mtx
        
    def corrupt_state(self):
        self.temp_st_mtx = self.st_mtx_in
        # for now, the identity
        self.out_st_mtx = self.temp_st_mtx
    
    def put_state(self):
        return self.out_st_mtx
        
    # As an improvement, the q_channel can have
    # IDs of its left and right neighbours.
#################################################
        
class c_channel:
    
    def get_phase_info(self, phase_info):
        self.phase_info = phase_info
    
    def put_phase_info(self):
        return self.phase_info
        
    #and so that they can validate their key
        
    def get_check_bits(self, check_bits):
        self.check_bits = check_bits
    
    def put_check_bits(self):
        return self.check_bits
    
    def ch_reset(self):
        self.check_bits = []
        self.phase_info = []