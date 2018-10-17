from pyneuron import ShotNoiseConductance, MATThresholds, Neuron, sr_experiment, steady_spike_train
import numpy as np
import pandas as pd
from functools import partial
from multiprocessing import Pool, cpu_count


exc = ShotNoiseConductance(
    rate=2.67,
    g_peak=0.0015,
    reversal=0,
    decay=3)

inh = ShotNoiseConductance(
    rate=3.73,
    g_peak=0.0015,
    reversal=-75,
    decay=10)

RS = MATThresholds(
    alpha1=30,
    alpha2=2,
    tau1=10,
    tau2=200,
    omega=-65,
    refractory_period=2,
    name='RS')

IB = MATThresholds(
    alpha1=7.5,
    alpha2=1.5,
    tau1=10,
    tau2=200,
    omega=-64.3,
    refractory_period=2,
    name='IB')

FS = MATThresholds(
    alpha1=10,
    alpha2=0.2,
    tau1=10,
    tau2=200,
    omega=-62.4,
    refractory_period=2,
    name='FS')

CH = MATThresholds(
    alpha1=-0.5,
    alpha2=0.4,
    tau1=10,
    tau2=200,
    omega=-61.8,
    refractory_period=2,
    name='CH')

neuron = Neuron(
    resting_potential=-80,
    membrane_resistance=50,
    membrane_capacitance=0.1,
    mats=[RS, IB, FS, CH])

neuron.append_conductance(exc)
neuron.append_conductance(inh)


def intensity_freq_func(intensity, B):
    exc = 2.67 * intensity
    inh = 3.73 * (1 + B * (intensity - 1))
    return exc, inh

def process_spike_train(spike_train, time_window, tot_time, offset=0):
    spike_counts = []
    
    time = offset

    while time + time_window <= tot_time:
        spike_counts.append(((spike_train >= time) & (spike_train < time + time_window)).sum())
        time += time_window
    
    return spike_counts

def obtain_spike_counts(B):
    spike_counts = {}

    for intensity in np.logspace(0, 1.6, 50):
        exc_intensity, inh_intensity = intensity_freq_func(intensity, B)
        
        neuron.time = 0
        offset = 1000
        tot_time = 1000 * 10 + offset
        spike_trains = steady_spike_train(neuron, tot_time, 0.1, exc_intensity, inh_intensity)
        
        for neuron_name, spike_train in spike_trains.items():
            for tw in [250, 500, 750, 1000]:
                ix = (tw, neuron_name, B, intensity)
                spike_counts[ix] = process_spike_train(spike_train, tw, tot_time, offset)

    return spike_counts


n_jobs = cpu_count()
p = Pool(n_jobs)

results = p.map(obtain_spike_counts, np.linspace(0, 1, 6))
        # res_dict[tw][B] = sersum(results)
result_dict = {}
for res in results:
    result_dict = {**result_dict, **res}

pd.Series(result_dict).to_pickle('steady_stimulus_noise_scan.pkl')


# res.to_pickle('test.pkl')
