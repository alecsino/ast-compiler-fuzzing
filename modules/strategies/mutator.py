import random
from datetime import datetime

from modules.strategies.random import Random
from modules.strategies.boundaries import Boundaries
from modules.strategies.modification import Modification
from modules.test import Input

import matplotlib.pyplot as plt

class Mutator:
    
    
    def __init__(self) -> None:
        self.strategies_names = {
            0: "Random",
            1: "Boundaries",
            2: "Modification",
        }
        self.strategies = [Random(), Boundaries(), Modification()]
        self.heuristic_stats = {
            0: [],
            1: [],
            2: [],
        }
        
    def mutate(self, input: Input) -> str:
        try: 
            strategy_index = random.randint(0, len(self.strategies)-1)
            mutated_value =  self.strategies[strategy_index].mutate(input)
        except ValueError as e:
            strategy_index = 0
            mutated_value =  self.strategies[strategy_index].mutate(input)
        self.heuristic_stats[strategy_index]   += [datetime.now()]
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