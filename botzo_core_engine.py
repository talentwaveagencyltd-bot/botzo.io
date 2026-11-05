"""
Botzo.io Core Orchestration Engine
Lightweight open-source framework for AI agent tool routing and webhook execution.
"""

import json
import logging
import time
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")
logger = logging.getLogger("botzo")


@dataclass
class Tool:
    """Represents an executable tool exposed to a Botzo Agent."""
    name: str
    description: str
    func: Callable[..., Any]
    parameters: Dict[str, str] = field(default_factory=dict)

    def execute(self, **kwargs) -> Any:
        logger.info(f"Executing tool '{self.name}' with args: {kwargs}")
        return self.func(**kwargs)

    def to_schema(self) -> Dict[str, Any]:
        """Exports the tool definition in standard JSON Schema format for LLM tool-calling."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": {
                "type": "object",
                "properties": self.parameters,
                "required": list(self.parameters.keys()),
            },
        }


class BotzoAgent:
    """
    Core agent orchestrator responsible for managing tool registries,
    processing incoming webhook payloads, and coordinating execution steps.
    """

    def __init__(self, name: str, model: str = "claude-3-7-sonnet-latest", max_retries: int = 3):
        self.name = name
        self.model = model
        self.max_retries = max_retries
        self.tools: Dict[str, Tool] = {}
        self.execution_history: List[Dict[str, Any]] = []

    def register_tool(self, description: str, parameters: Optional[Dict[str, str]] = None):
        """Decorator to register a Python function as an agent tool."""
        def decorator(func: Callable[..., Any]):
            tool_name = func.__name__
            self.tools[tool_name] = Tool(
                name=tool_name,
                description=description,
                func=func,
                parameters=parameters or {},
            )
            logger.info(f"Registered tool: {tool_name}")
            return func
        return decorator

    def list_tool_schemas(self) -> List[Dict[str, Any]]:
        """Returns structured schemas for all registered tools."""
        return [tool.to_schema() for tool in self.tools.values()]

    def invoke_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Safely invokes a registered tool with automatic retry and error capture."""
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' is not registered on agent '{self.name}'.")

        tool = self.tools[tool_name]
        attempt = 0
        while attempt < self.max_retries:
            try:
                start_time = time.time()
                result = tool.execute(**kwargs)
                duration_ms = round((time.time() - start_time) * 1000, 2)

                record = {
                    "agent": self.name,
                    "tool": tool_name,
                    "status": "success",
                    "duration_ms": duration_ms,
                    "output": result,
                }
                self.execution_history.append(record)
                return record
            except Exception as exc:
                attempt += 1
                logger.warning(f"Tool '{tool_name}' failed (attempt {attempt}/{self.max_retries}): {exc}")
                if attempt >= self.max_retries:
                    error_record = {
                        "agent": self.name,
                        "tool": tool_name,
                        "status": "error",
                        "error": str(exc),
                    }
                    self.execution_history.append(error_record)
                    return error_record
                time.sleep(0.5 * attempt)

    def run(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Primary entry point for processing a natural language instruction or webhook event.
        """
        logger.info(f"Agent '{self.name}' received task: {prompt}")
        return {
            "agent": self.name,
            "model": self.model,
            "task": prompt,
            "available_tools": list(self.tools.keys()),
            "context": context or {},
            "status": "ready_for_dispatch",
        }


if __name__ == "__main__":
    # Example standalone execution
    agent = BotzoAgent(name="botzo-core-demo")

    @agent.register_tool(
        description="Checks the health status of an external microservice.",
        parameters={"service_name": "string"},
    )
    def check_service_health(service_name: str) -> Dict[str, Any]:
        return {"service": service_name, "status": "operational", "uptime": "99.98%"}

    output = agent.invoke_tool("check_service_health", service_name="webhook-gateway")
    print(json.dumps(output, indent=2))