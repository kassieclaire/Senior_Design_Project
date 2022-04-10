# function imports
import sim_connect
from p_stop_curve import cascading_failure_function
from draw_plot import draw_plot, run_button_action, draw_figure
# from plot_topology import plot_topology
import generate_mpc_plot_networkx
import load_sim_data
# package imports
import os
import matplotlib
from matplotlib.ticker import NullFormatter  # useful for `logit` scale
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import PySimpleGUI as sg
from json import load
from tkinter.tix import TEXT
import networkx as nx
import tkinter as tk
from tkinter import filedialog
import shutil


# color and size specifications
TEXT_COLOR = '#000000'
BACKGROUND_COLOR = '#FFFFFF'
INPUT_BOX_SIZE = (25, 1)
INPUT_FRAME_SIZE = (300, 60)
# slider keys
SLIDER_ITERATIONS = 'iterations'
SLIDER_LOAD = 'slider_load'
SLIDER_INITIAL_FAILURES = 'slider_init_failures'
SLIDER_LOAD_SHED_CONST = 'slider_load_shed_const'
SLIDER_CAPACITY_ESTIMATION_ERROR = 'slider_line_cap_uncertainty'
MPC_PATH = 'case118_mpc_presim.mat'
SIM_STATE_MATRIX = 'case118_f2_r7_t1_e1_i100000_sm.mat'
SIM_INITIAL_FAILURES = 'case118_f2_r7_t1_e1_i100000_if.mat'
# Figure keys
FIGURE = 'figure_1'
# column keys
COLUMN_INPUT = 'input_column'
COLUMN_OUTPUT = 'output_column'
#descriptions and tooltips
description = " This is a Graphical User Interface \n for the SACE lab's cascading failure simulator, \n which simulates line failures in a grid \n after a number of initial failures"
# Tooltips
load_tooltip = "This is the load-generation ratio for the grid. \n" + \
    "1.0 represents the sum of the loads being equivalant to the max generation capacity\n" + \
    "and 0.0 represents no load"
operator_constraints_tooltip = "This represents the constraints to which grid operators are held when making load-shedding decisions. \n" + \
    "0.0 represents no load-shedding constraints, while 1.0 represents no load-shedding allowed"
error_tooltip = "This represents the estimation error operators have when determining the highest capacity of a line. \n" + \
    "0.0 represents perfect knowledge of line capacities, 1.0 represents minimum knowledge of line capacities"
initial_failures_tooltip = "This is the number of random line failures that occur at the start of the simulation."

# Temporarily defined values TODO: Actually calculate these per run!
cap_loss = 1500
delivery_loss_percent = 8
worst_cluster = 4
num_lines = 186


