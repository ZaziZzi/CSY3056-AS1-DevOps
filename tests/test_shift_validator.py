from src.shift_validator import validate_shift
import pytest


def test_valid_shift():
    result = validate_shift(8, 30, 4, "staff")
    assert result == "VALID"


def test_high_risk_shift():
    result = validate_shift(10, 30, 7, "manager")
    assert result == "HIGH_RISK"


def test_rejected_shift():
    result = validate_shift(15, 30, 2, "staff")
    assert result == "REJECTED"


def test_warning_shift():
    result = validate_shift(8, 10, 2, "staff")
    assert result == "WARNING"


def test_invalid_role():
    with pytest.raises(ValueError):
        validate_shift(8, 30, 2, "guest")


def test_negative_values():
    with pytest.raises(ValueError):
        validate_shift(-1, 30, 2, "staff")