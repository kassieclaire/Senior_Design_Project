

import load_sim_data
from ast import Num
from json import load
from random import seed
from xmlrpc.client import Boolean
import matplotlib.pyplot as plt
import networkx as nx
import scipy.io
import pandas as pd


MPC_PATH = 'case118_mpc_presim.mat'
SIM_STATE_MATRIX = 'case118_f2_r7_t1_e1_i100000_sm.mat'
SIM_INITIAL_FAILURES = 'case118_f2_r7_t1_e1_i100000_if.mat'

SEED = 42


class TopologyIterationData:
    def __init__(self, state_matrix, initial_failures, mpc_path):
        mpc = load_mpc(mpc_path)
        self.branch_dataframe = get_branch_dataframe(mpc)
        self.state_matrix = state_matrix
        self.initial_failures = initial_failures
        self.sim_end_indices = get_statematrix_steady_state_negative_one_indices(
            self.state_matrix)
        self.sim_index_most_failures = get_sim_index_with_most_failures(
            self.sim_end_indices)
        edges = [(self.branch_dataframe['from bus number'][i], self.branch_dataframe['to bus number'][i])
                 for i in range(self.branch_dataframe.shape[0])]
        self.graph = nx.Graph()
        self.graph.add_edges_from(edges)
        self.edge_labels = {edges[i]: i +
                            1 for i in range(self.branch_dataframe.shape[0])}
        # calculate the positions for the nodes
        # kamanda_kawai layout algorithm is deterministic, making results repeatable
        # save the positions into the graph object
        nx.set_node_attributes(
            self.graph, nx.kamada_kawai_layout(self.graph), 'pos')

    def plot_topology(self, iteration_index, step_index, fig=None, bus_labels: bool = True, branch_labels: bool = False):
        if fig is None:
            fig = plt.figure()
        else:
            fig = plt.figure(fig.number)
        failure_index_arr = get_failure_array_at_iteration(
            self.initial_failures, self.state_matrix, self.sim_end_indices, iteration_index, step_index)
        # shift the indices down 1 as python is zero-based and therefore networkx will be looking for zero-based indices
        failure_index_arr = [x - 1 for x in failure_index_arr]
        colors = labels_at_indices(
            failure_index_arr, 'r', 'b', self.branch_dataframe.shape[0])

        # TODO change the weight to reflect load
        weights = [5 if i == 'r' else 1 for i in colors]
        # draw the graph object onto the active figure
        # NOTE: position must be explicitly set, or else a nondeterministic spring layout will be used
        # This remains true even when
        nx.draw(self.graph, pos=nx.get_node_attributes(self.graph, 'pos'), with_labels=bus_labels, node_size=60,
                font_size=8, edge_color=colors, width=weights)
        if branch_labels:
            nx.draw_networkx_edge_labels(
                self.graph, pos=nx.get_node_attributes(self.graph, 'pos'), edge_labels=branch_labels, font_size=6, rotate=False)
        # plt.show()
        return fig

    def get_iteration_index_with_most_failures(self) -> int:
        """
        Returns the index of the iteration with the most failures
        """
        return self.sim_index_most_failures

    def get_iteration_start_end_steps(self, interation_index) -> int:
        startIndex = self.sim_end_indices[interation_index -
                                          1] + 1 if interation_index > 0 else 0
        endIndex = self.sim_end_indices[interation_index] + 1
        steps = endIndex - startIndex
        return startIndex, endIndex, steps

    def get_num_steps(self, interation_index) -> int:
        """
        Returns the number of steps (line failures after the initial failures) in the given iteration
        """
        _, _, steps = self.get_iteration_start_end_steps(interation_index)
        return steps


def load_mpc(path: str):
    mpc_matrix = scipy.io.loadmat(MPC_PATH)
    # removes data other than the actual MPC data
    mpc_matrix = mpc_matrix[list(mpc_matrix)[3]]
    return mpc_matrix


def get_branch_dataframe(mpc_matrix):
    # convert the branch data from the MPC into a dataframe
    # column details:
    # https://matpower.org/docs/ref/matpower5.0/caseformat.html
    branch_column_names = ['from bus number', 'to bus number', 'resistance', 'reactance', 'susceptance', 'rateA',
                           'rateB', 'rateC', 'ratio', 'angle', 'initial branch status', 'min angle difference', 'max angle difference']
    branch_data = pd.DataFrame(mpc_matrix['branch'][0][0], columns=branch_column_names).astype(
        {'from bus number': int, 'to bus number': int, 'initial branch status': int})
    return branch_data


