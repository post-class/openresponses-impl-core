"""Unit tests for BaseResponsesClient

Validates the interface definition of the abstract base class.
"""

import os
import sys
from abc import ABC
from collections.abc import AsyncIterator
from typing import Any

import pytest

# Add src directory to import path (for pytest execution compatibility)
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
_SRC = os.path.join(_ROOT, "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from openresponses_impl_core.client.base_responses_client import BaseResponsesClient
from openresponses_impl_core.models.openresponses_models import (
    CreateResponseBody,
    ResponseResource,
)
from openresponses_impl_core.models.response_event_types import ResponseStreamingEvent


class TestBaseResponsesClient:
    """Tests for BaseResponsesClient class"""

    def test_is_abstract_class(self):
        """Verify that BaseResponsesClient is an abstract base class"""
        assert issubclass(BaseResponsesClient, ABC)

    def test_cannot_instantiate_directly(self):
        """Verify that BaseResponsesClient cannot be instantiated directly"""
        with pytest.raises(TypeError) as exc_info:
            BaseResponsesClient()

        # Verify that the error message contains abstract method information
        assert "abstract" in str(exc_info.value).lower()
        assert "create_response" in str(exc_info.value)

    def test_has_create_response_method(self):
        """Verify that create_response method is defined"""
        assert hasattr(BaseResponsesClient, "create_response")
        assert callable(BaseResponsesClient.create_response)

    def test_create_response_is_abstract(self):
        """Verify that create_response is an abstract method"""
        method = BaseResponsesClient.create_response
        assert hasattr(method, "__isabstractmethod__")
        assert method.__isabstractmethod__ is True

    def test_create_response_signature(self):
        """Verify the signature of create_response method"""
        import inspect

        method = BaseResponsesClient.create_response
        sig = inspect.signature(method)

        # Verify parameters
        params = list(sig.parameters.keys())
        assert "self" in params
        assert "payload" in params
        assert "kwargs" in params

        # Verify payload parameter type hint (compare as string)
        payload_param = sig.parameters["payload"]
        payload_annotation_str = str(payload_param.annotation)
        assert "CreateResponseBody" in payload_annotation_str

        # Verify return type hint
        return_annotation = sig.return_annotation
        # Check as string since it's a Union type
        return_str = str(return_annotation)
        assert "ResponseResource" in return_str
        assert "AsyncIterator" in return_str
        assert "ResponseStreamingEvent" in return_str


class ConcreteResponsesClient(BaseResponsesClient):
    """Concrete class for testing (non-streaming)"""

    async def create_response(
        self, payload: CreateResponseBody, **kwargs: Any
    ) -> ResponseResource | AsyncIterator[ResponseStreamingEvent]:
        """Test implementation (non-streaming)"""
        # Return a dummy ResponseResource
        return ResponseResource(
            id="test_response_id",
            object="response",
            created_at=1234567890,
            completed_at=1234567900,
            status="completed",
            incomplete_details=None,
            model=payload.model or "gpt-4",
            previous_response_id=None,
            instructions=None,
            output=[],
            error=None,
            tools=[],
            tool_choice="auto",
            truncation="auto",
            parallel_tool_calls=True,
            text={"format": {"type": "text"}, "verbosity": None},
            top_p=1.0,
            presence_penalty=0.0,
            frequency_penalty=0.0,
            top_logprobs=0,
            temperature=payload.temperature or 1.0,
            reasoning=None,
            usage=None,
            max_output_tokens=payload.max_output_tokens,
            max_tool_calls=None,
            store=False,
            background=False,
            service_tier="default",
            metadata=None,
            safety_identifier=None,
            prompt_cache_key=None,
        )


class ConcreteStreamingResponsesClient(BaseResponsesClient):
    """Concrete class for testing (streaming)"""

    async def create_response(
        self, payload: CreateResponseBody, **kwargs: Any
    ) -> ResponseResource | AsyncIterator[ResponseStreamingEvent]:
        """Test implementation (streaming)"""

        async def event_generator():
            """Dummy event generator"""
            # Does not generate actual events, returns an empty generator
            return
            yield  # This line is not executed but necessary to be recognized as a generator

        return event_generator()


class TestConcreteImplementation:
    """Tests for concrete class implementation"""

    @pytest.mark.asyncio
    async def test_concrete_client_can_be_instantiated(self):
        """Verify that concrete class can be instantiated"""
        client = ConcreteResponsesClient()
        assert isinstance(client, BaseResponsesClient)

    @pytest.mark.asyncio
    async def test_concrete_client_create_response_non_streaming(
        self, sample_create_response_body_dict
    ):
        """Verify that non-streaming create_response of concrete class works"""
        client = ConcreteResponsesClient()
        payload = CreateResponseBody(**sample_create_response_body_dict)

        result = await client.create_response(payload)

        # Verify that ResponseResource is returned
        assert isinstance(result, ResponseResource)
        assert result.id == "test_response_id"
        assert result.model == "gpt-4"
        assert result.status == "completed"

    @pytest.mark.asyncio
    async def test_concrete_client_create_response_streaming(
        self, sample_create_response_body_stream_dict
    ):
        """Verify that streaming create_response of concrete class works"""
        client = ConcreteStreamingResponsesClient()
        payload = CreateResponseBody(**sample_create_response_body_stream_dict)

        result = await client.create_response(payload)

        # Verify that AsyncIterator is returned
        assert hasattr(result, "__aiter__")
        assert hasattr(result, "__anext__")

    @pytest.mark.asyncio
    async def test_payload_parameter_validation(self):
        """Validate payload parameter type"""
        client = ConcreteResponsesClient()

        # Pass an instance of CreateResponseBody type
        payload = CreateResponseBody(model="gpt-4", input="test")
        result = await client.create_response(payload)
        assert isinstance(result, ResponseResource)

    @pytest.mark.asyncio
    async def test_kwargs_parameter_support(self, sample_create_response_body_dict):
        """Verify that kwargs parameter is supported"""
        client = ConcreteResponsesClient()
        payload = CreateResponseBody(**sample_create_response_body_dict)

        # Verify that it works even when passing additional keyword arguments
        result = await client.create_response(payload, custom_param="test_value", another_param=123)
        assert isinstance(result, ResponseResource)
