from apm import *
import numpy as np
import random
import matplotlib.pyplot as plt
import time

# initial parameters
n_iter = 150 # number of cycles
x = 37.727 # true value
# filtered bias update
alpha = 0.0951
# mhe tuning
horizon = 30

# Select server
server = 'http://byu.apmonitor.com'
# Application names
app1 = 'mhe1'
app2 = 'mhe2'
# Clear previous application
apm(server,app1,'clear all')
apm(server,app2,'clear all')
# Load model and horizon
apm_load(server,app1,'valve.apm')
apm_load(server,app2,'valve.apm')
horizon = 50
apm_option(server,app1,'apm.ctrl_hor',50)
apm_option(server,app1,'apm.pred_hor',50)
apm_option(server,app2,'apm.ctrl_hor',50)
apm_option(server,app2,'apm.pred_hor',50)
# Load classifications
apm_info(server,app1,'FV','d')
apm_info(server,app2,'FV','d')
apm_info(server,app1,'CV','flow')
apm_info(server,app2,'CV','flow')
# Options
apm_option(server,app1,'apm.imode',5)
apm_option(server,app2,'apm.imode',5)
apm_option(server,app1,'apm.ev_type',1)
apm_option(server,app2,'apm.ev_type',2)
apm_option(server,app1,'d.STATUS',1)
apm_option(server,app2,'d.STATUS',1)
apm_option(server,app1,'flow.FSTATUS',1)
apm_option(server,app2,'flow.FSTATUS',1)
apm_option(server,app1,'flow.WMEAS',100)
apm_option(server,app2,'flow.WMEAS',100)
apm_option(server,app1,'flow.WMODEL',0)
apm_option(server,app2,'flow.WMODEL',10)
apm_option(server,app1,'flow.dcost',0)
apm_option(server,app2,'flow.dcost',0)
apm_option(server,app1,'apm.coldstart',1)
apm_option(server,app2,'apm.coldstart',1)
apm_option(server,app1,'apm.web_plot_freq',5)
apm_option(server,app2,'apm.web_plot_freq',5)
# Initialize both L1 and L2 applications
apm(server,app1,'solve')
apm(server,app2,'solve')
apm_option(server,app1,'apm.coldstart',0)
apm_option(server,app2,'apm.coldstart',0)

# Create storage for results
xtrue = x * np.ones(n_iter+1)
z = x * np.ones(n_iter+1)
timer = np.zeros(n_iter+1)
xb = np.empty(n_iter+1)
x1mhe = np.empty(n_iter+1)
x2mhe = np.empty(n_iter+1)

# initial estimator values
x0 = 40
xb[0] = x0
x1mhe[0] = x0
x2mhe[0] = x0

# add noise
for i in range(len(z)):
    z[i] = z[i] + (random.random()-0.5)*2.0
# outliers
z[50] = 100
z[100] = 0

# Create plot
plt.figure(figsize=(10,7))
plt.ion()
plt.show()

start_time = time.time()
prev_time = start_time

## Cycle through measurement sequentially
for k in range(1, n_iter+1):
    print('Cycle ' + str(k) + ' of ' + str(n_iter))
    
    # Sleep time
    sleep_max = 1.0
    sleep = sleep_max - (time.time() - prev_time)
    if sleep>=0.01:
            time.sleep(sleep-0.01)
    else:
            time.sleep(0.01)

    timer[k] = k

    # filtered bias update
    xb[k] = alpha * z[k] + (1.0-alpha) * xb[k-1] 
    
    # L2-norm MHE
    apm_meas(server,app2,'flow',z[k])
    sol2 = apm(server,app2,'solve')
    x2mhe[k] = apm_tag(server,app2,'flow.model')
        
    # L1-norm MHE
    apm_meas(server,app1,'flow',z[k])
    sol1 = apm(server,app1,'solve')
    x1mhe[k] = apm_tag(server,app1,'flow.model')

    # Plot
    plt.clf()
    ax=plt.subplot(1,1,1)
    ax.grid()
    plt.plot(timer[0:k],z[0:k],'kx',linewidth=2)
    plt.plot(timer[0:k],xb[0:k],'g--',linewidth=3)
    plt.plot(timer[0:k],x2mhe[0:k],'k-',linewidth=3)
    plt.plot(timer[0:k],x1mhe[0:k],'r.-',linewidth=3)
    plt.plot(timer[0:k],xtrue[0:k],'k:',linewidth=2)
    plt.legend(['Measurement','Filtered Bias Update',\
                'Sq Error MHE','l_1-Norm MHE', \
                'Actual Value'])
    plt.xlabel('Time (sec)')
    plt.ylabel('Flow Rate (T/hr)')
    plt.axis([0, timer[k], 32, 45])
    plt.draw()
    plt.pause(0.05)

apm_web(server,app1)
apm_web(server,app2)
