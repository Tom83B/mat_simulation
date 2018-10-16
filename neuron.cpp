#include <iostream>
#include <cstdlib>
#include <vector>
#include <cmath>
#include <ctime>
#include "neuron.h"
using namespace std;

int poisson_rand(double rate) {
	double randu = ((double) rand() / (RAND_MAX));
	double cummulation = 0;
	double pmf = exp(-rate);
	int poisson_rand = 0;

	// cout << endl << "randu: " << randu << endl;

	while (randu > cummulation) {
		// cout << "cummulation" << cummulation << endl;
		cummulation += pmf;
		poisson_rand += 1;
	    pmf *= rate / poisson_rand;
	}
	// cout << "finished with   " << cummulation << endl;

	return poisson_rand - 1;
}

ShotNoiseConductance::ShotNoiseConductance() {}

ShotNoiseConductance::ShotNoiseConductance(double rate, double g_peak, double reversal, double decay) {
	srand(std::time(nullptr));

	this->rate = rate;
	this->g_peak = g_peak;
	this->reversal = reversal;
	this->decay = decay;
	this->g = 0;
}

void ShotNoiseConductance::update(double dt) {
	int n_spikes = poisson_rand(rate);
	g += n_spikes * g_peak;
	g *= exp(-dt / decay);
}

void ShotNoiseConductance::set_rate(double rate) {
	this->rate = rate;
}

MATThresholds::MATThresholds(double alpha1, double alpha2, double tau1, double tau2, double omega, double refractory_period) {
	this->alpha1 = alpha1;
	this->alpha2 = alpha2;
	this->tau1 = tau1;
	this->tau2 = tau2;
	this->omega = omega;
	this->refractory_period = refractory_period;

	t1 = 0;
	t2 = 0;
	threshold = t1 + t2 + omega;
	past_spike_time = refractory_period;
}

void MATThresholds::fire(double time) {
	if (past_spike_time >= refractory_period) {
		t1 += alpha1;
		t2 += alpha2;
		spike_times.push_back(time);
		past_spike_time = 0;
	}
}

void MATThresholds::update(double dt) {
	past_spike_time += dt;
	t1 *= exp(-dt / tau1);
	t2 *= exp(-dt / tau2);
	threshold = t1 + t2 + omega;
}

vector<double> MATThresholds::get_spike_times() {
	return spike_times;
}

void MATThresholds::reset_spike_times() {
	vector<double> spike_times;
	this->spike_times = spike_times;
}

Neuron::Neuron() {}

Neuron::Neuron(double resting_potential, double membrane_resistance, double membrane_capacitance, vector<MATThresholds*> mats) {
	this->resting_potential = resting_potential;
	this->membrane_resistance = membrane_resistance;
	this->membrane_capacitance = membrane_capacitance;
	this->mats = mats;

	voltage = resting_potential;
	time_constant = membrane_capacitance * membrane_resistance;
	time = 0;
}

void Neuron::append_conductance(ShotNoiseConductance* conductance) {
	conductances.push_back(conductance);
}

void Neuron::integrate_voltage(double dt) {
	double tot_conductance = 0;
	double tot_gr = 0;
	double factor;

	// for (int i=0; i<conductances.size(); i++) {
	for (auto c : conductances) {
		tot_conductance += c->g;

		// cout << "conductance " << i << ":  " << conductances[i]->g << endl;
		// cout << conductances[i]->reversal << ":  " << tot_conductance << "   ";
		tot_gr += c->g * c->reversal;
	}
	// cout << endl;

	factor = 1. / dt + (1. + membrane_resistance * tot_conductance) / time_constant;
	// cout << voltage << "   factor: " << factor << "   dt: " << dt << "   tot_cond: " << tot_conductance << "   ";
    voltage = (voltage / dt + (resting_potential + membrane_resistance * tot_gr) / time_constant) / factor;
    // cout << voltage << endl;
}

void Neuron::timestep(double dt) {
	time += dt;

	for (auto c : conductances) {
		c->update(dt);
	}

	this->integrate_voltage(dt);

	for (auto mat : mats) {
		mat->update(dt);
		if (mat->threshold <= voltage) {
			mat->fire(time);
		}
	}
}

// int main(int argc, char const *argv[])
// {
// 	srand(time(nullptr));

// 	MATThresholds mat(10, 1, 10, 200, -60, 2);
// 	vector<MATThresholds*> mats;
// 	mats.push_back(&mat);

// 	Neuron neuron(-80, 50, 0.1, mats);
// 	ShotNoiseConductance exc (10, 0.0015, 0, 3);
// 	ShotNoiseConductance inh (5, 0.0015, -75, 10);

// 	neuron.append_conductance(&inh);
// 	neuron.append_conductance(&exc);

// 	for (int i=0; i<10000000; i++) {
// 		neuron.timestep(0.1);
// 		if (i % 10000 == 0) cout << i << endl;
// 		// cout << neuron.voltage << "   " << neuron.mats[0]->threshold << endl;
// 	}

// 	cout << mat.get_spike_times().size();

// 	return 0;
// }