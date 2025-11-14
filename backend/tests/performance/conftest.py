"""
Pytest fixtures for performance tests
"""
import pytest
import sys
import os

# Add the performance tests directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Now import from test_nfr_simple
import test_nfr_simple


@pytest.fixture(scope="session")
def token():
    """
    Session-scoped fixture that provides JWT authentication token
    Logs in once and reuses the token for all tests in this session
    """
    return test_nfr_simple.login_and_get_token()
