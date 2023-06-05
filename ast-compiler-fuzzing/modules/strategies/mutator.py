import random
from datetime import datetime

from modules.strategies.random import Random
from modules.strategies.boundaries import Boundaries
from modules.strategies.modification import Modification
from modules.test import Input

import matplotlib.pyplot as plt

class Mutator:
    
    
    def __init__(self) -> None:
        self.strategies = {
            "Random":  Random(),
            "Boundaries": Boundaries(),
             "Modification":  Modification(),
        }
        
        self.heuristic_stats = {
            "Random": [],
            "Boundaries": [],
            "Modification": [],
        }
        self.STRATEGY_TRIES = [*(["Random"] * 20 +["Boundaries"] * 5 + ["Modification"] * 10)] * 4
        
    
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
        self.heuristic_stats[strategy_name] += [datetime.now()]
        return mutated_value
    
    def mutate(self, input: Input, strategy_name: str) -> str:
        try: 
            mutated_value = self.strategies[strategy_name].mutate(input)
        except ValueError as e:
            strategy_name = "Random"
            mutated_value =  self.strategies[strategy_name].mutate(input)
        self.heuristic_stats[strategy_name] += [datetime.now()]
        return mutated_value
    
    def plot(self):
                
        strategies = [self.strategies_names[i] for i in self.heuristic_stats.keys()]
        count = [len(self.heuristic_stats[key]) for key in self.heuristic_stats]
        
        fig = plt.figure(figsize = (10, 5))
        
        plt.bar(strategies, count, color ='maroon', width = 0.4)
        
        plt.xlabel("Strategy")
        plt.ylabel("Strategy count")
        plt.title("Mutation strategies")
        plt.show()