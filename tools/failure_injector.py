import random
from tools import registry as base_registry

class FailureInjectedRegistry:
    def __init__(self, real_registry, failure_rate=0.5, affected_tools=None):
        self.real_registry = real_registry
        self.failure_rate = failure_rate
        self.affected_tools = affected_tools or [
            "financial_data_api",
            "sec_filing_search"
        ]
        self.injection_log = []

    def execute(self, tool_name, params):
        should_fail = (
            tool_name in self.affected_tools
            and random.random() < self.failure_rate
        )
        if should_fail:
            self.injection_log.append({"tool": tool_name, "params": params})
            return {
                "success": False,
                "error": f"[SIMULATED] {tool_name} intermittent failure",
                "report_note": (
                    f"Data from {tool_name} unavailable due to intermittent "
                    f"API failure. Report based on fallback sources."
                )
            }
        return self.real_registry.execute(tool_name, params)

    def get_tools_for_llm(self):
        return self.real_registry.get_tools_for_llm()

    def get_injection_summary(self):
        by_tool = {}
        for entry in self.injection_log:
            by_tool[entry["tool"]] = by_tool.get(entry["tool"], 0) + 1
        return {"total_injected": len(self.injection_log), "by_tool": by_tool}
