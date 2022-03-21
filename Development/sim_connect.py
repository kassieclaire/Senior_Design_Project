import os
import sys
from unittest import case
# defines
windows_executable = ".\\sim_executable\\cascading_failure_simulator.exe"
mac_executable = ""
# simulations to run and their settings
# batch_sizes = [64, 64]
# case_names = ["case118", "case118"]
# iterations_list = [10000, 10000]
# # f: initial failures
# f_list = [2, 2]
# # load generation ration
# r_list = [.7, .8]
# # e: estimation error
# e_list = [.1, .2]
# # theta: load shed const
# theta_list = [.1, .2]
# # for i in range(len(batch_sizes)):
# #     output_name = case_names[i] + "_" + str(f_list[i]) + "_" + str(r_list[i]).split(
# #         '.')[1] + "_" + str(theta_list[i]).split('.')[1] + "_" + str(e_list[i]).split('.')[1]
# #     arguments = case_names[i] + " " + str(iterations_list[i]) + " " + str(f_list[i]) + " " + str(
# #         r_list[i]) + " " + str(theta_list[i]) + " " + str(e_list[i]) + " " + output_name + " " + str(batch_sizes[i])
# #     print(arguments)
# #     os.system(executable + " " + arguments)

# print(executable)


def __get_fraction(num):
    return str(num).split('.')[1]


def get_output_name(case_name, initial_failures, load_generation_ratio, load_shed_constant, estimation_error, iterations):
    output_name = f"{case_name}_f{initial_failures}_r{__get_fraction(load_generation_ratio)}_t" + \
        f"{__get_fraction(load_shed_constant)}_e{__get_fraction(estimation_error)}_i{iterations}"
    return output_name


def run_simulation(case_name, iterations, initial_failures, load_generation_ratio, load_shed_constant, estimation_error, batch_size, output_name=None):
    if sys.platform == "win32":
        if output_name is None:
            output_name = get_output_name(
                case_name, initial_failures, load_generation_ratio, load_shed_constant, estimation_error, iterations)
        arguments = f"{case_name} {iterations} {initial_failures} {load_generation_ratio} {load_shed_constant} {estimation_error} {output_name} {batch_size}"
        print(arguments)
        os.system(f"{windows_executable} {arguments}")
        return output_name
    elif sys.platform == "linux" or sys.platform == "linux2":
        print("Work on Linux platform still in progress.")
        if output_name is None:
            output_name = get_output_name(
                case_name, initial_failures, load_generation_ratio, load_shed_constant, estimation_error, iterations)
        arguments = f"{case_name} {iterations} {initial_failures} {load_generation_ratio} {load_shed_constant} {estimation_error} {output_name} {batch_size}"
        print(arguments)
        os.system(f"{executable} {arguments}")
        return output_name
    elif sys.platform == "darwin":
        print("Work on Mac platform is still in progress")
        if output_name is None:
            output_name = get_output_name(
                case_name, initial_failures, load_generation_ratio, load_shed_constant, estimation_error, iterations)
        arguments = f"{case_name} {iterations} {initial_failures} {load_generation_ratio} {load_shed_constant} {estimation_error} {output_name} {batch_size}"
        print(arguments)
        os.system(f"{mac_executable} {arguments}")
        return output_name
        return 0
    else:
        print("Unknown platform: ", sys.platform)
        return 0


# print(run_simulation("case118", 10, 1, 0.7, 0.1, 0.1, 2, "blah"))
