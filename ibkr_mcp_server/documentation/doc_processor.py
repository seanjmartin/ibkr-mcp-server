"""Documentation processor for IBKR MCP tools."""

import os
from pathlib import Path
from typing import Dict, Optional, List
import re


class DocumentationProcessor:
    """Processes documentation queries and loads from individual markdown files."""
    
    def __init__(self):
        self.docs_dir = Path(__file__).parent / "tools"
        self.categories_dir = Path(__file__).parent / "categories"
        self._doc_cache = {}  # Cache loaded docs for performance
        self._category_mappings = self._load_category_mappings()
    
    def get_documentation(self, tool_or_category: str, aspect: str = "all") -> str:
        """Get documentation for a tool or category."""
        
        # Check if it's a direct tool match
        if self._is_tool_name(tool_or_category):
            return self._load_tool_documentation(tool_or_category, aspect)
        
        # Check if it's a category
        if self._is_category_name(tool_or_category):
            return self._load_category_documentation(tool_or_category, aspect)
        
        # Check for partial matches
        matches = self._find_partial_matches(tool_or_category)
        if matches:
            return self._format_search_results(tool_or_category, matches)
        
        return self._format_not_found(tool_or_category)
    
    def _is_tool_name(self, name: str) -> bool:
        """Check if a tool documentation file exists."""
        doc_file = self.docs_dir / f"{name}.md"
        return doc_file.exists()
    
    def _is_category_name(self, name: str) -> bool:
        """Check if a category documentation file exists."""
        category_file = self.categories_dir / f"{name.lower()}.md"
        return category_file.exists()
    
    def _load_tool_documentation(self, tool_name: str, aspect: str) -> str:
        """Load and parse individual tool documentation file."""
        doc_file = self.docs_dir / f"{tool_name}.md"
        
        if not doc_file.exists():
            return f"Documentation file not found for '{tool_name}'"
        
        # Cache the documentation
        if tool_name not in self._doc_cache:
            self._doc_cache[tool_name] = self._parse_markdown_doc(doc_file)
        
        return self._format_documentation(self._doc_cache[tool_name], aspect)
    
    def _load_category_documentation(self, category: str, aspect: str) -> str:
        """Load category documentation file."""
        category_file = self.categories_dir / f"{category.lower()}.md"
        
        if not category_file.exists():
            return f"Category documentation not found for '{category}'"
        
        cache_key = f"category_{category}"
        if cache_key not in self._doc_cache:
            self._doc_cache[cache_key] = self._parse_markdown_doc(category_file)
        
        return self._format_documentation(self._doc_cache[cache_key], aspect)
    
    def _parse_markdown_doc(self, file_path: Path) -> Dict:
        """Parse markdown documentation file into structured sections."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        sections = {}
        current_section = None
        current_content = []
        
        for line in content.split('\n'):
            # Check for main section headers (## Section)
            if line.startswith('## '):
                # Save previous section
                if current_section:
                    sections[current_section.lower()] = '\n'.join(current_content).strip()
                
                # Start new section
                current_section = line[3:].strip()
                current_content = []
            else:
                current_content.append(line)
        
        # Save last section
        if current_section:
            sections[current_section.lower()] = '\n'.join(current_content).strip()
        
        return sections
    
    def _format_documentation(self, sections: Dict, aspect: str) -> str:
        """Format documentation based on requested aspect."""
        if aspect == "all":
            # Return all sections formatted
            formatted_sections = []
            section_order = ['overview', 'parameters', 'examples', 'workflow', 'troubleshooting', 'related tools']
            
            for section_name in section_order:
                if section_name in sections:
                    formatted_sections.append(f"## {section_name.title()}\n{sections[section_name]}")
            
            # Add any remaining sections
            for section_name, content in sections.items():
                if section_name not in section_order:
                    formatted_sections.append(f"## {section_name.title()}\n{content}")
            
            return '\n\n'.join(formatted_sections)
        
        # Return specific aspect
        aspect_key = aspect.lower().replace('_', ' ')
        if aspect_key in sections:
            return f"## {aspect_key.title()}\n{sections[aspect_key]}"
        else:
            available = ', '.join(sections.keys())
            return f"Section '{aspect}' not found. Available sections: {available}"
    
    def _find_partial_matches(self, query: str) -> List[str]:
        """Find partial matches for tool names or categories."""
        matches = []
        query_lower = query.lower()
        
        # Check tool files
        if self.docs_dir.exists():
            for doc_file in self.docs_dir.glob("*.md"):
                tool_name = doc_file.stem
                if query_lower in tool_name.lower():
                    matches.append(tool_name)
        
        # Check category files
        if self.categories_dir.exists():
            for category_file in self.categories_dir.glob("*.md"):
                category_name = category_file.stem
                if query_lower in category_name.lower():
                    matches.append(f"{category_name} (category)")
        
        return matches
    
    def _format_search_results(self, query: str, matches: List[str]) -> str:
        """Format search results when no exact match found."""
        match_text = '\n'.join([f"• {match}" for match in matches])
        return f"# Search Results for '{query}'\n\nDid you mean one of these?\n\n{match_text}\n\nTry using the exact name with get_tool_documentation()."
    
    def _format_not_found(self, query: str) -> str:
        """Format response when no documentation found."""
        available_tools = []
        available_categories = []
        
        # Get available tools
        if self.docs_dir.exists():
            available_tools = [f.stem for f in self.docs_dir.glob("*.md")]
        
        # Get available categories
        if self.categories_dir.exists():
            available_categories = [f.stem for f in self.categories_dir.glob("*.md")]
        
        tools_text = '\n'.join([f"• {tool}" for tool in sorted(available_tools)])
        categories_text = '\n'.join([f"• {cat}" for cat in sorted(available_categories)])
        
        return f"""# Documentation Not Found

No documentation found for '{query}'.

**Available Tools:**
{tools_text}

**Available Categories:**
{categories_text}

**Usage Examples:**
• get_tool_documentation('get_forex_rates')
• get_tool_documentation('forex')
• get_tool_documentation('stop_loss', 'workflow')
"""
    
    def _load_category_mappings(self) -> Dict:
        """Load category to tool mappings."""
        return {
            "forex": ["get_forex_rates", "convert_currency"],
            "stop_loss": ["place_stop_loss", "get_stop_losses", "modify_stop_loss", "cancel_stop_loss"],
            "international": ["get_market_data", "resolve_international_symbol"],
            "portfolio": ["get_portfolio", "get_account_summary", "get_accounts", "switch_account", "get_connection_status"],
            "trading": ["place_stop_loss", "place_market_order", "place_limit_order", "cancel_order", "modify_order", "get_order_status", "place_bracket_order"],
            "order_placement": ["place_market_order", "place_limit_order", "place_bracket_order", "cancel_order", "modify_order", "get_order_status"],
            "market_data": ["get_market_data", "get_forex_rates"],
            "account": ["get_account_summary", "get_accounts", "switch_account", "get_connection_status"],
            "orders": ["place_market_order", "place_limit_order", "cancel_order", "modify_order", "get_order_status", "place_bracket_order", "get_open_orders", "get_completed_orders", "get_executions"]
        }


# Global processor instance
doc_processor = DocumentationProcessor()
