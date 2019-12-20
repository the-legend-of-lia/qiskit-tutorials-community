#!/usr/bin/env python
# coding: utf-8

# # _*Experiment with the Shor's Algorithm in Aqua*_
# 
# This notebook demonstrates how to experiment with the `Shor`'s algorithm in `Qiskit Aqua`.
# 
# We first import all necessary modules.

# In[1]:


from qiskit import BasicAer
from qiskit.aqua import QuantumInstance
from qiskit.aqua import run_algorithm
from qiskit.aqua.algorithms import Shor


# The [Shor's Factoring Algorithm](https://en.wikipedia.org/wiki/Shor's_algorithm) is explained in more detail in the corresponding notebook located in the directory `algorithms`. With Aqua, we can create a `Shor` instance by simply providing the target integer to be factored and run it, as follows.

# In[2]:


N = 15
shor = Shor(N)
backend = BasicAer.get_backend('qasm_simulator')
quantum_instance = QuantumInstance(backend, shots=1024)
ret = shor.run(quantum_instance)
print("The list of factors of {} as computed by the Shor's algorithm is {}.".format(N, ret['factors'][0]))


# The above step-by-step programatic approach can also be achieved by using a json configuration dictionary with the parameters for the algorithm and any other dependent objects it requires, as follows:

# In[3]:


params = {
    'problem': {
        'name': 'factoring',
    },
    'algorithm': {
        'name': 'Shor',
        'N': N,
    },
    'backend': {
        'shots': 1024,
    },
}
result_dict = run_algorithm(params, backend=backend)
print("The list of factors of {} as computed by the Shor's algorithm is {}.".format(N, result_dict['factors'][0]))

