

from random import seed
import matplotlib.pyplot as plt
import networkx as nx
import scipy.io
import pandas as pd

#TODO: change plot_topology function to take in a state matrix and a specific iteration within that state matrix, then, based on the failures, display those failures on the grid
MPC_PATH = 'case118_mpc_presim.mat'
SIM_STATE_MATRIX = 'case118_f2_r2_t1_e1_i100000_sm.mat'
SIM_INITIAL_FAILURES = 'case118_f2_r2_t1_e1_i100000_if.mat'

SEED = 42


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

def plot_topology():
    fig = plt.figure()
    mpc_matrix = load_mpc(MPC_PATH)
    branch_data = get_branch_dataframe(mpc_matrix)

    edges = [(branch_data['from bus number'][i], branch_data['to bus number'][i])
            for i in range(branch_data.shape[0])]


    g = nx.Graph()

    g.add_edges_from(edges)

    colors = ['r' if i % 10 == 0 else 'b' for i in range(branch_data.shape[0])]
    weights = [5 if i == 'r' else 1 for i in colors]

    # pos = nx.spring_layout(g, seed=SEED)
    pos = nx.kamada_kawai_layout(g)


    nx.draw(g, pos=pos, with_labels=True, node_size=60,
            font_size=8, edge_color=colors, width=weights)
    
    
    return fig
