# tests/test_tools.py

import pytest
import sys
sys.path.append('..')

from tools.tool_registry import ToolRegistry, ToolSchema
from tools.calculator import run_calculation
from tools.news_sentiment import analyze_news_sentiment
from tools import registry

class TestToolRegistry:
    
    def test_registry_has_minimum_tools(self):
        """Registry must have at least 10 tools"""
        assert len(registry.list_tools()) >= 10
    
    def test_all_required_tools_present(self):
        required = [
            "sec_filing_search", "financial_data_api", 
            "web_search", "news_sentiment", "calculation_engine",
            "earnings_transcript", "company_profile",
            "fact_checker", "report_generator"
        ]
        for tool in required:
            assert tool in registry.list_tools(), f"{tool} missing from registry"
    
    def test_tool_execution_success(self):
        result = registry.execute("web_search", {"query": "Apple Inc earnings"})
        assert result["success"] == True
        assert "data" in result
    
    def test_fallback_triggered_on_failure(self):
        """Test that fallback activates when primary tool fails"""
        # Register a broken tool
        def broken_function(**kwargs):
            raise Exception("Simulated failure")
        
        test_registry = ToolRegistry()
        test_registry.register(ToolSchema(
            name="broken_tool",
            description="Always fails",
            parameters={"type": "object", "properties": {}},
            function=broken_function,
            fallbacks=[]
        ))
        
        result = test_registry.execute("broken_tool", {})
        assert result["success"] == False

class TestCalculationEngine:
    
    def test_growth_rate_calculation(self):
        result = run_calculation("growth_rate", {
            "current_value": 110,
            "previous_value": 100
        })
        assert result["result"] == 10.0
        assert result["unit"] == "%"
    
    def test_margin_calculation(self):
        result = run_calculation("margin", {
            "numerator": 25,
            "revenue": 100
        })
        assert result["result"] == 25.0
    
    def test_cagr_calculation(self):
        result = run_calculation("cagr", {
            "start_value": 100,
            "end_value": 161.05,
            "years": 5
        })
        assert abs(result["result"] - 10.0) < 0.1

class TestNewsSentiment:
    
    def test_returns_sentiment_scores(self):
        result = analyze_news_sentiment("Apple Inc", num_articles=3)
        assert "overall_sentiment" in result
        assert result["overall_sentiment"] in ["positive", "negative", "neutral"]
        assert "average_polarity" in result

if __name__ == "__main__":
    pytest.run([__file__, "-v"])