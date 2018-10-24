from pyneuron import MATThresholds

thresholds = [-65, -64.3, -62.4, -61.8]

mat_parameters = {
    'RS': {
        'alpha1': 30,
        'alpha2': 2,
        'tau1': 10,
        'tau2': 200,
        'omega': thresholds[0],
        'refractory_period': 2,
        'name': 'RS'
    },
    'IB': {
        'alpha1': 7.5,
        'alpha2': 1.5,
        'tau1': 10,
        'tau2': 200,
        'omega': thresholds[1],
        'refractory_period': 2,
        'name': 'IB'
    },
    'FS': {
        'alpha1': 10,
        'alpha2': 0.2,
        'tau1': 10,
        'tau2': 200,
        'omega': thresholds[2],
        'refractory_period': 2,
        'name': 'FS'
    },
    'CH': {
        'alpha1': -0.5,
        'alpha2': 0.4,
        'tau1': 10,
        'tau2': 200,
        'omega': thresholds[3],
        'refractory_period': 2,
        'name': 'CH'
    },
}

def get_mat(mat_name):
    params = mat_parameters[mat_name]
    mat = MATThresholds(**params)
    return mat