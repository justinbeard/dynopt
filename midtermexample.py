

import gekko 
import numpy as np
import matplotlib.pyplot as plt

# Write data
boat = '''time,rpm,x
0.00,0.00,0.00
1.00,4007.30,0.00
2.00,4076.12,3.96
3.00,4032.04,9.59
4.00,5018.40,8.84
5.00,5033.08,25.65
6.00,5085.69,33.06
7.00,2084.71,38.92
8.00,2002.84,51.49
9.00,2082.02,64.40
10.00,2091.07,78.46
11.00,2074.44,88.33
12.00,2002.35,89.96
13.00,2013.06,107.71
14.00,0.00,117.54
15.00,0.00,121.15
16.00,0.00,131.14
17.00,0.00,130.36
18.00,0.00,138.19
19.00,0.00,147.58
20.00,0.00,150.32
21.00,0.00,155.60
22.00,0.00,155.86
23.00,0.00,152.69
24.00,0.00,163.63
25.00,0.00,167.09
26.00,0.00,166.98
27.00,0.00,170.07
28.00,0.00,172.09
29.00,0.00,170.63
30.00,0.00,175.21
'''

fid = open('boat.csv','w')
fid.write(boat)
fid.close()

#%% Model

#initialize model
m = gekko.GEKKO()

#set time
m.time = np.linspace(0,30,31)

#set parameters
m_boat = m.Param(value=500)
dens = m.Param(value=1000)
Cd = m.Param(value=0.05)
Ac = m.Param(value=0.8)

m_passengers = m.FV(value=400)
RPM = m.MV(lb=0,ub=5000)

#Variables
Fd = m.Var(value=0) #drag force
Fp = m.Var(value=0) #propeller force
x = m.CV(value=0) #position
v = m.CV(value=0) #velocity
a = m.Var(value=0) #acceleration

#Equations
m.Equation(Fd == 1/2 * dens * v**2 * Cd * Ac)
m.Equation(Fp == 40 * m.sqrt(RPM))
m.Equation(x.dt() == v)
m.Equation(v.dt() == a)
m.Equation((m_boat+m_passengers)*a == Fp - Fd)

## Simulation

m.options.IMODE = 4 #simulation
m.options.NODES = 3
m.options.TIME_SHIFT = 0 #allow resolving without timeshift
#don't use .MEAS to update values
RPM.FSTATUS = 0
m_passengers.FSTATUS = 0
v.FSTATUS = 0
x.FSTATUS = 0

#set RPM to jump from 0 to 5000 at time=1
RPM.value = np.ones(np.size(m.time))*5000
RPM.value[0:5]=0

#initially set passengers to 0
m_passengers.value = 0

m.solve(disp=False)

plt.figure(1)
plt.plot(m.time,v.value,'k--')
print("Velocity at time 6: ", v.value[10])

#add passengers
m_passengers.value = 400

m.solve(disp=False)
plt.plot(m.time,v.value,'r-')
print("Velocity at time 6: ", v.value[10])

#%% Estimation
#initialize model
m = gekko.GEKKO()

#set time
m.time = np.linspace(0,30,31)

#set parameters
m_boat = m.Param(value=500)
dens = m.Param(value=1000)
Cd = m.Param(value=0.05)
Ac = m.Param(value=0.8)

m_passengers = m.FV(value=400)
RPM = m.MV(lb=0,ub=5000)

#Variables
Fd = m.Var(value=0) #drag force
Fp = m.Var(value=0) #propeller force
x = m.CV(value=0) #position
v = m.CV(value=0) #velocity
a = m.Var(value=0) #acceleration

#Equations
m.Equation(Fd == 1/2 * dens * v**2 * Cd * Ac)
m.Equation(Fp == 40 * m.sqrt(RPM))
m.Equation(x.dt() == v)
m.Equation(v.dt() == a)
m.Equation((m_boat+m_passengers)*a == Fp - Fd)

#load data from csv
m.time, RPM.value, x.value = np.loadtxt('boat.csv', \
                delimiter=',',skiprows=1,unpack=True)
time, RPM_data, x_data = np.loadtxt('boat.csv', \
                delimiter=',',skiprows=1,unpack=True)

#set options
m.options.IMODE = 5 #Dynamic estimation
m.options.EV_TYPE = 2
RPM.STATUS = 0
v.STATUS = 0
m_passengers.STATUS = 1
x.STATUS = 1
x.WMODEL = 0

m.solve(disp=False)


plt.figure(2)
plt.subplot(3,1,1)
plt.plot(m.time,x.value,'r-')
plt.scatter(m.time,x_data)
plt.ylabel('x')
plt.subplot(3,1,2)
plt.plot(m.time,v.value,'k--')
plt.ylabel('v')
plt.subplot(3,1,3)
plt.plot(m.time,RPM.value,'b-')
plt.scatter(m.time,RPM_data)
plt.ylabel('RPM')
plt.xlabel('time')