def simple_gui(debug=False):
    # setup beforehand
    matplotlib.use('TkAgg')
    sg.theme('LightGrey1')

    menu_def = [
        ['&File', ['&Save Figure', '&Save Simple DF', '&Save States.mat', '&Save DF']]]

    # columns
    input_column = [[sg.Frame('Cascading Failure Simulation', [[sg.Text(description)]], border_width=10)],
                    [sg.Frame('Load', [[sg.Slider(orientation='horizontal', key=SLIDER_LOAD, range=(
                        0.0, 1.0), tooltip=load_tooltip, resolution=0.05)]], border_width=10)],
                    [sg.Frame('Initial Line Failures', [[sg.Slider(range=(0, 50), tooltip=initial_failures_tooltip, orientation='horizontal',
                                                                   key=SLIDER_INITIAL_FAILURES)]], border_width=10)],
                    [sg.Frame('Operator Constraints', [[sg.Slider(orientation='horizontal', key=SLIDER_LOAD_SHED_CONST, range=(
                        0.0, 1.0), tooltip=operator_constraints_tooltip, resolution=.05)]], border_width=10)],
                    [sg.Frame('Line Capacity Uncertainty', [[sg.Slider(orientation='horizontal',
                                                                       key=SLIDER_CAPACITY_ESTIMATION_ERROR, range=(0.0, 1.0), tooltip=error_tooltip, resolution=0.05)]], border_width=10)],
                    [sg.Button('More Options', button_color=(TEXT_COLOR, BACKGROUND_COLOR)), sg.Button(
                        'Run', button_color=(TEXT_COLOR, BACKGROUND_COLOR))]
                    ]
    output_column = [[sg.pin(sg.Canvas(key=FIGURE))],
                     [sg.Button('First', button_color=(TEXT_COLOR, BACKGROUND_COLOR)), sg.Button('Back', button_color=(TEXT_COLOR, BACKGROUND_COLOR)), sg.Button(
                         'Forward', button_color=(TEXT_COLOR, BACKGROUND_COLOR)), sg.Button('Last', button_color=(TEXT_COLOR, BACKGROUND_COLOR))],
                     [sg.Text('Loss of Delivery Capacity: '), sg.Text(
                         str(delivery_loss_percent) + "%")],
                     [sg.Text('Max Line Capacity: '),
                     sg.Text(str(cap_loss) + " MW")],
                     [sg.Text('Worst-off Cluster: '),
                      sg.Text(str(worst_cluster))],
                     [sg.Text('Probability of failure: '),
                     sg.Text('Click on Line')]
                     ]

    # full layout
    layout = [[sg.pin(sg.Menu(menu_def, pad=(200, 200), background_color=BACKGROUND_COLOR, text_color=TEXT_COLOR))],
              [sg.Text('Cascading failure Simulator GUI',
                       background_color=BACKGROUND_COLOR, text_color=TEXT_COLOR)],
               [sg.Column(input_column, key=COLUMN_INPUT, element_justification='c', background_color=BACKGROUND_COLOR),
                sg.Column(output_column, key=COLUMN_OUTPUT, element_justification='c', background_color=BACKGROUND_COLOR)]]

    # create the window with the layout
    window = sg.Window('Demo Application - Embedding Matplotlib In PySimpleGUI',
                       layout, finalize=True, element_justification='center', font='Helvetica 18', background_color=BACKGROUND_COLOR)
    # add the plot to the window
    #fig = draw_plot()

    # load mpc plotting data
    state_matrix = load_sim_data.load_state_matrix(SIM_STATE_MATRIX)
    initial_failures = load_sim_data.load_initial_failures(
        SIM_INITIAL_FAILURES)
    branch_data = generate_mpc_plot_networkx.get_branch_dataframe(
        generate_mpc_plot_networkx.load_mpc(MPC_PATH))
    negativeOneIndices = generate_mpc_plot_networkx.get_statematrix_steady_state_negative_one_indices(
        state_matrix)
    mostFailureSimIndex = generate_mpc_plot_networkx.get_sim_index_with_most_failures(
        negativeOneIndices)
    _, _, numIterations = generate_mpc_plot_networkx.get_simulation_start_end_iterations(
        negativeOneIndices, mostFailureSimIndex)
    simIteration = 0
    fig = generate_mpc_plot_networkx.plot_network(branch_data, initial_failures, state_matrix,
                                                  negativeOneIndices, mostFailureSimIndex, simIteration, True, False, fig=None)
    # fig = plot_topology()
    fig_canvas_agg = draw_figure(window[FIGURE].TKCanvas, fig)

    # run loop
    event = ''

    while True:
        event, values = window.read()
        print(event)
        print(values)
        if event == 'Run':
            print('the "run" button has been pressed!')
            case_name = 'case118'
            iterations = 100000  # TODO: Make this an input
            batch_size = 16
            load_generation_ratio = values[SLIDER_LOAD]
            initial_failures = int(values[SLIDER_INITIAL_FAILURES])
            load_shed_constant = values[SLIDER_LOAD_SHED_CONST]
            estimation_error = values[SLIDER_CAPACITY_ESTIMATION_ERROR]
            # info on figure update
            fig.clear()
            # TODO: Give this its own thread and some sort of mutex lock as well
            fig = run_button_action(fig, case_name, iterations, initial_failures,
                                    load_generation_ratio, load_shed_constant, estimation_error, batch_size)
            # draw_figure(window[FIGURE].TKCanvas, fig)
            fig.canvas.draw()
        # TODO: update these so they do stuff with the topology -- update the topology plot
        elif event == 'First':
            print(event)
            simIteration = 0
            fig.clear()
            fig = generate_mpc_plot_networkx.plot_network(branch_data, initial_failures, state_matrix,
                                                          negativeOneIndices, mostFailureSimIndex, simIteration, True, False, fig=fig)
            fig.canvas.draw()
        elif event == 'Last':
            print(event)
        elif event == 'Forward':
            print(event)
            simIteration += 1
            fig.clear()
            fig = generate_mpc_plot_networkx.plot_network(branch_data, initial_failures, state_matrix,
                                                          negativeOneIndices, mostFailureSimIndex, simIteration, True, False, fig=fig)
            fig.canvas.draw()
        elif event == 'Back':
            print(event)
            simIteration -= 1
            fig.clear()
            fig = generate_mpc_plot_networkx.plot_network(branch_data, initial_failures, state_matrix,
                                                          negativeOneIndices, mostFailureSimIndex, simIteration, True, False, fig=fig)
            fig.canvas.draw()
        elif event == 'More Options':
            # if user selects more options, then return the action more options
            window.close()
            # return the action for more options
            return 'more'

        elif event == 'Save Figure':
            # saves figure currently displayed
            root = tk.Tk()
            root.withdraw()
            file = filedialog.asksaveasfilename(
                filetypes=(("png", "*.png"), ("jpeg", "*.jpeg"), ("pdf", "*.pdf")), defaultextension=(("png", "*.png")))
            plt.savefig(file)

        elif event == 'Save DF':
            # saves states_dataframe.csv
            root = tk.Tk()
            root.withdraw()
            file = filedialog.asksaveasfilename(
                filetypes=(("csv", "*.csv"), ("Excel", "*.xlsx")), defaultextension=(("csv", "*.csv")))
            original = os.getcwd() + '\states_dataframe.csv'
            target = file
            shutil.copyfile(original, target)

        elif event == 'Save Simple DF':
            # saves states_simple.csv
            root = tk.Tk()
            root.withdraw()
            file = filedialog.asksaveasfilename(
                filetypes=(("csv", "*.csv"), ("Excel", "*.xlsx")), defaultextension=(("csv", "*.csv")))
            original = os.getcwd() + '\states_simple.csv'
            target = file
            shutil.copyfile(original, target)

        elif event == 'Save States.mat':
            # saves states in matlab file type
            root = tk.Tk()
            root.withdraw()
            file = filedialog.asksaveasfilename(
                filetypes=(("m", "*.m")), defaultextension=(("m", "*.m")))
            original = os.getcwd() + '\states.mat'
            target = file
            shutil.copyfile(original, target)

        # TODO add a proper event for windows closed (event == WIN_CLOSED)?
        elif event == sg.WIN_CLOSED:
            break

    window.close()
    # quit application
    return 'quit'
