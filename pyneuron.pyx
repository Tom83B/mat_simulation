# distutils: language = c++
# distutils: extra_compile_args = -std=c++11
# distutils: extra_link_args = -std=c++11

from libcpp.vector cimport vector
from libcpp.string cimport string
from cython.operator cimport dereference as deref
from neuron cimport ShotNoiseConductance as CShotNoiseConductance
from neuron cimport MATThresholds as CMATThresholds
from neuron cimport Neuron as CNeuron
from neuron cimport sr_experiment as _sr_experiment

import numpy as np
import pandas as pd

# Create a Cython extension type which holds a C++ instance
# as an attribute and create a bunch of forwarding methods
# Python extension type.
cdef class ShotNoiseConductance:
    cdef CShotNoiseConductance* conductance  # Hold a C++ instance which we're wrapping

    def __cinit__(self, double rate, double g_peak, double reversal, double decay):
        self.conductance = new CShotNoiseConductance(rate, g_peak, reversal, decay)

    def __dealloc__(self):
        del self.conductance

    @property
    def g(self):
        return deref(self.conductance).g

cdef class MATThresholds:
    cdef CMATThresholds* mat  # Hold a C++ instance which we're wrapping
    cdef string name

    def __cinit__(self, double alpha1, double alpha2, double tau1, double tau2, double omega,
            double refractory_period, name):
        self.mat = new CMATThresholds(alpha1, alpha2, tau1, tau2, omega, refractory_period)
        self.name = <string> name.encode('utf-8')

    def __dealloc__(self):
        del self.mat

    @property
    def threshold(self):
        return deref(self.mat).threshold


cdef class Neuron:
    cdef CNeuron neuron
    cdef vector[string] mat_names

    def __cinit__(self, double resting_potential, double membrane_resistance, double membrane_capacitance, mats):
        # cdef MATThresholds* c_mat
        cdef MATThresholds mat
        cdef vector[CMATThresholds*] mat_vec

        for mat in mats:
            mat_vec.push_back(mat.mat)
            self.mat_names.push_back(mat.name)

        self.neuron = CNeuron(resting_potential, membrane_resistance, membrane_capacitance, mat_vec)
        # self.mats = mats

    def append_conductance(self, ShotNoiseConductance cond):
        self.neuron.conductances.push_back(cond.conductance)

    cpdef void timestep(self, double dt):
        self.neuron.timestep(dt)

    # Attribute access
    @property
    def voltage(self):
        return self.neuron.voltage

def sr_experiment(Neuron neuron, double time_window, double dt,
        intensities, intensity_freq_func, int seed):
    exc_intensities, inh_intensities = np.array([np.array(intensity_freq_func(i)) for i in intensities]).T * dt

    cdef CNeuron c_neuron = neuron.neuron
    cdef vector[double] c_exc = exc_intensities
    cdef vector[double] c_inh = inh_intensities
    cdef vector[int] results

    mat_names = [name.decode("utf-8") for name in neuron.mat_names]

    results = _sr_experiment(c_neuron, time_window, dt, c_exc, c_inh, seed)
    result_array = np.array([x for x in results])

    return pd.DataFrame(result_array.reshape(-1, len(mat_names)), columns=mat_names, index=intensities).\
            groupby(level=0).agg(lambda x: list(x)).stack().swaplevel()
