# Symbolic Computation Module

Production-ready SymPy utilities integration for AIOS semi-autonomous agents.

## Overview

This module provides high-performance symbolic-to-numeric conversion, code generation, and mathematical computation capabilities for AI agents. It leverages SymPy's powerful utilities to enable agents to work with symbolic mathematics efficiently.

## Features

- **Fast Numerical Evaluation**: Convert symbolic expressions to optimized numerical functions using `lambdify`
- **Code Generation**: Generate compilable C, Fortran, Python, or Cython code from expressions
- **Automatic Compilation**: Use `autowrap` to compile and import generated code automatically  
- **Expression Caching**: LRU caching for repeated evaluations
- **Async/Await Support**: Full async support for non-blocking operations
- **Type Safety**: Pydantic models for strict input/output validation
- **Structured Logging**: JSON-formatted logs for production monitoring
- **Production-Ready**: Error handling, health checks, metrics, and graceful shutdown

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Basic Usage

```python
from symbolic_computation import SymbolicComputation

# Initialize engine
engine = SymbolicComputation()

# Evaluate expression
result = await engine.compute(
    expression="x**2 + sin(y)",
    variables={"x": 2.0, "y": 3.14},
    backend="numpy"
)

print(result.result)  # Numerical result
print(result.execution_time_ms)  # Performance metrics
```

### Code Generation

```python
# Generate C code
code_result = await engine.generate_code(
    expression="sqrt(x**2 + y**2)",
    variables=["x", "y"],
    language="C",
    function_name="distance"
)

print(code_result.source_code)
```

## Configuration

Configuration is managed through environment variables. Create a `.env` file:

```bash
# Cache settings
SYMBOLIC_CACHE_ENABLED=true
SYMBOLIC_CACHE_SIZE=128

# Performance
SYMBOLIC_DEFAULT_BACKEND=numpy
SYMBOLIC_ENABLE_METRICS=true

# Code generation
SYMBOLIC_CODEGEN_TEMP_DIR=/tmp/sympy_codegen
SYMBOLIC_DEFAULT_LANGUAGE=C

# Logging
SYMBOLIC_LOG_LEVEL=INFO
SYMBOLIC_ENABLE_STRUCTURED_LOGGING=true

# Security
SYMBOLIC_MAX_EXPRESSION_LENGTH=10000
SYMBOLIC_ALLOW_DANGEROUS_FUNCTIONS=false
```

## API Reference

### SymbolicComputation

Main interface for symbolic operations.

#### Methods

**`async compute(expression, variables, backend="numpy")`**

Evaluate symbolic expression numerically.

- **Parameters:**
  - `expression` (str): Mathematical expression
  - `variables` (dict): Variable values
  - `backend` (str): Numerical backend ('numpy', 'math', 'mpmath')
- **Returns:** `ComputationResult`

**`async generate_code(expression, variables, language="C", ...)`**

Generate code from symbolic expression.

- **Parameters:**
  - `expression` (str): Mathematical expression
  - `variables` (list): Variable names
  - `language` (str): Target language ('C', 'Fortran', 'Python', 'Cython')
  - `function_name` (str): Generated function name
  - `compile` (bool): Whether to compile code
- **Returns:** `CodeGenResult`

**`async health_check()`**

Perform system health check.

- **Returns:** Health status dictionary

### ExpressionEvaluator

High-performance expression evaluator with caching.

```python
from symbolic_computation.core import ExpressionEvaluator
from symbolic_computation.models import ComputationRequest, BackendType

evaluator = ExpressionEvaluator(cache_size=128)

request = ComputationRequest(
    expression="x**2 + y**2",
    variables=["x", "y"],
    backend=BackendType.NUMPY,
    values={"x": 3.0, "y": 4.0}
)

result = await evaluator.evaluate(request)
```

### CodeGenerator

Multi-language code generator.

```python
from symbolic_computation.core import CodeGenerator
from symbolic_computation.models import CodeGenRequest, CodeLanguage

codegen = CodeGenerator()

request = CodeGenRequest(
    expression="a*x**2 + b*x + c",
    variables=["x", "a", "b", "c"],
    language=CodeLanguage.C,
    function_name="quadratic"
)

result = await codegen.generate(request)
```

## Database Integration

While this module focuses on symbolic computation, it can be integrated with PostgreSQL and Neo4j:

### PostgreSQL for Results Storage

