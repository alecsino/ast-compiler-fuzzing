import random
from datetime import datetime
from modules.data_analyzer import DataAnalyzer

from modules.strategies.random import Random
from modules.strategies.boundaries import Boundaries
from modules.strategies.modification import Modification
from modules.test import Input

import matplotlib.pyplot as plt

class Mutator:
    
    
    def __init__(self, data_analyzer : DataAnalyzer) -> None:
        self.data_analyzer = data_analyzer
        self.strategies = {
            "Random":  Random(),
            "Boundaries": Boundaries(),
             "Modification":  Modification(),
        }
    
    def strategy(self, index: int) -> str:
        if 0 <= index < 0.60:
            return "Random"
        elif 0.60 <= index < 0.75:
            return "Boundaries"
        elif 0.75 <= index <= 1:
            return "Modification"
        
    def mutate(self, input: Input) -> str:
        try: 
            strategy_index = random.uniform(0, 1)
            strategy_name = self.strategy(strategy_index)
            mutated_value =  self.strategies[strategy_name].mutate(input)
        except ValueError as e:
            strategy_name = "Random"
            mutated_value =  self.strategies[strategy_name].mutate(input)
        # self.data_analyzer.register_mutation_type(strategy_name, mutated_value)
        return mutated_value
    
    