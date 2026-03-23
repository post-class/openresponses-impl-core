from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import Any

from openresponses_impl_core.models.openresponses_models import CreateResponseBody, ResponseResource
from openresponses_impl_core.models.response_event_types import ResponseStreamingEvent


class BaseResponsesClient(ABC):
    """Base class for OpenAI Responses API client (type-safe version)

    Defines the interface for the create_response method.
    Ensures type safety by using CreateResponseBody type.
    Behavior is controlled by the payload.stream field.
    """

    @abstractmethod
    async def create_response(
        self, payload: CreateResponseBody, **kwargs: Any
    ) -> ResponseResource | AsyncIterator[ResponseStreamingEvent]:
        """Create a response based on the stream field in the payload

        Behaves similarly to OpenAI AsyncOpenAI.responses.create, but
        accepts all parameters as a CreateResponseBody type.

        Args:
            payload: Request payload (CreateResponseBody type)
                    - stream: bool | None - Specifies streaming mode
                      - False/None (default): Non-streaming → Returns ResponseResource
                      - True: Streaming → Returns AsyncIterator[ResponseStreamingEvent]
                    - model: str | None - Model name (required)
                    - input: str | list - Input data
                    - instructions: str | None - System message
                    - Other parameters
            **kwargs: Additional parameters (implementation-dependent)

        Returns:
            When payload.stream=False/None: ResponseResource
            When payload.stream=True: AsyncIterator[ResponseStreamingEvent]

        Example:
            # Non-streaming
            payload = CreateResponseBody(
                stream=False,
                model="gpt-4",
                input="Hello"
            )
            response = await client.create_response(payload)

            # Streaming
            payload = CreateResponseBody(
                stream=True,
                model="gpt-4",
                input="Hello"
            )
            event_stream = await client.create_response(payload)
            async for event in event_stream:
                print(event)

        """
        ...
