# function imports
import sim_connect
from p_stop_curve import cascading_failure_function
from draw_plot import draw_plot, run_button_action, draw_figure
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
import tkinter as tk
from tkinter import filedialog
import shutil

# color and size specifications
TEXT_COLOR = '#000000'
BACKGROUND_COLOR = '#FFFFFF'
INPUT_BOX_SIZE = (25, 1)
INPUT_FRAME_SIZE = (300, 60)
# direct input names
TEXT_BOX_ITERATIONS = 'text_box_iterations'
ITERATIONS_INPUT = 'iterations_s'
LOAD_INPUT = 'load_s'
INITIAL_FAILURES_INPUT = 'initial_failures_s'
LOAD_SHED_INPUT = 'load_shed_s'
CAPACITY_ESTIMATION_ERROR_INPUT = 'capacity_error_s'
# Figure keys
FIGURE = 'figure_1'
FIGURE_2 = 'figure_2'
# column keys
COLUMN_INPUT = 'input_column'
COLUMN_OUTPUT = 'output_column'
#descriptions and tooltips
description = " This is a Graphical User Interface \n for the SACE lab's cascading failure simulator, \n which simulates line failures in a grid \n after a number of initial failures"
# Tooltips
tooltip_iterations = "The number of iterations to run the simulation for. \n" + \
    "Higher numbers of iterations will take longer, but will produce more reliable results."
load_tooltip = "This is the load-generation ratio for the grid. \n" + \
    "The load-generation ratio is the load on the grid as a percentage of its rated capacity. \n" + \
    "1.0 represents the sum of the loads being equivalant to the max generation capacity\n" + \
    "and 0.0 represents no load"
operator_constraints_tooltip = "This represents the constraints to which grid operators are held when making load-shedding decisions. \n" + \
    "Load-shedding is when a grid operator reduces or turns off electricity distribution to an area when the demand is larger than a power source can supply. \n" + \
    "0.0 represents no load-shedding constraints, while 1.0 represents no load-shedding allowed"
error_tooltip = "This represents the estimation error operators have when determining the highest capacity of a line. \n" + \
    "0.0 represents perfect knowledge of line capacities, 1.0 represents minimum knowledge of line capacities"
initial_failures_tooltip = "This is the number of random line failures that occur at the start of the simulation."

# Temporarily defined values TODO: Actually calculate these per run!
cap_loss = 1500
delivery_loss_percent = 8
worst_cluster = 4
num_lines = 186


