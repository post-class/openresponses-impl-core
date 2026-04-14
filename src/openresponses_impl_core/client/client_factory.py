from openresponses_impl_core.client.base_responses_client import BaseResponsesClient


class ClientFactory:
    """Factory class for creating LLM clients"""

    @staticmethod
    def create_client(
        *,
        vendor: str,
        model: str | None = None,
        deployment_platform: str | None = None,
        api_key: str | None = None,
        endpoint: str | None = None,
        api_version: str | None = None,
    ) -> BaseResponsesClient:
        """Create an LLM client corresponding to the specified request.

        Args:
            vendor: Vendor name (e.g., "openai", "google")
            model: Model name (e.g., "gpt-4", "gemini-2.5-pro")
            deployment_platform: Deployment platform (e.g., "azure", "openai", "aws")
            api_key: API key
            endpoint: Endpoint URL (used for Azure OpenAI)
            api_version: API version (used for Azure OpenAI)

            Example: For Azure OpenAI gpt-4
            vendor="openai"
            model="gpt-4"
            deployment_platform="azure"
            api_key="your-azure-api-key"
            endpoint="https://your-resource.openai.azure.com"
            api_version="2024-10-21"

            Example: For OpenAI official gpt-4
            vendor="openai"
            model="gpt-4"
            deployment_platform="openai"
            api_key="your-openai-api-key"
            endpoint=""
            api_version=""

            Example: For Google Gemini
            vendor="google"
            model="gemini-2.5-pro"
            api_key="your-google-api-key"

        Returns:
            Client instance

        Raises:
            ValueError: When an unsupported vendor/platform combination is specified

        """

        # For Azure OpenAI
        if vendor == "openai" and deployment_platform == "azure":
            from openresponses_impl_client_openai.client.openai_responses_client import (
                OpenAIResponsesClient,
            )

            return OpenAIResponsesClient(
                vendor="azure",
                model=model or "",
                azure_openai_endpoint=endpoint or "",
                azure_openai_api_key=api_key or "",
                azure_openai_api_version=api_version or "2024-10-21",
            )

        # For OpenAI official (deployment_platform is "openai" or empty)
        if vendor == "openai" and (deployment_platform == "openai" or not deployment_platform):
            from openresponses_impl_client_openai.client.openai_responses_client import (
                OpenAIResponsesClient,
            )

            return OpenAIResponsesClient(
                vendor="openai",
                model=model or "",
                openai_api_key=api_key or "",
            )

        # For Google Gemini
        if vendor == "google":
            from openresponses_impl_client_google.client.gemini_responses_client import (
                GeminiResponsesClient,
            )

            return GeminiResponsesClient(
                model=model or "",
                google_api_key=api_key,
            )

        raise ValueError(
            f"Unsupported vendor/deployment_platform combination: "
            f"vendor={vendor}, deployment_platform={deployment_platform}. "
            f"Supported: vendor=openai + deployment_platform=azure or "
            f"vendor=openai + deployment_platform=openai/empty or "
            f"vendor=google"
        )
