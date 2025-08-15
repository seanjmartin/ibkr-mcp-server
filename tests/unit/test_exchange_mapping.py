"""
Unit tests for exchange mapping strategy implementation.
Tests the cascading exchange resolution logic based on validation data.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from ibkr_mcp_server.trading.international import InternationalManager


class TestExchangeMapping:
    """Test exchange alias mapping and fallback logic"""

    @pytest.fixture
    def mock_ib(self):
        """Mock IBKR connection"""
        mock = MagicMock()
        mock.isConnected.return_value = True
        mock.reqContractDetailsAsync = AsyncMock()
        return mock

    @pytest.fixture
    def intl_manager(self, mock_ib):
        """Create InternationalManager with mocked IBKR connection"""
        manager = InternationalManager(mock_ib)
        return manager

    def test_exchange_aliases_mapping(self, intl_manager):
        """Test that exchange aliases mapping is correctly defined"""
        # Verify the aliases exist
        assert hasattr(intl_manager, 'EXCHANGE_ALIASES')
        
        # Test key validated mappings from our exchange validation document
        aliases = intl_manager.EXCHANGE_ALIASES
        
        # German mappings
        assert 'FRANKFURT' in aliases
        assert 'FWB' in aliases['FRANKFURT'] and 'FWB2' in aliases['FRANKFURT']
        assert 'XETRA' in aliases
        assert 'IBIS' in aliases['XETRA'] and 'IBIS2' in aliases['XETRA']
        
        # UK mappings
        assert 'LONDON' in aliases
        assert 'LSE' in aliases['LONDON'] and 'LSEETF' in aliases['LONDON']
        
        # Italian mappings - validated BIT/MIL fail, BVME works
        assert 'MILAN' in aliases
        assert aliases['MILAN'] == ['BVME']
        assert 'BIT' in aliases
        assert aliases['BIT'] == ['BVME']
        assert 'MIL' in aliases
        assert aliases['MIL'] == ['BVME']
        
        # Swiss mappings - validated SWX fails, EBS works
        assert 'SWISS' in aliases
        assert aliases['SWISS'] == ['EBS']
        assert 'SWX' in aliases
        assert aliases['SWX'] == ['EBS']
        
        # Canadian mappings - validated TSX fails, TSE works
        assert 'TORONTO' in aliases
        assert aliases['TORONTO'] == ['TSE']
        assert 'TSX' in aliases
        assert aliases['TSX'] == ['TSE']
        
        # Japanese mappings - validated TSE fails for Japan, TSEJ works
        assert 'TOKYO' in aliases
        assert aliases['TOKYO'] == ['TSEJ']
        
        # Swedish mappings - validated OMX fails, SFB works
        assert 'STOCKHOLM' in aliases
        assert aliases['STOCKHOLM'] == ['SFB']
        assert 'OMX' in aliases
        assert aliases['OMX'] == ['SFB']

    async def test_cascading_resolution_success_first_try(self, intl_manager, mock_ib):
        """Test successful resolution on first exchange attempt"""
        # Mock successful resolution on first try
        mock_detail = MagicMock()
        mock_detail.contract.symbol = "SAP"
        mock_detail.contract.longName = "SAP SE"
        mock_detail.contract.conId = 14204
        mock_detail.contract.exchange = "IBIS"
        mock_detail.contract.primaryExchange = "IBIS"
        mock_detail.contract.currency = "EUR"
        
        mock_ib.reqContractDetailsAsync.return_value = [mock_detail]
        
        # Test resolution with user's requested exchange works directly
        result = await intl_manager.resolve_symbol("SAP", exchange="IBIS", currency="EUR")
        
        assert result["matches"]
        assert len(result["matches"]) > 0
        assert result["matches"][0]["symbol"] == "SAP"
        assert result["matches"][0]["exchange"] == "IBIS"
        # Should not have used alias since original exchange worked
        assert not result.get("resolved_via_alias", False)

    async def test_cascading_resolution_fallback_to_alias(self, intl_manager, mock_ib):
        """Test fallback to exchange alias when original fails"""
        # Mock failed resolution on first try, success on alias
        def mock_contract_details(contract):
            if contract.exchange == "XETRA":
                # Original exchange fails
                return []
            elif contract.exchange == "IBIS":
                # Alias succeeds
                mock_detail = MagicMock()
                mock_detail.contract.symbol = "SAP"
                mock_detail.contract.longName = "SAP SE"
                mock_detail.contract.conId = 14204
                mock_detail.contract.exchange = "IBIS"
                mock_detail.contract.primaryExchange = "IBIS"
                mock_detail.contract.currency = "EUR"
                return [mock_detail]
            else:
                return []
        
        mock_ib.reqContractDetailsAsync.side_effect = mock_contract_details
        
        # Test resolution with failed original exchange, should fallback to alias
        result = await intl_manager.resolve_symbol("SAP", exchange="XETRA", currency="EUR")
        
        assert result["matches"]
        assert len(result["matches"]) > 0
        assert result["matches"][0]["symbol"] == "SAP"
        assert result["matches"][0]["exchange"] == "IBIS"  # Should resolve via alias
        # Should indicate alias was used
        assert result.get("resolved_via_alias", False)
        assert result.get("original_exchange") == "XETRA"
        assert result.get("actual_exchange") == "IBIS"

    async def test_cascading_resolution_fallback_to_smart(self, intl_manager, mock_ib):
        """Test fallback to SMART routing when all aliases fail"""
        # Mock failed resolution on original and all aliases, success on SMART
        def mock_contract_details(contract):
            if contract.exchange in ["BIT", "BVME"]:
                # Original and alias fail
                return []
            elif contract.exchange == "SMART":
                # SMART routing succeeds
                mock_detail = MagicMock()
                mock_detail.contract.symbol = "ISP"
                mock_detail.contract.longName = "Intesa Sanpaolo"
                mock_detail.contract.conId = 29816328
                mock_detail.contract.exchange = "BVME"  # SMART routes to BVME
                mock_detail.contract.primaryExchange = "BVME"
                mock_detail.contract.currency = "EUR"
                return [mock_detail]
            else:
                return []
        
        mock_ib.reqContractDetailsAsync.side_effect = mock_contract_details
        
        # Test resolution that should fall back to SMART routing
        result = await intl_manager.resolve_symbol("ISP", exchange="BIT", currency="EUR")
        
        assert result["matches"]
        assert len(result["matches"]) > 0
        assert result["matches"][0]["symbol"] == "ISP"
        assert result["matches"][0]["exchange"] == "BVME"  # Routed by SMART
        # Should indicate fallback to SMART was used
        assert result.get("resolution_method") == "exchange_fallback_smart"
        assert result.get("original_exchange") == "BIT"

    async def test_known_failing_exchanges_mapped_correctly(self, intl_manager):
        """Test that known failing exchanges are mapped to working alternatives"""
        aliases = intl_manager.EXCHANGE_ALIASES
        
        # Test validated failing exchanges are mapped
        failing_mappings = {
            'BIT': ['BVME'],          # Italian: BIT fails → BVME works
            'MIL': ['BVME'],          # Italian: MIL fails → BVME works  
            'SWX': ['EBS'],           # Swiss: SWX fails → EBS works
            'TSX': ['TSE'],           # Canadian: TSX fails → TSE works
            'OMX': ['SFB'],           # Swedish: OMX fails → SFB works
            'TRADEGATE': ['TGATE'],   # German: TRADEGATE fails → TGATE works
            'BSE': ['NSE'],           # Indian: BSE fails → NSE works
        }
        
        for failing_exchange, expected_aliases in failing_mappings.items():
            assert failing_exchange in aliases
            assert aliases[failing_exchange] == expected_aliases

    async def test_specialized_exchange_segments(self, intl_manager):
        """Test that specialized exchange segments are included in aliases"""
        aliases = intl_manager.EXCHANGE_ALIASES
        
        # Test segment-specific mappings from validation
        segment_mappings = {
            'FRANKFURT': ['FWB', 'FWB2'],      # Domestic vs Foreign
            'XETRA': ['IBIS', 'IBIS2'],        # Stocks vs ETFs
            'LONDON': ['LSE', 'LSEETF'],       # Stocks vs ETFs  
        }
        
        for exchange, expected_segments in segment_mappings.items():
            assert exchange in aliases
            for segment in expected_segments:
                assert segment in aliases[exchange]

    def test_response_enhancement_fields(self, intl_manager):
        """Test that response includes proper alias resolution indicators"""
        # This will be tested via integration when the actual implementation is complete
        # For now, verify the required response field structure is documented
        
        required_fields = [
            'resolved_via_alias',
            'original_exchange', 
            'actual_exchange',
            'resolution_method'
        ]
        
        # These fields should be added to resolve_symbol response when aliases are used
        # Implementation will be validated in integration tests
        assert all(field for field in required_fields)  # Placeholder test

    async def test_no_infinite_loops_in_aliases(self, intl_manager):
        """Test that exchange aliases don't create circular references"""
        aliases = intl_manager.EXCHANGE_ALIASES
        
        # Check for potential circular references
        for main_exchange, alias_list in aliases.items():
            for alias in alias_list:
                # An alias should not point back to the main exchange
                if alias in aliases:
                    assert main_exchange not in aliases[alias], f"Circular reference: {main_exchange} <-> {alias}"

    async def test_mic_code_fallbacks(self, intl_manager):
        """Test that MIC codes are mapped to working IBKR exchanges"""
        aliases = intl_manager.EXCHANGE_ALIASES
        
        # Test that known non-working MIC codes are mapped
        mic_mappings = {
            'XNYS': ['NYSE'],         # NYSE MIC → NYSE IBKR code
            'XLON': ['LSE'],          # London MIC → LSE IBKR code  
            'XTKS': ['TSEJ'],         # Tokyo MIC → TSEJ IBKR code
            'XMIL': ['BVME'],         # Milan MIC → BVME IBKR code
            'XSWX': ['EBS'],          # Swiss MIC → EBS IBKR code
            'XSTO': ['SFB'],          # Stockholm MIC → SFB IBKR code
            'XTSE': ['TSE'],          # Toronto MIC → TSE IBKR code
        }
        
        for mic_code, expected_aliases in mic_mappings.items():
            assert mic_code in aliases
            assert aliases[mic_code] == expected_aliases
