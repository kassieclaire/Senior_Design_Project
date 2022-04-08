%% Problem B 
close all;
clear all;

num=[0.9];
den=[1 2 1 0];

g=tf(num,den);
gd=c2d(g,0.2,'impulse')
[gm,pm]=margin(gd)

margin(gd)
