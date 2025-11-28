import pytest
from streamlit.testing.v1 import AppTest

def test_app_starts():
    """Smoke test to ensure streamlit app compiles and runs without error."""
    at = AppTest.from_file("app.py")
    at.run()
    assert not at.exception