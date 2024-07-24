import numpy as np
import matplotlib.pyplot as plt
from cstr_reactor import simulate_cstr, cstr  # Ensure cstr is imported
from scipy.integrate import odeint

# PID parameters and initial conditions
Kc = 9.23461230362
tauI = 0.22836124114
tauD = 0.0

# Control loop
def pid_control(T_ss, u_ss, t, Tf, Caf, x0):
    # u_ss = 300 
    # T_ss = 324.475443431599
    # Tf = 1 
    # Caf = 350 
    op = np.ones(len(t)) * u_ss
    sp = np.ones(len(t)) * T_ss
    u = np.ones(len(t)) * u_ss
    op = np.ones(len(t)) * u_ss
    P = np.zeros(len(t))
    I = np.zeros(len(t))
    D = np.zeros(len(t))
    dpv = np.zeros(len(t))
    pv = np.zeros(len(t))

    #sp[0] = 300 to start and then increase by 7 every 20 steps 
    for i in range(15):
        sp[i * 20:(i + 1) * 20] = 300 + i * 7.0
    sp[300] = sp[299]
    e = np.zeros(len(t))
    ie = np.zeros(len(t))
    dpv = np.zeros(len(t))
    
    # x0 = [0.87725294608097, 324.475443431599]
    # So Ca[0] = 0.87725294608097,
    # T[0] = 324.475443431599
    Ca = np.ones(len(t)) * x0[0]
    T = np.ones(len(t)) * x0[1]

    #T[0] = 324.475443431599
    T[0] = T_ss

    plt.figure(figsize=(10, 7))
    plt.ion()
    plt.show()

    for i in range(len(t) - 1):
        # [0. 0.03333]
        # delta_t = 0.03333
        delta_t = t[i + 1] - t[i]
        # e[0] = 300 - 324.475443431599 = -24.475443431599
        e[i] = sp[i] - T[i]
   
        if i >= 1:
            # ie is showing as 0.8158481143866329610 not the value below wtf 
            # ie[1] = 0 + -24.475443431599 * 0.033 = −0.8076896332427671.
            ie[i] += e[i] * delta_t   
            dpv[i] = (pv[i] - pv[i - 1]) / delta_t

        P[i] = Kc * e[i]
        I[i] = Kc / tauI * ie[i]
        D[i] = -Kc * tauD * dpv[i]
        op[i] = op[0] + P[i] + I[i] + D[i]
        # op is showing as 250     
        # op[1] = 300.0 + 9.23461230362 * -24.475443431599 + (-24.475443431599 * 0.033) / 0.22836124114 = 
        # op[i] = op[0] + Kc * e[i] + ie[i] / tauI
        # u[1] = 300.0 
        u[i + 1] = op[i]

        x0 = [Ca[i], T[i]]
        ts = [t[i], t[i + 1]]

        y = simulate_cstr(x0, ts, u[i + 1], Tf, Caf)
        Ca[i + 1] = y[-1][0]
        T[i + 1] = y[-1][1]

        plt.clf()
        plt.subplot(3, 1, 1)
        plt.plot(t[:i + 1], sp[:i + 1], 'r--', label='Setpoint')
        plt.plot(t[:i + 1], T[:i + 1], 'b-', label='Process Variable (Reactor Temp)')
        plt.ylabel('Reactor Temperature (C)')
        plt.legend(loc='best')

        plt.subplot(3, 1, 2)
        plt.plot(t[:i + 1], op[:i + 1], 'k-', label='Control Output (Cooling Jacket Temp)')
        plt.ylabel('Cooling Jacket Temperature (C)')
        plt.xlabel('Time (sec)')
        plt.legend(loc='best')

        plt.subplot(3, 1, 3)
        plt.plot(t[:i + 1], Ca[:i + 1], 'g-', label='Concentration Ca')
        plt.ylabel('Concentration Ca')
        plt.xlabel('Time (sec)')
        plt.legend(loc='best')

        plt.pause(0.01)

    op[-1] = op[-2]
    ie[-1] = ie[-2]

    data = np.vstack((t, u, T, Ca, op, ie)).T
    header = 'Time,u_control_output,T_Reactor_Temperature,Ca_Concentration_Reactor,op_Cooling_Jacket_Temperature,ie_Integral_of_Error'
    np.savetxt('data_doublet_steps.txt', data, delimiter=',', header=header, comments='')

    plt.ioff()
    plt.show()

    return u, T

# Main execution
if __name__ == "__main__":
    # [0. 0.03333 0.06667 0.1 0.13333 0.16667 0.2 0.23333 0.26667 0.3]
    t = np.linspace(0, 10, 301)
    x0 = [0.87725294608097, 324.475443431599]
    u_ss = 300.0
    T_ss = 324.475443431599

    u, T = pid_control(T_ss, u_ss, t, 350, 1, x0)
