# Natural Language Code Generation API Reference

This document provides a reference for the RebelDESK Natural Language Code Generation API, which includes the `NaturalLanguageCodeGenerator` class.

## NaturalLanguageCodeGenerator

The `NaturalLanguageCodeGenerator` class provides functionality for generating code from natural language descriptions using local AI models.

### Class Definition

```python
class NaturalLanguageCodeGenerator:
    """
    Natural language code generation provider using local AI models.
    
    This class provides code generation from natural language descriptions using a local AI model.
    It handles parsing natural language descriptions and generating appropriate code in the
    target programming language.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the natural language code generator.
        
        Args:
            config: Configuration dictionary for the generator.
        """
```

### Properties

- `config`: The configuration dictionary for the generator.
- `client`: The local AI client used to communicate with the AI server.
- `model_name`: The name of the AI model to use.
- `max_tokens`: The maximum number of tokens to generate.
- `temperature`: The temperature to use for sampling.
- `top_p`: The top-p value to use for sampling.
- `context_window`: The size of the context window.
- `language_prompts`: A dictionary mapping language names to prompt prefixes.
- `default_language`: The default programming language to use.

### Methods

#### `is_available() -> bool`

Check if the natural language code generator is available.

**Returns**:
- `bool`: True if the generator is available, False otherwise.

#### `generate_code(description: str, language: Optional[str] = None, context: Optional[str] = None) -> Dict[str, Any]`

Generate code from a natural language description.

**Args**:
- `description`: The natural language description of the code to generate.
- `language`: The programming language to generate code in. If None, the default language will be used.
- `context`: Optional context code to help guide the generation.

**Returns**:
- `Dict[str, Any]`: A dictionary containing the generated code and metadata.

#### `generate_code_with_explanation(description: str, language: Optional[str] = None, context: Optional[str] = None) -> Dict[str, Any]`

Generate code from a natural language description with an explanation.

**Args**:
- `description`: The natural language description of the code to generate.
- `language`: The programming language to generate code in. If None, the default language will be used.
- `context`: Optional context code to help guide the generation.

**Returns**:
- `Dict[str, Any]`: A dictionary containing the generated code, explanation, and metadata.

#### `improve_code(code: str, instructions: str, language: Optional[str] = None) -> Dict[str, Any]`

Improve existing code based on instructions.

**Args**:
- `code`: The existing code to improve.
- `instructions`: Instructions for how to improve the code.
- `language`: The programming language of the code. If None, it will be inferred.

**Returns**:
- `Dict[str, Any]`: A dictionary containing the improved code and metadata.

#### `_clean_generated_code(generated_code: str, language: str) -> str`

Clean up generated code by removing markdown formatting and unnecessary text.

**Args**:
- `generated_code`: The generated code to clean up.
- `language`: The programming language of the code.

**Returns**:
- `str`: The cleaned up code.

#### `_parse_code_and_explanation(response: str, language: str) -> Tuple[str, str]`

Parse the response to extract code and explanation.

**Args**:
- `response`: The response from the AI model.
- `language`: The programming language of the code.

**Returns**:
- `Tuple[str, str]`: The code and explanation.

#### `_infer_language(code: str) -> str`

Infer the programming language from the code.

**Args**:
- `code`: The code to infer the language from.

**Returns**:
- `str`: The inferred programming language.

## Usage Examples

### Generating Code

```python
from src.ai import NaturalLanguageCodeGenerator

# Create a natural language code generator
generator = NaturalLanguageCodeGenerator()

# Generate code from a natural language description
result = generator.generate_code(
    description="Create a function that calculates the factorial of a number",
    language="python"
)

if result["success"]:
    print(result["code"])
else:
    print(f"Error: {result['error']}")
```

### Generating Code with Explanation

```python
from src.ai import NaturalLanguageCodeGenerator

# Create a natural language code generator
generator = NaturalLanguageCodeGenerator()

# Generate code with an explanation from a natural language description
result = generator.generate_code_with_explanation(
    description="Create a function that calculates the factorial of a number",
    language="python"
)

if result["success"]:
    print("Code:")
    print(result["code"])
    print("\nExplanation:")
    print(result["explanation"])
else:
    print(f"Error: {result['error']}")
```

### Improving Code

```python
from src.ai import NaturalLanguageCodeGenerator

# Create a natural language code generator
generator = NaturalLanguageCodeGenerator()

# Improve existing code based on instructions
code = """
def factorial(n):
    if n <= 1:
        return 1
    else:
        return n * factorial(n-1)
"""

result = generator.improve_code(
    code=code,
    instructions="Add error handling for negative numbers and add a docstring",
    language="python"
)

if result["success"]:
    print(result["code"])
else:
    print(f"Error: {result['error']}")
```

### Using Context

```python
from src.ai import NaturalLanguageCodeGenerator

# Create a natural language code generator
generator = NaturalLanguageCodeGenerator()

# Generate code with context
context = """
class ShoppingCart:
    def __init__(self):
        self.items = []
        
    def add_item(self, item, price, quantity=1):
        self.items.append({
            'item': item,
            'price': price,
            'quantity': quantity
        })
"""

result = generator.generate_code(
    description="Add a method to calculate the total price of all items in the cart",
    language="python",
    context=context
)

if result["success"]:
    print(result["code"])
else:
    print(f"Error: {result['error']}")
```

## Configuration

The `NaturalLanguageCodeGenerator` class can be configured using a configuration dictionary. The following configuration options are available:

- `base_url`: The URL of the local AI server (default: http://127.0.0.1:1234)
- `model_name`: The name of the AI model to use (default: deepseek-r1-distill-llama-8b)
- `max_tokens`: The maximum number of tokens to generate (default: 500)
- `temperature`: The temperature to use for sampling (default: 0.2)
- `top_p`: The top-p value to use for sampling (default: 0.95)
- `context_window`: The size of the context window (default: 2048)
- `default_language`: The default programming language to use (default: python)

Example:

```python
config = {
    "base_url": "http://localhost:8080",
    "model_name": "custom-model",
    "max_tokens": 1000,
    "temperature": 0.5,
    "top_p": 0.8,
    "context_window": 4096,
    "default_language": "javascript"
}

generator = NaturalLanguageCodeGenerator(config)
```

## Supported Languages

The `NaturalLanguageCodeGenerator` class supports the following programming languages:

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

## Requirements

To use the `NaturalLanguageCodeGenerator` class, you need:

- A local AI server running at the configured URL
- The specified AI model loaded in the server
