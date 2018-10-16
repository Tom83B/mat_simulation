#include "neuron.h"

using namespace std;

class Simulation {
	vector<double> voltage;
	ShotNoiseConductance exc, inh;

public:
	Simulation(Neuron, ShotNoiseConductance, ShotNoiseConductance);
	void run(double, double, double, double);  // time, dt, exc_rate, inh_rate
	Neuron neuron;
};