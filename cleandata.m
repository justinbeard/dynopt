close all
clear all
clc

%% Load Data
load('calibdata.mat')

%% Correlate Data
[C,ia,ib] = intersect(estimate_time,euler_truth_time);

new_estimate_time=estimate_time(ia);
new_estimate_position=estimate_position(ia,:);
new_estimate_rpy=estimate_rpy(ia,:);
new_euler_truth_time=euler_truth_time(ib);
new_truth_position=truth_position(ib,:);
new_euler_truth_rpy=euler_truth_rpy(ib,:);

%% Rotate camera frame
n = length(new_estimate_time);
rci = zeros(3,1);
rbi = zeros(3,1);
rcbc = zeros(n,3);
rcbb = zeros(n,3);

for i = 1:n
    rci = [new_estimate_position(i,1);new_estimate_position(i,2);new_estimate_position(i,3)];
    rbi = [new_truth_position(i,1);new_truth_position(i,2);new_truth_position(i,3)];
    rtemp = rci-rbi;
    rotmatx = rotationmat(new_estimate_rpy(i,1),new_estimate_rpy(i,2),new_estimate_rpy(i,3));
    rcbc(i,:) = rotmatx*rtemp;
end

for j = 1:n
    delphi = new_estimate_rpy(j,1) - new_euler_truth_rpy(j,1);
    deltheta = new_estimate_rpy(j,2) - new_euler_truth_rpy(j,2);
    delpsi = new_estimate_rpy(j,3) - new_euler_truth_rpy(j,3);
    
    rotmatx = rotationmat(delphi,deltheta,delpsi);
    
    rcbb(j,:) = rotmatx\rcbc(j,:).';
end

plot(new_euler_truth_time, rcbb(:,1), 'r-',...
     new_euler_truth_time, rcbb(:,2), 'g-',...
     new_euler_truth_time, rcbb(:,3), 'b-',...
     new_euler_truth_time, rcbc(:,1), 'r--',...
     new_euler_truth_time, rcbc(:,2), 'g--',...
     new_euler_truth_time, rcbc(:,3), 'b--')
ylabel('m')
legend('x_{ArUco}','y_{ArUco}','z_{ArUco}','x','y','z')

csvwrite('rcbc.csv',rcbc)
csvwrite('rcbb.csv',rcbb)
csvwrite('estimateangles.csv',new_estimate_rpy)
csvwrite('eulerangles.csv',new_euler_truth_rpy)
csvwrite('time.csv',new_estimate_time)

function rxy = rotationmat(phi,theta,psi)
% This function inputs phi, theta, and psi (roll, pitch, and yaw), creating
%a custom rotation matrix (3x3) with the different angles given.

rpsi=[cos(psi),sin(psi),0;-sin(psi),cos(psi),0;0,0,1];
rtheta=[cos(theta),0,-sin(theta);0,1,0;sin(theta),0,cos(theta)];
rphi=[1,0,0;0,cos(phi),sin(phi);0,-sin(phi),cos(phi)];

rxy=rpsi*rtheta*rphi;
end