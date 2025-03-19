# Natural Language Code Generation

RebelDESK includes a powerful feature that allows you to generate code from natural language descriptions using AI. This feature leverages local AI models to understand your requirements and generate appropriate code in various programming languages.

## Overview

The Natural Language Code Generation feature allows you to:

- Generate code from natural language descriptions
- Choose from multiple programming languages
- Get explanations of how the generated code works
- Provide context code to guide the generation
- Improve existing code based on natural language instructions
- Insert generated code directly into the editor

## Using Natural Language Code Generation

To access the Natural Language Code Generation feature:

1. Open RebelDESK
2. Go to **Tools > AI > Generate Code from Description**
3. In the dialog that appears, enter a description of the code you want to generate
4. Select the target programming language from the dropdown
5. Optionally, provide context code to help guide the generation
6. Click the **Generate Code** button
7. Review the generated code and explanation
8. Click **Insert Code** to insert the code into your editor, or **Close** to cancel

## Example Use Cases

Here are some examples of how you can use Natural Language Code Generation:

### Basic Function Generation

Description:
```
Create a function that calculates the factorial of a number
```

Generated Python Code:
```python
def factorial(n):
    """
    Calculate the factorial of a number.
    
    Args:
        n: A non-negative integer
        
    Returns:
        The factorial of n
    """
    if n <= 1:
        return 1
    else:
        return n * factorial(n-1)
```

### Class Generation

Description:
```
Create a class that represents a bank account with deposit and withdraw methods
```

Generated Python Code:
```python
class BankAccount:
    """
    A class representing a bank account with deposit and withdraw methods.
    """
    
    def __init__(self, account_number, balance=0):
        """
        Initialize a new bank account.
        
        Args:
            account_number: The account number
            balance: The initial balance (default: 0)
        """
        self.account_number = account_number
        self.balance = balance
        self.transactions = []
    
    def deposit(self, amount):
        """
        Deposit money into the account.
        
        Args:
            amount: The amount to deposit
            
        Returns:
            The new balance
        """
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        
        self.balance += amount
        self.transactions.append(("deposit", amount))
        return self.balance
    
    def withdraw(self, amount):
        """
        Withdraw money from the account.
        
        Args:
            amount: The amount to withdraw
            
        Returns:
            The new balance
            
        Raises:
            ValueError: If the amount is negative or exceeds the balance
        """
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        
        self.balance -= amount
        self.transactions.append(("withdraw", amount))
        return self.balance
    
    def get_balance(self):
        """
        Get the current balance.
        
        Returns:
            The current balance
        """
        return self.balance
    
    def get_transaction_history(self):
        """
        Get the transaction history.
        
        Returns:
            A list of transactions
        """
        return self.transactions
```

### Algorithm Implementation

Description:
```
Implement a binary search algorithm
```

Generated Python Code:
```python
def binary_search(arr, target):
    """
    Perform binary search on a sorted array.
    
    Args:
        arr: A sorted array
        target: The value to search for
        
    Returns:
        The index of the target if found, otherwise -1
    """
    left = 0
    right = len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1
```

## Using Context Code

You can provide context code to help guide the generation. This is useful when you want to generate code that integrates with existing code or follows a specific style.

For example, if you have the following context code:

```python
class ShoppingCart:
    def __init__(self):
        self.items = []
        
    def add_item(self, item, price, quantity=1):
        self.items.append({
            'item': item,
            'price': price,
            'quantity': quantity
        })
```

And you provide the description:

```
Add a method to calculate the total price of all items in the cart
```

The generated code will integrate with the existing class:

```python
def calculate_total(self):
    """
    Calculate the total price of all items in the cart.
    
    Returns:
        The total price
    """
    total = 0
    for item in self.items:
        total += item['price'] * item['quantity']
    return total
```

## Supported Languages

The Natural Language Code Generation feature supports the following programming languages:

- Python
- JavaScript
- TypeScript
- Java
- C++
- C#
- Rust
- Go
- Ruby
- PHP
- Swift
- Kotlin
- Lua

## Configuration

The Natural Language Code Generation feature can be configured in the RebelDESK settings:

- **AI > Base URL**: The URL of the local AI server (default: http://127.0.0.1:1234)
- **AI > Model Name**: The name of the AI model to use (default: deepseek-r1-distill-llama-8b)
- **AI > Default Language**: The default programming language to use (default: python)

## Requirements

To use the Natural Language Code Generation feature, you need:

- A local AI server running at the configured URL
- The specified AI model loaded in the server

## Limitations

- The quality of the generated code depends on the capabilities of the AI model
- The feature requires a local AI server to be running
- The feature may not work well for very complex code generation tasks
- The generated code may not always be optimal or follow best practices
- The feature may not work well for languages or frameworks that the AI model has limited knowledge of
