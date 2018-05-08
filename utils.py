import time
import threading
from contextlib import contextmanager
import thread
import networkx as nx
import copy


class TimeoutException(Exception):
    pass


@contextmanager
def time_limit(seconds):
    timer = threading.Timer(seconds, lambda: thread.interrupt_main())
    timer.start()
    try:
        yield
    except KeyboardInterrupt:
        raise TimeoutException()
    finally:
        timer.cancel()


def timing(f):
    '''
    Measures time of function execution
    '''

    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        print '\n{0} function took {1:.3f} ms'.format(
            f.__name__, (time2 - time1) * 1000.0)
        return ret, '{0:.3f} ms'.format((time2 - time1) * 1000.0)

    return wrap


def read_dimacs_graph(file_path):
    edges = []  # list of edges
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith('e'):
                _, v1, v2 = line.split()
                edges.append((int(v1), int(v2)))
            else:
                continue
        return nx.Graph(edges)


def arguments():
    import argparse
    parser = argparse.ArgumentParser(
        description='Compute maximum clique for a given graph')
    parser.add_argument('--path', type=str, required=True,
                        help='Path to dimacs-format graph file')
    parser.add_argument('--time', type=int, default=60,
                        help='Time limit in seconds')
    return parser.parse_args()


def find_mwis(bnc_class):
    '''
         maximum weighted independent set problem
            w_1 * x1 + w_2 * x2 + ... + w_n * xn -> max\n
            criterion for node: small degree, big weight
            (number_of_nodes - node_degree) + weight -> max
            xi + xj <= 1, for every pair (i,j) which connected by edge\n
     '''

    def compute_score(candidate):
        degree_func = bnc_class.graph.degree
        node_degree = degree_func[candidate[0]]
        # node_score = len(bnc_class.nodes) - node_degree + candidate[1] #number of nodes - node-degree + node_weight
        alpha = 0.7
        b = len(bnc_class.nodes) - 1.0
        score_reducer = (1.0 / b) * node_degree
        node_score = alpha * candidate[1] - (1 - alpha) * score_reducer
        return node_score

    def incorporate_mwis(curr_mwis, mwis_cand_list):
        best_candidate = max(mwis_cand_list, key=lambda x: compute_score(x))
        best_cand_neighbors = bnc_class.adj_matrix[best_candidate[0] - 1].todense()  # returned row of adj matrix - 2d scipy matrix

        new_curr_mwis = curr_mwis + [best_candidate]
        new_cand_list = [cand_ for cand_ in mwis_cand_list if
                         (cand_[0] != best_candidate[0]) & (best_cand_neighbors[0, cand_[0] - 1] != 1)]

        if not new_cand_list:
            return new_curr_mwis
        else:
            return incorporate_mwis(new_curr_mwis, new_cand_list)

    mwis_candidates_with_weights = zip(bnc_class.clique_candidates, bnc_class.clique_candidates_weights)
    return incorporate_mwis([], mwis_candidates_with_weights)
