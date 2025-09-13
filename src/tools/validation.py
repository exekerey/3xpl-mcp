"""
Validation utilities for aggregate tools.
"""
import re
import logging
from typing import List

logger = logging.getLogger(__name__)


class SQLValidationError(Exception):
    """Raised when SQL query validation fails."""
    pass


def validate_sql_query(sql_query: str) -> None:
    """
    Basic validation for SQL queries to prevent dangerous operations.
    
    Args:
        sql_query: The SQL query string to validate
        
    Raises:
        SQLValidationError: If the query contains dangerous operations
    """
    if not sql_query or not sql_query.strip():
        raise SQLValidationError("SQL query cannot be empty")
    
    # Convert to lowercase for checking
    query_lower = sql_query.lower().strip()
    
    # List of dangerous operations to block
    dangerous_operations = [
        'drop', 'delete', 'update', 'insert', 'alter', 
        'create', 'truncate', 'exec', 'execute'
    ]
    
    # Check for dangerous operations
    for operation in dangerous_operations:
        if re.search(rf'\b{operation}\b', query_lower):
            raise SQLValidationError(f"Dangerous SQL operation '{operation}' is not allowed")
    
    # Ensure query starts with SELECT
    if not query_lower.startswith('select'):
        raise SQLValidationError("Only SELECT queries are allowed")
    
    logger.debug(f"SQL query validation passed: {sql_query[:50]}...")


def validate_blockchain_name(blockchain: str) -> None:
    """
    Validate blockchain name format.
    
    Args:
        blockchain: The blockchain name to validate
        
    Raises:
        ValueError: If the blockchain name format is invalid
    """
    if not blockchain:
        raise ValueError("Blockchain name cannot be empty")
    
    if not isinstance(blockchain, str):
        raise ValueError("Blockchain name must be a string")
    
    # Blockchain names should be lowercase with dashes
    if not re.match(r'^[a-z0-9-]+$', blockchain):
        raise ValueError("Blockchain name must be lowercase with dashes instead of spaces")
    
    logger.debug(f"Blockchain name validation passed: {blockchain}")


def validate_module_name(module: str, blockchain: str) -> None:
    """
    Validate module name format.
    
    Args:
        module: The module name to validate
        blockchain: The blockchain name for context
        
    Raises:
        ValueError: If the module name format is invalid
    """
    if not module:
        raise ValueError("Module name cannot be empty")
    
    if not isinstance(module, str):
        raise ValueError("Module name must be a string")
    
    # Module should be prefixed with blockchain name
    if not module.startswith(blockchain):
        raise ValueError(f"Module name '{module}' must be prefixed with blockchain name '{blockchain}'")
    
    # Module names should be lowercase with dashes
    if not re.match(r'^[a-z0-9-]+$', module):
        raise ValueError("Module name must be lowercase with dashes")
    
    logger.debug(f"Module name validation passed: {module}")


def validate_address(address: str) -> None:
    """
    Basic validation for blockchain addresses.
    
    Args:
        address: The address to validate
        
    Raises:
        ValueError: If the address format is invalid
    """
    if not address:
        raise ValueError("Address cannot be empty")
    
    if not isinstance(address, str):
        raise ValueError("Address must be a string")
    
    # Basic length and character checks
    address = address.strip()
    if len(address) < 10:
        raise ValueError("Address is too short")
    
    if len(address) > 200:
        raise ValueError("Address is too long")
    
    logger.debug(f"Address validation passed: {address[:10]}...")


def validate_transaction_hash(tx_hash: str) -> None:
    """
    Basic validation for transaction hashes.
    
    Args:
        tx_hash: The transaction hash to validate
        
    Raises:
        ValueError: If the transaction hash format is invalid
    """
    if not tx_hash:
        raise ValueError("Transaction hash cannot be empty")
    
    if not isinstance(tx_hash, str):
        raise ValueError("Transaction hash must be a string")
    
    # Basic length and character checks
    tx_hash = tx_hash.strip()
    if len(tx_hash) < 32:
        raise ValueError("Transaction hash is too short")
    
    if len(tx_hash) > 200:
        raise ValueError("Transaction hash is too long")
    
    logger.debug(f"Transaction hash validation passed: {tx_hash[:10]}...")


def validate_block_height(height: int) -> None:
    """
    Validate block height.
    
    Args:
        height: The block height to validate
        
    Raises:
        ValueError: If the block height is invalid
    """
    if not isinstance(height, int):
        raise ValueError("Block height must be an integer")
    
    if height < 0:
        raise ValueError("Block height cannot be negative")
    
    if height > 1_000_000_000:  # Reasonable upper bound
        raise ValueError("Block height is unreasonably high")
    
    logger.debug(f"Block height validation passed: {height}")


def safe_execute_sql(connection, schema: dict, data: list, sql_query: str):
    """
    Safely execute SQL operations with validation.
    
    Args:
        connection: Database connection
        schema: Table schema definition
        data: Data to populate the table
        sql_query: SQL query to execute
        
    Returns:
        Query result
    """
    from src.core.db import unwrap_into_table, get_aggregate
    
    # Validate the SQL query
    validate_sql_query(sql_query)
    
    # Populate the table and execute query
    unwrap_into_table(connection, schema, data)
    result = get_aggregate(connection, sql_query)
    
    logger.debug(f"SQL query executed successfully, returned {len(result) if isinstance(result, list) else 1} results")
    return result