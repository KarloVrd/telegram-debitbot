from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter

class StatCalculator(ABC):
    """Abstract base class for all stat calculators"""
    
    @abstractmethod
    def calculate(self, logs: Optional[List[Dict]] = None, state: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """Calculate the statistic from logs and/or current state
        
        Args:
            logs: Command logs (optional, pass None if not needed)
            state: Current user balances (optional, pass None if not needed)
        """
        pass
    
    @abstractmethod
    def get_display_name(self) -> str:
        """Get the display name for this statistic"""
        pass
    
    @abstractmethod
    def format_result(self, result: Dict[str, Any]) -> str:
        """Format the result for display"""
        pass
    
    def requires_logs(self) -> bool:
        """Override this to return False if calculator doesn't need logs"""
        return True
    
    def requires_state(self) -> bool:
        """Override this to return False if calculator doesn't need state"""
        return True

class TransactionVolumeCalculator(StatCalculator):
    """Calculates total transaction volume for each user"""
    
    def calculate(self, logs: Optional[List[Dict]] = None, state: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        if logs is None:
            return {}
            
        stats = defaultdict(float)
        
        for log in logs:
            command_parts = log["command"].split(" ")
            if command_parts[0] == "t":
                # Parse transaction command
                from DebitHandler import DebitHandler
                command = DebitHandler.resolvingAlgebraFormations(command_parts)
                don = command[1].capitalize()
                amounts = command[3::2]
                
                total_amount = sum(float(amount) for amount in amounts)
                stats[don] += total_amount
        
        return dict(stats)
    
    def requires_logs(self) -> bool:
        return True
    
    def requires_state(self) -> bool:
        return False
    
    def get_display_name(self) -> str:
        return "Transaction Volume"
    
    def format_result(self, result: Dict[str, Any]) -> str:
        if not result:
            return "No transaction data available"
        
        sorted_users = sorted(result.items(), key=lambda x: x[1], reverse=True)
        lines = [f"{user}: {volume:.2f}" for user, volume in sorted_users]
        return "\n".join(lines)

class TransactionCountCalculator(StatCalculator):
    """Calculates number of transactions each user made"""
    
    def calculate(self, logs: Optional[List[Dict]] = None, state: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        if logs is None:
            return {}
            
        stats = defaultdict(int)
        
        for log in logs:
            command_parts = log["command"].split(" ")
            if command_parts[0] in ["t", "td", "tg", "tdex", "tgex"]:
                from DebitHandler import DebitHandler
                command = DebitHandler.resolvingAlgebraFormations(command_parts)
                don = command[1].capitalize()
                stats[don] += 1
        
        return dict(stats)
    
    def requires_logs(self) -> bool:
        return True
    
    def requires_state(self) -> bool:
        return False
    
    def get_display_name(self) -> str:
        return "Transaction Count"
    
    def format_result(self, result: Dict[str, Any]) -> str:
        if not result:
            return "No transaction data available"
        
        sorted_users = sorted(result.items(), key=lambda x: x[1], reverse=True)
        lines = [f"{user}: {count} transactions" for user, count in sorted_users]
        return "\n".join(lines)

class UserInteractionCalculator(StatCalculator):
    """Calculates who interacts with whom most frequently"""
    
    def calculate(self, logs: Optional[List[Dict]] = None, state: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        if logs is None:
            return {}
            
        interactions = defaultdict(lambda: defaultdict(int))
        
        for log in logs:
            command_parts = log["command"].split(" ")
            if command_parts[0] == "t":
                from DebitHandler import DebitHandler
                command = DebitHandler.resolvingAlgebraFormations(command_parts)
                don = command[1].capitalize()
                recs = command[2::2]
                
                for rec in recs:
                    rec = rec.capitalize()
                    interactions[don][rec] += 1
                    interactions[rec][don] += 1
        
        return {user: dict(user_interactions) for user, user_interactions in interactions.items()}
    
    def requires_logs(self) -> bool:
        return True
    
    def requires_state(self) -> bool:
        return False
    
    def get_display_name(self) -> str:
        return "User Interactions"
    
    def format_result(self, result: Dict[str, Any]) -> str:
        if not result:
            return "No interaction data available"
        
        lines = []
        for user, interactions in result.items():
            if interactions:
                sorted_interactions = sorted(interactions.items(), key=lambda x: x[1], reverse=True)
                top_interaction = sorted_interactions[0]
                lines.append(f"{user} ↔ {top_interaction[0]}: {top_interaction[1]} interactions")
        
        return "\n".join(lines)
    
class TotalAmountTransferredCalculator(StatCalculator):
    """Calculates total amount transferred by each user"""
    
    def calculate(self, logs: Optional[List[Dict]] = None, state: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        if logs is None:
            return {"total": 0}
            
        total = 0
        for log in logs:
            if "command" not in log:
                continue
            command_parts = log["command"].split(" ")
            if command_parts[0] == "t":
                from DebitHandler import DebitHandler
                command = DebitHandler.resolvingAlgebraFormations(command_parts)
                amounts = command[3::2]
                total += sum(abs(float(amount)) for amount in amounts)

            elif command_parts[0] in ["td", "tg", "tdex", "tgex"]:
                from DebitHandler import DebitHandler
                command = DebitHandler.resolvingAlgebraFormations(command_parts)
                total += abs(float(command[-1]))

        return {"total": total}

    def requires_logs(self) -> bool:
        return True
    
    def requires_state(self) -> bool:
        return False

    def get_display_name(self) -> str:
        return "Total Amount Transferred"
    
    def format_result(self, result: Dict[str, Any]) -> str:
        if not result:
            return "No transfer data available"
        return f"Total amount transferred: {result['total']:.2f}"

class CommandUsageCalculator(StatCalculator):
    """Calculates usage frequency of different commands"""
    
    def calculate(self, logs: Optional[List[Dict]] = None, state: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        if logs is None:
            return {}
            
        command_count = Counter()
        
        for log in logs:
            command_parts = log["command"].split(" ")
            command = command_parts[0]
            command_count[command] += 1
        
        return dict(command_count)
    
    def requires_logs(self) -> bool:
        return True
    
    def requires_state(self) -> bool:
        return False
    
    def get_display_name(self) -> str:
        return "Command Usage"
    
    def format_result(self, result: Dict[str, Any]) -> str:
        if not result:
            return "No command data available"
        
        sorted_commands = sorted(result.items(), key=lambda x: x[1], reverse=True)
        lines = [f"{cmd}: {count} times" for cmd, count in sorted_commands]
        return "\n".join(lines)

class StatsCalculatorManager:
    """Manages and coordinates different stat calculators"""
    
    def __init__(self):
        self.calculators = {
            "volume": TransactionVolumeCalculator(),
            "count": TransactionCountCalculator(),
            "interactions": UserInteractionCalculator(),
            "commands": CommandUsageCalculator(),
            "total": TotalAmountTransferredCalculator(),
        }
    
    def add_calculator(self, name: str, calculator: StatCalculator):
        """Add a new stat calculator"""
        self.calculators[name] = calculator
    
    def remove_calculator(self, name: str):
        """Remove a stat calculator"""
        if name in self.calculators:
            del self.calculators[name]

    def get_stat_instance(self, name: str) -> Optional[StatCalculator]:
        """Get an instance of a specific stat calculator"""
        return self.calculators.get(name)
        
    def get_available_stats(self) -> List[str]:
        """Get list of available stat types"""
        return list(self.calculators.keys())
    
    def calculate_stat(self, stat_type: str, logs: Optional[List[Dict]], state: Optional[Dict[str, float]]) -> Optional[str]:
        """Calculate a specific statistic with improved parameter handling"""

        if stat_type not in self.calculators:
            return None
        
        calculator = self.calculators[stat_type]
        
        # Validate that we have the required data
        if calculator.requires_logs() and (logs is None):
            return f"❌ {calculator.get_display_name()}: No log data available"
        
        if calculator.requires_state() and (state is None):
            return f"❌ {calculator.get_display_name()}: No state data available"
        
        # Only pass the data that the calculator actually needs
        logs_param = logs if calculator.requires_logs() else None
        state_param = state if calculator.requires_state() else None
        
        try:
            result = calculator.calculate(logs_param, state_param)
            return calculator.format_result(result)
        except Exception as e:
            return f"❌ {calculator.get_display_name()}: Error calculating ({str(e)})"
    
    def calculate_all_stats(self, logs: List[Dict], state: Dict[str, float]) -> str:
        """Calculate all available statistics with improved error handling"""
        results = []
        
        for name, calculator in self.calculators.items():
            try:                
                # Only pass the data that the calculator actually needs
                logs_param = logs if calculator.requires_logs() else None
                state_param = state if calculator.requires_state() else None
                
                result = calculator.calculate(logs_param, state_param)
                formatted = calculator.format_result(result)
                results.append(f"📊 {calculator.get_display_name()}:\n{formatted}")
            except Exception as e:
                results.append(f"❌ {calculator.get_display_name()}: Error calculating ({str(e)})")
        
        return "\n\n" + "="*30 + "\n\n".join(results)
    
    def get_stats_summary(self, logs: Optional[List[Dict]], state: Optional[Dict[str, float]]) -> str:
        """Get a summary of key statistics with improved handling"""
        summary_stats = ["volume", "count", "total"]
        results = []
        
        for stat_type in summary_stats:
            if stat_type in self.calculators:
                result = self.calculate_stat(stat_type, logs, state)
                if result and not result.startswith("❌"):
                    # Extract just the formatted result part
                    results.append(f"📈 {result}")
                # Skip failed calculations in summary
        
        return "\n\n" + "="*20 + "\n\n".join(results) if results else "No statistics available"
