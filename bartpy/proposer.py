from abc import abstractclassmethod
from copy import deepcopy
from typing import Callable

import numpy as np

from bartpy.errors import NoSplittableVariableException
from bartpy.tree import LeafNode, TreeStructure, split_node, TreeMutation


class TreeMutationProposer:

    def __init__(self, tree_structure: TreeStructure):
        self.tree_structure = tree_structure

    @abstractclassmethod
    def proposal(self) -> TreeMutation:
        raise NotImplementedError()


class GrowTreeMutationProposer(TreeMutationProposer):

    def __init__(self, tree_structure: TreeStructure):
        super().__init__(tree_structure)

    def proposal(self) -> TreeMutation:
        node = self.tree_structure.random_splittable_leaf_node()
        if node is None:
            raise NoSplittableVariableException()
        updated_node = split_node(node)
        return TreeMutation("grow", node, updated_node)


class PruneTreeMutationProposer(TreeMutationProposer):

    def __init__(self, tree_structure: TreeStructure):
        super().__init__(tree_structure)

    def proposal(self) -> TreeMutation:
        node = self.tree_structure.random_leaf_parent()
        updated_node = LeafNode(node.data)
        return TreeMutation("prune", node, updated_node)


class ChangeTreeMutationProposer(TreeMutationProposer):

    def __init__(self, tree_structure: TreeStructure):
        super().__init__(tree_structure)

    def proposal(self) -> TreeMutation:
        node = self.tree_structure.random_leaf_parent()
        updated_node = deepcopy(node)
        leaf_node = LeafNode(updated_node.data)
        updated_split_node = split_node(leaf_node)
        return TreeMutation("change", node, updated_split_node)


class Proposer:

    def __init__(self, p_grow: float, p_prune: float, p_change: float):
        self.p_grow = p_grow
        self.p_prune = p_prune
        self.p_change = p_change

    def sample_mutation_method(self) -> Callable[[TreeStructure], TreeMutationProposer]:
        method = np.random.choice([ChangeTreeMutationProposer, GrowTreeMutationProposer, PruneTreeMutationProposer], p=[self.p_change, self.p_grow, self.p_prune])
        print(method)
        return method

    def propose(self, tree_structure: TreeStructure) -> TreeMutation:
        method = self.sample_mutation_method()
        try:
            return method(tree_structure).proposal()
        except NoSplittableVariableException:
            return self.propose(tree_structure)


if __name__ == "__main__":
    from bartpy.data import Data
    import pandas as pd
    from bartpy.sigma import Sigma
    from bartpy.model import Model

    data = Data(pd.DataFrame({"b": [1, 2, 3]}), pd.Series([1, 2, 3]), normalize=True)
    sigma = Sigma(1., 2.)
    model = Model(data, sigma)

    change = Proposer(0, 0, 1).propose(model.trees[0])
    print(change.existing_node.split)
    print(change.updated_node.split)