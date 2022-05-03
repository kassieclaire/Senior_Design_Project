# import os and sys
import os
import sys

# function which organizes simulation data into its respective folders


def organize_simulation(simulation_name, debug=False):
    ##Folder Creation##
    # create a folder named Simulation_Data if it doesn't exist already
    if not os.path.exists('Simulation_Data'):
        os.makedirs('Simulation_Data')
    # create a folder named Simulation_Data/[simulation_name] if it doesn't exist already
    if not os.path.exists('Simulation_Data' + os.sep + simulation_name):
        os.makedirs('Simulation_Data' + os.sep + simulation_name)
    # create a folder named Simulation_Data/[simulation_name]/tops if it doesn't exist already
    if not os.path.exists('Simulation_Data' + os.sep + simulation_name + os.sep + 'tops'):
        os.makedirs('Simulation_Data' + os.sep +
                    simulation_name + os.sep + 'tops')

    ##Initial File Copying##
    # move the states file named [simulation_name]_sm to the Simulation_Data/[simulation_name] folder
    os.rename(simulation_name + '_sm.mat', 'Simulation_Data' +
              os.sep + simulation_name + os.sep + simulation_name + '_sm.mat')
    # move the initial_failures file named [simulation_name]_if to the Simulation_Data/[simulation_name] folder
    os.rename(simulation_name + '_if.mat', 'Simulation_Data' +
              os.sep + simulation_name + os.sep + simulation_name + '_if.mat')
    # move the dataframe file named [simulation_name]_df to the Simulation_Data/[simulation_name] folder
    os.rename(simulation_name + '_df.csv', 'Simulation_Data' +
              os.sep + simulation_name + os.sep + simulation_name + '_df.csv')
    # move the pstop file named [simulation_name]_pstop to the Simulation_Data/[simulation_name] folder
    os.rename(simulation_name + '_pstop.csv', 'Simulation_Data' +
              os.sep + simulation_name + os.sep + simulation_name + '_pstop.csv')
    # move the simulation log file named [simulation_name]_log to the Simulation_Data/[simulation_name] folder
    os.rename(simulation_name + '_log.txt', 'Simulation_Data' +
              os.sep + simulation_name + os.sep + simulation_name + '_log.txt')

    ##Top File Copying##
    # move the top files with names file_x in folder_mpc to the Simulation_Data/[simulation_name]/[simulation_name]_tops folder
    for file in os.listdir('folder_mpc'):
        # grab the second part of the filename after the underscore minus the .mat, which is the iteration number
        iteration_number = file.split('_')[1].split('.')[0]
        # move the file to the Simulation_Data/[simulation_name]/tops folder and rename it appropriately
        os.rename('folder_mpc' + os.sep + file, 'Simulation_Data' + os.sep + simulation_name +
                  os.sep + 'tops' + os.sep + simulation_name + f"_n{iteration_number}_top.mat")

# return whether the simulation folder exists or not


def simulation_folder_exists(simulation_name):
    return os.path.exists('Simulation_Data' + os.sep + simulation_name)
# return a string of the states matrix file name


def get_states_matrix_file_name(simulation_name):
    return 'Simulation_Data' + os.sep + simulation_name + os.sep + simulation_name + '_sm.mat'
# return a string of the initial failures matrix file name


def get_initial_failures_matrix_file_name(simulation_name):
    return 'Simulation_Data' + os.sep + simulation_name + os.sep + simulation_name + '_if.mat'
# return a string of the dataframe file name


def get_dataframe_file_name(simulation_name):
    return 'Simulation_Data' + os.sep + simulation_name + os.sep + simulation_name + '_df.csv'
# return a string of the pstop file name


def get_pstop_file_name(simulation_name):
    return 'Simulation_Data' + os.sep + simulation_name + os.sep + simulation_name + '_pstop.csv'
# return a string of the top file name


def get_top_file_name(simulation_name, iteration_number):
    return 'Simulation_Data' + os.sep + simulation_name + os.sep + 'tops' + os.sep + simulation_name + f"_n{iteration_number}_top.mat"
