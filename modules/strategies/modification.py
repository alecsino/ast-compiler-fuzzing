from modules.test import Input
from modules import constants
import random


class Modification:
    
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
                return self._generate_numb(input.value, constants.Short, int, random.randint) if input.len is None else "{" + ", ".join([self._generate_numb(input.value, constants.Short, int, random.randint) for i in input.value.split(", ")]) + "}"
            case constants.Type.SHORT:
                return self._generate_numb(input.value, constants.Short, int, random.randint) if input.len is None else "{" + ", ".join([self._generate_numb(input.value, constants.Short, int, random.randint) for i in input.value.split(", ")]) + "}"
            case constants.Type.LONG:
                return self._generate_numb(input.value, constants.Int, int, random.randint) if input.len is None else "{" + ", ".join([self._generate_numb(input.value, constants.Int, int, random.randint) for i in input.value.split(", ")]) + "}"
            case constants.Type.FLOAT:
                return self._generate_numb(input.value, constants.Float, float, random.uniform) if input.len is None else "{" + ", ".join([self._generate_numb(i, constants.Float, float, random.uniform) for i in input.value.split(", ")]) + "}"
            case constants.Type.DOUBLE:
                return self._generate_numb(input.value, constants.Double, float, random.uniform) if input.len is None else "{" + ", ".join([self._generate_numb(i, constants.Double, float, random.uniform) for i in input.value.split(", ")]) + "}"
            case constants.Type.CHAR:
                return "\'" + random.choice(constants.CHARACTERS) + "\'" if input.len is None else "\"" + self._generate_string(input.value, input.len) + "\""
            case _:
                 raise ValueError(f"Type {input.type} not supported")
             

    def _generate_numb(self, value, type_class, converter, random_generator) -> str:
        """
        Generate a new number adding to the original one.
        
        Args: 
            value (str): the original value
            type_class (class): the class of the type of the value
            converter (function): the function to convert the value to the type
            random_generator (function): the function to generate a random number
        
        Returns:
            str: the new value
        """        
        rand_val = random_generator(type.MIN, type.MAX)
        
        while type.MIN > converter(input.value) + rand_val or converter(input.value) + rand_val > type.MAX:
                rand_val = random.uniform(type.MIN , type.MAX)
                
        return str(converter(input.value)+ rand_val)

    def _generate_string(self, value, max_len) -> str:
        """
        Generate a new string by modifying the original one.
        
        Args: 
            value (str): the original value
            len (int): the maximum length of the new string
        
        Returns:
            str: the new value
        """        
        character = random.choice(constants.CHARACTERS) 
        if len(value + character) > max_len:
            value[random.randint(0, max_len-1)] = character
        else:
            value += character
        return value
             
        