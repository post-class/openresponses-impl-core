"""Unit tests for ClientFactory

Validates the behavior of the LLM client factory.
"""

import os
import sys
from types import ModuleType
from unittest.mock import MagicMock, patch

import pytest

# Add src directory to import path (for pytest execution compatibility)
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
_SRC = os.path.join(_ROOT, "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from openresponses_impl_core.client.base_responses_client import BaseResponsesClient
from openresponses_impl_core.client.client_factory import ClientFactory


# Create mock module for testing
def _create_mock_openai_module():
    """Create openresponses_impl_client_openai module for testing"""
    if "openresponses_impl_client_openai" not in sys.modules:
        mock_module = ModuleType("openresponses_impl_client_openai")
        mock_client_module = ModuleType("openresponses_impl_client_openai.client")
        mock_openai_responses_client_module = ModuleType(
            "openresponses_impl_client_openai.client.openai_responses_client"
        )

        # Build module hierarchy
        sys.modules["openresponses_impl_client_openai"] = mock_module
        sys.modules["openresponses_impl_client_openai.client"] = mock_client_module
        sys.modules["openresponses_impl_client_openai.client.openai_responses_client"] = (
            mock_openai_responses_client_module
        )

        # Create mock for OpenAIResponsesClient class
        mock_openai_responses_client_module.OpenAIResponsesClient = MagicMock()


def _create_mock_google_module():
    """Create openresponses_impl_client_google module for testing"""
    if "openresponses_impl_client_google" not in sys.modules:
        mock_module = ModuleType("openresponses_impl_client_google")
        mock_client_module = ModuleType("openresponses_impl_client_google.client")
        mock_gemini_responses_client_module = ModuleType(
            "openresponses_impl_client_google.client.gemini_responses_client"
        )

        # Build module hierarchy
        sys.modules["openresponses_impl_client_google"] = mock_module
        sys.modules["openresponses_impl_client_google.client"] = mock_client_module
        sys.modules["openresponses_impl_client_google.client.gemini_responses_client"] = (
            mock_gemini_responses_client_module
        )

        # Create mock for GeminiResponsesClient class
        mock_gemini_responses_client_module.GeminiResponsesClient = MagicMock()


# Create mock module before starting tests
_create_mock_openai_module()
_create_mock_google_module()


class TestClientFactory:
    """Tests for ClientFactory class"""

    def test_factory_has_create_client_method(self):
        """Verify that create_client method exists"""
        assert hasattr(ClientFactory, "create_client")
        assert callable(ClientFactory.create_client)

    def test_create_client_is_static_method(self):
        """Verify that create_client is a static method"""
        import inspect

        method = ClientFactory.create_client
        assert isinstance(inspect.getattr_static(ClientFactory, "create_client"), staticmethod)

    @patch("openresponses_impl_client_openai.client.openai_responses_client.OpenAIResponsesClient")
    def test_create_openai_client(self, mock_openai_client_class):
        """Test OpenAI official client creation"""
        # Setup mock
        mock_client_instance = MagicMock(spec=BaseResponsesClient)
        mock_openai_client_class.return_value = mock_client_instance

        # Create OpenAI official client
        result = ClientFactory.create_client(
            vendor="openai",
            model="gpt-4",
            deployment_platform="openai",
            api_key="test-api-key",
        )

        # Verify that OpenAIResponsesClient was called with correct arguments
        mock_openai_client_class.assert_called_once_with(
            vendor="openai",
            model="gpt-4",
            openai_api_key="test-api-key",
        )

        # Verify that the return value is the mock instance
        assert result == mock_client_instance

    @patch("openresponses_impl_client_openai.client.openai_responses_client.OpenAIResponsesClient")
    def test_create_openai_client_without_deployment_platform(self, mock_openai_client_class):
        """Test OpenAI client creation when deployment_platform is omitted"""
        # Setup mock
        mock_client_instance = MagicMock(spec=BaseResponsesClient)
        mock_openai_client_class.return_value = mock_client_instance

        # Omit deployment_platform (defaults to OpenAI official)
        result = ClientFactory.create_client(
            vendor="openai",
            model="gpt-4",
            api_key="test-api-key",
        )

        # Verify that OpenAIResponsesClient was called with correct arguments
        mock_openai_client_class.assert_called_once_with(
            vendor="openai",
            model="gpt-4",
            openai_api_key="test-api-key",
        )

        assert result == mock_client_instance

    @patch("openresponses_impl_client_openai.client.openai_responses_client.OpenAIResponsesClient")
    def test_create_azure_openai_client(self, mock_openai_client_class):
        """Test Azure OpenAI client creation"""
        # Setup mock
        mock_client_instance = MagicMock(spec=BaseResponsesClient)
        mock_openai_client_class.return_value = mock_client_instance

        # Create Azure OpenAI client
        result = ClientFactory.create_client(
            vendor="openai",
            model="gpt-4",
            deployment_platform="azure",
            api_key="test-azure-api-key",
            endpoint="https://test-resource.openai.azure.com",
            api_version="2024-10-21",
        )

        # Verify that OpenAIResponsesClient was called with correct arguments
        mock_openai_client_class.assert_called_once_with(
            vendor="azure",
            model="gpt-4",
            azure_openai_endpoint="https://test-resource.openai.azure.com",
            azure_openai_api_key="test-azure-api-key",
            azure_openai_api_version="2024-10-21",
        )

        assert result == mock_client_instance

    @patch("openresponses_impl_client_openai.client.openai_responses_client.OpenAIResponsesClient")
    def test_create_azure_openai_client_with_default_api_version(self, mock_openai_client_class):
        """Test Azure OpenAI client creation (with default api_version)"""
        # Setup mock
        mock_client_instance = MagicMock(spec=BaseResponsesClient)
        mock_openai_client_class.return_value = mock_client_instance

        # Omit api_version
        result = ClientFactory.create_client(
            vendor="openai",
            model="gpt-4",
            deployment_platform="azure",
            api_key="test-azure-api-key",
            endpoint="https://test-resource.openai.azure.com",
        )

        # Verify that default api_version is used
        mock_openai_client_class.assert_called_once_with(
            vendor="azure",
            model="gpt-4",
            azure_openai_endpoint="https://test-resource.openai.azure.com",
            azure_openai_api_key="test-azure-api-key",
            azure_openai_api_version="2024-10-21",
        )

        assert result == mock_client_instance

    @patch("openresponses_impl_client_google.client.gemini_responses_client.GeminiResponsesClient")
    def test_create_google_client(self, mock_gemini_client_class):
        """Test Google Gemini client creation"""
        # Setup mock
        mock_client_instance = MagicMock(spec=BaseResponsesClient)
        mock_gemini_client_class.return_value = mock_client_instance

        result = ClientFactory.create_client(
            vendor="google",
            model="gemini-2.5-pro",
            deployment_platform="vertex-ai",
            api_key="test-google-api-key",
        )

        mock_gemini_client_class.assert_called_once_with(
            model="gemini-2.5-pro",
            google_api_key="test-google-api-key",
        )

        assert result == mock_client_instance

    @patch("openresponses_impl_client_google.client.gemini_responses_client.GeminiResponsesClient")
    def test_create_google_client_without_deployment_platform(self, mock_gemini_client_class):
        """Test Google Gemini client creation when deployment_platform is omitted"""
        # Setup mock
        mock_client_instance = MagicMock(spec=BaseResponsesClient)
        mock_gemini_client_class.return_value = mock_client_instance

        result = ClientFactory.create_client(
            vendor="google",
            model="gemini-2.5-pro",
            api_key="test-google-api-key",
        )

        mock_gemini_client_class.assert_called_once_with(
            model="gemini-2.5-pro",
            google_api_key="test-google-api-key",
        )

        assert result == mock_client_instance

    def test_unsupported_vendor_raises_error(self):
        """Verify that ValueError is raised for unsupported vendor"""
        with pytest.raises(ValueError) as exc_info:
            ClientFactory.create_client(
                vendor="anthropic",  # Unsupported
                model="claude-3",
                deployment_platform="aws",
                api_key="test-api-key",
            )

        error_message = str(exc_info.value)
        assert "Unsupported" in error_message
        assert "vendor" in error_message
        assert "anthropic" in error_message

    def test_unsupported_deployment_platform_raises_error(self):
        """Verify that ValueError is raised for unsupported deployment_platform"""
        with pytest.raises(ValueError) as exc_info:
            ClientFactory.create_client(
                vendor="openai",
                model="gpt-4",
                deployment_platform="aws",  # Unsupported
                api_key="test-api-key",
            )

        error_message = str(exc_info.value)
        assert "Unsupported" in error_message
        assert "deployment_platform" in error_message
        assert "aws" in error_message

    @patch("openresponses_impl_client_openai.client.openai_responses_client.OpenAIResponsesClient")
    def test_create_client_with_none_values(self, mock_openai_client_class):
        """Verify that None values are handled appropriately"""
        # Setup mock
        mock_client_instance = MagicMock(spec=BaseResponsesClient)
        mock_openai_client_class.return_value = mock_client_instance

        # Pass None for model and api_key
        result = ClientFactory.create_client(
            vendor="openai",
            model=None,
            deployment_platform="openai",
            api_key=None,
        )

        # Verify that they are converted to empty strings
        mock_openai_client_class.assert_called_once_with(
            vendor="openai",
            model="",
            openai_api_key="",
        )

        assert result == mock_client_instance

    @patch("openresponses_impl_client_openai.client.openai_responses_client.OpenAIResponsesClient")
    def test_create_azure_client_with_none_values(self, mock_openai_client_class):
        """Verify that None values are handled appropriately for Azure OpenAI"""
        # Setup mock
        mock_client_instance = MagicMock(spec=BaseResponsesClient)
        mock_openai_client_class.return_value = mock_client_instance

        # Pass None for endpoint, api_key, api_version
        result = ClientFactory.create_client(
            vendor="openai",
            model=None,
            deployment_platform="azure",
            api_key=None,
            endpoint=None,
            api_version=None,
        )

        # Verify that they are converted to empty strings or default values
        mock_openai_client_class.assert_called_once_with(
            vendor="azure",
            model="",
            azure_openai_endpoint="",
            azure_openai_api_key="",
            azure_openai_api_version="2024-10-21",
        )

        assert result == mock_client_instance

    @patch("openresponses_impl_client_google.client.gemini_responses_client.GeminiResponsesClient")
    def test_create_google_client_with_none_values(self, mock_gemini_client_class):
        """Verify that None values are handled appropriately for Google Gemini"""
        # Setup mock
        mock_client_instance = MagicMock(spec=BaseResponsesClient)
        mock_gemini_client_class.return_value = mock_client_instance

        result = ClientFactory.create_client(
            vendor="google",
            model=None,
            deployment_platform=None,
            api_key=None,
        )

        mock_gemini_client_class.assert_called_once_with(
            model="",
            google_api_key=None,
        )

        assert result == mock_client_instance


class TestClientFactoryIntegration:
    """Integration tests for ClientFactory (including actual imports)"""

    @patch("openresponses_impl_client_openai.client.openai_responses_client.OpenAIResponsesClient")
    def test_openai_client_import_path(self, mock_openai_client_class):
        """Verify that the import path for OpenAIResponsesClient is correct"""
        # Setup mock
        mock_client_instance = MagicMock(spec=BaseResponsesClient)
        mock_openai_client_class.return_value = mock_client_instance

        # Verify that mock module is imported correctly and client is created
        result = ClientFactory.create_client(
            vendor="openai",
            model="gpt-4",
            deployment_platform="openai",
            api_key="test-api-key",
        )

        # Verify that OpenAIResponsesClient was called
        mock_openai_client_class.assert_called_once()
        assert result == mock_client_instance

    @patch("openresponses_impl_client_google.client.gemini_responses_client.GeminiResponsesClient")
    def test_google_client_import_path(self, mock_gemini_client_class):
        """Verify that the import path for GeminiResponsesClient is correct"""
        # Setup mock
        mock_client_instance = MagicMock(spec=BaseResponsesClient)
        mock_gemini_client_class.return_value = mock_client_instance

        result = ClientFactory.create_client(
            vendor="google",
            model="gemini-2.5-pro",
            api_key="test-google-api-key",
        )

        mock_gemini_client_class.assert_called_once()
        assert result == mock_client_instance


class TestClientFactoryEdgeCases:
    """Edge case tests for ClientFactory"""

    def test_empty_string_vendor(self):
        """Verify that error is raised for empty string vendor"""
        with pytest.raises(ValueError) as exc_info:
            ClientFactory.create_client(
                vendor="",
                model="gpt-4",
                deployment_platform="openai",
                api_key="test-api-key",
            )

        assert "Unsupported" in str(exc_info.value)

    def test_case_sensitive_vendor(self):
        """Verify that vendor is case-sensitive"""
        with pytest.raises(ValueError) as exc_info:
            ClientFactory.create_client(
                vendor="OpenAI",  # Uppercase
                model="gpt-4",
                deployment_platform="openai",
                api_key="test-api-key",
            )

        assert "Unsupported" in str(exc_info.value)

    def test_case_sensitive_deployment_platform(self):
        """Verify that deployment_platform is case-sensitive"""
        with pytest.raises(ValueError) as exc_info:
            ClientFactory.create_client(
                vendor="openai",
                model="gpt-4",
                deployment_platform="Azure",  # Uppercase
                api_key="test-api-key",
            )

        assert "Unsupported" in str(exc_info.value)
