from copy import deepcopy
from typing import List, Optional

import numpy as np

from bartpy.data import Data
from bartpy.splitcondition import CombinedCondition, SplitCondition


class Split:
    """
    The Split class represents the conditioned data at any point in the decision tree
    It contains the logic for:

     - Maintaining a record of which rows of the covariate matrix are in the split
     - Being able to easily access a `Data` object with the relevant rows
     - Applying `SplitConditions` to further break up the data
    """

    def __init__(self, data: Data, combined_condition: Optional[CombinedCondition]=None):
        self._data = data
        if combined_condition is None:
            combined_condition = CombinedCondition(self._data.variables, [])
        self._combined_condition = combined_condition

    @property
    def data(self):
        return self._data

    def combined_condition(self):
        return self._combined_condition

    def condition(self, data: Data=None) -> np.ndarray:
        if data is None:
            return ~self._data.mask[:,0]
        else:
            return self.out_of_sample_condition(data.X)

    def out_of_sample_condition(self, X: np.ndarray):
        self._combined_condition.condition(X)

    def out_of_sample_conditioner(self) -> CombinedCondition:
        return self._combined_condition

    def __add__(self, other: SplitCondition):

        return Split(self._data + other,
                     self._combined_condition + other)

    def most_recent_split_condition(self) -> Optional[SplitCondition]:
        return self._combined_condition.most_recent_split_condition()

    def update_y(self, y):
        self._data.update_y(y)
