# function imports
import sim_connect
from p_stop_curve import cascading_failure_function
import draw_plot
from draw_plot import draw_figure
# from draw_plot import draw_plot, run_button_action, draw_figure, simple_run_button_action
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
import gui_utilities
from gui_utilities import FONT, TEXT_COLOR, BACKGROUND_COLOR
import simulation_select
import time
import sim_connect
from sim_connect import SimulationStatus
import ui_text
# import simulation organization
from organize_simulation import organize_simulation
import enum

# color and size specifications

SIZE_INPUT_BOX = (24, 1)
SIZE_SLIDER = (20, 20)
SIZE_INPUT_FRAME = (300, 60)

# slider keys
KEY_INPUT_BOX_ITERATIONS = 'text_box_iterations'
DEFAULT_INPUT_BOX_ITERATIONS = 100000
KEY_SLIDER_LOAD = 'slider_load'
DEFAULT_SLIDER_LOAD = 0.7
KEY_SLIDER_INITIAL_FAILURES = 'slider_init_failures'
DEFAULT_SLIDER_INITIAL_FAILURES = 2
KEY_SLIDER_LOAD_SHED_CONST = 'slider_load_shed_const'
DEFAULT_SLIDER_LOAD_SHED_CONST = 0.1
KEY_SLIDER_CAPACITY_ESTIMATION_ERROR = 'slider_line_cap_uncertainty'
DEFAULT_SLIDER_CAPACITY_ESTIMATION_ERROR = 0.1
MPC_PATH = 'case118_mpc_presim.mat'
PATH_SIM_STATE_MATRIX = 'case118_f2_r7_t1_e1_i100000_sm.mat'
PATH_SIM_INITIAL_FAILURES = 'case118_f2_r7_t1_e1_i100000_if.mat'
# Figure keys
KEY_FIGURE = 'figure_1'
# column keys
COLUMN_INPUT = 'input_column'
COLUMN_OUTPUT = 'output_column'
LABEL_BUTTON_SAVE = 'Save Image'
KEY_BUTTON_SAVE = 'save_button'
KEY_BUTTON_ANIMATE = 'animate_button'
KEY_TIMER_ANIMATE = 'animate_action_timer'
KEY_BUTTON_SIM_RUN = 'run_button'
TEXT_BUTTON_SIM_RUN = 'Run'
KEY_BUTTON_SIM_CANCEL = 'cancel_button'
TEXT_BUTTON_SIM_CANCEL = 'Cancel'
ANIMATE_TOPOLOGY_DELAY = 0.5
KEY_PROGRESS_BAR = 'progress_bar'
KEY_TIMER_PROGRESS_BAR = 'progress_bar_timer'
GROUP_ID_RADIO_PLOT_TYPE = 'radio_plot_type'
KEY_RADIO_PSTOP = 'radio_pstop'
TEXT_RADIO_PSTOP = 'PStop Graph'
KEY_RADIO_TOPOLOGY_PLAYTHROUGH = 'radio_topology'
TEXT_RADIO_TOPOLOGY_PLAYTHROUGH = 'Simulation Playthrough'
KEY_TEXT_TOP_LABEL = 'text_top_label'

SIMULATION_COMPLETE_ACTION = 'simulation_complete'
SIMULATION_LOADED_ACTION = 'simulation_loaded'

KEY_TEXT_SELECTED_SIM = 'sim_text'
KEY_TEXT_SIM_STEP = 'step_text'
KEY_TEXT_SIM_STATUS = 'sim_status'

# descriptions and tooltips
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


class FigureState(enum.Enum):
    PSTOP = 1
    TOPOLOGY = 2


def disable_forward_back_buttons(window, simStep, numIterations):
    """
    Disables the iteration control buttons based on whether the iteration is at the start of end of the simulation
    :param window: The window to disable the buttons in
    :param simStep: The current step number
    :param numIterations: The total number of steps in the iteration of the simulation
    """
    if simStep == 0:
        window['Back'].update(disabled=True)
        window['First'].update(disabled=True)
    else:
        window['Back'].update(disabled=False)
        window['First'].update(disabled=False)
    if simStep == numIterations - 1:
        window['Forward'].update(disabled=True)
        window['Last'].update(disabled=True)
    else:
        window['Forward'].update(disabled=False)
        window['Last'].update(disabled=False)


