import json
from typing import Any, Dict

import pytest

from domain_adaptation import mortgage_domain_adapter as adapter_module
from domain_adaptation.mortgage_domain_adapter import MortgageDomainAdapter


class _FakeIntegration:
    """Lightweight mock for L9ToThIntegration to supply predictable payloads."""

    def _fake_response(self, label: str) -> Dict[str, Any]:
        return {
            "status": "success",
            "label": label,
            "reasoning_results": {
                "deductive": {
                    "reasoning_type": "deductive",
                    "confidence_score": 0.88,
                    "reasoning_graph": {
                        "nodes": [
                            {"id": 0, "text": "Assess borrower", "confidence": 0.91}
                        ],
                        "edges": {(0, 1)},
                        "summary": [("Assess borrower", 0.91)]
                    }
                }
            },
            "metadata": {"tuple_payload": ("alpha", "beta")}
        }

    async def enhance_pattern_detection(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._fake_response("pattern")

    async def enhance_error_correction(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._fake_response("error")

    async def enhance_decision_making(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._fake_response("decision")


@pytest.mark.asyncio
async def test_mortgage_domain_adapter_adapt_l9_system_serializable(monkeypatch: pytest.MonkeyPatch) -> None:
    """MortgageDomainAdapter should return a JSON-serializable structure after adaptation."""

    monkeypatch.setattr(adapter_module, "L9ToThIntegration", _FakeIntegration)

    adapter = MortgageDomainAdapter()
    result = await adapter.adapt_l9_system()

    # Should be able to serialize the entire structure without TypeErrors.
    serialized = json.dumps(result)
    assert isinstance(serialized, str)

    # Adaptation history should mirror the serialized-safe result.
    assert adapter.adaptation_history[0] == result

    graph_payload = result["adaptations"]["pattern_detection"]["toth_analysis"]["reasoning_results"]["deductive"]["reasoning_graph"]
    assert isinstance(graph_payload["edges"], list)
    assert all(isinstance(edge, list) for edge in graph_payload["edges"])


class StubIntegration:
    """Simple async stub for the ToTh integration used by the mortgage adapter."""

    def __init__(self):
        self.calls = []

    async def enhance_pattern_detection(self, *, pattern_data: str, context: str):
        self.calls.append(("pattern", pattern_data, context))
        return {"source": "stub", "operation": "pattern"}

    async def enhance_error_correction(self, *, error_context: str, error_details: str):
        self.calls.append(("error", error_context, error_details))
        return {"source": "stub", "operation": "error"}

    async def enhance_decision_making(self, *, decision_context: str, options):
        self.calls.append(("decision", decision_context, tuple(options)))
        return {"source": "stub", "operation": "decision"}


@pytest.mark.asyncio
async def test_adapt_l9_system_with_stub_integration():
    """The adapter should use the injected integration for all adaptation steps."""

    stub_integration = StubIntegration()
    adapter = MortgageDomainAdapter(integration=stub_integration)

    result = await adapter.adapt_l9_system()

    assert result["status"] == "success"
    assert result["adaptations"]["pattern_detection"]["toth_analysis"] == {"source": "stub", "operation": "pattern"}
    assert result["adaptations"]["error_correction"]["toth_analysis"] == {"source": "stub", "operation": "error"}
    assert result["adaptations"]["decision_making"]["toth_analysis"] == {"source": "stub", "operation": "decision"}

    recorded_operations = [call[0] for call in stub_integration.calls]
    assert recorded_operations.count("pattern") == 1
    assert recorded_operations.count("error") == 1
    assert recorded_operations.count("decision") == 1


@pytest.mark.asyncio
async def test_helper_coroutines_are_mock_friendly():
    """Helper coroutines should work with lightweight mocked integrations."""

    stub_integration = StubIntegration()
    adapter = MortgageDomainAdapter(integration=stub_integration)

    pattern_result = await adapter._adapt_pattern_detection()
    error_result = await adapter._adapt_error_correction()
    decision_result = await adapter._adapt_decision_making()

    assert pattern_result["toth_analysis"] == {"source": "stub", "operation": "pattern"}
    assert error_result["toth_analysis"] == {"source": "stub", "operation": "error"}
    assert decision_result["toth_analysis"] == {"source": "stub", "operation": "decision"}
