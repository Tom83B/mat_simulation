#ifndef NEURON_H
#define NEURON_H
using namespace std;

class ShotNoiseConductance {
	double rate, g_peak, decay;

	public:
		ShotNoiseConductance();
		ShotNoiseConductance(double, double, double, double);
		void update(double);
		void set_rate(double);
		double g, reversal;
};

class MATThresholds {
	double alpha1, alpha2, tau1, tau2, omega, t1, t2, refractory_period, past_spike_time;
	vector<double> spike_times;

	public:
		MATThresholds();
		MATThresholds(double, double, double, double, double, double);
		void fire(double);
		void update(double);
		vector<double> get_spike_times();
		void reset_spike_times();
		double threshold;
};

class Neuron {
	double resting_potential, membrane_resistance, membrane_capacitance, time_constant, time;

	public:
		Neuron();
		Neuron(double, double, double, vector<MATThresholds*>);
		void append_conductance(ShotNoiseConductance*);
		void integrate_voltage(double);
		void timestep(double);
		vector<ShotNoiseConductance*> conductances;
		vector<MATThresholds*> mats;
		double voltage;

};

#endif