#include <iostream>
#include <vector>
#include <cmath>
#include <fstream>
#include <functional>

namespace physcalc {
    constexpr double G = 6.67430e-11;
    //modified rk4 method to work with vector of doubles and a derivative function
    std::vector<double> rk4(
        const std::vector<double>& y,
        double dt,
        std::function<std::vector<double>(const std::vector<double>&)> deriv)
    {
        std::vector<double> k1 = deriv(y);
        std::vector<double> y2(y.size());
        for (size_t i = 0; i < y.size(); ++i)
            y2[i] = y[i] + 0.5 * dt * k1[i];
        std::vector<double> k2 = deriv(y2);
        for (size_t i = 0; i < y.size(); ++i)
            y2[i] = y[i] + 0.5 * dt * k2[i];

        std::vector<double> k3 = deriv(y2);
        for (size_t i = 0; i < y.size(); ++i)
            y2[i] = y[i] + dt * k3[i];

        std::vector<double> k4 = deriv(y2);
        std::vector<double> result(y.size());
        for (size_t i = 0; i < y.size(); ++i)
            result[i] = y[i] + (dt / 6.0) *
                (k1[i] + 2*k2[i] + 2*k3[i] + k4[i]);

        return result;
    }
    //Euler method
    std::vector<double> euler(
        const std::vector<double>& y,
        double dt,
        std::function<std::vector<double>(const std::vector<double>&)> deriv)
    {
        std::vector<double> dydt = deriv(y);
        std::vector<double> result(y.size());

        for (size_t i = 0; i < y.size(); ++i)
            result[i] = y[i] + dt * dydt[i];
        return result;
    }
    // derivative with any amount of planets chosen.
    std::vector<double> n_body_derivative(
        const std::vector<double>& state,
        const std::vector<double>& masses)
    {
        const int N = masses.size();
        std::vector<double> dydt(6*N, 0.0);

        // dx/dt = v
        for (int i = 0; i < N; ++i) {
            dydt[6*i + 0] = state[6*i + 3];
            dydt[6*i + 1] = state[6*i + 4];
            dydt[6*i + 2] = state[6*i + 5];
        }

        // dv/dt = gravitational acceleration
        for (int i = 0; i < N; ++i) {

            double xi = state[6*i + 0];
            double yi = state[6*i + 1];
            double zi = state[6*i + 2];

            double ax = 0.0;
            double ay = 0.0;
            double az = 0.0;

            for (int j = 0; j < N; ++j) {
                if (i == j) continue;

                double dx = state[6*j + 0] - xi;
                double dy = state[6*j + 1] - yi;
                double dz = state[6*j + 2] - zi;

                double eps = 1e-5; // softening
                double r = std::sqrt(dx*dx + dy*dy + dz*dz + eps*eps);

                double factor = G * masses[j] / (r*r*r);

                ax += factor * dx;
                ay += factor * dy;
                az += factor * dz;
            }

            dydt[6*i + 3] = ax;
            dydt[6*i + 4] = ay;
            dydt[6*i + 5] = az;
        }

        return dydt;
    }
}

class Planet {
private:
    const double mass;
    const double radius;
    std::vector<double> position;
    std::vector<double> velocity;

public:
    Planet(double m, double r,
           const std::vector<double>& pos,
           const std::vector<double>& vel)
        : mass(m), radius(r), position(pos), velocity(vel) {}

    double get_mass() const { return mass; }
    const std::vector<double>& get_position() const { return position; }
    const std::vector<double>& get_velocity() const { return velocity; }

    void set_position(const std::vector<double>& pos) { position = pos; }
    void set_velocity(const std::vector<double>& vel) { velocity = vel; }
};

int main() {

    bool use_rk4 = false;

    double m = 1e23;
    double r = 10.0;
    double R = 300000.0;
    double v = std::sqrt(physcalc::G * m / R);

    Planet p1(m, r,
        { R, 0.0, 0.0 },
        { 0.0,  1.1*v, 0.0 });
    Planet p2(2*m, r,
        { -R/2.0,  std::sqrt(3)*R/2.0, 0.0 },
        { -1.2*v*std::sqrt(3)/2.0, -v/2.0, 0.0 });

    Planet p3(1.1*m, r,
        { -R/2.0, -std::sqrt(3)*R/2.0, 0.0 },
        { v*std::sqrt(3)/2.0, -v/2.0, 0.0 });

    std::vector<Planet> planets = {p1, p2, p3};

    int N = planets.size();
    double dt = 0.1;
    //Add more planets if needed, change this to have 4 and then go to the if statement below to add output in the txt for the Nth planet
    std::ofstream f1("planet12.txt");
    std::ofstream f2("planet22.txt");
    std::ofstream f3("planet32.txt");
    // Mass vector
    std::vector<double> masses;
    for (const auto& p : planets)
        masses.push_back(p.get_mass());

    auto deriv = [&](const std::vector<double>& state)
    {
        return physcalc::n_body_derivative(state, masses);
    };

    for (int step = 0; step < 500000; ++step) {

        std::vector<double> state(6*N);
        for (int i = 0; i < N; ++i) {
            const auto& pos = planets[i].get_position();
            const auto& vel = planets[i].get_velocity();

            state[6*i+0] = pos[0];
            state[6*i+1] = pos[1];
            state[6*i+2] = pos[2];
            state[6*i+3] = vel[0];
            state[6*i+4] = vel[1];
            state[6*i+5] = vel[2];
        }

        std::vector<double> next;
        if (use_rk4)
            next = physcalc::rk4(state, dt, deriv);
        else
            next = physcalc::euler(state, dt, deriv);

        for (int i = 0; i < N; ++i) {
            planets[i].set_position(
                { next[6*i+0], next[6*i+1], next[6*i+2] });

            planets[i].set_velocity(
                { next[6*i+3], next[6*i+4], next[6*i+5] });
        }
        if (N >= 3) {
            const auto& p1p = planets[0].get_position();
            const auto& p2p = planets[1].get_position();
            const auto& p3p = planets[2].get_position();
            f1 << p1p[0] << " " << p1p[1] << "\n";
            f2 << p2p[0] << " " << p2p[1] << "\n";
            f3 << p3p[0] << " " << p3p[1] << "\n";
        }
    }

    return 0;
}
