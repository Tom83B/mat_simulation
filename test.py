from pyneuron import ShotNoiseConductance, MATThresholds, Neuron, sr_experiment
import numpy as np

exc = ShotNoiseConductance(
	rate=10,
	g_peak=0.0015,
	reversal=0,
	decay=3)

inh = ShotNoiseConductance(
	rate=2,
	g_peak=0.0015,
	reversal=-75,
	decay=10)

mat = MATThresholds(
	alpha1=10,
	alpha2=1,
	tau1=10,
	tau2=200,
	omega=-50,
	refractory_period=2,
    name='FS')

mat2 = MATThresholds(
	alpha1=10,
	alpha2=1,
	tau1=10,
	tau2=200,
	omega=-50,
	refractory_period=2,
    name='RS')

neuron = Neuron(
	resting_potential=-80,
	membrane_resistance=50,
	membrane_capacitance=0.1,
	mats=[mat, mat2])

neuron.append_conductance(exc)
neuron.append_conductance(inh)


def intensity_freq_func(intensity):
    return 10, 5

intensities = np.ones(10)

spike_counts = sr_experiment(neuron, 1000, 0.1, intensities, intensity_freq_func)
print(spike_counts)

# for i in range(1):
# 	neuron.timestep(0.01)
# 	print(neuron.voltage)