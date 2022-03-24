import matplotlib.pyplot as plt
from p_stop_curve import cascading_failure_function
import sim_connect
import os
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
#Matplotlib helper function
def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg
#draw a basic plot using initial settings
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

#draw a more plot using inputs
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
    # generate the graph
    p_stop_df = cascading_failure_function(
        states_matrix_name=name + "_sm", initial_failure_table_name=name + "_if")
    fig = plt.figure()
    plt.plot('x_values', 'cascade_stop', data=p_stop_df,
             color='skyblue', linewidth=1)
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