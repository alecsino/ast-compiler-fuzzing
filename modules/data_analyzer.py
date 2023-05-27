import csv
import datetime
from typing import Any
from modules.test import Stats


class DataAnalyzer:
    """The class contains all analysis of the perfomance of the project."""
    
    def __init__(self, args) -> None:
        self.directory = args.analysis
        
    def register_improvement(self, test_name: str, stats: Stats, old_stats: Stats, old_inputs: list[str], mutated_inputs: list[str]) -> None:
        """Register an improvement."""
        
        with open(self.directory + "/improvement_fuzzer.csv", mode='a') as f:
            writer = csv.writer(f)
            writer.writerow([test_name, stats.max_rateo, old_stats.max_rateo if old_stats else "not_available", old_inputs, mutated_inputs])
        
    def register_interesting_test(self, test_name: str, stats: Stats, date: datetime, n_iteration: int) -> None:
        """Register an interesting test."""
    
        with open(self.directory  + "/interesting_tests.csv", mode='a') as f:
            writer = csv.writer(f)
            writer.writerow([test_name, stats.max_rateo, date, n_iteration])
    
    def register_mutation_type(self, mutation_type: str, mutated_value: Any):
        """Register a mutation type."""
        
        with open(self.directory  + "/mutation_type.csv", mode='a') as f:
            writer = csv.writer(f)
            writer.writerow([mutation_type, mutated_value])  