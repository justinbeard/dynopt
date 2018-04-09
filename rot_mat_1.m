function [pn_dot,pe_dot,h_dot] = rot_mat_1(phi,theta,psi,u,v,w)

rotmax = [cos(theta)*cos(psi),sin(phi)*sin(theta)*cos(psi)-cos(theta)*sin(psi),cos(phi)*sin(theta)*cos(psi)+sin(theta)*sin(psi);...
    cos(theta)*cos(psi),sin(phi)*sin(theta)*sin(psi)+cos(theta)*cos(psi),cos(phi)*sin(theta)*sin(psi)-sin(phi)*cos(psi);...
    sin(theta),-sin(phi)*cos(theta),-cos(phi)*cos(theta)];

dirmat = [u;v;w];

output = rotmax*dirmat;

pn_dot = output(1);
pe_dot = output(2);
h_dot = output(3);

end