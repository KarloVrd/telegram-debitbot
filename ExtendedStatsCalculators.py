from StatsCalculator import StatCalculator
from typing import Dict, List, Any
from collections import defaultdict
import datetime

class AverageTransactionCalculator(StatCalculator):
    """Calculates average transaction size for each user"""
    
    def calculate(self, logs: List[Dict], state: Dict[str, float]) -> Dict[str, Any]:
        user_totals = defaultdict(float)
        user_counts = defaultdict(int)
        
        for log in logs:
            command_parts = log["command"].split(" ")
            if command_parts[0] == "t":
                from DebitHandler import DebitHandler
                command = DebitHandler.resolvingAlgebraFormations(command_parts)
                don = command[1].capitalize()
                amounts = command[3::2]
                
                for amount in amounts:
                    user_totals[don] += float(amount)
                    user_counts[don] += 1
        
        averages = {}
        for user in user_totals:
            if user_counts[user] > 0:
                averages[user] = user_totals[user] / user_counts[user]
        
        return averages
    
    def get_display_name(self) -> str:
        return "Average Transaction Size"
    
    def format_result(self, result: Dict[str, Any]) -> str:
        if not result:
            return "No transaction data available"
        
        sorted_users = sorted(result.items(), key=lambda x: x[1], reverse=True)
        lines = [f"{user}: {avg:.2f} avg" for user, avg in sorted_users]
        return "\n".join(lines)

class BiggestSpenderCalculator(StatCalculator):
    """Finds who made the largest single transaction"""
    
    def calculate(self, logs: List[Dict], state: Dict[str, float]) -> Dict[str, Any]:
        biggest_transaction = {"user": None, "amount": 0, "timestamp": None}
        
        for log in logs:
            command_parts = log["command"].split(" ")
            if command_parts[0] == "t":
                from DebitHandler import DebitHandler
                command = DebitHandler.resolvingAlgebraFormations(command_parts)
                don = command[1].capitalize()
                amounts = command[3::2]
                
                total_amount = sum(float(amount) for amount in amounts)
                if total_amount > biggest_transaction["amount"]:
                    biggest_transaction = {
                        "user": don,
                        "amount": total_amount,
                        "timestamp": log.get("timestamp", "Unknown")
                    }
        
        return biggest_transaction
    
    def get_display_name(self) -> str:
        return "Biggest Spender"
    
    def format_result(self, result: Dict[str, Any]) -> str:
        if not result["user"]:
            return "No transaction data available"
        
        return f"{result['user']}: {result['amount']:.2f} (on {result['timestamp']})"

class ActivityFrequencyCalculator(StatCalculator):
    """Calculates how active each user is (commands per day/week)"""
    
    def calculate(self, logs: List[Dict], state: Dict[str, float]) -> Dict[str, Any]:
        user_activity = defaultdict(int)
        
        # Count all command usage per user
        for log in logs:
            command_parts = log["command"].split(" ")
            if len(command_parts) > 1:
                user = command_parts[1].capitalize()
                user_activity[user] += 1
        
        # Convert to activity level description
        activity_levels = {}
        for user, count in user_activity.items():
            if count >= 50:
                level = "Very Active"
            elif count >= 20:
                level = "Active"
            elif count >= 10:
                level = "Moderate"
            elif count >= 5:
                level = "Low"
            else:
                level = "Minimal"
            
            activity_levels[user] = {"count": count, "level": level}
        
        return activity_levels
    
    def get_display_name(self) -> str:
        return "User Activity Levels"
    
    def format_result(self, result: Dict[str, Any]) -> str:
        if not result:
            return "No activity data available"
        
        sorted_users = sorted(result.items(), key=lambda x: x[1]["count"], reverse=True)
        lines = [f"{user}: {data['level']} ({data['count']} commands)" 
                for user, data in sorted_users]
        return "\n".join(lines)

class DebtorCreditorCalculator(StatCalculator):
    """Identifies the biggest debtors and creditors"""
    
    def calculate(self, logs: List[Dict], state: Dict[str, float]) -> Dict[str, Any]:
        # Current state already contains the net balance
        debtors = {user: balance for user, balance in state.items() if balance < 0}
        creditors = {user: balance for user, balance in state.items() if balance > 0}
        
        biggest_debtor = min(debtors.items(), key=lambda x: x[1]) if debtors else (None, 0)
        biggest_creditor = max(creditors.items(), key=lambda x: x[1]) if creditors else (None, 0)
        
        return {
            "biggest_debtor": biggest_debtor,
            "biggest_creditor": biggest_creditor,
            "total_debt": sum(debtors.values()),
            "total_credit": sum(creditors.values()),
            "debt_count": len(debtors),
            "credit_count": len(creditors)
        }
    
    def get_display_name(self) -> str:
        return "Debt & Credit Analysis"
    
    def format_result(self, result: Dict[str, Any]) -> str:
        lines = []
        
        if result["biggest_debtor"][0]:
            lines.append(f"💸 Biggest Debtor: {result['biggest_debtor'][0]} ({result['biggest_debtor'][1]:.2f})")
        
        if result["biggest_creditor"][0]:
            lines.append(f"💰 Biggest Creditor: {result['biggest_creditor'][0]} ({result['biggest_creditor'][1]:.2f})")
        
        lines.extend([
            f"📊 Total Debt: {result['total_debt']:.2f} ({result['debt_count']} users)",
            f"📈 Total Credit: {result['total_credit']:.2f} ({result['credit_count']} users)"
        ])
        
        return "\n".join(lines)

# Example of how to add these new calculators to the system
def add_extended_calculators(stats_manager):
    """Add extended calculators to the stats manager"""
    stats_manager.add_calculator("average", AverageTransactionCalculator())
    stats_manager.add_calculator("biggest", BiggestSpenderCalculator())
    stats_manager.add_calculator("activity", ActivityFrequencyCalculator())
    stats_manager.add_calculator("debt", DebtorCreditorCalculator())
