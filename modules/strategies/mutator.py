import random

from modules.strategies.random import Random
from modules.strategies.boundaries import Boundaries
from modules.strategies.modification import Modification
from modules.test import Input

class Mutator:
    
    def __init__(self) -> None:
        self.strategies = [Random(), Boundaries(), Modification()]
        
        
    def mutate(self, input: Input) -> str:
        
        try: 
            return self.strategies[random.randint(0, len(self.strategies)-1)].mutate(input)
        except ValueError as e:
            pass
        return self.strategies[0].mutate(input)
        