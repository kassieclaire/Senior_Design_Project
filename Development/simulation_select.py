
import load_sim_data
import PySimpleGUI as sg
import gui_utilities
from gui_utilities import TEXT_COLOR, BACKGROUND_COLOR
import generate_mpc_plot_networkx

SLIDER_MIN_LINE_FAILURES = 'slider_min_line_failures'
SLIDER_MIN_LINE_FAILURES_TOOLTIP = 'filters the simulation results based on the minimum number of line failures'
SLIDER_MAX_LINE_FAILURES = 'slider_max_line_failures'
SLIDER_MAX_LINE_FAILURES_TOOLTIP = 'filters the simulation results based on the maximum number of line failures'
ITERATION_SELECTION_LIST = 'selection_list'
UPDATE_FILTERS_BUTTON = 'update_filters_button'


def getGUIElement():
    layout = sg.Column([[gui_utilities.make_slider_with_frame('Minimum Line Failures', SLIDER_MIN_LINE_FAILURES, range=(0, 100), resolution=1)],
                        [gui_utilities.make_slider_with_frame(
                            'Maximum Line Failures', SLIDER_MAX_LINE_FAILURES, range=(0, 100), resolution=1, default_value=100)],
                        [sg.Button('Update Filters',
                                   key=UPDATE_FILTERS_BUTTON, enable_events=True, button_color=(TEXT_COLOR, BACKGROUND_COLOR))],
                        [sg.Listbox(values=[], key=ITERATION_SELECTION_LIST, enable_events=True, size=(15, 10))]])
    return layout


def display_iterations(window, graph_data, min_line_failures, max_line_failures):
    """
    """
    iterations_index_list = filter_iterations(
        graph_data, min_line_failures, max_line_failures)
    window[ITERATION_SELECTION_LIST].update(values=iterations_index_list)


def filter_iterations(graph_data: generate_mpc_plot_networkx.TopologyIterationData, min_line_failures, max_line_failures, iteration_indices: 'list[int]' = None):
    """
    Returns an array of iteration indices that have a number of line failures in the range [min_line_failures, max_line_failures]
    @param graph_data: TopologyIterationData object of the simulation to filter
    @param min_line_failures: minimum number of line failures of the simulations to leave
    @param max_line_failures: maximum number of line failures of the simulations to leave
    @param iteration_indices: list of iteration indices to filter. Optional, will use all iterations if not specified
    """
    if iteration_indices is None:
        iteration_indices = range(graph_data.get_num_iterations())

    validRange = range(min_line_failures, max_line_failures + 1)
    filtered_iterations = [i for i in
                           iteration_indices if graph_data.get_total_failures_at_iteration(i) in validRange]
    return filtered_iterations


if __name__ == '__main__':
    SIM_STATE_MATRIX = 'case118_f2_r7_t1_e1_i100000_sm.mat'
    SIM_INITIAL_FAILURES = 'case118_f2_r7_t1_e1_i100000_if.mat'
    MPC_PATH = 'case118_mpc_presim.mat'
    state_matrix = load_sim_data.load_state_matrix(SIM_STATE_MATRIX)
    initial_failures = load_sim_data.load_initial_failures(
        SIM_INITIAL_FAILURES)
    graph_data = generate_mpc_plot_networkx.TopologyIterationData(
        state_matrix, initial_failures, MPC_PATH)
    # branch_data = generate_mpc_plot_networkx.get_branch_dataframe(
    #     generate_mpc_plot_networkx.load_mpc(MPC_PATH))
    # negativeOneIndices = generate_mpc_plot_networkx.get_statematrix_steady_state_negative_one_indices(
    #     state_matrix)
    # mostFailureSimIndex = generate_mpc_plot_networkx.get_sim_index_with_most_failures(
    #     negativeOneIndices)
    iter = filter_iterations(graph_data, 0, 3)
    print(iter)
    print([graph_data.get_total_failures_at_iteration(i) for i in iter])
