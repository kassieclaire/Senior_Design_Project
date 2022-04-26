#import os and sys
import os, sys

#function which organizes simulation data into its respective folder
def organize_simulation(simulation_name, debug = False):
    #create a folder named Simulation_Data if it doesn't exist already
    if not os.path.exists('Simulation_Data'):
        os.makedirs('Simulation_Data')
    #create a folder named Simulation_Data/[simulation_name] if it doesn't exist already
    if not os.path.exists('Simulation_Data' + os.sep +  simulation_name):
        os.makedirs('Simulation_Data' + os.sep +  simulation_name)
    #create a folder named Simulation_Data/[simulation_name]/[simulation_name]_tops if it doesn't exist already
    if not os.path.exists('Simulation_Data' + os.sep +  simulation_name + os.sep + simulation_name + '_tops'):
        os.makedirs('Simulation_Data' + os.sep +  simulation_name + os.sep + simulation_name + '_tops')
    #move the states file named [simulation_name]_sm to the Simulation_Data/[simulation_name] folder
    os.rename('Simulation_Data' + os.sep +  simulation_name + os.sep + simulation_name + '_sm', 'Simulation_Data' + os.sep +  simulation_name + os.sep + simulation_name + '_sm')
    #move the initial_failures file named [simulation_name]_if to the Simulation_Data/[simulation_name] folder
    os.rename('Simulation_Data' + os.sep +  simulation_name + os.sep + simulation_name + '_if', 'Simulation_Data' + os.sep +  simulation_name + os.sep + simulation_name + '_if')
    #move the dataframe file named [simulation_name]_df to the Simulation_Data/[simulation_name] folder
    os.rename('Simulation_Data' + os.sep +  simulation_name + os.sep + simulation_name + '_df', 'Simulation_Data' + os.sep +  simulation_name + os.sep + simulation_name + '_df')
    #move the pstop file named [simulation_name]_pstop to the Simulation_Data/[simulation_name] folder
    os.rename('Simulation_Data' + os.sep + simulation_name + os.sep + simulation_name + '_pstop', 'Simulation_Data' +os.sep + simulation_name + os.sep + simulation_name + '_pstop')
    #move the simulation log file named [simulation_name]_log to the Simulation_Data/[simulation_name] folder
    os.rename('Simulation_Data' + os.sep +  simulation_name + os.sep + simulation_name + '_log', 'Simulation_Data' + os.sep +  simulation_name + os.sep + simulation_name + '_log')
    #move the end of simulation topology file named [simulation_name]_top to the Simulation_Data/[simulation_name]/[simulation_name]_tops folder
    os.rename('Simulation_Data' + os.sep + simulation_name + os.sep + simulation_name + '_tops' + os.sep + simulation_name + '_top', 'Simulation_Data_tops' + os.sep + simulation_name + os.sep + simulation_name + '_tops' + os.sep + simulation_name + '_top')
