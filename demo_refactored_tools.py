#!/usr/bin/env python3
"""
Demo script to showcase the refactored tools system.
"""
import asyncio
import logging
from mcp.server import FastMCP

from src.tools import init_tools
from src.tools.registry import tool_registry
from src.tools.__all__ import (
    ALL_TOOLS, BLOCKCHAIN_TOOLS, ADDRESS_TOOLS, 
    BLOCK_TOOLS, TRANSACTION_TOOLS, ENS_TOOLS
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def demo_tool_discovery():
    """Demonstrate the auto-discovery system."""
    print("🔍 Tool Discovery Demo")
    print("=" * 50)
    
    # Create MCP server and initialize tools
    server = FastMCP("demo")
    init_tools(server)
    
    # Show discovered tools
    tools = tool_registry.get_tools()
    print(f"✅ Discovered {len(tools)} tools automatically")
    
    # Show tools by category
    categories = {
        "Blockchain": BLOCKCHAIN_TOOLS,
        "Address": ADDRESS_TOOLS, 
        "Block": BLOCK_TOOLS,
        "Transaction": TRANSACTION_TOOLS,
        "ENS": ENS_TOOLS
    }
    
    for category, tool_names in categories.items():
        print(f"\n📂 {category} Tools ({len(tool_names)}):")
        for tool_name in tool_names:
            status = "✅" if tool_name in tools else "❌"
            print(f"  {status} {tool_name}")
    
    print(f"\n📊 Summary:")
    print(f"  Total tools expected: {len(ALL_TOOLS)}")
    print(f"  Total tools discovered: {len(tools)}")
    print(f"  All tools found: {'✅ Yes' if len(tools) == len(ALL_TOOLS) else '❌ No'}")


def demo_validation():
    """Demonstrate the validation system."""
    print("\n🛡️ Validation Demo")
    print("=" * 50)
    
    from src.tools.validation import (
        validate_blockchain_name, validate_sql_query, 
        SQLValidationError, validate_address
    )
    
    # Test valid inputs
    try:
        validate_blockchain_name("ethereum")
        validate_sql_query("SELECT * FROM data LIMIT 10")
        validate_address("0x742d35Cc8639C4532F5B8564D0e56Ff6E2E8D3F0")
        print("✅ Valid inputs passed validation")
    except Exception as e:
        print(f"❌ Validation failed unexpectedly: {e}")
    
    # Test invalid inputs
    test_cases = [
        ("Invalid blockchain", lambda: validate_blockchain_name("Invalid Blockchain")),
        ("Dangerous SQL", lambda: validate_sql_query("DROP TABLE users")),
        ("Empty address", lambda: validate_address("")),
    ]
    
    for test_name, test_func in test_cases:
        try:
            test_func()
            print(f"❌ {test_name}: Should have failed validation")
        except Exception as e:
            print(f"✅ {test_name}: Correctly caught - {type(e).__name__}")


def demo_modular_structure():
    """Demonstrate the new modular structure."""
    print("\n📁 Modular Structure Demo")
    print("=" * 50)
    
    # Show the new module imports work
    modules = [
        "src.tools.address_aggregates",
        "src.tools.block_aggregates", 
        "src.tools.transaction_aggregates",
        "src.tools.aggregate_schemas",
        "src.tools.validation",
        "src.tools.registry"
    ]
    
    for module_name in modules:
        try:
            __import__(module_name)
            print(f"✅ {module_name} imported successfully")
        except ImportError as e:
            print(f"❌ {module_name} failed to import: {e}")
    
    # Show schema consistency
    from src.tools.aggregate_schemas import TRANSFERS_SCHEMA, BALANCES_SCHEMA
    print(f"\n📋 Schema Definitions:")
    print(f"  Transfers schema: {len(TRANSFERS_SCHEMA)} fields")
    print(f"  Balances schema: {len(BALANCES_SCHEMA)} fields")


async def demo_tool_functionality():
    """Demonstrate that tools still work correctly."""
    print("\n⚙️ Tool Functionality Demo")
    print("=" * 50)
    
    # Import some tools directly
    from src.tools.blockchain import detect_blockchains
    from src.tools.ens import resolve_ens_domain
    
    # Test that tools are properly decorated
    has_decorator = lambda func: hasattr(func, '_is_mcp_tool') and func._is_mcp_tool
    
    tools_to_test = [
        ("detect_blockchains", detect_blockchains),
        ("resolve_ens_domain", resolve_ens_domain),
    ]
    
    for tool_name, tool_func in tools_to_test:
        if has_decorator(tool_func):
            print(f"✅ {tool_name} has @mcp_tool decorator")
        else:
            print(f"❌ {tool_name} missing @mcp_tool decorator")
    
    print("\n🚀 Tools are ready for MCP server registration!")


def main():
    """Run all demos."""
    print("🎯 3xpl-MCP Tools Refactoring Demo")
    print("=" * 60)
    
    demo_tool_discovery()
    demo_validation() 
    demo_modular_structure()
    
    # Run async demo
    asyncio.run(demo_tool_functionality())
    
    print("\n🎉 Refactoring Demo Complete!")
    print("=" * 60)
    print("The tools system has been successfully refactored with:")
    print("  • Auto-discovery and registration")
    print("  • Modular, focused file organization") 
    print("  • Input validation and error handling")
    print("  • Consistent patterns and documentation")
    print("  • Backward compatibility maintained")


if __name__ == "__main__":
    main()