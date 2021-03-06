from json import load
from tkinter.tix import TEXT
import sim_connect
from p_stop_curve import cascading_failure_function
from matplotlib.ticker import NullFormatter  # useful for `logit` scale
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import PySimpleGUI as sg
import matplotlib
import os
from PIL import Image, ImageTk
from urllib import request
#some defines for sizes for things for standardization
TEXT_COLOR = '#000000'
BACKGROUND_COLOR = '#FFFFFF'
INPUT_BOX_SIZE = (25,1)
INPUT_FRAME_SIZE = (300,60)
# slider names
SLIDER_ITERATIONS = 'iterations'
SLIDER_LOAD = 'slider_load'
SLIDER_INITIAL_FAILURES = 'slider_init_failures'
SLIDER_LOAD_SHED_CONST = 'slider_load_shed_const'
SLIDER_CAPACITY_ESTIMATION_ERROR = 'slider_line_cap_uncertainty'

# direct input names
ITERATIONS_INPUT = 'iterations_s'
LOAD_INPUT = 'load_s'
INITIAL_FAILURES_INPUT = 'initial_failures_s'
LOAD_SHED_INPUT = 'load_shed_s'
CAPACITY_ESTIMATION_ERROR_INPUT = 'capacity_error_s'
# column names (input and output) (used as keys)
COLUMN_INPUT = 'input_column'
COLUMN_OUTPUT = 'output_column'
COLUMN_INPUT_S = 'input_column_s'
COLUMN_OUTPUT_S = 'output_column_s'
# Figure keys
FIGURE = 'figure_1'
FIGURE_2 = 'figure_2'

matplotlib.use('TkAgg')
"""
    Simultaneous PySimpleGUI Window AND a Matplotlib Interactive Window
    A number of people have requested the ability to run a normal PySimpleGUI window that
    launches a MatplotLib window that is interactive with the usual Matplotlib controls.
    It turns out to be a rather simple thing to do.  The secret is to add parameter block=False to plt.show()
"""
# define values here
cap_loss = 1500
delivery_loss_percent = 8
worst_cluster = 4
num_lines = 186
# end defines


def draw_plot():
    p_stop_df = cascading_failure_function()
    fig = plt.figure()
    plt.plot('x_values', 'cascade_stop', data=p_stop_df,
             color='skyblue', linewidth=1)
    plt.xlabel('Number of Failed Lines')
    plt.ylabel('Cascade-Stop Probability')
    plt.title('Cascade-Stop Probability vs Number of Line Failures')
    # show legend
    plt.legend()
    # set title
    plt.title = "Cascade-Stop Probability vs Number of Line Failures"
    #plt.plot([0.1, 0.2, 0.5, 0.7])
    # plt.show(block=False)
    return fig


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
    # fig = plt.figure()
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


# ------------------------------- Beginning of Matplotlib helper code -----------------------


def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg


# description
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

sg.theme('LightGrey1')

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
                [sg.Button('More Options', button_color = (TEXT_COLOR, BACKGROUND_COLOR)), sg.Button('Run', button_color = (TEXT_COLOR, BACKGROUND_COLOR))]
                ]
# TODO: get rid of this, make it display the pstop instead
#filename = os.getcwd() + "/graph_png.png"
# Resize PNG file to size (300, 300)
#size = (300, 300)
# im = Image.open(filename)
# im = im.resize(size, resample=Image.BICUBIC)
# image = ImageTk.PhotoImage(image=im)
output_column = [[sg.Canvas(key=FIGURE)],
                 # output_column = [[sg.Image(filename=filename)],
                 [sg.Text('Loss of Delivery Capacity: '), sg.Text(
                     str(delivery_loss_percent) + "%")],
                 [sg.Text('Max Line Capacity: '),
                  sg.Text(str(cap_loss) + " MW")],
                 [sg.Text('Worst-off Cluster: '), sg.Text(str(worst_cluster))],
                 [sg.Text('Probability of failure: '),
                  sg.Text('Click on Line')],
                 ]

