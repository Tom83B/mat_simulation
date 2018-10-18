from pyneuron import ShotNoiseConductance, MATThresholds, Neuron, sr_experiment
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

thresholds = [-60, -60, -60, -60]

RS = MATThresholds(
    alpha1=30,
    alpha2=2,
    tau1=10,
    tau2=200,
    omega=thresholds[0],
    refractory_period=2,
    name='RS')

IB = MATThresholds(
    alpha1=7.5,
    alpha2=1.5,
    tau1=10,
    tau2=200,
    omega=thresholds[1],
    refractory_period=2,
    name='IB')

FS = MATThresholds(
    alpha1=10,
    alpha2=0.2,
    tau1=10,
    tau2=200,
    omega=thresholds[2],
    refractory_period=2,
    name='FS')

CH = MATThresholds(
    alpha1=-0.5,
    alpha2=0.4,
    tau1=10,
    tau2=200,
    omega=thresholds[3],
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

def obtain_sr(seed, B, tw):
    func = partial(intensity_freq_func, B=B)
    return sr_experiment(neuron, tw, 0.1, intensities, func, seed)

def sersum(serlist):
    tmp = serlist[0]
    for ser in serlist[1:]:
        tmp = tmp + ser
    return tmp

intensities = np.random.permutation(np.repeat(np.logspace(0, 1.6, 100), 500))

res_dict = {}

n_jobs = cpu_count()
p = Pool(n_jobs)

for tw in [1000, 750, 500, 250]:
    print(tw)
    res_dict[tw] = {}
    for B in [0, 0.2, 0.4, 0.6, 0.8, 1]:
        func = partial(obtain_sr, B=B, tw=tw)
        # results = func(1)
        results = p.map(func, range(n_jobs))
        res_dict[tw][B] = sersum(results)

def merge_results(res_dict):
    tobeser = {}

    for k1, item in res_dict.items():
        for k2, subitem in item.items():
            for ix, lst in subitem.iteritems():
                index = (k1, k2, *ix)
                tobeser[index] = lst
                
    return pd.Series(tobeser)

res = merge_results(res_dict)
res.to_pickle('test.pkl')
