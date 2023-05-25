from modules.test import Input
from modules import constants
import random


class Random:
    
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
                    return  str(random.randint(constants.INT_MIN, constants.INT_MAX)) if input.len is None or not input.is_declared else "{" + ", ".join([str(random.randint(constants.INT_MIN, constants.INT_MAX)) for i in range(input.len)]) + "}"     
            case constants.Type.SHORT:
                    return  str(random.randint(constants.SHORT_MIN, constants.SHORT_MAX)) if input.len is None or not input.is_declared  else  "{" + ", ".join([str(random.randint(constants.SHORT_MIN, constants.SHORT_MAX)) for i in range(input.len)]) + "}" 
            case constants.Type.LONG:
                return str(random.randint(constants.LONG_MIN, constants.LONG_MAX)) if input.len is None or not input.is_declared else "{" + ", ".join([str(random.randint(constants.LONG_MIN, constants.LONG_MAX)) for i in range(input.len)]) + "}"
            case constants.Type.FLOAT:
                return str(random.uniform(constants.FLOAT_MIN, constants.FLOAT_MAX)) if input.len is None or not input.is_declared else "{" + ", ".join([str(random.uniform(constants.FLOAT_MIN, constants.FLOAT_MAX)) for i in range(input.len)]) + "}"
            case constants.Type.DOUBLE:
                return str(random.uniform(constants.DOUBLE_MIN, constants.DOUBLE_MAX)) if input.len is None or not input.is_declared else "{" +", ".join([str(random.uniform(constants.DOUBLE_MIN, constants.DOUBLE_MAX)) for i in range(input.len)]) + "}"
            case constants.Type.CHAR:
                return "\'" + random.choice(constants.CHARACTERS) + "\'" if input.len is None or not input.is_declared  else "\"" + "".join([random.choice (constants.CHARACTERS) for i in range(input.len-1)]) + "\""
            case _:
                 raise ValueError(f"Type {input.type} not supported")