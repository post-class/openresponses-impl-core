"""pytest common fixtures

This file is a configuration file that pytest automatically loads.
Defines fixtures shared across all tests.
"""

import os
import sys

import pytest

# Add src directory to import path (ensures compatibility during pytest execution)
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
_SRC = os.path.join(_ROOT, "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)


@pytest.fixture
def sample_create_response_body_dict():
    """Sample data for CreateResponseBody (dictionary format)"""
    return {
        "model": "gpt-4",
        "input": "Hello, world!",
        "stream": False,
        "temperature": 0.7,
        "max_output_tokens": 1000,
    }


@pytest.fixture
def sample_create_response_body_stream_dict():
    """Sample data for CreateResponseBody (for streaming)"""
    return {
        "model": "gpt-4",
        "input": "Hello, world!",
        "stream": True,
        "temperature": 0.7,
        "max_output_tokens": 1000,
    }
