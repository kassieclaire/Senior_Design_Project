import os
import sys
import subprocess
from unittest import case
# defines for executables -- make sure to include path, etc.
windows_executable = ".\\sim_executable\\cascading_failure_simulator.exe"
mac_executable = "./sim_executable_mac/run_cascading_failure_simulator.sh"
mac_matlab_loc = "/Applications/MATLAB_R2021b.app"
linux_executable = "./sim_executable_linux/run_cascading_failure_simulator.sh /usr/local/MATLAB/MATLAB_Runtime/v911/"
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
        # TODO add a warning if the runtime is not installed
        if output_name is None:
            output_name = get_output_name(
                case_name, initial_failures, load_generation_ratio, load_shed_constant, estimation_error, iterations)
        arguments = f"{case_name} {iterations} {initial_failures} {load_generation_ratio} {load_shed_constant} {estimation_error} {output_name} {batch_size}"
        print(arguments)
        #run the simulation as a subprocess with a live output out
        proc = subprocess.Popen(windows_executable + " " + arguments, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        #return the output name and the pipe out of the process
        return output_name, proc.stdout
    elif sys.platform == "linux" or sys.platform == "linux2":
        # TODO add a warning if the runtime is not installed
        print("Work on Linux platform still in progress.")
        if output_name is None:
            output_name = get_output_name(
                case_name, initial_failures, load_generation_ratio, load_shed_constant, estimation_error, iterations)
        arguments = f"{case_name} {iterations} {initial_failures} {load_generation_ratio} {load_shed_constant} {estimation_error} {output_name} {batch_size}"
        print(arguments)
        #run the simulation as a subprocess with a live output out
        proc = subprocess.Popen(linux_executable + " " + arguments, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        #return the output name and the pipe out of the process
        return output_name, proc.stdout
    elif sys.platform == "darwin":
        print("Work on Mac platform is still in progress")
        if output_name is None:
            output_name = get_output_name(
                case_name, initial_failures, load_generation_ratio, load_shed_constant, estimation_error, iterations)
        #arguments = f"{mac_matlab_loc} {case_name} {iterations} {initial_failures} {load_generation_ratio} {load_shed_constant} {estimation_error} {output_name} {batch_size}"
        arguments = [mac_executable, mac_matlab_loc, case_name, str(iterations), str(initial_failures), str(load_generation_ratio), str(load_shed_constant), str(estimation_error), output_name, str(batch_size)]
        print(arguments)
        #run the simulation as a subprocess with a live output out
        proc = subprocess.Popen(args=arguments, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        #return the output name and the pipe out of the process
        return output_name, proc
    else:
        print("Unknown platform: ", sys.platform)
        return 0


# print(run_simulation("case118", 10, 1, 0.7, 0.1, 0.1, 2, "blah"))