def complex_gui(debug=False):
    # setup beforehand
    # set the style of the plot
    # plt.style.use('ieee')
    # set the plot dpi to 300
    #matplotlib.rcParams['figure.dpi'] = 200
    # set the plot size to be square
    #matplotlib.rcParams['figure.figsize'] = (3, 2.5)
    matplotlib.use('TkAgg')
    sg.theme('LightGrey1')

    menu_def = [
        ['&File', ['&Save Figure', '&Save Simple DF', '&Save States.mat', '&Save DF']]]

    # columns
    input_column = [[sg.Frame('Cascading Failure Simulation', [[sg.Text(description)]], border_width=10)],
                    [sg.Frame('Iterations', [[sg.InputText(key=TEXT_BOX_ITERATIONS, tooltip=tooltip_iterations,
                                                           size=INPUT_BOX_SIZE)]], border_width=10)],
                    [sg.Frame('Load', [[sg.InputText(key=LOAD_INPUT, tooltip=load_tooltip,
                                                     size=INPUT_BOX_SIZE)]], border_width=10, size=INPUT_FRAME_SIZE)],
                    [sg.Frame('Initial Line Failures', [[sg.InputText(key=INITIAL_FAILURES_INPUT, tooltip=load_tooltip,
                                                                      size=INPUT_BOX_SIZE)]], border_width=10, size=INPUT_FRAME_SIZE)],
                    [sg.Frame('Load Shed Constraints', [[sg.InputText(key=LOAD_SHED_INPUT, tooltip=load_tooltip,
                                                                      size=INPUT_BOX_SIZE)]], border_width=10, size=INPUT_FRAME_SIZE)],
                    [sg.Frame('Line Capacity Uncertainty', [[sg.InputText(key=CAPACITY_ESTIMATION_ERROR_INPUT, tooltip=load_tooltip,
                                                                          size=INPUT_BOX_SIZE)]], border_width=10, size=INPUT_FRAME_SIZE)],
                    [sg.Button('Less Options', button_color=(
                        TEXT_COLOR, BACKGROUND_COLOR)), sg.Button('Run', button_color=(TEXT_COLOR, BACKGROUND_COLOR))]
                    ]
    output_column = [[sg.Canvas(key=FIGURE)],
                     # output_column = [[sg.Image(filename=filename)],
                     [sg.Text('Loss of Delivery Capacity: '), sg.Text(
                         str(delivery_loss_percent) + "%")],
                     [sg.Text('Max Line Capacity: '),
                      sg.Text(str(cap_loss) + " MW")],
                     [sg.Text('Worst-off Cluster: '),
                      sg.Text(str(worst_cluster))],
                     [sg.Text('Probability of failure: '),
                      sg.Text('Click on Line')],
                     ]

    # full layout
    layout = [[sg.pin(sg.Menu(menu_def, pad=(200, 200), background_color=BACKGROUND_COLOR, text_color=TEXT_COLOR)),
               sg.Text('Cascading failure Simulator GUI', background_color=BACKGROUND_COLOR, text_color=TEXT_COLOR)],
              [sg.Column(input_column, key=COLUMN_INPUT, element_justification='c', background_color=BACKGROUND_COLOR),
               sg.Column(output_column, key=COLUMN_OUTPUT, element_justification='c', background_color=BACKGROUND_COLOR)]]

    # create the window with the layout
    window = sg.Window('Demo Application - Embedding Matplotlib In PySimpleGUI',
                       layout, finalize=True, element_justification='center', font='Helvetica 18', background_color=BACKGROUND_COLOR)
    # add the plot to the window
    fig = draw_plot()
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
            try:
                iterations = int(values[TEXT_BOX_ITERATIONS])
            except ValueError:
                print(
                    f'Invalid input for iterations. Using default value of {iterations}')
                print(type(window[TEXT_BOX_ITERATIONS]))
                window[TEXT_BOX_ITERATIONS].Update(str(iterations))
                window.refresh()
            batch_size = 16
            load_generation_ratio = float(values[LOAD_INPUT])
            initial_failures = int(values[INITIAL_FAILURES_INPUT])
            load_shed_constant = float(values[LOAD_SHED_INPUT])
            estimation_error = float(values[CAPACITY_ESTIMATION_ERROR_INPUT])
            # info on figure update
            fig.clear()
            # TODO: Give this its own thread, and some sort of mutex lock as well
            fig = run_button_action(fig, case_name, iterations, initial_failures,
                                    load_generation_ratio, load_shed_constant, estimation_error, batch_size)
            # fig_canvas_agg.draw()
            #draw_figure(fig_canvas_agg, fig)
            fig.canvas.draw()

        elif event == 'Less Options':
            # if user selects more options, then return the action more options
            window.close()
            # return the action for more options
            return 'less'

        elif event == 'Save Figure':
            # saves figure currently displayed
            root = tk.Tk()
            root.withdraw()
            file = filedialog.asksaveasfilename(
                filetypes=(("png", "*.png"), ("jpeg", "*.jpeg"), ("pdf", "*.pdf")), defaultextension=(("png", "*.png")))
            if file != '':
                plt.savefig(file)

        elif event == 'Save DF':
            # saves states_dataframe.csv
            root = tk.Tk()
            root.withdraw()
            file = filedialog.asksaveasfilename(
                filetypes=(("csv", "*.csv"), ("Excel", "*.xlsx")), defaultextension=(("csv", "*.csv")))
            original = os.getcwd() + '\states_dataframe.csv'
            if file != '':
                target = file
                shutil.copyfile(original, target)

        elif event == 'Save Simple DF':
            # saves states_simple.csv
            root = tk.Tk()
            root.withdraw()
            file = filedialog.asksaveasfilename(
                filetypes=(("csv", "*.csv"), ("Excel", "*.xlsx")), defaultextension=(("csv", "*.csv")))
            original = os.getcwd() + '\states_simple.csv'
            if file != '':
                target = file
                shutil.copyfile(original, target)

        elif event == 'Save States.mat':
            # saves states in matlab file type
            root = tk.Tk()
            root.withdraw()
            file = filedialog.asksaveasfilename(
                filetypes=[("mat", "*.mat")], defaultextension=("mat", "*.mat"))
            original = os.getcwd() + '\states.mat'
            if file != '':
                target = file
                shutil.copyfile(original, target)


        # TODO add a proper event for windows closed (event == WIN_CLOSED)?
        elif event == sg.WIN_CLOSED:
            break

    window.close()
    # quit application
    return 'quit'
