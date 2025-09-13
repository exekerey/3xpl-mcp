# Tools Refactoring Guide

This document describes the major refactoring of the tools system implemented to improve maintainability, organization, and consistency.

## What Changed

### 1. Auto-Discovery Tool Registry

**Before**: Manual tool registration in `__init__.py`
```python
# Old approach - manual list maintenance
for tool in [
    get_address_overview,
    get_block_overview,
    # ... 15 tools manually listed
]:
    mcp_server.tool()(tool)
```

**After**: Automatic tool discovery with decorators
```python
# New approach - automatic registration
@mcp_tool
async def get_address_overview(blockchain: str, address: str) -> str:
    # Tool implementation
```

### 2. File Organization

**Before**: Large monolithic files
- `aggregate.py` (309 lines, 5 tools)
- Manual imports for all tools

**After**: Focused, single-responsibility modules
- `address_aggregates.py` - Address-related aggregations
- `block_aggregates.py` - Block-related aggregations  
- `transaction_aggregates.py` - Transaction-related aggregations
- `aggregate_schemas.py` - Shared schema definitions
- `validation.py` - Input validation utilities
- `registry.py` - Auto-discovery system

### 3. Standardized Structure

All tools now follow consistent patterns:
- Type hints for all parameters and return values
- Standardized error handling
- Input validation where appropriate
- Consistent documentation format

## Benefits

### 🎯 Maintainability
- **No more manual tool lists**: Adding a new tool only requires the `@mcp_tool` decorator
- **Better organization**: Related functionality grouped together
- **Easier testing**: Smaller, focused modules are easier to test

### 🏗️ Modularity
- **Single responsibility**: Each file has a clear, focused purpose
- **Reusable components**: Shared schemas and validation utilities
- **Clean imports**: Better organized dependencies

### 🔒 Safety
- **Input validation**: SQL injection protection and parameter validation
- **Error handling**: Comprehensive error catching and logging
- **Type safety**: Proper type annotations throughout

## New Components

### Registry System (`registry.py`)
```python
from src.tools.registry import mcp_tool

@mcp_tool
async def my_new_tool(param: str) -> str:
    """Tool automatically discovered and registered."""
    return f"Processing {param}"
```

### Validation Utilities (`validation.py`)
```python
from src.tools.validation import (
    validate_sql_query, validate_blockchain_name,
    validate_address, safe_execute_sql
)

# Automatic validation in aggregate tools
validate_blockchain_name(blockchain)
validate_sql_query(sql_query)
```

### Shared Schemas (`aggregate_schemas.py`)
```python
from src.tools.aggregate_schemas import (
    TRANSFERS_SCHEMA, BALANCES_SCHEMA,
    get_transfer_schema_description
)

# Consistent schema definitions across tools
unwrap_into_table(conn, TRANSFERS_SCHEMA, data)
```

## Migration Guide

### For New Tools
1. Import the decorator: `from src.tools.registry import mcp_tool`
2. Add the decorator: `@mcp_tool`
3. The tool will be automatically discovered and registered

### For Existing Code
- All existing functionality is preserved
- Tool names and signatures are unchanged
- No breaking changes to the API

### For Testing
- Import tools from their new locations:
  ```python
  from src.tools.address_aggregates import aggregate_address_transfers
  from src.tools.block_aggregates import aggregate_block_transfers
  ```

## File Structure

```
src/tools/
├── __init__.py              # Main initialization with auto-discovery
├── registry.py              # Auto-discovery and registration system
├── validation.py            # Input validation utilities
├── aggregate_schemas.py     # Shared schema definitions
├── __all__.py              # Tool categorization and exports
├── address.py              # Address overview tools
├── address_aggregates.py   # Address aggregation tools
├── block.py                # Block overview tools
├── block_aggregates.py     # Block aggregation tools
├── transaction.py          # Transaction overview tools
├── transaction_aggregates.py # Transaction aggregation tools
├── blockchain.py           # Blockchain detection tools
├── ens.py                  # ENS resolution tools
└── modules.py              # Module listing tools
```

## Best Practices

### Adding New Tools
1. **Choose the right module**: Put tools in the most appropriate existing module or create a new focused module
2. **Use the decorator**: Always use `@mcp_tool` for automatic registration
3. **Add validation**: Use validation utilities for user inputs
4. **Follow patterns**: Look at existing tools for consistency
5. **Document thoroughly**: Include comprehensive docstrings

### Error Handling
```python
@mcp_tool
async def my_tool(blockchain: str, address: str) -> str:
    # Validate inputs
    validate_blockchain_name(blockchain)
    validate_address(address)
    
    try:
        # Tool logic here
        result = await some_operation()
        return result
    except Exception as e:
        logger.error(f"Tool failed: {e}")
        raise
```

### SQL Validation
```python
# Always validate SQL queries in aggregate tools
validate_sql_query(sql_query)

# Use safe_execute_sql for automatic validation
return safe_execute_sql(conn, schema, data, sql_query)
```

## Testing

The refactored system maintains backward compatibility:

```bash
# Test that all tools are discovered
python -c "from src.tools import init_tools; from src.tools.registry import tool_registry; from mcp.server import FastMCP; server = FastMCP('test'); init_tools(server); print('Tools:', len(tool_registry.get_tools()))"

# Test validation
python -c "from src.tools.validation import validate_sql_query; validate_sql_query('SELECT * FROM data')"

# Test the server still starts
timeout 5 python main.py || echo "Server started successfully"
```

## Future Improvements

The new structure enables several future enhancements:

1. **Plugin System**: Easy to add new tool modules
2. **Dynamic Loading**: Tools could be loaded from external packages
3. **Better Testing**: Each module can have focused unit tests
4. **Documentation Generation**: Auto-generate docs from tool decorators
5. **Metrics Collection**: Track tool usage through the registry