def get_statematrix_steady_state_negative_one_indices(state_matrix) -> 'list[int]':
    return [i for i, x in enumerate(state_matrix['Steady State']) if x == -1]


def get_sim_index_with_most_failures(line_failed_negative_one_indices) -> int:
    maxFailures = 0
    maxIndex = 0
    for i in range(1, len(line_failed_negative_one_indices)):
        numFailures = line_failed_negative_one_indices[i] - \
            line_failed_negative_one_indices[i - 1] - 1
        if(numFailures > maxFailures):
            maxFailures = numFailures
            maxIndex = i
    return maxIndex


def get_simulation_start_end_iterations(line_failed_negative_one_indices, simulation_index):
    startIndex = line_failed_negative_one_indices[simulation_index -
                                                  1] + 1 if simulation_index > 0 else 0
    endIndex = line_failed_negative_one_indices[simulation_index] + 1
    iterations = endIndex - startIndex
    return startIndex, endIndex, iterations


def get_single_simulation_state_matrix(state_matrix, line_failed_negative_one_indices, simulation_index):
    startIndex, endIndex, _ = get_simulation_start_end_iterations(
        line_failed_negative_one_indices, simulation_index)
    # startIndex = line_failed_negative_one_indices[simulation_index -
    #                                               1] + 1 if simulation_index > 0 else 0
    # endIndex = line_failed_negative_one_indices[simulation_index] + 1
    return state_matrix[startIndex:endIndex]

# def get_failure_labels_at_index(self, iteration: int, failedLabel, liveLabel) -> 'list[int]':
#         failures = self.get_failures_until_iteration(iteration)
#         return [failedLabel if i in failures else liveLabel for i in range(self.total_lines)]


def get_failure_array_at_iteration(initial_failures, state_matrix, line_failed_negative_one_indices, simulation_index, iteration_index):
    state_matrix = get_single_simulation_state_matrix(
        state_matrix, line_failed_negative_one_indices, simulation_index)
    # initial_failures = initial_failures[simulation_index]
    failures = initial_failures[simulation_index] + \
        state_matrix['Failed Line Index'][1:iteration_index + 1].tolist()
    return failures


def labels_at_indices(arr: 'list[int]', val_if_present, val_if_not_present, num_indices) -> list:
    return [val_if_present if i in arr else val_if_not_present for i in range(num_indices)]


def plot_network(mpc_branch_dataframe, initial_failures, state_matrix, simulation_end_index_array, simulation_index, iteration_index, bus_labels: bool = True, branch_labels: bool = False, axes=None, fig=None):
    if fig is None:
        fig = plt.figure()
    else:
        fig = plt.figure(fig.number)
    failure_indix_arr = get_failure_array_at_iteration(
        initial_failures, state_matrix, simulation_end_index_array, simulation_index, iteration_index)
    # shift the indices down 1 as python is zero-based and therefore networkx will be looking for zero-based indices
    failure_indix_arr = [x - 1 for x in failure_indix_arr]
    colors = labels_at_indices(
        failure_indix_arr, 'r', 'b', mpc_branch_dataframe.shape[0])
    edges = [(mpc_branch_dataframe['from bus number'][i], mpc_branch_dataframe['to bus number'][i])
             for i in range(mpc_branch_dataframe.shape[0])]
    g = nx.Graph()
    g.add_edges_from(edges)
    edge_labels = {edges[i]: i +
                   1 for i in range(mpc_branch_dataframe.shape[0])}
    # TODO change the weight to reflect load
    weights = [5 if i == 'r' else 1 for i in colors]
    # calculate the positions for the nodes
    # kamanda_kawai layout algorithm is deterministic, making results repeatable
    # save the positions into the graph object
    nx.set_node_attributes(g, nx.kamada_kawai_layout(g), 'pos')
    # draw the graph object onto the active figure
    # NOTE: position must be explicitly set, or else a nondeterministic spring layout will be used
    # This remains true even when
    nx.draw(g, pos=nx.get_node_attributes(g, 'pos'), ax=axes, with_labels=bus_labels, node_size=60,
            font_size=8, edge_color=colors, width=weights)
    if branch_labels:
        nx.draw_networkx_edge_labels(
            g, pos=nx.get_node_attributes(g, 'pos'), ax=axes, edge_labels=edge_labels, font_size=6, rotate=False)
    # plt.show()
    return fig


def increment_if_result_in_range(val: Num, increment_val: Num, rng: range) -> Num:
    return val + increment_val if val + increment_val in rng else val