```python
import asyncpg

# Store computation results
async with pool.acquire() as conn:
    await conn.execute("""
        INSERT INTO computations (expression, result, execution_time)
        VALUES ($1, $2, $3)
    """, result.expression_str, result.result, result.execution_time_ms)
```

### Neo4j for Expression Graph

```python
from neo4j import AsyncGraphDatabase

# Store expression dependency graph
async with driver.session() as session:
    await session.run("""
        CREATE (e:Expression {text: $expr, variables: $vars})
    """, expr=expression, vars=variables)
```

## SymPy Utilities Used

This module leverages the following SymPy utilities:

1. **`sympy.utilities.lambdify`**
   - Fast numerical evaluation
   - Multi-backend support (NumPy, math, mpmath)
   - Array broadcasting with NumPy

2. **`sympy.utilities.autowrap`**
   - Automatic code compilation
   - Cython/F2PY backends
   - Binary Python extension generation

3. **`sympy.utilities.codegen`**
   - Multi-language code generation
   - C, Fortran, Python output
   - Header file generation

4. **`sympy.utilities.iterables`**
   - Flattening nested structures
   - Variations and permutations
   - Iterator utilities

5. **`sympy.utilities.memoization`**
   - Recurrence memoization
   - Performance optimization
   - Caching decorators

6. **`sympy.utilities.decorator`**
   - Function decoration
   - Vectorization support

## Testing

Run tests with pytest:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=symbolic_computation --cov-report=html

# Run specific test class
pytest tests/test_symbolic_computation.py::TestExpressionEvaluator
```

Coverage target: **>80%**

## Deployment

### Docker

```bash
# Build image
docker-compose build

# Run container
docker-compose up

# Run tests in container
docker-compose run app pytest
```

### Production Deployment

1. Set environment variables
2. Configure logging aggregation
3. Enable health check endpoint
4. Set up monitoring for metrics
5. Configure rate limiting if exposed as API

## Performance Considerations

### Caching

The module uses LRU caching for lambdified expressions:

```python
# First call: compiles expression
result1 = await engine.compute("x**2", {"x": 2.0})

# Second call: uses cached function (faster)
result2 = await engine.compute("x**2", {"x": 3.0})
```

### Backend Selection

- **NumPy**: Best for array operations and vectorization
- **Math**: Fastest for scalar operations
- **Mpmath**: For arbitrary precision
- **SymPy**: For symbolic results

### Optimization

Use common subexpression elimination:

```python
from symbolic_computation.utils import optimize_expression

optimized = optimize_expression("x**2 + 2*x**2 + x**2")
# Result: Eliminates redundant x**2 computations
```

## Integration with Your AIOS Repo

### Step 1: Add to Your Agent

```python
from symbolic_computation import SymbolicComputation

class YourAgent:
    def __init__(self):
        self.symbolic = SymbolicComputation()

    async def process_mathematical_task(self, expression, values):
        result = await self.symbolic.compute(expression, values)
        return result.result
```

### Step 2: Use in Tool Registry

```python
# In your tool_registry.py
from symbolic_computation import SymbolicComputation

class MathTool:
    def __init__(self):
        self.engine = SymbolicComputation()

    async def evaluate(self, expr: str, vars: dict):
        return await self.engine.compute(expr, vars)
```

### Step 3: Generate Agent Code

```python
# Generate optimized code for agent execution
code_result = await engine.generate_code(
    expression="complex_agent_logic",
    variables=["state", "input", "context"],
    language="Cython",
    compile=True
)

# Use compiled code in agent
compiled_func = code_result.compiled_function
result = compiled_func(state, input, context)
```

## Examples

See `examples/` directory for:

- Basic evaluation
- Multi-variable expressions
- Code generation workflows
- Caching demonstrations
- Integration patterns

## Contributing

1. Follow PEP 8 style guidelines
2. Add type hints to all functions
3. Write tests for new features (maintain >80% coverage)
4. Update documentation
5. Use structured logging

## License

MIT License - see LICENSE file

## References

- [SymPy Documentation](https://docs.sympy.org/)
- [SymPy Utilities Module](https://docs.sympy.org/latest/modules/utilities/index.html)
- [SymPy Code Generation](https://docs.sympy.org/latest/modules/codegen.html)
- [Lambdify Function](https://docs.sympy.org/latest/modules/utilities/lambdify.html)
- [Autowrap Module](https://docs.sympy.org/latest/modules/utilities/autowrap.html)