def simple_gui(debug=False):
    # setup beforehand
    matplotlib.use('TkAgg')
    sg.theme('LightGrey1')

    menu_def = [
        ['&File', ['&Save Figure', '&Save Simple DF', '&Save States.mat', '&Save DF']],
        # ['&About', ['&Inputs', '&Outputs', '&Software']]]
        ['&About', ['&'+ui_text.TITLE_ABOUT_INPUTS_POPUP, '&'+ui_text.TITLE_ABOUT_OUTPUTS_POPUP, '&'+ui_text.TITLE_ABOUT_SIMULATOR_POPUP]]]

    # columns
    input_column = [  # [sg.Frame('Cascading Failure Simulation', [[sg.Text(description)]], border_width=10)],
        [sg.Text('Simulation Inputs')],
        [sg.Frame('Iterations', [[sg.Input(key=KEY_INPUT_BOX_ITERATIONS, tooltip=tooltip_iterations,
                                           size=SIZE_INPUT_BOX, default_text=str(DEFAULT_INPUT_BOX_ITERATIONS))]], border_width=10, relief='flat')],
        [sg.HorizontalSeparator()],
        [gui_utilities.make_slider_with_frame(
            label='Load', key=KEY_SLIDER_LOAD, tooltip=load_tooltip, range=(0.0, 1.0), resolution=0.05, size=SIZE_SLIDER, default_value=DEFAULT_SLIDER_LOAD)],
        [sg.HorizontalSeparator()],
        [gui_utilities.make_slider_with_frame(
            label='Initial Line Failures', key=KEY_SLIDER_INITIAL_FAILURES, tooltip=initial_failures_tooltip, range=(0, 50), resolution=1, size=SIZE_SLIDER, default_value=DEFAULT_SLIDER_INITIAL_FAILURES)],
        [sg.HorizontalSeparator()],
        [gui_utilities.make_slider_with_frame(
            label='Operator Constraints', key=KEY_SLIDER_LOAD_SHED_CONST, tooltip=operator_constraints_tooltip, range=(0.0, 1.0), resolution=0.05, size=SIZE_SLIDER, default_value=DEFAULT_SLIDER_LOAD_SHED_CONST)],
        [sg.HorizontalSeparator()],
        [gui_utilities.make_slider_with_frame(
            label='Line Capacity Uncertainty', key=KEY_SLIDER_CAPACITY_ESTIMATION_ERROR, tooltip=error_tooltip, range=(0.0, 1.0), resolution=0.05, size=SIZE_SLIDER, default_value=DEFAULT_SLIDER_CAPACITY_ESTIMATION_ERROR)],
        [sg.Button(TEXT_BUTTON_SIM_RUN, key=KEY_BUTTON_SIM_RUN, button_color=(
            TEXT_COLOR, BACKGROUND_COLOR)),
         sg.Button(TEXT_BUTTON_SIM_CANCEL, key=KEY_BUTTON_SIM_CANCEL, button_color=(TEXT_COLOR, BACKGROUND_COLOR), disabled=True)],
        [sg.Text('Status:', size=(8, 1)), sg.Text('No simulation running.',
                                                  key=KEY_TEXT_SIM_STATUS, size=(20, 1))],
        [sg.Text('Progress:', size=(8, 1)), sg.ProgressBar(key=KEY_PROGRESS_BAR,
                                                           orientation='horizontal', max_value=100, size=(20, 20))]
    ]

    output_column = [[sg.Text('Simulation Outputs', background_color=BACKGROUND_COLOR, text_color=TEXT_COLOR)],
                     [sg.Text('No Simulation Loaded', key=KEY_TEXT_TOP_LABEL, size=(
                         90, 2), background_color=BACKGROUND_COLOR, text_color=TEXT_COLOR)],
                     [sg.Column(
                         [[sg.Radio(TEXT_RADIO_PSTOP, GROUP_ID_RADIO_PLOT_TYPE, key=KEY_RADIO_PSTOP, default=True, enable_events=True),
                           sg.Radio(TEXT_RADIO_TOPOLOGY_PLAYTHROUGH, GROUP_ID_RADIO_PLOT_TYPE,
                                    key=KEY_RADIO_TOPOLOGY_PLAYTHROUGH, enable_events=True)],
                          [sg.pin(sg.Canvas(key=KEY_FIGURE))],
                          [sg.Text('', key=KEY_TEXT_SELECTED_SIM)],
                             [sg.Text('', key=KEY_TEXT_SIM_STEP)],
                             [sg.Button('First', button_color=(TEXT_COLOR, BACKGROUND_COLOR)), sg.Button('Back', button_color=(TEXT_COLOR, BACKGROUND_COLOR)), sg.Button(
                                 'Forward', button_color=(TEXT_COLOR, BACKGROUND_COLOR)), sg.Button('Last', button_color=(TEXT_COLOR, BACKGROUND_COLOR))],
                             [sg.Button('Play', key=KEY_BUTTON_ANIMATE, button_color=(
                                 TEXT_COLOR, BACKGROUND_COLOR))],
                             [sg.Text('Average number of failed lines:', size=(32, 1)),
                              sg.Text('', key=ui_text.KEY_TEXT_OUTPUT_AVG_FAILED_LINES, size=(6, 1), justification='right')],
                             [sg.Text('Maximum number of failed lines:', size=(32, 1)),
                              sg.Text('', key=ui_text.KEY_TEXT_OUTPUT_MAX_FAILED_LINES, size=(6, 1), justification='right')],
                             [sg.Text('Average accumulated failed capacity:', size=(32, 1)),
                              sg.Text('', key=ui_text.KEY_TEXT_OUTPUT_AVG_ACC_FAILED_CAPACITY, size=(6, 1), justification='right')],
                             [sg.Text('Maximum accumulated failed capacity:', size=(32, 1)),
                              sg.Text('', key=ui_text.KEY_TEXT_OUTPUT_MAX_ACC_FAILED_CAPACITY, size=(6, 1), justification='right')]], element_justification='c'),
                      simulation_select.getGUIElement()]
                     ]

    # full layout
    layout = [[sg.pin(sg.Menu(menu_def, pad=(0, 0), background_color=BACKGROUND_COLOR, text_color=TEXT_COLOR))],
              [sg.Column(input_column, key=COLUMN_INPUT, element_justification='c', background_color=BACKGROUND_COLOR),
               sg.VerticalSeparator(),
               sg.Column(output_column)]]
    #    simulation_select.getGUIElement()]]

    # create the window with the layout
    window = sg.Window('Cascading Failure Simulator',
                       layout, finalize=True, element_justification='center', font=gui_utilities.FONT, background_color=BACKGROUND_COLOR)
    # add the plot to the window
    # fig = draw_plot()

    # load mpc plotting data
    state_matrix = load_sim_data.load_state_matrix(PATH_SIM_STATE_MATRIX)
    initial_failures = load_sim_data.load_initial_failures(
        PATH_SIM_INITIAL_FAILURES)
    graph_data = generate_mpc_plot_networkx.TopologyIterationData(
        state_matrix, initial_failures, MPC_PATH)
    # branch_data = generate_mpc_plot_networkx.get_branch_dataframe(
    #     generate_mpc_plot_networkx.load_mpc(MPC_PATH))
    # negativeOneIndices = generate_mpc_plot_networkx.get_statematrix_steady_state_negative_one_indices(
    #     state_matrix)
    # mostFailureSimIndex = generate_mpc_plot_networkx.get_sim_index_with_most_failures(
    #     negativeOneIndices)
    iteration_index = graph_data.get_iteration_index_with_most_failures()
    num_steps = graph_data.get_num_steps(
        iteration_index)
    num_iterations = graph_data.get_num_iterations()
    simulation_obj: sim_connect.Simulation = None

    simStep = 0
    animateTopology = False
    figure_display_state = FigureState.PSTOP
    # fig = graph_data.plot_topology(
    #     iteration_index, simStep)
    fig = plt.figure()
    # fig = generate_mpc_plot_networkx.plot_network(branch_data, initial_failures, state_matrix,
    #                                               negativeOneIndices, mostFailureSimIndex, simStep, True, False, fig=None)
    # fig = plot_topology()
    fig_canvas_agg = draw_figure(window[KEY_FIGURE].TKCanvas, fig)
    disable_forward_back_buttons(window, simStep, num_steps)
    # update_step_text(window, simStep, num_steps)
    gui_utilities.update_text(window, KEY_TEXT_SIM_STEP,
                              ui_text.FORMAT_TEXT_SIM_STEP, (simStep, num_steps - 1))

    # TODO change this hardcoded value
    simulation_select.display_iterations(
        window, graph_data, 0, 3000)
    gui_utilities.update_text(window, KEY_TEXT_SELECTED_SIM,
                              ui_text.FORMAT_TEXT_SELECTED_SIM, (iteration_index, num_iterations))

    # run loop
    event = ''

    redrawFigure = False

    while True:
        event, values = window.read()
        print(event)
        print(values)
        if event == KEY_BUTTON_SIM_RUN:
            print('the "run" button has been pressed!')
            case_name = 'case118'
            iterations = 100000  # TODO: Make this an input
            try:
                iterations = int(values[KEY_INPUT_BOX_ITERATIONS])
            except ValueError:
                print(
                    f'Invalid input for iterations. Using default value of {iterations}')
                print(type(window[KEY_INPUT_BOX_ITERATIONS]))
                window[KEY_INPUT_BOX_ITERATIONS].Update(str(iterations))
                window.refresh()
            batch_size = 16
            load_generation_ratio = values[KEY_SLIDER_LOAD]
            initial_failures = int(values[KEY_SLIDER_INITIAL_FAILURES])
            load_shed_constant = values[KEY_SLIDER_LOAD_SHED_CONST]
            estimation_error = values[KEY_SLIDER_CAPACITY_ESTIMATION_ERROR]
            # info on figure update
            # fig.clear()
            # TODO: Give this its own thread and some sort of mutex lock as well
            # simStep = 0
            # (initial_failures, state_matrix, negativeOneIndices, mostFailureSimIndex, fig) = simple_run_button_action(fig, case_name, iterations, initial_failures,
            #                                                                                                           load_generation_ratio, load_shed_constant, estimation_error, batch_size, branch_data)
            # graph_data, fig = simple_run_button_action(fig, case_name, iterations, initial_failures,
            #                                            load_generation_ratio, load_shed_constant, estimation_error, batch_size)
            simulation_obj = sim_connect.Simulation(
                case_name, iterations, initial_failures, load_generation_ratio, load_shed_constant, estimation_error, batch_size)
            window[KEY_PROGRESS_BAR].UpdateBar(0)
            # if the simulation has not been run yet, run it
            if simulation_obj.get_simulation_status() == sim_connect.SimulationStatus.NOT_RUN:
                print("Running simulation...")
                gui_utilities.update_text(
                    window, KEY_TEXT_SIM_STATUS, ui_text.FORMAT_TEXT_SIM_STATUS, ('simulation starting...'))
                window[KEY_BUTTON_SIM_CANCEL].update(disabled=False)
                window[KEY_BUTTON_SIM_RUN].update(disabled=True)
                window.perform_long_operation(
                    simulation_obj.run_simulation, SIMULATION_COMPLETE_ACTION)
                window.perform_long_operation(
                    lambda: time.sleep(1), KEY_TIMER_PROGRESS_BAR)
            # otherwise, load the simulation data
            else:
                print('Simulation already performed, loading simulation data...')
                gui_utilities.update_text(
                    window, KEY_TEXT_SIM_STATUS, ui_text.FORMAT_TEXT_SIM_STATUS, ('loading data...'))
                window.perform_long_operation(
                    simulation_obj.load_simulation, SIMULATION_LOADED_ACTION)

            # TODO run the simulation in a separate thread

            # iteration_index = graph_data.get_iteration_index_with_most_failures()
            # num_steps = graph_data.get_num_steps(
            #     iteration_index)
            # num_iterations = graph_data.get_num_iterations()
            # update_sim_text(window, iteration_index, num_iterations)
            # update_step_text(window, simStep, num_steps)
            # simulation_select.display_iterations(
            #     window, graph_data, int(values[simulation_select.SLIDER_MIN_LINE_FAILURES]), int(values[simulation_select.SLIDER_MAX_LINE_FAILURES]))
            # # graph_data = generate_mpc_plot_networkx.TopologyIterationData(
            # #     state_matrix, initial_failures, MPC_PATH)
            # # draw_figure(window[FIGURE].TKCanvas, fig)
            # redrawFigure = True

        elif event == SIMULATION_COMPLETE_ACTION:
            # check if the simulation has been fully run
            # if it is not complete and has reached this point, this means the simulation was killed
            if simulation_obj.get_simulation_status() != sim_connect.SimulationStatus.COMPLETE:
                gui_utilities.update_text(
                    window, KEY_TEXT_SIM_STATUS, ui_text.FORMAT_TEXT_SIM_STATUS, ('simulation cancelled'))
            # otherwise, the simulation has been completed, load it
            else:
                print('Simulation complete!')
                print('Loading simulation data...')
                gui_utilities.update_text(
                    window, KEY_TEXT_SIM_STATUS, ui_text.FORMAT_TEXT_SIM_STATUS, ('loading data...'))
                window.perform_long_operation(
                    simulation_obj.load_simulation, SIMULATION_LOADED_ACTION)
            window[KEY_BUTTON_SIM_CANCEL].update(disabled=True)
            window[KEY_BUTTON_SIM_RUN].update(disabled=False)

        elif event == SIMULATION_LOADED_ACTION:
            print('Simulation loaded!')
            simStep = 0
            gui_utilities.update_text(
                window, KEY_TEXT_SIM_STATUS, ui_text.FORMAT_TEXT_SIM_STATUS, (
                    'simulation loaded'))
            gui_utilities.update_text(
                window, KEY_TEXT_TOP_LABEL, ui_text.FORMAT_TEXT_TOP_LABEL, (simulation_obj.iterations, simulation_obj.initial_failures, simulation_obj.load_generation_ratio, simulation_obj.load_shed_constant, simulation_obj.estimation_error))
            graph_data = generate_mpc_plot_networkx.TopologyIterationData(
                simulation_obj.get_states_dataframe(), simulation_obj.get_initial_failure_array(), case_name=case_name)
            iteration_index = graph_data.get_iteration_index_with_most_failures()
            num_steps = graph_data.get_num_steps(
                iteration_index)
            num_iterations = graph_data.get_num_iterations()
            gui_utilities.update_text(window, KEY_TEXT_SELECTED_SIM,
                                      ui_text.FORMAT_TEXT_SELECTED_SIM, (iteration_index, num_iterations))
            # update_step_text(window, simStep, num_steps)
            gui_utilities.update_text(window, KEY_TEXT_SIM_STEP,
                                      ui_text.FORMAT_TEXT_SIM_STEP, (simStep, num_steps - 1))
            print('max num failed lines: ', graph_data.get_max_failed_lines())
            print('avg num failed lines: ', graph_data.get_avg_failed_lines())
            print('max accumulated failed line capacity: ',
                  graph_data.get_max_accumulated_failed_line_capacity())
            print('avg accumulated failed line capacity: ',
                  graph_data.get_average_accumulated_failed_line_capacity())
            gui_utilities.update_text(window, ui_text.KEY_TEXT_OUTPUT_AVG_FAILED_LINES,
                                      ui_text.FORMAT_TEXT_OUTPUT_AVG_FAILED_LINES, (graph_data.get_avg_failed_lines()))
            gui_utilities.update_text(window, ui_text.KEY_TEXT_OUTPUT_MAX_FAILED_LINES,
                                      ui_text.FORMAT_TEXT_OUTPUT_MAX_FAILED_LINES, (graph_data.get_max_failed_lines()))
            gui_utilities.update_text(window, ui_text.KEY_TEXT_OUTPUT_AVG_ACC_FAILED_CAPACITY,
                                      ui_text.FORMAT_TEXT_OUTPUT_AVG_ACC_FAILED_CAPACITY, (graph_data.get_average_accumulated_failed_line_capacity()))
            gui_utilities.update_text(window, ui_text.KEY_TEXT_OUTPUT_MAX_ACC_FAILED_CAPACITY,
                                      ui_text.FORMAT_TEXT_OUTPUT_MAX_ACC_FAILED_CAPACITY, (graph_data.get_max_accumulated_failed_line_capacity()))
            simulation_select.display_iterations(
                window, graph_data, int(values[simulation_select.SLIDER_MIN_LINE_FAILURES]), int(values[simulation_select.SLIDER_MAX_LINE_FAILURES]))
            redrawFigure = True

        elif event == KEY_TIMER_PROGRESS_BAR:
            # print('Progress bar timer fired!')
            percent_complete = int(
                simulation_obj.get_fraction_complete() * 100)
            window[KEY_PROGRESS_BAR].UpdateBar(percent_complete)
            # only change the status to reflect completeness once the first batch starts, and if other completeness items are not present
            if percent_complete > 0.0 and simulation_obj.get_simulation_status() == SimulationStatus.RUNNING:
                print('updating percentage')
                gui_utilities.update_text(
                    window, KEY_TEXT_SIM_STATUS, ui_text.FORMAT_TEXT_SIM_STATUS, ('%d%% complete' % percent_complete))
            if simulation_obj.get_simulation_status() == sim_connect.SimulationStatus.RUNNING:
                window.perform_long_operation(
                    lambda: time.sleep(1), KEY_TIMER_PROGRESS_BAR)

        elif event == KEY_BUTTON_SIM_CANCEL:
            print('Simulation cancelled!')
            gui_utilities.update_text(
                window, KEY_TEXT_SIM_STATUS, ui_text.FORMAT_TEXT_SIM_STATUS, ('cancelling...'))
            simulation_obj.kill_simulation()

        # handle selection between the chart types
        elif event == KEY_RADIO_PSTOP:
            figure_display_state = FigureState.PSTOP
            redrawFigure = True
        elif event == KEY_RADIO_TOPOLOGY_PLAYTHROUGH:
            figure_display_state = FigureState.TOPOLOGY
            redrawFigure = True

        # TODO: update these so they do stuff with the topology -- update the topology plot
        elif event == 'First':
            print(event)
            redrawFigure = True
            simStep = 0
            animateTopology = False
            window[KEY_BUTTON_ANIMATE].update(text='Play')

        elif event == 'Last':
            print(event)
            redrawFigure = True
            simStep = num_steps - 1
            animateTopology = False
            window[KEY_BUTTON_ANIMATE].update(text='Play')

        elif event == 'Forward':
            print(event)
            redrawFigure = True
            simStep += 1
            animateTopology = False
            window[KEY_BUTTON_ANIMATE].update(text='Play')

        elif event == 'Back':
            print(event)
            redrawFigure = True
            simStep -= 1
            animateTopology = False
            window[KEY_BUTTON_ANIMATE].update(text='Play')

        elif animateTopology and event == KEY_TIMER_ANIMATE:
            print(event)
            redrawFigure = True
            simStep += 1
            window.perform_long_operation(lambda: time.sleep(
                ANIMATE_TOPOLOGY_DELAY), KEY_TIMER_ANIMATE)

        elif event == KEY_BUTTON_ANIMATE:
            # it animateTopology is false, start animation
            if not animateTopology:
                animateTopology = True
                window.perform_long_operation(lambda: time.sleep(
                    ANIMATE_TOPOLOGY_DELAY), KEY_TIMER_ANIMATE)
                window[KEY_BUTTON_ANIMATE].update(text='Pause')
            else:
                animateTopology = False
                window[KEY_BUTTON_ANIMATE].update(text='Play')

            # elif event == simulation_select.SLIDER_MIN_LINE_FAILURES or event == simulation_select.SLIDER_MAX_LINE_FAILURES:
        elif event == simulation_select.UPDATE_FILTERS_BUTTON:
            simulation_select.display_iterations(
                window, graph_data, int(values[simulation_select.SLIDER_MIN_LINE_FAILURES]), int(values[simulation_select.SLIDER_MAX_LINE_FAILURES]))

        elif event == simulation_select.ITERATION_SELECTION_LIST:
            iteration_index = values[simulation_select.ITERATION_SELECTION_LIST][0].get_iteration_index(
            )
            num_steps = graph_data.get_num_steps(
                iteration_index)
            gui_utilities.update_text(window, KEY_TEXT_SELECTED_SIM,
                                      ui_text.FORMAT_TEXT_SELECTED_SIM, (iteration_index, num_iterations))
            simStep = 0
            redrawFigure = True

        elif event == 'More Options':
            # if user selects more options, then return the action more options
            window.close()
            # return the action for more options
            return 'more'

        elif event == KEY_BUTTON_SAVE:
            root = tk.Tk()
            root.withdraw()
            file = filedialog.asksaveasfilename(
                filetypes=(("png", "*.png"), ("jpeg", "*.jpeg"), ("pdf", "*.pdf"), ("svg", "*.svg")), defaultextension=(("png", "*.png")))
            # This checks if file is some representation of empty, ie '' or ()
            # handles the fact that an empty return from asksaveasfilename returns '' on windows and () on linux
            if file:
                plt.savefig(file, dpi=450)

        elif event == 'Save Figure':
            # saves figure currently displayed
            root = tk.Tk()
            root.withdraw()
            file = filedialog.asksaveasfilename(filetypes=(
                ("png", "*.png"), ("jpeg", "*.jpeg"), ("pdf", "*.pdf"), ("svg", "*.svg")), defaultextension=(("png", "*.png")))
            if file:
                plt.savefig(file, dpi=450)

        elif event == 'Save DF':
            # saves states_dataframe.csv
            root = tk.Tk()
            root.withdraw()
            file = filedialog.asksaveasfilename(
                filetypes=(("csv", "*.csv"), ("Excel", "*.xlsx")), defaultextension=(("csv", "*.csv")))
            # TODO the states dataframe CANNOT be hardcoded
            original = os.getcwd() + '\states_dataframe.csv'
            if file:
                target = file
                shutil.copyfile(original, target)

        elif event == 'Save Simple DF':
            # saves states_simple.csv
            root = tk.Tk()
            root.withdraw()
            file = filedialog.asksaveasfilename(
                filetypes=(("csv", "*.csv"), ("Excel", "*.xlsx")), defaultextension=(("csv", "*.csv")))
            original = os.getcwd() + '\states_simple.csv'
            if file:
                target = file
                shutil.copyfile(original, target)

        elif event == 'Save States.mat':
            # saves states in matlab file type
            root = tk.Tk()
            root.withdraw()
            file = filedialog.asksaveasfilename(
                filetypes=[("mat", "*.mat")], defaultextension=(("mat", "*.mat")))
            original = os.getcwd() + '\states.mat'
            if file != '':
                target = file
                shutil.copyfile(original, target)

        # cases for the about dropdown menu items
        elif event == ui_text.TITLE_ABOUT_INPUTS_POPUP:
            # explains the inputs and what they mean
            sg.popup(*ui_text.TEXT_ABOUT_INPUTS_POPUP,
                     title=ui_text.TITLE_ABOUT_INPUTS_POPUP)
        elif event == ui_text.TITLE_ABOUT_OUTPUTS_POPUP:
            # explains the outputs and what they mean
            sg.popup(*ui_text.TEXT_ABOUT_OUTPUTS_POPUP,
                     title=ui_text.TITLE_ABOUT_OUTPUTS_POPUP)
        elif event == ui_text.TITLE_ABOUT_SIMULATOR_POPUP:
            # explains the importance of the software
            sg.popup(*ui_text.TEXT_ABOUT_SIMULATOR_POPUP,
                     title=ui_text.TITLE_ABOUT_SIMULATOR_POPUP)

        # TODO add a proper event for windows closed (event == WIN_CLOSED)?
        elif event == sg.WIN_CLOSED:
            # kill the simulation, if running
            # will do nothing if not running
            if simulation_obj is not None:
                simulation_obj.kill_simulation()
            # break out of the loop so that the program will close
            break

        # check the bounds on the simulation iteration
        if simStep < 0:
            simStep = 0
        elif simStep >= num_steps:
            simStep = num_steps - 1
            # if the simulation is playing through failures, stop it, as it has reached the end
            animateTopology = False
            window[KEY_BUTTON_ANIMATE].update(text='Play')
        # redraw the figure if the iteration has changed
        # only redraw if a simulation is loaded, avoids crashes
        if redrawFigure and simulation_obj is not None:
            # update_step_text(window, simStep, num_steps)
            gui_utilities.update_text(window, KEY_TEXT_SIM_STEP,
                                      ui_text.FORMAT_TEXT_SIM_STEP, (simStep, num_steps - 1))
            fig.clear()
            if figure_display_state == FigureState.TOPOLOGY:
                fig = graph_data.plot_topology(
                    iteration_index, simStep, fig=fig)
            elif figure_display_state == FigureState.PSTOP:
                fig = draw_plot.draw_pstop_curve(
                    fig, simulation_obj.get_states_dataframe())
            fig.canvas.draw()
            redrawFigure = False
        # disable first and last buttons if at the beginning or end of the simulation
        disable_forward_back_buttons(window, simStep, num_steps)

    window.close()
    # quit application
    return 'quit'
