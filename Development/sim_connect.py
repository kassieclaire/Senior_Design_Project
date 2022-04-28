from generate_states_dataframe import generate_states_df
from enum import Enum
import os
import sys
import subprocess
from unittest import case
from load_sim_data import load_initial_failures

# defines for executables -- make sure to include path, etc.
windows_executable = ".\\sim_executable\\cascading_failure_simulator.exe"
mac_executable = ""
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


class SimulationStatus(Enum):
    NOT_RUN = 0  # for simulations that have not been run
    RUNNING = 1  # for simulations that are currently running
    COMPLETE = 2  # for simulations that have been run but not loaded
    LOADING = 3  # for simulations that are currently having their matrices loaded
    LOADED = 4  # for simulations that have been loaded into memory of the python program


class Simulation:
    def __init__(self, case_name, iterations, initial_failures, load_generation_ratio, load_shed_constant, estimation_error, batch_size=16) -> None:
        self.case_name = case_name
        self.iterations = iterations
        self.initial_failures = initial_failures
        self.load_generation_ratio = load_generation_ratio
        self.load_shed_constant = load_shed_constant
        self.estimation_error = estimation_error
        self.batch_size = batch_size
        self.output_name = self.__generate_output_name(
            case_name, initial_failures, load_generation_ratio, load_shed_constant, estimation_error, iterations)
        self.state_matrix = None
        self.initial_failure_array = None
        # if the simulation files exist, mark the simulation as complete (but not loaded), otherwise mark it as not run
        if os.path.exists(self.output_name + "_sm.mat") and os.path.exists(self.output_name + "_if.mat"):
            self.status = SimulationStatus.COMPLETE
            self.fraction_complete = 1.0
        else:
            self.status = SimulationStatus.NOT_RUN
            self.fraction_complete = 0.0

    def __get_fraction(self, num):
        return str(num).split('.')[1]

    def __generate_output_name(self, case_name, initial_failures, load_generation_ratio, load_shed_constant, estimation_error, iterations):
        output_name = f"{case_name}_f{initial_failures}_r{self.__get_fraction(load_generation_ratio)}_t" + \
            f"{self.__get_fraction(load_shed_constant)}_e{self.__get_fraction(estimation_error)}_i{iterations}"
        return output_name

    def get_output_name(self):
        return self.output_name

    def get_simulation_status(self) -> SimulationStatus:
        return self.status

    def get_fraction_complete(self) -> float:
        """
        Returns the fraction of the simulation that has been completed.
        :return: float value in range [0, 1] that represents the fraction of the simulation that has been completed.
        """
        return self.fraction_complete

    def get_states_dataframe(self):
        """
        Returns the state matrix dataframe for the simulation if the simulation is loaded, otherwise returns None.
        """
        if self.status == SimulationStatus.LOADED:
            return self.state_matrix
        else:
            return None

    def get_initial_failure_array(self):
        """
        Returns the initial failures arrays for the simulation if the simulation is loaded, otherwise returns None.
        """
        if self.status == SimulationStatus.LOADED:
            return self.initial_failure_array
        else:
            return None

    def __get_argument_array(self):
        return [self.case_name, str(self.iterations), str(self.initial_failures), str(self.load_generation_ratio), str(self.load_shed_constant), str(self.estimation_error), self.output_name, str(self.batch_size)]

    def run_simulation(self):
        """
        Calls the matlab executable to run the simulation.
        """
        if self.status != SimulationStatus.NOT_RUN:
            print("Simulation has already been run.")
            return
        self.status = SimulationStatus.RUNNING
        self.fraction_complete = 0.0
        # call the matlab executable
        argString = " ".join(self.__get_argument_array())
        # argString = f"{self.case_name} {self.iterations} {self.initial_failures} {self.load_generation_ratio} {self.load_shed_constant} {self.estimation_error} {self.output_name} {self.batch_size}"
        if sys.platform == "win32":
            # TODO add a warning if the runtime is not installed
            print(argString)
            # TODO run the simulation as a subprocess
            #subprocess.run([windows_executable, arguments])
            os.system(f"{windows_executable} {argString}")
            # return output_name
        elif sys.platform == "linux" or sys.platform == "linux2":
            # TODO add a warning if the runtime is not installed
            print("Work on Linux platform still in progress.")
            # if output_name is None:
            #     output_name = get_output_name(
            #         case_name, initial_failures, load_generation_ratio, load_shed_constant, estimation_error, iterations)
            # argString = f"{case_name} {iterations} {initial_failures} {load_generation_ratio} {load_shed_constant} {estimation_error} {output_name} {batch_size}"
            print(argString)
            os.system(f"{linux_executable} {argString}")
            # return output_name
        elif sys.platform == "darwin":
            print("Work on Mac platform is still in progress")
            # if output_name is None:
            #     output_name = get_output_name(
            #         case_name, initial_failures, load_generation_ratio, load_shed_constant, estimation_error, iterations)
            # argString = f"{case_name} {iterations} {initial_failures} {load_generation_ratio} {load_shed_constant} {estimation_error} {output_name} {batch_size}"
            print(argString)
            os.system(f"{mac_executable} {argString}")
            # return output_name
            # return 0
        else:
            print("Unknown platform: ", sys.platform)
            return

        self.status = SimulationStatus.COMPLETE
        self.fraction_complete = 1.0

    def load_simulation(self):
        if self.status != SimulationStatus.COMPLETE:
            print("Simulation has not been run or has already been loaded.")
            return
        self.status = SimulationStatus.LOADING
        self.state_matrix = generate_states_df(
            states_matrix_name=self.output_name + "_sm.mat", initial_failure_table_name=self.output_name + "_if.mat")
        self.initial_failure_array = load_initial_failures(
            self.output_name + "_if.mat")
        self.status = SimulationStatus.LOADED

    def simulate_and_load(self):
        self.run_simulation()
        self.load_simulation()


