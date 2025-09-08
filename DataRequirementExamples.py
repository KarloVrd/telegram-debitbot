"""
Examples of statistics that require different combinations of data
"""

from StatsCalculator import StatCalculator
from typing import Dict, List, Any, Optional
from collections import defaultdict

class StateOnlyCalculator(StatCalculator):
    """Example of a statistic that only needs current state (no logs)"""
    
    def calculate(self, logs: Optional[List[Dict]] = None, state: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        if state is None:
            return {"user_count": 0, "total_balance": 0, "average_balance": 0}
        
        user_count = len(state)
        total_balance = sum(state.values())
        average_balance = total_balance / user_count if user_count > 0 else 0
        
        return {
            "user_count": user_count,
            "total_balance": round(total_balance, 2),
            "average_balance": round(average_balance, 2)
        }
    
    def requires_logs(self) -> bool:
        return False  # This stat doesn't need logs!
    
    def requires_state(self) -> bool:
        return True
    
    def get_display_name(self) -> str:
        return "Current Balance Summary"
    
    def format_result(self, result: Dict[str, Any]) -> str:
        return (f"👥 Total Users: {result['user_count']}\n"
                f"💰 Total Balance: {result['total_balance']}\n"
                f"📊 Average Balance: {result['average_balance']}")

class LogsOnlyCalculator(StatCalculator):
    """Example of a statistic that only needs logs (no current state)"""
    
    def calculate(self, logs: Optional[List[Dict]] = None, state: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        if logs is None:
            return {"total_commands": 0, "unique_days": 0}
        
        total_commands = len(logs)
        
        # Count unique days (if timestamp available)
        unique_dates = set()
        for log in logs:
            timestamp = log.get("timestamp", "unknown")
            if timestamp != "unknown":
                # Extract date part (this would need proper parsing based on your format)
                date_part = str(timestamp).split()[0] if ' ' in str(timestamp) else str(timestamp)
                unique_dates.add(date_part)
        
        return {
            "total_commands": total_commands,
            "unique_days": len(unique_dates) if unique_dates else 1
        }
    
    def requires_logs(self) -> bool:
        return True
    
    def requires_state(self) -> bool:
        return False  # This stat doesn't need current state!
    
    def get_display_name(self) -> str:
        return "Activity Summary"
    
    def format_result(self, result: Dict[str, Any]) -> str:
        avg_per_day = result['total_commands'] / result['unique_days'] if result['unique_days'] > 0 else 0
        return (f"📝 Total Commands: {result['total_commands']}\n"
                f"📅 Active Days: {result['unique_days']}\n"
                f"⚡ Avg Commands/Day: {avg_per_day:.1f}")

class NeitherNeededCalculator(StatCalculator):
    """Example of a statistic that needs neither logs nor state (meta info)"""
    
    def calculate(self, logs: Optional[List[Dict]] = None, state: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        # This could return system info, configuration, etc.
        return {
            "bot_version": "2.4",
            "available_commands": ["t", "td", "tg", "na", "nr", "stats"],
            "max_users": 40,
            "max_groups": 15
        }
    
    def requires_logs(self) -> bool:
        return False  # No logs needed
    
    def requires_state(self) -> bool:
        return False  # No state needed
    
    def get_display_name(self) -> str:
        return "Bot Information"
    
    def format_result(self, result: Dict[str, Any]) -> str:
        return (f"🤖 Bot Version: {result['bot_version']}\n"
                f"⚙️ Available Commands: {len(result['available_commands'])}\n"
                f"👥 Max Users: {result['max_users']}\n"
                f"👨‍👩‍👧‍👦 Max Groups: {result['max_groups']}")

class BothNeededCalculator(StatCalculator):
    """Example of a statistic that needs both logs and state"""
    
    def calculate(self, logs: Optional[List[Dict]] = None, state: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        if logs is None or state is None:
            return {"accuracy": 0, "active_users": 0}
        
        # Calculate "accuracy" - users who made transactions vs users with non-zero balance
        users_with_transactions = set()
        for log in logs:
            command_parts = log["command"].split(" ")
            if command_parts[0] in ["t", "td", "tg", "tdex", "tgex"]:
                from DebitHandler import DebitHandler
                command = DebitHandler.resolvingAlgebraFormations(command_parts)
                if len(command) > 1:
                    users_with_transactions.add(command[1].capitalize())
        
        users_with_balance = {user for user, balance in state.items() if balance != 0}
        
        # Users who have transactions should correlate with non-zero balances
        overlap = len(users_with_transactions.intersection(users_with_balance))
        total_active = len(users_with_transactions.union(users_with_balance))
        accuracy = (overlap / total_active * 100) if total_active > 0 else 100
        
        return {
            "accuracy": round(accuracy, 1),
            "active_users": total_active,
            "transaction_users": len(users_with_transactions),
            "balance_users": len(users_with_balance)
        }
    
    def requires_logs(self) -> bool:
        return True  # Needs logs for transaction history
    
    def requires_state(self) -> bool:
        return True  # Needs state for current balances
    
    def get_display_name(self) -> str:
        return "Data Consistency Analysis"
    
    def format_result(self, result: Dict[str, Any]) -> str:
        return (f"✅ Data Accuracy: {result['accuracy']}%\n"
                f"🎯 Active Users: {result['active_users']}\n"
                f"💸 Users w/ Transactions: {result['transaction_users']}\n"
                f"💰 Users w/ Balance: {result['balance_users']}")

# Function to add these examples to your stats manager
def add_example_calculators(stats_manager):
    """Add example calculators showing different data requirements"""
    stats_manager.add_calculator("balance_summary", StateOnlyCalculator())
    stats_manager.add_calculator("activity", LogsOnlyCalculator())
    stats_manager.add_calculator("bot_info", NeitherNeededCalculator())
    stats_manager.add_calculator("consistency", BothNeededCalculator())

if __name__ == "__main__":
    print("""
    Data Requirements Examples
    =========================
    
    StateOnlyCalculator:
    - requires_logs(): False
    - requires_state(): True
    - Only gets current balances, no log history
    
    LogsOnlyCalculator:
    - requires_logs(): True  
    - requires_state(): False
    - Only gets command history, no current balances
    
    NeitherNeededCalculator:
    - requires_logs(): False
    - requires_state(): False
    - Gets neither! Perfect for meta-information
    
    BothNeededCalculator:
    - requires_logs(): True
    - requires_state(): True
    - Gets both logs and state for correlation analysis
    
    This flexible design means:
    - No wasted data processing
    - Clear dependencies
    - Easy to optimize performance
    - Simple to understand what each stat needs
    """)
