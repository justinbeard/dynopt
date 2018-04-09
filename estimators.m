clear all; close all; clc

% intial parameters
n_iter = 150; % number of measurements
x = 37.727; % true value

% Generate output and state noise
s1 = 0.1;
s2 = 1.0;
r1 = rand(n_iter,1);
r2 = rand(n_iter,1);
n1 = norminv(r1,0.0,s1);
n2 = norminv(r2,0.0,s2);
z = x + n1 + n2;

% Plot Histogram of Random State and Measurement Noise
figure(1)
subplot(2,1,1)
histfit(n1,20)
h = get(gca,'Children');
set(h(2),'FaceColor',[.8 .8 1])
legend('State Noise Distribution','Normal Distribution')
ylabel('Probability Count')

subplot(2,1,2)
histfit(n2,20)
h = get(gca,'Children');
set(h(2),'FaceColor',[.8 .8 1])
legend('Measurement Noise Distribution','Normal Distribution')
ylabel('Probability Count')
xlabel('Noise Distribution')

% Process and Measurement Variances
Q = s1^2;  % process variance
R = s2^2;  % measurement variance

% intial guesses - initialize all methods to 42.0
xhat(1) = 42.0;
xtrue(1) = x;

% filtered bias update initialization
alpha = 0.0951;
xb(1) = xhat(1);
b(1) = 0;

% kalman filter initialization
P(1) = 0.5;
Pminus(1) = P(1);
xhatminus(1) = xhat(1);

% idf initialization
xidf(1) = xhat(1);
bidf(1) = 0;
Kidf = 0.095e-10;
Tidf = 1.000e-10;
Integral_idf = 0;

% mhe tuning
horizon = 30;

% L1-norm and L2-norm MHE
x1mhe(1) = xhat(1);
x2mhe(1) = xhat(1);
% Add APM functions to path
addpath('apm');
% Select server
server = 'http://byu.apmonitor.com';
% Application names
app1 = 'mhe1';
app2 = 'mhe2';
% Clear previous application
apm(server,app1,'clear all');
apm(server,app2,'clear all');
% Load model and horizon
apm_load(server,app1,'valve.apm');
apm_load(server,app2,'valve.apm');
horizon = 50;
apm_option(server,app1,'apm.ctrl_hor',50);
apm_option(server,app1,'apm.pred_hor',50);
apm_option(server,app2,'apm.ctrl_hor',50);
apm_option(server,app2,'apm.pred_hor',50);
%csv_load(server,app1,'horizon50.csv');
%csv_load(server,app2,'horizon50.csv');
% Load classifications
apm_info(server,app1,'FV','d');
apm_info(server,app2,'FV','d');
apm_info(server,app1,'CV','flow');
apm_info(server,app2,'CV','flow');
% Options
apm_option(server,app1,'apm.imode',5);
apm_option(server,app2,'apm.imode',5);
apm_option(server,app1,'apm.ev_type',1);
apm_option(server,app2,'apm.ev_type',2);
apm_option(server,app1,'d.STATUS',1);
apm_option(server,app2,'d.STATUS',1);
apm_option(server,app1,'flow.FSTATUS',1);
apm_option(server,app2,'flow.FSTATUS',1);
apm_option(server,app1,'flow.WMEAS',100);
apm_option(server,app2,'flow.WMEAS',100);
apm_option(server,app1,'flow.WMODEL',0);
apm_option(server,app2,'flow.WMODEL',10);
apm_option(server,app1,'flow.dcost',0);
apm_option(server,app2,'flow.dcost',0);
apm_option(server,app1,'apm.coldstart',1);
apm_option(server,app2,'apm.coldstart',1);
apm_option(server,app1,'apm.web_plot_freq',5);
apm_option(server,app2,'apm.web_plot_freq',5);
% Initialize both L1 and L2 applications
apm(server,app1,'solve');
apm(server,app2,'solve');

include_outliers = true;
if (include_outliers),
   % outliers
   z(50) = 100;
   z(100) = 0;
end

%% Cycle through measurement sequentially
for k = 2:n_iter,
    disp(['Cycle ' int2str(k) ' of ' int2str(n_iter)]);
    time(k) = k;
    xtrue(k) = x;

    % filtered bias update
    xb(k) = alpha * z(k) + (1-alpha) * xb(k-1); 
    
    % kalman filter update
    % xhat      % a posteri estimate of x
    % P         % a posteri error estimate
    % xhatminus % a priori estimate of x
    % Pminus    % a priori error estimate
    % K         % gain or blending factor
    xhatminus(k) = xhat(k-1);
    Pminus(k) = P(k-1)+Q;
    % measurement update
    K(k) = Pminus(k)/( Pminus(k)+R );
    xhat(k) = xhatminus(k)+K(k)*(z(k)-xhatminus(k));
    P(k) = (1-K(k))*Pminus(k);

    % idf update
    error = z(k)-xidf(k-1);
    Integral_idf = Integral_idf + error;
    % idf bias update
    bidf(k) = (Kidf * error) + ((Kidf / Tidf) * Integral_idf);
    % this is equivalent to filtered bias update when Tidf = 1
    %bidf(k) = ((Kidf / Tidf) * Integral_idf);
    xidf(k) = xidf(1) + bidf(k);

    % L2-norm MHE
    apm_meas(server,app2,'flow',z(k));
    sol2 = apm(server,app2,'solve');
    x2mhe(k) = apm_tag(server,app2,'flow.model');
        
    % L1-norm MHE
    apm_meas(server,app1,'flow',z(k));
    sol1 = apm(server,app1,'solve');
    x1mhe(k) = apm_tag(server,app1,'flow.model');
end

% calculate error band for Kalman filter
for k = 1:n_iter
    % calculate 95% confidence interval
    delta(k) = 1.96 * sqrt(P(k));
end

figure(2)
plot(time,z,'kx','LineWidth',1)
hold on
plot(time,xb,'g--','LineWidth',8)
plot(time,xhat,'b-.','LineWidth',5)
plot(time,xidf,'k:','LineWidth',3)
plot(time,x2mhe,'k-','LineWidth',3)
plot(time,x1mhe,'r.-','LineWidth',3)
plot(time,xtrue,'k:','LineWidth',2)
legend('Measurement','Filtered Bias Update','Kalman Estimate',...
    'IDF^{TM}','Sq Error MHE','l_1-Norm MHE','Actual Value')
xlabel('Time (sec)')
ylabel('Flow Rate (T/hr)')

if (include_outliers),
    axis([0 n_iter 32 50]);
end

figure(3)
plot(time,z,'k.','LineWidth',1)
hold on
plot(time,xhat+delta,'k-','LineWidth',2)
plot(time,xhat,'b-.','LineWidth',3)
plot(time,xhat-delta,'k-','LineWidth',2)
plot(time,xtrue,'k:','LineWidth',2)
legend('Measurement','Kalman 95% Upper CI',...
    'Kalman Estimate','Kalman 95% Lower CI','Actual Value')
xlabel('Time (sec)')
ylabel('Flow Rate (T/hr)')

apm_web(server,app1);
apm_web(server,app2);
