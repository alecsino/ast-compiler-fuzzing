import json
from modules.test import Stats
import dataclasses


class Serializer(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Stats):
            return dataclasses.asdict(obj)
        return super().default(obj)
    
    
def load_checkpoint(checkpoint_path: str):
    """Load from the checkpoint file the stats found so far.

    Args:
        checkpoint_path (str): the path of the checkpoint file
    """
    
    print("Loading checkpoint")
    
    with open(checkpoint_path, "r") as file:
        dict_stat_list = json.load(file)
        
    print(f"Loaded {len(dict_stat_list)} interesting stat")
    return [ Stats(**dict_stat) for dict_stat in dict_stat_list]


def write_checkpoint(checkpoint_path: str, stats_list: list[Stats]):
    """Write to the checkpoint file the stats found so far.

    Args:
        checkpoint_path (str): the path of the checkpoint file
        stats_list (list[Stats]): the list of stats
    """
    
    print("Writing checkpoint")
    
    with open(checkpoint_path, "w") as file:
        json.dump(stats_list, file,  cls=Serializer)