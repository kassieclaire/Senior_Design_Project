
import pandas as pd
import numpy as np
import scipy.io

from sim_failure_structure import Simulation_Line_History

SIM_STATE_MATRIX = 'case118_f2_r7_t1_e1_i100000_sm.mat'
SIM_INITIAL_FAILURES = 'case118_f2_r7_t1_e1_i100000_if.mat'


def load_state_matrix(states_matrix_name='states', number_of_lines=186):
    # Temporarily loading in matrix
    # the states matrix input -- temporary
    mat = scipy.io.loadmat(states_matrix_name)
    states_column_names = ['Total Line Failures', 'Maximum failed line capacity',
                           'Load shed from previous step', 'Difference in Load Shed',
                           'Load', 'Free Space 1', 'Free Space 2', 'Steady State',
                           'Capacity of Failed Ones', 'Capacity of Failed Ones 2', 'Failed Line Index',
                           'Capacity of Failed One', 'Time of Failure Event',
                           'Accumulation of Failed Capacities', 'Free Space 3', 'Demand-Loadshed Difference',
                           'Free Space 4', 'Generation']
    data = mat['States']
    states_df = pd.DataFrame(data=data, columns=states_column_names)
    states_df = states_df.astype({'Total Line Failures': int, 'Maximum failed line capacity': float,
                                  'Load shed from previous step': float, 'Difference in Load Shed': float,
                                  'Load': float, 'Free Space 1': int, 'Free Space 2': int, 'Steady State': int,
                                  'Capacity of Failed Ones': float, 'Capacity of Failed Ones 2': float, 'Failed Line Index': int,
                                  'Capacity of Failed One': float, 'Time of Failure Event': float,
                                  'Accumulation of Failed Capacities': float, 'Free Space 3': int, 'Demand-Loadshed Difference': float,
                                  'Free Space 4': int, 'Generation': float})
    states_df.drop(columns=['Free Space 1', 'Free Space 2',
                   'Free Space 3', 'Free Space 4'], inplace=True)

    return states_df

    # # Save the dataframe
    # states_df.to_csv(r'states_dataframe.csv', index=False)
    # states_simple_df = states_df.copy()
    # states_simple_df.to_csv(r'states_simple.csv', index=False)
    # states_simple_df.drop(columns=['Maximum failed line capacity',
    #                                'Load shed from previous step', 'Difference in Load Shed',
    #                                'Load', 'Capacity of Failed Ones', 'Capacity of Failed Ones 2', 'Failed Line Index',
    #                                'Capacity of Failed One', 'Time of Failure Event', 'Demand-Loadshed Difference',
    #                                'Generation'], inplace=True)
    # total_states = [0] * (number_of_lines + 1)
    # stable_states = [0] * (number_of_lines + 1)
    # for index, row in states_df.iterrows():
    #     #print(row['Total Line Failures'])
    #     total_line_failures = int(row['Total Line Failures'])
    #     steady_state = int(row['Steady State'])
    #     if(total_line_failures > 0):
    #         total_states[total_line_failures] = total_states[total_line_failures] + 1
    #         if (steady_state == -1):
    #             stable_states[total_line_failures] = stable_states[total_line_failures] + 1
    # cascade_stop = [0]*(number_of_lines + 1)
    # for i in range(number_of_lines):
    #     if (total_states[i] != 0):
    #         cascade_stop[i] = stable_states[i]/total_states[i]


def load_initial_failures(initial_failure_table_name='initial_failures', number_of_lines=186):
    # cell of arrays containing the initial failures for each iteration
    initial_failures_mat = scipy.io.loadmat(initial_failure_table_name)
    # print(initial_failures_mat['Initial_Failure_Table'])
    initial_failures_arrays = [
        l.tolist() for l in initial_failures_mat['Initial_Failure_Table']]
    # print(initial_failures_arrays[:10])
    # change initial failure matrix into list of lists
    initial_failures = [l.tolist()[0] for l in initial_failures_arrays[0]]

    return initial_failures
    # print(initial_failures)
    # print(mat)
    # print(states_df)
    # print("Iteration track = ", iteration_track) #check, should be the number of iterations run
    # print(cluster_failures)
    # print(cluster_failures_topological_factors)
    # Cascading Failure Curve Code
    # Plotting code
    # cascading_failure_df = pd.DataFrame(
    #     {'x_values': range(0, number_of_lines+1), 'cascade_stop': cascade_stop})
    # return cascading_failure_df


# def generate_simulation_history_array(state_matrix, initial_failures) -> 'list[Simulation_Line_History]':

#     for i, single_sim_init_failures in enumerate(initial_failures):
#         print(i, single_sim_init_failures)

if __name__ == '__main__':
    state_matrix = load_state_matrix(SIM_STATE_MATRIX)
    initial_failures = load_initial_failures(SIM_INITIAL_FAILURES)

    # state_matrix = state_matrix[:100]
    initial_failures = initial_failures[:100]

    # print(state_matrix['Failed Line Index'])
    print(max(state_matrix['Failed Line Index']))
    print(initial_failures)

    # generate_simulation_history_array(state_matrix, initial_failures)
    print(state_matrix.shape)
    # print([state_matrix['Failed Line Index'][i]
    #   for i in range(state_matrix.shape[0])])
