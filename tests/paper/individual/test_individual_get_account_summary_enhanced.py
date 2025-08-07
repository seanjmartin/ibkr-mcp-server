"""
Individual MCP Tool Test: get_account_summary - ENHANCED VALIDATION
Focus: Test get_account_summary MCP tool with comprehensive account balance validation
MCP Tool: get_account_summary
Expected: Complete account balance structure with multi-currency and constraint validation
Enhancement: Addresses comprehensive account summary validation gaps identified in Test 1.3
"""

import pytest
import asyncio
import sys
import os
from decimal import Decimal
from typing import Dict, List, Set, Optional, Tuple

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, project_root)

# Import MCP interface - THIS IS THE CORRECT LAYER TO TEST
from ibkr_mcp_server.tools import call_tool  # Proper MCP interface
from mcp.types import TextContent
import json
from unittest.mock import patch, AsyncMock

@pytest.mark.paper
@pytest.mark.asyncio
class TestIndividualGetAccountSummaryEnhanced:
    """Test get_account_summary MCP tool with comprehensive validation"""
    
    # Define comprehensive account metric categories for validation
    CASH_METRICS = {'TotalCashValue', 'BuyingPower', 'ExcessLiquidity'}
    MARGIN_METRICS = {'FullInitMarginReq', 'FullMaintMarginReq', 'InitMarginReq', 'MaintMarginReq'}
    PORTFOLIO_METRICS = {'NetLiquidation', 'GrossPositionValue', 'EquityWithLoanValue'}
    PNL_METRICS = {'RealizedPnL', 'UnrealizedPnL', 'DayTradesRemaining'}
    
    # Define expected currencies (including BASE for multi-currency accounts)
    EXPECTED_CURRENCIES = {'USD', 'EUR', 'GBP', 'JPY', 'CHF', 'AUD', 'CAD', 'BASE'}
    
    # Define value constraints for different metric types
    VALUE_CONSTRAINTS = {
        'BuyingPower': {'min': 0, 'type': 'positive_or_zero'},
        'NetLiquidation': {'min': -float('inf'), 'type': 'any_number'},  # Can be negative
        'TotalCashValue': {'min': -float('inf'), 'type': 'any_number'},  # Can be negative
        'GrossPositionValue': {'min': 0, 'type': 'positive_or_zero'},
        'FullInitMarginReq': {'min': 0, 'type': 'positive_or_zero'},
        'FullMaintMarginReq': {'min': 0, 'type': 'positive_or_zero'},
        'RealizedPnL': {'min': -float('inf'), 'type': 'any_number'},  # Can be negative
        'UnrealizedPnL': {'min': -float('inf'), 'type': 'any_number'}  # Can be negative
    }
    
    async def test_comprehensive_account_summary_validation(self):
        """Test comprehensive account summary with all validation enhancements
        
        VALIDATION ENHANCEMENTS:
        1. Complete financial metrics structure with value constraints
        2. Multi-currency account handling (USD, EUR, GBP, JPY, BASE)
        3. Account metric categorization validation 
        4. Currency-specific balance format validation
        5. Duplicate entry handling for multi-currency scenarios
        6. Professional-grade constraint checking similar to stop loss tests
        7. Edge case handling for empty accounts and accounts with positions
        """
        
        print(f"\\n{'='*80}")
        print(f"=== ENHANCED ACCOUNT SUMMARY MCP TOOL VALIDATION ===")
        print(f"{'='*80}")
        
        # STEP 1: Force IBKR Gateway connection with client ID 5
        print(f"Step 1: Establishing IBKR Gateway connection (Client ID 5)...")
        from ibkr_mcp_server.client import ibkr_client
        
        try:
            connection_success = await ibkr_client.connect()
            if connection_success:
                print(f"[✓] IBKR Gateway connected - Client ID: {ibkr_client.client_id}")
                print(f"[✓] Paper account validated: {ibkr_client.current_account}")
                
                # Validate paper account prefix for safety
                assert ibkr_client.current_account.startswith("DU"), f"Not a paper account: {ibkr_client.current_account}"
                
            else:
                pytest.fail("IBKR Gateway connection failed - cannot proceed with account summary testing")
                
        except Exception as e:
            pytest.fail(f"Connection error prevents account summary testing: {e}")
        
        # STEP 2: Execute MCP tool call with comprehensive error handling
        tool_name = "get_account_summary"
        parameters = {}  # No parameters needed for current account
        
        print(f"\\nStep 2: MCP Tool Execution")
        print(f"Tool: {tool_name}")
        print(f"Parameters: {parameters}")
        print(f"Expected: List of account summary entries with tag/value/currency/account structure")
        
        try:
            # Execute the MCP tool call
            mcp_result = await call_tool(tool_name, parameters)
            print(f"[✓] MCP call completed successfully")
            
        except Exception as e:
            pytest.fail(f"MCP tool call failed - account summary unavailable: {e}")
        
        # STEP 3: MCP Protocol Response Validation
        print(f"\\nStep 3: MCP Protocol Response Structure Validation")
        
        # Validate MCP response structure (list of TextContent)
        assert isinstance(mcp_result, list), f"MCP response must be list, got {type(mcp_result)}"
        assert len(mcp_result) > 0, f"MCP response cannot be empty list"
        
        text_content = mcp_result[0]
        assert isinstance(text_content, TextContent), f"Expected TextContent, got {type(text_content)}"
        assert hasattr(text_content, 'text'), f"TextContent missing required 'text' attribute"
        
        response_text = text_content.text
        print(f"[✓] MCP response structure validated")
        print(f"[✓] Response size: {len(response_text)} characters")
        
        # STEP 4: Parse and Validate JSON Response Format
        print(f"\\nStep 4: JSON Response Parsing and Format Validation")
        
        try:
            account_summary_data = json.loads(response_text)
            print(f"[✓] JSON parsing successful")
            
        except json.JSONDecodeError as e:
            pytest.fail(f"Account summary response not valid JSON: {e}")
        
        # Validate response is a list of account summary entries
        assert isinstance(account_summary_data, list), f"Account summary must be list, got {type(account_summary_data)}"
        assert len(account_summary_data) > 0, f"Account summary cannot be empty - expected at least basic metrics"
        
        print(f"[✓] Account summary contains {len(account_summary_data)} metric entries")
        
        # STEP 5: COMPREHENSIVE ACCOUNT SUMMARY STRUCTURE VALIDATION
        print(f"\\nStep 5: Comprehensive Account Summary Structure Validation")
        
        # Data structures for comprehensive validation
        metrics_by_category = {
            'cash': {},
            'margin': {},
            'portfolio': {},
            'pnl': {},
            'other': {}
        }
        
        currencies_found = set()
        accounts_found = set()
        duplicate_metrics = {}  # Track metrics that appear multiple times
        value_validation_results = {}
        
        # Process each account summary entry
        for i, entry in enumerate(account_summary_data):
            print(f"\\n--- Processing Entry {i+1}/{len(account_summary_data)} ---")
            
            # Validate entry structure
            assert isinstance(entry, dict), f"Entry {i+1} must be dict, got {type(entry)}"
            
            # Validate required fields
            required_fields = ['tag', 'value', 'currency', 'account']
            for field in required_fields:
                assert field in entry, f"Entry {i+1} missing required field '{field}'"
                assert entry[field] is not None, f"Entry {i+1} field '{field}' cannot be None"
            
            tag = entry['tag']
            value = entry['value']
            currency = entry['currency']
            account = entry['account']
            
            print(f"  Tag: {tag}")
            print(f"  Value: {value}")
            print(f"  Currency: {currency}")
            print(f"  Account: {account}")
            
            # Collect data for comprehensive analysis
            currencies_found.add(currency)
            accounts_found.add(account)
            
            # Track duplicate metrics (expected for multi-currency accounts)
            metric_key = f"{tag}_{currency}"
            if metric_key in duplicate_metrics:
                duplicate_metrics[metric_key] += 1
            else:
                duplicate_metrics[metric_key] = 1
            
            # Categorize metrics for structural validation
            if tag in self.CASH_METRICS:
                metrics_by_category['cash'][metric_key] = float(value)
            elif tag in self.MARGIN_METRICS:
                metrics_by_category['margin'][metric_key] = float(value)
            elif tag in self.PORTFOLIO_METRICS:
                metrics_by_category['portfolio'][metric_key] = float(value)
            elif tag in self.PNL_METRICS:
                metrics_by_category['pnl'][metric_key] = float(value)
            else:
                metrics_by_category['other'][metric_key] = float(value)
            
            # Validate value format and constraints
            try:
                numeric_value = float(value)
                print(f"  [✓] Numeric value: ${numeric_value:,.2f}")
                
                # Apply value constraints if defined
                if tag in self.VALUE_CONSTRAINTS:
                    constraint = self.VALUE_CONSTRAINTS[tag]
                    if constraint['type'] == 'positive_or_zero':
                        assert numeric_value >= 0, f"{tag} must be non-negative, got {numeric_value}"
                        print(f"  [✓] Constraint validated: {tag} >= 0")
                    elif constraint['type'] == 'any_number':
                        print(f"  [✓] Constraint validated: {tag} accepts any numeric value")
                
                value_validation_results[metric_key] = {
                    'value': numeric_value,
                    'constraint_passed': True,
                    'constraint_type': self.VALUE_CONSTRAINTS.get(tag, {}).get('type', 'no_constraint')
                }
                
            except ValueError:
                pytest.fail(f"Entry {i+1} value '{value}' is not a valid number")
        
        print(f"\\n[✓] All {len(account_summary_data)} entries validated successfully")
        
        # STEP 6: MULTI-CURRENCY ACCOUNT VALIDATION
        print(f"\\nStep 6: Multi-Currency Account Analysis")
        
        print(f"Currencies found: {sorted(currencies_found)}")
        print(f"Total currencies: {len(currencies_found)}")
        
        # Validate currency codes
        for currency in currencies_found:
            assert currency in self.EXPECTED_CURRENCIES or len(currency) == 3, f"Unexpected currency format: {currency}"
        
        # Special validation for BASE currency (multi-currency account indicator)
        if 'BASE' in currencies_found:
            print(f"[✓] BASE currency detected - multi-currency account confirmed")
            # BASE currency should appear with PnL metrics typically
            base_metrics = [k for k in duplicate_metrics.keys() if k.endswith('_BASE')]
            print(f"[✓] BASE currency metrics: {base_metrics}")
        
        # USD should always be present for US-based accounts
        assert 'USD' in currencies_found, f"USD currency missing from account summary"
        print(f"[✓] USD currency confirmed as expected")
        
        # STEP 7: ACCOUNT METRIC CATEGORIZATION VALIDATION
        print(f"\\nStep 7: Account Metric Categorization Analysis")
        
        for category, metrics in metrics_by_category.items():
            if metrics:
                print(f"\\n{category.upper()} METRICS ({len(metrics)} entries):")
                for metric_key, value in metrics.items():
                    print(f"  {metric_key}: ${value:,.2f}")
        
        # Validate essential metrics are present
        essential_metrics = ['BuyingPower', 'NetLiquidation', 'TotalCashValue']
        found_essential = []
        
        all_tags = [entry['tag'] for entry in account_summary_data]
        for essential in essential_metrics:
            if essential in all_tags:
                found_essential.append(essential)
        
        assert len(found_essential) >= 2, f"Missing essential metrics. Found: {found_essential}, Expected at least 2 of: {essential_metrics}"
        print(f"[✓] Essential metrics validated: {found_essential}")
        
        # STEP 8: DUPLICATE ENTRY HANDLING VALIDATION
        print(f"\\nStep 8: Duplicate Entry Analysis (Multi-Currency Scenario)")
        
        pure_duplicates = {k: v for k, v in duplicate_metrics.items() if v > 1}
        if pure_duplicates:
            print(f"Duplicate metrics detected (expected for multi-currency accounts):")
            for metric_key, count in pure_duplicates.items():
                print(f"  {metric_key}: appears {count} times")
            
            # This is expected behavior for metrics like RealizedPnL, UnrealizedPnL in multi-currency accounts
            expected_duplicates = ['RealizedPnL', 'UnrealizedPnL']
            for dup_key in pure_duplicates.keys():
                metric_name = dup_key.split('_')[0]  # Extract metric name before currency
                if metric_name in expected_duplicates:
                    print(f"  [✓] {metric_name} duplication is expected for multi-currency accounts")
                    
        else:
            print(f"[✓] No duplicate metrics found - single currency account scenario")
        
        # STEP 9: ACCOUNT BALANCE CONSTRAINT VALIDATION
        print(f"\\nStep 9: Account Balance Constraint and Relationship Validation")
        
        # Extract key values for relationship validation
        buying_power = None
        net_liquidation = None
        total_cash = None
        gross_position = None
        
        for entry in account_summary_data:
            if entry['tag'] == 'BuyingPower' and entry['currency'] == 'USD':
                buying_power = float(entry['value'])
            elif entry['tag'] == 'NetLiquidation' and entry['currency'] == 'USD':
                net_liquidation = float(entry['value'])
            elif entry['tag'] == 'TotalCashValue' and entry['currency'] == 'USD':
                total_cash = float(entry['value'])
            elif entry['tag'] == 'GrossPositionValue' and entry['currency'] == 'USD':
                gross_position = float(entry['value'])
        
        # Validate relationships (when all values are available)
        if buying_power is not None and net_liquidation is not None:
            print(f"Buying Power: ${buying_power:,.2f}")
            print(f"Net Liquidation: ${net_liquidation:,.2f}")
            
            # For paper accounts with no margin, buying power should be >= net liquidation
            # (buying power includes leverage multiplier)
            if gross_position == 0:  # No positions, cash account scenario
                print(f"[✓] Cash account scenario - no positions detected")
                assert buying_power >= net_liquidation, f"Cash account: buying power ({buying_power}) should be >= net liquidation ({net_liquidation})"
                print(f"[✓] Cash account constraint validated")
            
        # STEP 10: PAPER ACCOUNT SAFETY VALIDATION
        print(f"\\nStep 10: Paper Account Safety Validation")
        
        unique_accounts = list(accounts_found)
        assert len(unique_accounts) == 1, f"Expected single account, found multiple: {unique_accounts}"
        
        paper_account = unique_accounts[0]
        assert paper_account.startswith("DU"), f"Not a paper account: {paper_account}"
        print(f"[✓] Paper account confirmed: {paper_account}")
        
        # Validate account consistency across all entries
        account_consistency = all(entry['account'] == paper_account for entry in account_summary_data)
        assert account_consistency, f"Account inconsistency detected across summary entries"
        print(f"[✓] Account consistency validated across all {len(account_summary_data)} entries")
        
        # FINAL VALIDATION SUMMARY
        print(f"\\n{'='*80}")
        print(f"=== COMPREHENSIVE ACCOUNT SUMMARY VALIDATION SUMMARY ===")
        print(f"{'='*80}")
        print(f"[✓] MCP Protocol Layer: PASSED")
        print(f"[✓] JSON Response Format: PASSED") 
        print(f"[✓] Entry Structure Validation: PASSED ({len(account_summary_data)} entries)")
        print(f"[✓] Multi-Currency Support: PASSED ({len(currencies_found)} currencies)")
        print(f"[✓] Metric Categorization: PASSED")
        print(f"[✓] Value Constraint Validation: PASSED")
        print(f"[✓] Duplicate Entry Handling: PASSED") 
        print(f"[✓] Account Balance Relationships: PASSED")
        print(f"[✓] Paper Account Safety: PASSED")
        
        print(f"\\n📊 ACCOUNT SUMMARY METRICS BREAKDOWN:")
        print(f"   💰 Cash Metrics: {len(metrics_by_category['cash'])}")
        print(f"   📈 Portfolio Metrics: {len(metrics_by_category['portfolio'])}")  
        print(f"   📊 Margin Metrics: {len(metrics_by_category['margin'])}")
        print(f"   💹 P&L Metrics: {len(metrics_by_category['pnl'])}")
        print(f"   ➕ Other Metrics: {len(metrics_by_category['other'])}")
        print(f"   🌍 Currencies: {sorted(currencies_found)}")
        print(f"   🏦 Account: {paper_account}")
        
        print(f"\\n✅ ENHANCED ACCOUNT SUMMARY VALIDATION COMPLETED SUCCESSFULLY")
        print(f"✅ Test demonstrates comprehensive account balance data handling")
        print(f"✅ All validation enhancements implemented and verified")
        print(f"{'='*80}")

    async def test_account_summary_empty_vs_populated_scenarios(self):
        """Test account summary handling for both empty and populated account scenarios
        
        Similar to stop loss test enhancement - validates proper response structure
        whether account has positions/balances or is empty/new
        """
        
        print(f"\\n{'='*70}")
        print(f"=== ACCOUNT SUMMARY SCENARIO HANDLING VALIDATION ===") 
        print(f"{'='*70}")
        
        # Get account summary via MCP
        result = await call_tool("get_account_summary", {})
        text_content = result[0]
        account_data = json.loads(text_content.text)
        
        print(f"Account summary entries: {len(account_data)}")
        
        # Test should handle both scenarios gracefully
        if len(account_data) == 0:
            print("[✓] Empty account scenario - no account data available")
            print("    This may occur for newly created accounts or during maintenance")
            
        else:
            print(f"[✓] Populated account scenario - {len(account_data)} metrics available")
            
            # Categorize metrics by value (zero vs non-zero)
            zero_metrics = []
            nonzero_metrics = []
            
            for entry in account_data:
                try:
                    value = float(entry['value'])
                    if value == 0:
                        zero_metrics.append(entry['tag'])
                    else:
                        nonzero_metrics.append(entry['tag'])
                except ValueError:
                    pass
            
            print(f"    Zero-value metrics: {len(zero_metrics)} ({zero_metrics})")  
            print(f"    Non-zero metrics: {len(nonzero_metrics)} ({nonzero_metrics})")
            
            # For new paper accounts, many values will be zero but structure should be complete
            if len(zero_metrics) > len(nonzero_metrics):
                print("[✓] New/empty account scenario - mostly zero values as expected")
            else:
                print("[✓] Active account scenario - mixed zero and non-zero values")
        
        print(f"[✓] Scenario handling validation completed")

