import matplotlib.pyplot as plt
from generate_mpc_plot_networkx import plot_network
from p_stop_curve import cascading_failure_function
from pStop_Generic import generate_generic_pStop
import generate_mpc_plot_networkx
from generate_states_dataframe import generate_states_df
from load_sim_data import load_initial_failures
import sim_connect
import os
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import generate_mpc_plot_networkx
# Matplotlib helper function


def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg
# draw a basic plot using initial settings


def draw_plot():
    p_stop_df = cascading_failure_function()
    fig = plt.figure()
    plt.plot('x_values', 'cascade_stop', data=p_stop_df,
             color='skyblue', linewidth=1)
    plt.xlabel('Number of Failed Lines')
    plt.ylabel('Cascade-Stop Probability')
    # show legend
    plt.legend()
    # set title
    plt.title = "Cascade-Stop Probability vs Number of Line Failures"
    #plt.plot([0.1, 0.2, 0.5, 0.7])
    # plt.show(block=False)
    return fig

# draw a more plot using inputs


def run_button_action(fig, case_name, iterations, initial_failures, load_generation_ratio, load_shed_constant, estimation_error, batch_size):
    """
    docstring
    TODO update this
    """
    # step 1: get the name
    name = sim_connect.get_output_name(
        case_name, initial_failures, load_generation_ratio, load_shed_constant, estimation_error, iterations)
    # if the simulation has not been run with the current settings, run the simulation
    if not os.path.exists(name + "_sm.mat"):
        print("Simulation with current settings has not been run, running simulation.")
        sim_connect.run_simulation(case_name, iterations, initial_failures, load_generation_ratio,
                                   load_shed_constant, estimation_error, batch_size, output_name=name)
    else:
        print('Simulation with current settings already performed, loading matrices.')
    # generate the df
    states_df = generate_states_df(states_matrix_name=name + "_sm", initial_failure_table_name=name + "_if", clusters_matrix_name='cluster_branch_118',
                                   number_of_lines=186, use_test_cluster=False, output_df_name="states_dataframe", use_simplified_df=False, save_as_csv=False)
    # generate the df using pstop_generic
    p_stop_df = generate_generic_pStop(states_df=states_df)
    # generate the graph
    #fig = plt.figure()
    plt.plot('x_values', 'cascade_stop', data=p_stop_df,
             color='skyblue', linewidth=5)
    plt.xlabel('Number of Failed Lines')
    plt.ylabel('Cascade-Stop Probability')
    # plt.title('Cascade-Stop Probability vs Number of Line Failures')
    # show legend
    plt.legend()
    # set title
    plt.title = "Cascade-Stop Probability vs Number of Line Failures"
    plt.autoscale()
    #plt.plot([0.1, 0.2, 0.5, 0.7])
    # plt.show(block=False)
    return fig


def simple_run_button_action(fig, case_name, iterations, initial_failures, load_generation_ratio, load_shed_constant, estimation_error, batch_size):
    """
    docstring
    TODO update this
    """
    #tempoary fix: create process variable
    graph_data = None
    process = None
    # get branch data
    # step 1: get the name
    name = sim_connect.get_output_name(
        case_name, initial_failures, load_generation_ratio, load_shed_constant, estimation_error, iterations)
    # if the simulation has not been run with the current settings, run the simulation
    if not os.path.exists(name + "_sm.mat"):
        print("Simulation with current settings has not been run, running simulation.")
        _, process = sim_connect.run_simulation(case_name, iterations, initial_failures, load_generation_ratio,
                                   load_shed_constant, estimation_error, batch_size, output_name=name)
    else:
        print('Simulation with current settings already performed, loading matrices.')
        graph_data, fig = initially_plot_network(name, fig)
    return name, graph_data, fig, process
#function that only does the graphing part of the simple run button action
def initially_plot_network(name, fig):
    #generate the df
    states_df = generate_states_df(states_matrix_name=name + "_sm", initial_failure_table_name=name + "_if", clusters_matrix_name='cluster_branch_118',
                                      number_of_lines=186, use_test_cluster=False, output_df_name="states_dataframe", use_simplified_df=False, save_as_csv=False)
    #load the initial failures
    initial_failures = load_initial_failures(
        initial_failure_table_name=name + "_if", number_of_lines=186)
    #get the graph data
    graph_data = generate_mpc_plot_networkx.TopologyIterationData(
        states_df, initial_failures, f'{name}_mpc_presim.mat')
    #set the simulation iteration to 0
    simIteration = 0
    #generate the topology plot
    fig = graph_data.plot_topology(
        graph_data.get_iteration_index_with_most_failures(), 0, fig)
    return graph_data, fig