if __name__ == '__main__':
    mpc_matrix = load_mpc(MPC_PATH)
    mpc_branch_dataframe = get_branch_dataframe(mpc_matrix)

    # print(branch_data)

    # edges = [(branch_data['from bus number'][i], branch_data['to bus number'][i])
    #          for i in range(branch_data.shape[0])]

    # # print(edges)

    # g = nx.Graph()

    # g.add_edges_from(edges)

    # edge_labels = {edges[i]: i + 1 for i in range(branch_data.shape[0])}
    # # print(edge_labels)

    # colors = ['r' if i % 10 == 0 else 'b' for i in range(branch_data.shape[0])]
    # weights = [5 if i == 'r' else 1 for i in colors]
    # # print(colors)

    # # pos = nx.spring_layout(g, seed=SEED)
    # pos = nx.kamada_kawai_layout(g)

    # nx.draw(g, pos=pos, with_labels=True, node_size=60,
    #         font_size=8, edge_color=colors, width=weights)
    # nx.draw_networkx_edge_labels(
    # g, pos, edge_labels=edge_labels, font_size=6, rotate=False)
    # plt.show()

    # print(max(branch_data['from bus number']))
    # print(max(branch_data['to bus number']))

    state_matrix = load_sim_data.load_state_matrix(SIM_STATE_MATRIX)
    initial_failures = load_sim_data.load_initial_failures(
        SIM_INITIAL_FAILURES)

    # state_matrix = state_matrix[:100]
    # initial_failures = initial_failures[:100]

    # print(state_matrix['Failed Line Index'])
    # print(max(state_matrix['Failed Line Index']))
    # print(initial_failures)

    # generate_simulation_history_array(state_matrix, initial_failures)
    print(state_matrix.shape)
    # print([state_matrix['Failed Line Index'][i]
    #   for i in range(state_matrix.shape[0])])

    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(state_matrix[['Steady State', 'Failed Line Index']])

    negativeOneIndices = get_statematrix_steady_state_negative_one_indices(
        state_matrix)

    print([x for x in zip(negativeOneIndices, range(len(negativeOneIndices)))])
    # print(get_single_simulation_state_matrix(state_matrix, zeroIndices, 30))
    print(get_sim_index_with_most_failures(negativeOneIndices))
    # print(get_single_simulation_state_matrix(state_matrix, zeroIndices, get_sim_index_with_most_failures(zeroIndices)))
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(get_single_simulation_state_matrix(state_matrix, negativeOneIndices,
                                                 get_sim_index_with_most_failures(negativeOneIndices)))
        # print(get_single_simulation_state_matrix(state_matrix, negativeOneIndices, 0))

    for i in range(10):
        print(get_failure_array_at_iteration(initial_failures, state_matrix,
                                             negativeOneIndices, get_sim_index_with_most_failures(negativeOneIndices), i))

    print()

    print(labels_at_indices([1, 2, 6], 'present', 'not present', 15))

    # fig = plot_network(branch_data, initial_failures, state_matrix,
    #                    negativeOneIndices, get_sim_index_with_most_failures(negativeOneIndices), 4, True, False)
    # fig.show()

    # plt.figure(fig.number)
    # plt.show()

    most_failure_sim_index = get_sim_index_with_most_failures(
        negativeOneIndices)
    iteration = 0
    _, _, numIterations = get_simulation_start_end_iterations(
        negativeOneIndices, most_failure_sim_index)
    print(f"{numIterations} iterations")
    plt.ion()
    # fig = plt.figure()
    fig = None
    # ax = plt.axes()
    ax = None
    # print(fig.axes)
    while(1):
        # for i in range(numIterations):
        #     fig = plot_network(branch_data, initial_failures, state_matrix,
        #                        negativeOneIndices, get_sim_index_with_most_failures(negativeOneIndices), iteration, True, False)
        #     plt.figure(fig.number)
        #     plt.show(block=False)

        action = input("w to advance, s to go back, x to exit")
        if action == 'w':
            iteration += 1
            # plt.close()
        elif action == 's':
            iteration -= 1
            # plt.close()
        elif action == 'x':
            break
        if fig is not None:
            fig.clear()
        fig = plot_network(mpc_branch_dataframe, initial_failures, state_matrix,
                           negativeOneIndices, get_sim_index_with_most_failures(negativeOneIndices), iteration, True, False, ax, fig)
        plt.show(block=False)
    # plt.figure(fig.number)