# Create layout for more input options/better outputs (more options)
input_column_s = [[sg.Frame('Cascading Failure Simulation', [[sg.Text(description)]], border_width=10)],
                  [sg.Frame('Load', [[sg.InputText(key=LOAD_INPUT, tooltip=load_tooltip,
                            size=INPUT_BOX_SIZE)]], border_width=10, size=INPUT_FRAME_SIZE)],
                  [sg.Frame('Initial Line Failures', [[sg.Slider(range=(0, 50), tooltip=initial_failures_tooltip, orientation='horizontal',
                                                                 key=SLIDER_INITIAL_FAILURES)]], border_width=10)],
                  [sg.Frame('Operator Constraints (TEST)', [[sg.Slider(orientation='horizontal', key=SLIDER_LOAD_SHED_CONST, range=(
                      0.0, 1.0), tooltip=operator_constraints_tooltip, resolution=.05)]], border_width=10)],
                  [sg.Frame('Line Capacity Uncertainty', [[sg.Slider(orientation='horizontal',
                                                                     key=SLIDER_CAPACITY_ESTIMATION_ERROR, range=(0.0, 1.0), tooltip=error_tooltip, resolution=0.05)]], border_width=10)],
                  [sg.Button('More Options'), sg.Button('Run')]
                  ]
output_column_s = [[sg.Canvas(key=FIGURE_2)],
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

layout = [[sg.Text('Cascading failure Simulator GUI', background_color=BACKGROUND_COLOR, text_color = 'Black')],
          [sg.Column(input_column, key = COLUMN_INPUT, element_justification='c', background_color=BACKGROUND_COLOR), sg.Column(output_column, key = COLUMN_OUTPUT, element_justification='c', background_color=BACKGROUND_COLOR),
           sg.pin(sg.Column(input_column_s, key = COLUMN_INPUT_S, element_justification='c', visible = False, background_color=BACKGROUND_COLOR)), sg.pin(sg.Column(output_column_s, key=COLUMN_OUTPUT_S, element_justification='c', visible = False, background_color=BACKGROUND_COLOR))]]
# create the form and show it without the plot
window = sg.Window('Demo Application - Embedding Matplotlib In PySimpleGUI',
                   layout, finalize=True, element_justification='center', font='Helvetica 18', background_color=BACKGROUND_COLOR)
# add the plot to the window
fig = draw_plot()
fig_canvas_agg = draw_figure(window[FIGURE].TKCanvas, fig)
# Add the plot to the more options window
fig_canvas_agg = draw_figure(window[FIGURE_2].TKCanvas, fig)

event = ''
while True:
    event, values = window.read()
    print(event)
    print(values)
    if event == 'Run':
        print('the "run" button has been pressed!')
        case_name = 'case118'
        iterations = 100000  # TODO: Make this an input
        initial_failures = 2
        batch_size = 16
        load_generation_ratio = values[SLIDER_LOAD]
        initial_failures = int(values[SLIDER_INITIAL_FAILURES])
        load_shed_constant = values[SLIDER_LOAD_SHED_CONST]
        estimation_error = values[SLIDER_CAPACITY_ESTIMATION_ERROR]
        # info on figure update
        fig.clear()
        fig = run_button_action(fig, case_name, iterations, initial_failures,
                                load_generation_ratio, load_shed_constant, estimation_error, batch_size)
        # draw_figure(window[FIGURE].TKCanvas, fig)
        fig.canvas.draw()
    elif event == 'More Options':
        # make non-special columns invisible
        window[COLUMN_INPUT].Update(visible=False)
        window[COLUMN_OUTPUT].Update(visible=False)
        # make more options visible
        window[COLUMN_INPUT_S].Update(visible=True)
        window[COLUMN_OUTPUT_S].Update(visible=True)
        fig_canvas_agg = draw_figure(window[FIGURE].TKCanvas, fig)
        window.refresh()
    # TODO add a proper event for windows closed (event == WIN_CLOSED)?
    elif event == sg.WIN_CLOSED:
        break

window.close()
