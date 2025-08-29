"""
Example of how to add custom statistics to the DebitBot

This demonstrates the flexibility of the new stats system - you can easily
add new statistic types without modifying the core DebitHandler code.
"""

from StatsCalculator import StatCalculator
from typing import Dict, List, Any
from collections import defaultdict

class MostGenerousCalculator(StatCalculator):
    """Finds who gives money to others most frequently"""
    
    def calculate(self, logs: List[Dict], state: Dict[str, float]) -> Dict[str, Any]:
        generosity_count = defaultdict(int)
        generosity_amount = defaultdict(float)
        
        for log in logs:
            command_parts = log["command"].split(" ")
            if command_parts[0] == "t":  # Only regular transactions
                from DebitHandler import DebitHandler
                command = DebitHandler.resolvingAlgebraFormations(command_parts)
                don = command[1].capitalize()
                amounts = command[3::2]
                
                # Count how many people they gave money to
                generosity_count[don] += len(amounts)
                
                # Total amount given
                total_given = sum(float(amount) for amount in amounts)
                generosity_amount[don] += total_given
        
        # Combine count and amount for a generosity score
        generosity_score = {}
        for user in generosity_count:
            # Score = number of transactions * average amount
            avg_amount = generosity_amount[user] / generosity_count[user] if generosity_count[user] > 0 else 0
            generosity_score[user] = {
                "score": generosity_count[user] * avg_amount,
                "transactions": generosity_count[user],
                "total_amount": generosity_amount[user],
                "avg_amount": avg_amount
            }
        
        return generosity_score
    
    def get_display_name(self) -> str:
        return "Most Generous Users"
    
    def format_result(self, result: Dict[str, Any]) -> str:
        if not result:
            return "No generosity data available"
        
        sorted_users = sorted(result.items(), key=lambda x: x[1]["score"], reverse=True)
        lines = []
        for user, data in sorted_users[:5]:  # Top 5 most generous
            lines.append(
                f"🏆 {user}: {data['transactions']} gifts, "
                f"{data['total_amount']:.2f} total, "
                f"{data['avg_amount']:.2f} avg"
            )
        
        return "\n".join(lines)

class CommandTimeAnalysisCalculator(StatCalculator):
    """Analyzes when commands are most frequently used (if timestamps available)"""
    
    def calculate(self, logs: List[Dict], state: Dict[str, float]) -> Dict[str, Any]:
        hour_usage = defaultdict(int)
        day_usage = defaultdict(int)
        
        for log in logs:
            timestamp = log.get("timestamp")
            if timestamp:
                # This would need proper timestamp parsing based on your log format
                # For now, we'll count total commands per user as a fallback
                command_parts = log["command"].split(" ")
                command = command_parts[0]
                hour_usage[command] += 1
        
        # Since we don't have real timestamps, let's analyze command diversity
        command_diversity = len(hour_usage)
        most_used_command = max(hour_usage.items(), key=lambda x: x[1]) if hour_usage else ("none", 0)
        
        return {
            "command_diversity": command_diversity,
            "most_used_command": most_used_command,
            "command_usage": dict(hour_usage)
        }
    
    
    def get_display_name(self) -> str:
        return "Command Usage Analysis"
    
    def format_result(self, result: Dict[str, Any]) -> str:
        lines = [
            f"📊 Command Diversity: {result['command_diversity']} different commands used",
            f"🏆 Most Used: {result['most_used_command'][0]} ({result['most_used_command'][1]} times)"
        ]
        
        # Show top 3 commands
        sorted_commands = sorted(result['command_usage'].items(), key=lambda x: x[1], reverse=True)
        lines.append("Top Commands:")
        for cmd, count in sorted_commands[:3]:
            lines.append(f"  • {cmd}: {count} times")
        
        return "\n".join(lines)

# Example usage - this is how you would add these stats to your bot:
def add_custom_stats_example(debit_handler):
    """
    Example of how to add custom statistics to an existing DebitHandler instance
    """
    # Add the new calculators
    debit_handler.stats_manager.add_calculator("generous", MostGenerousCalculator())
    debit_handler.stats_manager.add_calculator("timing", CommandTimeAnalysisCalculator())
    
    print("Added custom statistics!")
    print("Available stats:", debit_handler.stats_manager.get_available_stats())

if __name__ == "__main__":
    print("""
    Custom Stats Example
    ===================
    
    This file demonstrates how to create custom statistics for the DebitBot.
    
    To add a new statistic:
    1. Create a class that inherits from StatCalculator
    2. Implement calculate(), get_display_name(), and format_result() methods
    3. Add it to the stats manager using add_calculator()
    
    Your new stat will automatically be available via:
    - /stat <your_stat_name>
    - /statsall (includes your stat)
    - /statlist (shows your stat in the list)
    
    No need to modify the core DebitHandler code!
    """)
