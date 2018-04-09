
from gekko import GEKKO
import numpy as np

time = np.loadtxt('time.csv', delimiter=',')

x_aruco, y_aruco, z_aruco = np.loadtxt('rcbc.csv', delimiter=',', unpack='true')
phi_aruco, theta_aruco, psi_aruco = np.loadtxt('estimateangles.csv', delimiter=',', unpack='true')


x_euler, y_euler, z_euler = np.loadtxt('rcbb.csv', delimiter=',', unpack='true')

phi_euler, theta_euler, psi_euler = np.loadtxt('eulerangles.csv', delimiter=',', unpack='true')

#%% Model

#Initialize model
m = GEKKO()

m.time = time

x_euler_model = m.CV(value = x_euler)
y_euler_model = m.CV(value = y_euler)
z_euler_model = m.CV(value = z_euler)
phi_euler_model = m.CV(value = phi_euler)
theta_euler_model = m.CV(value = theta_euler)
psi_euler_model = m.CV(value = psi_euler)

x_aruco_model = m.CV(value = x_aruco)
y_aruco_model = m.CV(value = y_aruco)
z_aruco_model = m.CV(value = z_aruco)
phi_aruco_model = m.CV(value = phi_aruco)
theta_aruco_model = m.CV(value = theta_aruco)
psi_aruco_model = m.CV(value = psi_aruco)

x_offset = m.MV(value = 0)
y_offset = m.MV(value = 0)
z_offset = m.MV(value = 0)
phi_offset = m.MV(value = 0)
theta_offset = m.MV(value = 0)
psi_offset = m.MV(value = 0)


m.Equation(0 == x_euler_model - x_aruco_model + x_offset)
m.Equation(0 == y_euler_model - y_aruco_model + y_offset)
m.Equation(0 == z_euler_model - z_aruco_model + z_offset)
m.Equation(0 == phi_euler_model - phi_aruco_model + phi_offset)
m.Equation(0 == theta_euler_model - theta_aruco_model + theta_offset)
m.Equation(0 == psi_euler_model - psi_aruco_model + psi_offset)

# Solve options
rmt = True # Remote: True or False
# For rmt=True, specify server
m.server = 'http://byu.apmonitor.com'

#time array 
m.time = np.arange(50)

#Parameters
u = m.Param(value=42)
d = m.FV(value=0)
Cv = m.Param(value=1)
tau = m.Param(value=0.1)

#Variable
flow = m.CV(value=42)

#Equation 
m.Equation(tau * flow.dt() == -flow + Cv * u + d)

# Options
m.options.imode = 5
m.options.ev_type = 1 #start with l1 norm
m.options.coldstart = 1
m.options.solver = 1  # APOPT solver

d.status = 1
flow.fstatus = 1
flow.wmeas = 100
flow.wmodel = 0
#flow.dcost = 0

# Initialize L1 application
m.solve(remote=rmt)

#%% Other Setup
# Create storage for results
xtrue = x * np.ones(n_iter+1)
z = x * np.ones(n_iter+1)
time = np.zeros(n_iter+1)
xb = np.empty(n_iter+1)
x1mhe = np.empty(n_iter+1)
x2mhe = np.empty(n_iter+1)

# initial estimator values
x0 = 40
xb[0] = x0
x1mhe[0] = x0
x2mhe[0] = x0

# outliers
for i in range(n_iter+1):
    z[i] = x + (random.random()-0.5)*2.0
z[50] = 100
z[100] = 0

#%% L1 Application

## Cycle through measurement sequentially
for k in range(1, n_iter+1):
    print( 'Cycle ' + str(k) + ' of ' + str(n_iter))
    time[k] = k

    # L1-norm MHE
    flow.meas = z[k] 
    m.solve(remote=rmt)
    x1mhe[k] = flow.model

print("Finished L1")
#%% L2 application

#clear L1//
m.clear_data()
# Options for L2
m.options.ev_type = 2 #start with l1 norm
m.options.coldstart = 1 #reinitialize

flow.wmodel = 10

# Initialize L2 application
m.solve(remote=rmt)

## Cycle through measurement sequentially
for k in range(1, n_iter+1):
    print ('Cycle ' + str(k) + ' of ' + str(n_iter))
    time[k] = k

    # L2-norm MHE
    flow.meas = z[k] 
    m.solve(remote=rmt)
    x2mhe[k] = flow.model

#%% Filtered bias update

## Cycle through measurement sequentially
for k in range(1, n_iter+1):
    print ('Cycle ' + str(k) + ' of ' + str(n_iter))
    time[k] = k

    # filtered bias update
    xb[k] = alpha * z[k] + (1.0-alpha) * xb[k-1] 


#%% plot results
import matplotlib.pyplot as plt
plt.figure(1)
plt.plot(time,z,'kx',linewidth=2)
plt.plot(time,xb,'g--',linewidth=3)
plt.plot(time,x2mhe,'k-',linewidth=3)
plt.plot(time,x1mhe,'r.-',linewidth=3)
plt.plot(time,xtrue,'k:',linewidth=2)
plt.legend(['Measurement','Filtered Bias Update','Sq Error MHE','l_1-Norm MHE','Actual Value'])
plt.xlabel('Time (sec)')
plt.ylabel('Flow Rate (T/hr)')
plt.axis([0, time[n_iter], 32, 45])
plt.show()