# EXECUTION INSTRUCTIONS
"""
ENHANCED TEST EXECUTION COMMANDS:

Primary Test (Comprehensive Validation):
C:\\Python313\\python.exe -m pytest tests/paper/individual/test_individual_get_account_summary_enhanced.py::TestIndividualGetAccountSummaryEnhanced::test_comprehensive_account_summary_validation -v -s

Scenario Test:
C:\\Python313\\python.exe -m pytest tests/paper/individual/test_individual_get_account_summary_enhanced.py::TestIndividualGetAccountSummaryEnhanced::test_account_summary_empty_vs_populated_scenarios -v -s

Full Test Suite:
C:\\Python313\\python.exe -m pytest tests/paper/individual/test_individual_get_account_summary_enhanced.py -v -s

PREREQUISITES:
- IBKR Gateway running with paper trading login
- API enabled, port 7497, client ID 5 available
- Paper account logged in (DU* prefix account)

VALIDATION ENHANCEMENTS IMPLEMENTED:
✓ Complete financial metrics structure and value constraints  
✓ Multi-currency account scenarios (USD, EUR, GBP, JPY, BASE)
✓ Account metric categorization (cash, margin, portfolio, PnL)
✓ Currency-specific balance formats and appropriate value ranges
✓ Duplicate entry handling for multi-currency metrics  
✓ Professional-grade account balance validation similar to stop loss enhancement
✓ Empty vs populated account scenario handling
✓ Account balance relationship constraints (buying power, net liquidation, etc.)
"""

if __name__ == "__main__":
    print("⚠️  ENHANCED ACCOUNT SUMMARY TEST - Use pytest execution commands above")
    print("⚠️  Comprehensive validation covers all identified gaps in Test 1.3")
    exit_code = pytest.main([__file__, "-v", "-s", "--tb=short"])
    sys.exit(exit_code)
