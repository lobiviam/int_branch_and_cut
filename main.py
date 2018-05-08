from utils import *
from sandbox import *
from networkx.algorithms.approximation.clique import max_clique
import cplex
import sys
sys.setrecursionlimit(3000)


class branch_and_cut:
    def __init__(self, graph, precision=1e-5):
        self.graph = graph
        self.adj_matrix = nx.adjacency_matrix(self.graph)
        self.precision = precision
        self.nodes = self.graph.nodes
        self.ind_sets = []
        self.not_connected = nx.complement(self.graph).edges  # dopolnenie grapha
        # self.current_maximum_clique_len = len(max_clique(self.graph))
        # self.heuristic_max_clique =
        # self.heuristic_max_clique_len =
        # print(self.heuristic_max_clique_len)
        self.current_max_clique = max_clique(self.graph)
        self.current_maximum_clique_len = len(self.current_max_clique)
        self.branch_num = 0

        self.get_ind_sets()
        self.reduced_master_problem = self.construct_reduced_master_problem()
        self.mwis_problem = None
        self.current_obj_values = []

    def get_ind_sets(self):
        strategies = [nx.coloring.strategy_largest_first,
                      nx.coloring.strategy_random_sequential,
                      nx.coloring.strategy_independent_set,
                      nx.coloring.strategy_connected_sequential_bfs,
                      nx.coloring.strategy_connected_sequential_dfs,
                      nx.coloring.strategy_saturation_largest_first]

        for strategy in strategies:
            d = nx.coloring.greedy_color(self.graph, strategy=strategy)  # return dict (keys - nodes, values - color)
            for color in set(color for node, color in d.items()):
                self.ind_sets.append(
                    [key for key, value in d.items() if value == color])
        # self.min_coloring = min(self.ind_sets, key=lambda x: len(x))

    def construct_reduced_master_problem(self):
        '''
        Construct Reduced master problem
        nodes: list of names of all nodes in graph
        ind_sets: list of independent sets (each as list of nodes names)

        Problem\n
        x1 + x2 + ... + xn -> max\n
        xk + ... + xl <= 1  (ind_set_num times, [k...l] - nodes from independent set)\n
        0 <= x1 <= 1\n
        ...\n
        0 <= xn <= 1\n

        '''
        problem = cplex.Cplex()
        problem.objective.set_sense(problem.objective.sense.maximize)

        obj = [1.0] * len(self.nodes)
        upper_bounds = [1.0] * len(self.nodes)
        types = [problem.variables.type.continuous] * len(self.nodes)
        columns_names = [str(it) for it in sorted(self.graph.nodes)]

        problem.set_log_stream(None)
        problem.set_results_stream(None)
        problem.set_warning_stream(None)
        problem.set_error_stream(None)

        problem.variables.add(obj=obj, ub=upper_bounds, names=columns_names, types=types)

        constraints = []

        for ind_set in self.ind_sets:
            constraints.append([[str(x) for x in ind_set], [1.0] * len(ind_set)])
        ind_sets_len = len(self.ind_sets)
        right_hand_side = [1.0] * ind_sets_len
        constraint_names = ['c{0}'.format(key) for key, value in enumerate(self.ind_sets)]
        constraint_senses = ['L'] * ind_sets_len

        problem.linear_constraints.add(lin_expr=constraints,
                                       senses=constraint_senses,
                                       rhs=right_hand_side,
                                       names=constraint_names)
        return problem

    def filter_solution(self, solution):
        return list(map(lambda x: x[0], filter(lambda x: x[1] == 1, enumerate(solution, start=1))))

    def get_branching_variable(self):
        def is_integer_weight(_pair):
            return not _pair[0].is_integer()

        def get_first_element(_pair):
            return _pair[0]

        def nvl(_seq):
            return [(None, None)] if len(_seq) < 1 else _seq

        return max(
            nvl(list(
                filter(is_integer_weight, zip(self.clique_candidates_weights, self.clique_candidates))
            )),
            key=get_first_element
        )[1]

    def add_constraint(self, constraints, rhs, name, sense='L'):
        num_constraints = len(constraints)
        constraints = [str(x) for x in constraints]
        self.reduced_master_problem.linear_constraints.add(lin_expr=[[constraints, [1.0] * num_constraints]],
                                                           senses=[sense],
                                                           rhs=[rhs],
                                                           names=[name])

    def solve_rmp(self):
        try:
            self.reduced_master_problem.solve()

            if self.reduced_master_problem.solution.get_status() != 101:  # An optimal integer solution has been found
                print(self.reduced_master_problem.solution.get_status())
                print(self.reduced_master_problem.solution.get_status_string())
                raise cplex.exceptions.CplexSolverError

            self.current_obj_values = self.reduced_master_problem.solution.get_values()
            self.current_obj_sum = sum(self.current_obj_values)
            self.clique_candidates = []
            self.clique_candidates_weights = []
            for value, name in zip(self.current_obj_values, self.reduced_master_problem.variables.get_names()):
                if value - self.precision > 0:  # solver value- 1*10^-5
                    self.clique_candidates.append(int(name))
                    self.clique_candidates_weights.append(value)
            return True

        except cplex.exceptions.CplexSolverError:
            self.current_obj_values = []
            self.current_obj_sum = None
            self.clique_candidates = []
            self.clique_candidates_weights = []
            return False

    def delete_branch(self, name):
        self.reduced_master_problem.linear_constraints.delete(name)

    def branching(self, bvar):
        branch_num = self.branch_num

        self.add_constraint([bvar], 0.0, 'branch_{}_{}'.format(branch_num, 0), sense='E')
        branch_2 = self.solve
        self.delete_branch('branch_{}_{}'.format(branch_num, 0))

        self.add_constraint([bvar], 1.0, 'branch_{}_{}'.format(branch_num, 1), sense='E')
        branch_1 = self.solve
        self.delete_branch('branch_{}_{}'.format(branch_num, 1))

        return max(branch_1, branch_2, key=lambda x: len(x))

    def check_clique(self):
        subgraph = self.graph.subgraph(self.clique_candidates)
        for node1 in subgraph.nodes:
            for node2 in subgraph.nodes:
                if node1 != node2:
                    if not subgraph.has_edge(node1, node2):
                        return False
        return True

    @property
    def solve(self):

        self.branch_num += 1

        if not self.solve_rmp():
            return []

        if self.current_obj_sum <= self.current_maximum_clique_len:
            return self.current_max_clique

        mwis_counter = 0
        mwis_solution = find_mwis(self)
        mwis_weight_sum = sum([tpl_a[1] for tpl_a in mwis_solution])

        prev_obj_sum = self.current_obj_sum
        obj_sum_repeat = 0

        while mwis_weight_sum > 1 and self.current_obj_sum > self.current_maximum_clique_len and obj_sum_repeat < 20:
            mwis_counter += 1
            self.add_constraint([str(tpl_b[0]) for tpl_b in mwis_solution], 1.0,
                                'MWIS_{}_{}'.format(self.branch_num, mwis_counter))
            if not self.solve_rmp():
                return []

            mwis_solution = find_mwis(self)
            mwis_weight_sum = sum([tpl_c[1] for tpl_c in mwis_solution])

            if self.current_obj_sum - prev_obj_sum < 0.1:
                obj_sum_repeat += 1
            else:
                obj_sum_repeat = 0
            prev_obj_sum = self.current_obj_sum

        branching_variable = self.get_branching_variable()
        if branching_variable is None:  # all weights are integer
            if self.check_clique():
                if self.current_maximum_clique_len < len(self.clique_candidates):
                    self.current_maximum_clique_len = len(self.clique_candidates)
                    self.current_max_clique = self.clique_candidates
                return self.current_max_clique
            else:  # get all non-incidents nodes in clique candidates and add to constraint in rmp
                inversed_cand_graph = nx.complement(self.graph.subgraph(self.clique_candidates))
                for key, edge in enumerate(inversed_cand_graph.edges()):
                    self.add_constraint(edge, 1.0, 'not_clique_{0}_{1}'.format(self.branch_num, key))
                return self.solve
        else:
            return self.branching(str(branching_variable))


@timing
def solve_clique(graph):
    clique = branch_and_cut(graph).solve
    return clique


def main():
    args = arguments()
    graph = read_dimacs_graph(args.path)
    try:
        with time_limit(args.time):
            clq = solve_clique(graph)
            print len(clq[0])
    except TimeoutException:
        print("Timed out!")
        sys.exit(0)


if __name__ == '__main__':
    main()