def __get_fraction(num):
    return str(num).split('.')[1]


def __generate_output_name(case_name, initial_failures, load_generation_ratio, load_shed_constant, estimation_error, iterations):
    output_name = f"{case_name}_f{initial_failures}_r{__get_fraction(load_generation_ratio)}_t" + \
        f"{__get_fraction(load_shed_constant)}_e{__get_fraction(estimation_error)}_i{iterations}"
    return output_name


def run_simulation(case_name, iterations, initial_failures, load_generation_ratio, load_shed_constant, estimation_error, batch_size, output_name=None):
    if sys.platform == "win32":
        # TODO add a warning if the runtime is not installed
        if output_name is None:
            output_name = __generate_output_name(
                case_name, initial_failures, load_generation_ratio, load_shed_constant, estimation_error, iterations)
        arguments = f"{case_name} {iterations} {initial_failures} {load_generation_ratio} {load_shed_constant} {estimation_error} {output_name} {batch_size}"
        print(arguments)
        # run the simulation as a subprocess
        #subprocess.run([windows_executable, arguments])
        os.system(f"{windows_executable} {arguments}")
        return output_name
    elif sys.platform == "linux" or sys.platform == "linux2":
        # TODO add a warning if the runtime is not installed
        print("Work on Linux platform still in progress.")
        if output_name is None:
            output_name = __generate_output_name(
                case_name, initial_failures, load_generation_ratio, load_shed_constant, estimation_error, iterations)
        arguments = f"{case_name} {iterations} {initial_failures} {load_generation_ratio} {load_shed_constant} {estimation_error} {output_name} {batch_size}"
        print(arguments)
        os.system(f"{linux_executable} {arguments}")
        return output_name
    elif sys.platform == "darwin":
        print("Work on Mac platform is still in progress")
        if output_name is None:
            output_name = __generate_output_name(
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
