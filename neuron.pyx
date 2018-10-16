# distutils: language=c++

from libcpp.vector cimport vector
from libc.math cimport exp
from scipy.stats import poisson

cdef extern from "math.h":
    double sin(double x)

cdef class ShotNoiseConductance:
    cdef public:
        double rate, g, g_peak, reversal, decay

    def __cinit__(self, double rate, double g_peak, double reversal, double decay):
        self.rate, self.g_peak, self.reversal, self.decay = rate, g_peak, reversal, decay
        cdef distribution = poisson_distribution(rate)
        self.distribution = distribution

    def connect_to(self, Neuron neuron):
        neuron.conductances.push_back(self)

    cdef void update(self, dt):
        cdef int n_spikes = distribution(self.generator)
        self.g += n_spikes * self.g_peak
        self.g *= exp(-dt / self.decay)



cdef class MATThresholds:
    cdef public:
        double alpha1, alpha2, omega, threshold, tc1, tc2, refractory_period, past_spike_time
        vector[double] spike_times

    def __cinit__(self, double alpha1, double alpha2, double omega, double refractory_period):
        self.alpha1, self.alpha2, self.omega = alpha1, alpha2, omega
        self.tc1 = 0
        self.tc2 = 0
        self.refractory_period = refractory_period

        self.threshold = self.tc1 + self.tc2
        self.past_spike_time = refractory_period

    cdef void fire(self, double time):
        if self.past_spike_time >= self.refractory_period:
            self.tc1 += self.alpha1
            self.tc2 += self.alpha2
            self.spike_times.push_back(time)
            self.past_spike_time = 0

    cdef void update(self, double dt):
        self.past_spike_time += dt
        self.tc1 *= exp(-dt / 10.)
        self.tc2 *= exp(-dt / 200.)
        self.threshold = self.tc1 + self.tc2


cdef class Neuron:
    cdef public:
        double resting_potential, membrane_resistance, membrane_capacitance, voltage, time_constant, time
        vector[MATThresholds] mats
        vector[ShotNoiseConductance] conductances

    def __cinit__(self, double resting_potential, double membrane_resistance,
            double membrane_capacitance, vector[MATThresholds] mats):
        self.resting_potential = resting_potential
        self.membrane_resistance = membrane_resistance
        self.membrane_capacitance = membrane_capacitance
        self.mats = mats

        self.voltage = self.resting_potential
        self.time_constant = self.membrane_capacitance * self.membrane_resistance
        self.time = 0

    cdef integrate_voltage(self, dt):
        factor = 1. / dt + (1. + self.membraneResistance * sum(c.g for c in self.conductances)) / self.timeConstant
        self.voltage = (self.voltage / dt + (self.resting_potential + self.membrane_resistance * sum(c.g * c.reversal for c in self.conductances)) \
                            / self.timeConstant) / factor


    cdef timestep(self, double dt):
        self.time += dt

        for c in self.conductances:
            c.update(dt)

        self.integrate_voltage(dt)

        for mat in self.mats:
            mat.update(dt)
            if mat.threshold <= self.voltage:
                mat.fire(self.time)