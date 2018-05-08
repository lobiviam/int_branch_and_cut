import numpy as np
import networkx as nx

from contextlib import contextmanager
# d=dict()
# d['k']=[1,2,3,4,5,6]
# d['j']=2
# d['a']='test'
# print d.items()


#
# list1 = ['a','b','c','d','e']
# list2 = [1,2,3,4,5]
# zip_result = zip(list1,list2)
# print(zip_result)
# result1= []
# result2 = []
# for name, value in zip(list1,list2):
#     result1.append(name)
#     result2.append(value)
# print(result1)
# print(result2)

from main import branch_and_cut, read_dimacs_graph


def class_inner_fields_test(ex_class):
    print ex_class.clique_candidates


# graph = read_dimacs_graph(r"C:\Users\Olga\PycharmProjects\branch_and_cut\DIMACS\johnson8-2-4.clq.txt")
# bnb = branch_and_cut(graph)
# bnb.solve()
# class_inner_fields_test(bnb)

'''
def find_mwis(bnc_class):
'''
'''
     maximum weighted independent set problem
        w_1 * x1 + w_2 * x2 + ... + w_n * xn -> max\n
        criterion for node: small degree, big weight
        (number_of_nodes - node_degree) + weight -> max
        xi + xj <= 1, for every pair (i,j) which connected by edge\n
'''
'''
    def compute_score(candidate_list):
        score = []
        for candidate in candidate_list:
            node_degree = bnc_class.graph.degree[str(candidate[0])]
            node_score = len(bnc_class.nodes) - node_degree + candidate[1] #number of nodes - node-degree + node_weight
            score.append([candidate[0], node_score])
        return score

    def incorporate_mwis(curr_mwis, mwis_cand_list):
        node_scores_for_mwis = compute_score(mwis_cand_list)
        best_node = max(node_scores_for_mwis, key=lambda x: x[1])[0]
        best_node_neighbors = nx.all_neighbors(bnc_class.graph, str(best_node))

        neighbors_in_mwis_candidates = list(set(best_node_neighbors) &
                                            set([it_[0] for it_ in mwis_candidates_with_weights]))
        new_curr_mwis = curr_mwis + [best_node]
        new_cand_list = [cand_ for cand_ in mwis_cand_list if
                         cand_[0] != best_node | cand_[0] not in neighbors_in_mwis_candidates]
        if not new_cand_list:
            return new_curr_mwis
        else:
            return incorporate_mwis(new_curr_mwis, new_cand_list)

    mwis_candidates_with_weights = zip(bnc_class.clique_candidates, bnc_class.clique_candidates_weights)
    return incorporate_mwis([], mwis_candidates_with_weights)
'''

# graph = read_dimacs_graph(r"C:\Users\Olga\PycharmProjects\branch_and_cut\DIMACS\johnson8-2-4.clq.txt")
# bnb = branch_and_cut(graph)
# bnb.solve
# my_mwis = find_mwis(bnb)
# print(my_mwis)
