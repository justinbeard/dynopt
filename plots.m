load('calibdata.mat')

% Compare position data

subplot(2,1,1)
plot(estimate_time, estimate_position(:,1), 'r-',...
     estimate_time, estimate_position(:,2), 'g-',...
     estimate_time, estimate_position(:,3), 'b-',...
     truth_time, truth_position(:,1), 'r--',...
     truth_time, truth_position(:,2), 'g--',...
     truth_time, truth_position(:,3), 'b--')
ylabel('m')
legend('x_{ArUco}','y_{ArUco}','z_{ArUco}','x','y','z')

% compare angle data

subplot(2,1,2)
plot(estimate_time, estimate_rpy(:,1), 'r-',...
     estimate_time, estimate_rpy(:,2), 'g-',...
     estimate_time, estimate_rpy(:,3), 'b-',...
     euler_truth_time, euler_truth_rpy(:,1), 'r--',...
     euler_truth_time, euler_truth_rpy(:,2), 'g--',...
     euler_truth_time, euler_truth_rpy(:,3), 'b--')
ylabel('rad')
xlabel('time (s)')
legend('\phi_{ArUco}','\theta_{ArUco}','\psi_{ArUco}','x','y','z')