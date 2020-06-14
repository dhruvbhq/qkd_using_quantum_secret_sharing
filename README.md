# qkd_using_quantum_secret_sharing
## Project Title: Simulation of the multi-node Quantum Key Distribution protocol using Quantum Secret Sharing
#### File guide:

A) Files needed for noiseless QKD using QSS experiment:

A.1) qkd_using_qss_base.py

A.2) qkd_using_experiment.py

A.3) qkd_using_qss_noiseless.py (contains main())


C) Files needed for Eavesdropping case

C.1) All files in A)

C.2) qkd_using_qss_eavesdrop.py (contains main())

Sample output transcripts of the programs have also been uploaded for noiseless and eavesdropping cases (single and multi-experiment runs).

#### Brief Summary:
1. This program simulates the Quantum Key Distribution protocol using Quantum Secret Sharing developed in the paper: 
"Two-Party Secret Key Distribution via a Modified Quantum Secret Sharing Protocol" 

   (DOI: 10.1364/OE.23.007300 (OSA)) 

   Link: https://www.osapublishing.org/oe/abstract.cfm?uri=oe-23-6-7300

2. The basic experiment is noiseless, but existing base classes can be easily overridden (OOP) to implement custom noise models/eavesdropping.

3. The functionality to validate the key by comparing the first half of the key for bit errors has been implemented.

4. Measurement outcomes are implemented using numpy's random number generation.

5. Detailed transcripts print a summary of the results of the experiment.

6. Classes for various nodes, along with Alice's and Bob's nodes, having the capability to apply randomly chosen phases to qubits (as per the protocol), and communicating via separate quantum channels have been implemented.

#### Overview of code/classes:
##### qkd_using_qss_base.py contains:

-> basic node class with capability to apply randomly chosen phases.

-> node classes for Alice and Bob, which extend from the above basic node class and have their special capabilities, including total phase tracking and hence key generation, as required by the protocol.

-> Classes for the classical and quantum channels.

##### qkd_using_qss_experiment.py contains:

-> QKD using QSS experiment class, which is structured into various phases for initializing and building the experiment, connecting the nodes with respective quantum channels, qubit transmissions, declaration of phases, key generation and validation.

##### qkd_using_qss_noiseless.py contains:

-> main() to execute the experiment, with options to choose the number of qubits, number of nodes, and number/detail level of the debugging prints.

-> A "Small" experiment runs for 1 iteration and prints out a lot of debugging information in the transcript. The total number of nodes and the number of qubits transmitted by Alice are small as well, as compared to the "Big" experiment, which runs for 10 iterations. The small experiment can be used for detailed analysis.

-> SIZE_TX represents the number of qubits prepared by Alice.

-> SYSTEM_SIZE is the number of intermediate nodes apart from Alice and Bob.

-> IS_QUIET is used to control the number of debug messages, with 2 settings.

##### qkd_using_qss_eavesdrop.py contains:

-> an overridden quantum channel with eavesdropping (the model chosen is that the eavesdropper can randomly generate a set of bases out of 0/1 and +/- bases, measure the incoming qubits, and return the collapsed state).

-> main() to execute the experiment, with every quantum channel involved being overridden by the eavesdropped one.
