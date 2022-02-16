import os
import sys
from unittest import case
# defines
executable = "..\\..\\..\\sim_executable\\cascading_failure_simulator.exe"
# simulations to run and their settings
batch_sizes = [64, 64]
case_names = ["case118", "case118"]
iterations_list = [10000, 10000]
# f: initial failures
f_list = [2, 2]
# load generation ration
r_list = [.7, .8]
# e: estimation error
e_list = [.1, .2]
# theta: load shed const
theta_list = [.1, .2]
# for i in range(len(batch_sizes)):
#     output_name = case_names[i] + "_" + str(f_list[i]) + "_" + str(r_list[i]).split(
#         '.')[1] + "_" + str(theta_list[i]).split('.')[1] + "_" + str(e_list[i]).split('.')[1]
#     arguments = case_names[i] + " " + str(iterations_list[i]) + " " + str(f_list[i]) + " " + str(
#         r_list[i]) + " " + str(theta_list[i]) + " " + str(e_list[i]) + " " + output_name + " " + str(batch_sizes[i])
#     print(arguments)
#     os.system(executable + " " + arguments)

print(executable)


def __get_fraction(num):
    return str(num).split('.'[1])


def get_output_name(case_name, initial_failures, load_generation_ratio, load_shed_constant, estimation_error):
    output_name = f"{case_name}_{initial_failures}_{__get_fraction(load_generation_ratio)}_" + \
        f"{__get_fraction(load_shed_constant)}_{__get_fraction(estimation_error)}"
    return output_name


print(get_output_name("case118", 1, 2, .7, .1, 0.2, "out", 100))


def run_simulation(case_name, iterations, initial_failures, load_generation_ratio, load_shed_constant, estimation_error, output_name, batch_size):
    print("blah")
    output_name = get_output_name(
        case_name, initial_failures, load_generation_ratio, load_shed_constant, estimation_error)
