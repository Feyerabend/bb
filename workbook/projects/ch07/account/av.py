from datetime import datetime

class AccountingMachine:
    def __init__(self):
        self.accounts = {}  # Holds account balances
        self.verifications = []  # Stores each transaction as a verification
    
    def create_account(self, account_name):
        """Creates an account with a zero balance."""
        if account_name not in self.accounts:
            self.accounts[account_name] = 0
            print(f"Account '{account_name}' created.")
        else:
            print(f"Account '{account_name}' already exists.")
    
    def get_balance(self, account_name):
        """Returns the current balance of an account."""
        return self.accounts.get(account_name, None)
    
    def _log_verification(self, debits, credits):
        """Logs a verified transaction as a unique verification entry."""
        verification = {
            'date': datetime.now(),
            'debits': debits,
            'credits': credits
        }
        self.verifications.append(verification)
        print("Verification logged:", verification)
    
    def debit(self, account_name, amount):
        """Debits an amount to a given account."""
        if account_name in self.accounts:
            self.accounts[account_name] += amount
        else:
            raise ValueError(f"Account '{account_name}' does not exist.")
    
    def credit(self, account_name, amount):
        """Credits an amount from a given account."""
        if account_name in self.accounts:
            self.accounts[account_name] -= amount
        else:
            raise ValueError(f"Account '{account_name}' does not exist.")
    
    def make_transaction(self, debits, credits):
        """Executes a transaction by debiting and crediting accounts."""
        total_debits = sum(amount for _, amount in debits)
        total_credits = sum(amount for _, amount in credits)
        
        # Check if the transaction is balanced
        if total_debits != total_credits:
            raise ValueError("Transaction is not balanced. Debits do not equal credits.")
        
        # Apply debits
        for account_name, amount in debits:
            self.debit(account_name, amount)
        
        # Apply credits
        for account_name, amount in credits:
            self.credit(account_name, amount)
        
        # Log the transaction
        self._log_verification(debits, credits)
        print("Transaction completed successfully.\n")

# Usage example:
machine = AccountingMachine()

# Create accounts
machine.create_account("Cash")
machine.create_account("Revenue")
machine.create_account("Expense")

# Check initial balances
print("\nInitial Balances:")
print("Cash:", machine.get_balance("Cash"))
print("Revenue:", machine.get_balance("Revenue"))
print("Expense:", machine.get_balance("Expense"))

# Make a balanced transaction: Debit Cash, Credit Revenue
print("\nTransaction 1: Debit Cash 100, Credit Revenue 100")
machine.make_transaction(debits=[("Cash", 100)], credits=[("Revenue", 100)])

# Make a balanced transaction: Debit Expense, Credit Cash
print("\nTransaction 2: Debit Expense 50, Credit Cash 50")
machine.make_transaction(debits=[("Expense", 50)], credits=[("Cash", 50)])

# Check balances after transactions
print("\nBalances after Transactions:")
print("Cash:", machine.get_balance("Cash"))
print("Revenue:", machine.get_balance("Revenue"))
print("Expense:", machine.get_balance("Expense"))

# Print all verifications
print("\nAll Verifications:")
for v in machine.verifications:
    print(v)
