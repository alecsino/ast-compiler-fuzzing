from modules.test import Input
from modules import constants
import random


class Boundaries:
    
    def mutate(self, input: Input) -> str:
        """
        Generate a random value for the input.
        
        Args:
            input (Input): the inputs to generate a random value for
            
        Raises:
            ValueError: if the type of the input is not supported
        
        Returns:
            str: the random value as a string
        """
        
        match input.type:
            case constants.Type.INT:
                    return  str(random.choice([constants.INT_MIN, constants.INT_MAX, -1, 0, 1])) if input.len is None or not input.is_declared else "{" + ", ".join([str(random.choice([constants.INT_MIN, constants.INT_MAX, -1, 0, 1])) for i in range(input.len)]) + "}"     
            case constants.Type.SHORT:
                    return  str(random.choice([constants.SHORT_MIN, constants.SHORT_MAX, -1, 0, 1])) if input.len is None or not input.is_declared else  "{" + ", ".join([str(random.choice([constants.SHORT_MIN, constants.SHORT_MAX, -1, 0, 1])) for i in range(input.len)]) + "}" 
            case constants.Type.LONG:
                return str(random.choice([constants.LONG_MAX, constants.LONG_MIN, -1, 0, 1])) if input.len is None or not input.is_declared else "{" + ", ".join([str(random.choice([constants.LONG_MAX, constants.LONG_MIN, -1, 0, 1])) for i in range(input.len)]) + "}"
            case constants.Type.FLOAT:
                return str(random.choice([constants.FLOAT_MAX, constants.FLOAT_MIN, -1.15, 0, 1.15])) if input.len is None or not input.is_declared else "{" +  ", ".join([str(random.choice([constants.FLOAT_MAX, constants.FLOAT_MIN, -1.15, 0, 1.15])) for i in range(input.len)]) + "}"
            case constants.Type.DOUBLE:
                return str(random.choice([constants.DOUBLE_MAX, constants.DOUBLE_MIN, -1.1514, 0, 1.1515]))  if input.len is None or not input.is_declared  else "{" +  ", ".join([str(random.choice([constants.DOUBLE_MAX, constants.DOUBLE_MIN, -1.15, 0, 1.15])) for i in range(input.len)]) + "}"
            case constants.Type.CHAR:
                return "\'" + random.choice(["\0"]) + "\'" if input.len is None or not input.is_declared else "\"" + (random.choice(["\0"]) * input.len) + "\""
            case _:
                 raise ValueError(f"Type {input.type} not supported")