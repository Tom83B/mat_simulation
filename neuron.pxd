from libcpp.vector cimport vector

cdef extern from "neuron.cpp":
    pass

# Decalre the class with cdef
cdef extern from "neuron.h":
    cdef cppclass ShotNoiseConductance:
        # ShotNoiseConductance() except +
        ShotNoiseConductance(double, double, double, double) except +
        double g, reversal

    cdef cppclass MATThresholds:
        MATThresholds() except +
        MATThresholds(double, double, double, double, double, double) except +
        vector[double] get_spike_times()
        double threshold

    cdef cppclass Neuron:
        Neuron() except +
        Neuron(double, double, double, vector[MATThresholds*]) except +
        void append_conductance(ShotNoiseConductance)
        void timestep(double)
        vector[ShotNoiseConductance*] conductances
        vector[MATThresholds*] mats
        double voltage

cdef extern from "simulation.cpp":
    vector[int] sr_experiment(Neuron neuron, double time_window, double dt,
                       vector[double] exc_intensities, vector[double] inh_intensities, int seed)
