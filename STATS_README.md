# Flexible Statistics System

The DebitBot now includes a powerful and extensible statistics system that allows you to easily add new types of statistics without modifying the core bot code. **The system is optimized to only pass the data each statistic actually needs.**

## Key Features

✅ **Flexible Data Requirements** - Stats can require logs, state, both, or neither  
✅ **Performance Optimized** - Only required data is loaded and passed  
✅ **Easy to Extend** - Add new stats with minimal code  
✅ **Type Safe** - Clear interfaces and error handling  

## Available Commands

### Basic Stats Commands
- `/stats` - Shows a summary of key statistics (transaction volume, count, total transferred)
- `/stat <type>` - Shows a specific statistic type
- `/statsall` - Shows all available statistics
- `/statlist` - Lists all available statistic types

### Built-in Statistics Types

#### Core Statistics
- **volume** - Total transaction volume per user (logs only)
- **count** - Number of transactions per user (logs only)  
- **interactions** - Who interacts with whom most frequently (logs only)
- **commands** - Usage frequency of different commands (logs only)
- **total** - Total amount transferred across all transactions (logs only)

#### Extended Statistics (if ExtendedStatsCalculators.py is available)
- **average** - Average transaction size per user
- **biggest** - Biggest single transaction and who made it
- **activity** - User activity levels based on command usage
- **debt** - Debt and credit analysis (biggest debtors/creditors)

## Data Requirements

The new system allows statistics to declare exactly what data they need:

### Logs Only (Historical Data)
```python
def requires_logs(self) -> bool:
    return True
    
def requires_state(self) -> bool:
    return False  # Don't need current balances
```
Examples: command usage, transaction history, user interactions

### State Only (Current Data)  
```python
def requires_logs(self) -> bool:
    return False  # Don't need history
    
def requires_state(self) -> bool:
    return True
```
Examples: current balance analysis, user count, debt/credit ratios

### Both Required
```python
def requires_logs(self) -> bool:
    return True
    
def requires_state(self) -> bool:
    return True
```
Examples: consistency analysis, comparing history vs current state

### Neither Required
```python  
def requires_logs(self) -> bool:
    return False
    
def requires_state(self) -> bool:
    return False
```
Examples: bot info, system statistics, configuration details

## Adding Custom Statistics

### Step 1: Create a Calculator Class

```python
from StatsCalculator import StatCalculator
from typing import Dict, List, Any, Optional

class MyCustomCalculator(StatCalculator):
    def calculate(self, logs: Optional[List[Dict]] = None, state: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        # Check what data you actually have
        if logs is None and self.requires_logs():
            return {"error": "No logs available"}
        if state is None and self.requires_state():
            return {"error": "No state available"}
            
        # Your calculation logic here
        return {"result": "your calculated data"}
    
    def requires_logs(self) -> bool:
        return True  # Set based on what you need
    
    def requires_state(self) -> bool:
        return False  # Set based on what you need
    
    def get_display_name(self) -> str:
        return "My Custom Statistic"
    
    def format_result(self, result: Dict[str, Any]) -> str:
        return f"Result: {result['result']}"
```

### Step 2: Register the Calculator

```python
# Only the data your calculator needs will be passed!
debit_handler.stats_manager.add_calculator("mycustom", MyCustomCalculator())
```

## Performance Benefits

The system now optimizes data usage:

```python
# Before: Always passed both logs and state
calculator.calculate(all_logs, full_state)  

# Now: Only passes what's needed
if calculator.requires_logs() and calculator.requires_state():
    calculator.calculate(logs, state)
elif calculator.requires_logs():
    calculator.calculate(logs, None)  # No state processing!
elif calculator.requires_state():
    calculator.calculate(None, state)  # No log processing!
else:
    calculator.calculate(None, None)  # No data loading at all!
```

This means:
- 🚀 **Faster execution** for state-only stats (no log processing)
- 💾 **Lower memory usage** when logs aren't needed
- 🔧 **Clearer code** - explicit about data dependencies
- 📊 **Better scalability** as your bot grows

## Examples

See these files for implementation examples:
- `StatsCalculator.py` - Core system and basic calculators
- `ExtendedStatsCalculators.py` - Advanced calculator examples  
- `DataRequirementExamples.py` - Examples of different data requirements
- `CustomStatsExample.py` - How to create custom statistics
