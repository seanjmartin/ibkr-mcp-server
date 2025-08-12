"""
Unit tests for Documentation System.

Tests all documentation functionality:
- Documentation loader (8 tests)
- Category-based documentation
- Tool-specific documentation
- Documentation search
- Output formatting
- Error handling
- Caching mechanism
- Integration with MCP tools

Total: 8 comprehensive documentation tests
"""
import pytest
from unittest.mock import Mock, patch

from ibkr_mcp_server.documentation.doc_processor import DocumentationProcessor, doc_processor


@pytest.mark.unit
class TestDocumentationSystem:
    """Test documentation system (8 tests)"""
    
    @pytest.fixture
    def doc_manager(self):
        """Create documentation manager for testing"""
        return DocumentationProcessor()
    
    def test_documentation_loader(self, doc_manager):
        """Test documentation loading mechanism"""
        # Test that documentation processor can be instantiated without errors
        try:
            processor = DocumentationProcessor()
            assert processor is not None
        except Exception as e:
            pytest.fail(f"Documentation processor creation should not raise exception: {e}")
        
        # Test that the processor has expected attributes
        assert hasattr(processor, 'docs_dir')
        assert hasattr(processor, 'categories_dir')
        assert hasattr(processor, '_doc_cache')
        assert hasattr(processor, '_category_mappings')
        
        # Test that the processor has main methods
        assert hasattr(processor, 'get_documentation')
        assert callable(processor.get_documentation)
    
    def test_documentation_categories(self, doc_manager):
        """Test category-based documentation"""
        # Test forex category
        forex_docs = doc_manager.get_documentation("forex")
        assert isinstance(forex_docs, str)
        assert len(forex_docs) > 0
        
        # Test stop_loss category
        stop_loss_docs = doc_manager.get_documentation("stop_loss")
        assert isinstance(stop_loss_docs, str)
        
        # Test portfolio category
        portfolio_docs = doc_manager.get_documentation("portfolio")
        assert isinstance(portfolio_docs, str)
        
        # Test international category
        intl_docs = doc_manager.get_documentation("international")
        assert isinstance(intl_docs, str)
    
    def test_documentation_tool_specific(self, doc_manager):
        """Test tool-specific documentation"""
        # Test get_forex_rates tool
        forex_tool_docs = doc_manager.get_documentation("get_forex_rates")
        assert isinstance(forex_tool_docs, str)
        
        # Test get_market_data tool
        market_tool_docs = doc_manager.get_documentation("get_market_data")
        assert isinstance(market_tool_docs, str)
        
        # Test place_stop_loss tool
        stop_tool_docs = doc_manager.get_documentation("place_stop_loss")
        assert isinstance(stop_tool_docs, str)
    
    def test_documentation_search(self, doc_manager):
        """Test documentation search functionality"""
        # Search for forex-related content using partial matches
        search_results = doc_manager._find_partial_matches("forex")
        assert isinstance(search_results, list)
        
        # Search for stop loss content
        stop_results = doc_manager._find_partial_matches("stop")
        assert isinstance(stop_results, list)
        
        # Search for non-existent content
        empty_results = doc_manager._find_partial_matches("nonexistent_term_12345")
        assert isinstance(empty_results, list)
        assert len(empty_results) == 0
    
    def test_documentation_formatting(self, doc_manager):
        """Test documentation output formatting"""
        # Test that documentation is properly formatted
        forex_docs = doc_manager.get_documentation("forex")
        
        # Should be readable text
        assert isinstance(forex_docs, str)
        assert len(forex_docs) > 10  # Some content
        
        # Should not contain raw markup or formatting issues
        assert not forex_docs.startswith("{{")
        assert not forex_docs.endswith("}}")
    
    def test_documentation_error_handling(self, doc_manager):
        """Test documentation system error handling"""
        # Test invalid category
        invalid_docs = doc_manager.get_documentation("invalid_category_12345")
        assert isinstance(invalid_docs, str)
        assert "not found" in invalid_docs.lower() or "available" in invalid_docs.lower()
        
        # Test invalid tool
        invalid_tool_docs = doc_manager.get_documentation("invalid_tool_12345")
        assert isinstance(invalid_tool_docs, str)
        assert "not found" in invalid_tool_docs.lower() or "available" in invalid_tool_docs.lower()
        
        # Test None input (should not crash)
        try:
            none_docs = doc_manager.get_documentation("")
            assert isinstance(none_docs, str)
        except Exception as e:
            pytest.fail(f"Should handle empty input gracefully: {e}")
    
    def test_documentation_caching(self, doc_manager):
        """Test documentation caching mechanism"""
        # Test that repeated calls work consistently 
        first_call = doc_manager.get_documentation("forex")
        second_call = doc_manager.get_documentation("forex")
        
        # Should return same content (caching working)
        assert first_call == second_call
        
        # Test cache clearing works
        doc_manager._doc_cache.clear()
        third_call = doc_manager.get_documentation("forex")
        
        # Should still return same content (reloaded from source)
        assert first_call == third_call
    
    def test_documentation_integration(self, doc_manager):
        """Test integration with MCP tool system"""
        # Test that category mappings exist
        assert hasattr(doc_manager, '_category_mappings')
        assert isinstance(doc_manager._category_mappings, dict)
        
        # Test that some expected categories exist
        expected_categories = ["forex", "stop_loss", "portfolio", "international"]
        
        for category in expected_categories:
            docs = doc_manager.get_documentation(category)
            assert isinstance(docs, str)
            assert len(docs) > 10  # Should have some documentation
        
        # Test that global processor exists
        from ibkr_mcp_server.documentation.doc_processor import doc_processor
        assert doc_processor is not None
        assert isinstance(doc_processor, DocumentationProcessor)
