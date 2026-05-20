"""
Test Suite for Shift Validator Module

Comprehensive test coverage for workforce scheduling validation engine.
Tests include valid scenarios, invalid scenarios, edge cases, and business rule enforcement.
"""

import pytest
from src.shift_validator import validate_shift


# ============================================================================
# Valid Scenario Tests
# ============================================================================


def test_valid_day_shift_staff():
    """Test valid day shift for staff member."""
    result = validate_shift("John Doe", 25, 8, "day", "staff")
    assert result["valid"] is True
    assert len(result["errors"]) == 0
    assert len(result["warnings"]) == 0


def test_valid_evening_shift_manager():
    """Test valid evening shift for manager."""
    result = validate_shift("Jane Smith", 30, 8, "evening", "manager")
    assert result["valid"] is True
    assert len(result["errors"]) == 0
    assert len(result["warnings"]) == 0


def test_valid_night_shift_adult():
    """Test valid night shift for adult employee."""
    result = validate_shift("Bob Johnson", 35, 8, "night", "supervisor")
    assert result["valid"] is True
    assert len(result["errors"]) == 0
    assert len(result["warnings"]) == 0


def test_valid_maximum_shift_hours():
    """Test valid shift at maximum allowed hours (12 hours)."""
    result = validate_shift("Alice Brown", 28, 12, "day", "staff")
    assert result["valid"] is True
    assert len(result["errors"]) == 0


def test_valid_minimum_shift_hours():
    """Test valid shift with minimal hours."""
    result = validate_shift("Charlie Davis", 22, 0.5, "day", "staff")
    assert result["valid"] is True
    assert len(result["errors"]) == 0


def test_valid_all_roles():
    """Test that all valid roles are accepted."""
    roles = ["staff", "supervisor", "manager"]
    for role in roles:
        result = validate_shift("Test Employee", 25, 8, "day", role)
        assert result["valid"] is True, f"Role '{role}' should be valid"


def test_valid_all_shift_types():
    """Test that all valid shift types are accepted."""
    shift_types = ["day", "evening", "night"]
    for shift_type in shift_types:
        result = validate_shift("Test Employee", 25, 8, shift_type, "staff")
        assert result["valid"] is True, f"Shift type '{shift_type}' should be valid"


def test_valid_with_adequate_rest_period():
    """Test shift is valid with adequate rest between consecutive shifts."""
    result = validate_shift("Employee", 25, 8, "day", "staff", rest_hours_since_last_shift=10)
    assert result["valid"] is True
    assert len(result["errors"]) == 0


# ============================================================================
# Invalid Scenario Tests - Employee Name Validation
# ============================================================================


def test_empty_name():
    """Test that empty name is rejected."""
    result = validate_shift("", 25, 8, "day", "staff")
    assert result["valid"] is False
    assert "Employee name cannot be empty" in result["errors"]


def test_whitespace_only_name():
    """Test that whitespace-only name is rejected."""
    result = validate_shift("   ", 25, 8, "day", "staff")
    assert result["valid"] is False
    assert "Employee name cannot be empty" in result["errors"]


def test_none_name():
    """Test that None name is rejected."""
    result = validate_shift(None, 25, 8, "day", "staff")
    assert result["valid"] is False
    assert "Employee name cannot be empty" in result["errors"]


# ============================================================================
# Invalid Scenario Tests - Shift Hours Validation
# ============================================================================


def test_negative_shift_hours():
    """Test that negative shift hours are rejected."""
    result = validate_shift("Employee", 25, -1, "day", "staff")
    assert result["valid"] is False
    assert "Shift hours cannot be negative" in result["errors"]


def test_shift_hours_exceed_maximum():
    """Test that shift hours exceeding 12 are rejected."""
    result = validate_shift("Employee", 25, 13, "day", "staff")
    assert result["valid"] is False
    assert "Shift hours cannot exceed 12 hours" in result["errors"]


def test_shift_hours_far_exceed_maximum():
    """Test that significantly over-limit shifts are rejected."""
    result = validate_shift("Employee", 25, 20, "day", "staff")
    assert result["valid"] is False
    assert "Shift hours cannot exceed 12 hours" in result["errors"]


# ============================================================================
# Invalid Scenario Tests - Shift Type Validation
# ============================================================================


def test_invalid_shift_type_lowercase():
    """Test that invalid shift type is rejected."""
    result = validate_shift("Employee", 25, 8, "afternoon", "staff")
    assert result["valid"] is False
    assert any("Invalid shift type" in error for error in result["errors"])


def test_invalid_shift_type_typo():
    """Test that misspelled shift type is rejected."""
    result = validate_shift("Employee", 25, 8, "nite", "staff")
    assert result["valid"] is False
    assert any("Invalid shift type" in error for error in result["errors"])


def test_invalid_shift_type_empty():
    """Test that empty shift type is rejected."""
    result = validate_shift("Employee", 25, 8, "", "staff")
    assert result["valid"] is False
    assert any("Invalid shift type" in error for error in result["errors"])


# ============================================================================
# Invalid Scenario Tests - Role Validation
# ============================================================================


def test_invalid_role_admin():
    """Test that 'admin' role is rejected (not in valid roles)."""
    result = validate_shift("Employee", 25, 8, "day", "admin")
    assert result["valid"] is False
    assert any("Invalid employee role" in error for error in result["errors"])


def test_invalid_role_guest():
    """Test that 'guest' role is rejected."""
    result = validate_shift("Employee", 25, 8, "day", "guest")
    assert result["valid"] is False
    assert any("Invalid employee role" in error for error in result["errors"])


def test_invalid_role_empty():
    """Test that empty role is rejected."""
    result = validate_shift("Employee", 25, 8, "day", "")
    assert result["valid"] is False
    assert any("Invalid employee role" in error for error in result["errors"])


def test_invalid_role_case_sensitivity():
    """Test that role validation is case-sensitive."""
    result = validate_shift("Employee", 25, 8, "day", "STAFF")
    assert result["valid"] is False
    assert any("Invalid employee role" in error for error in result["errors"])


# ============================================================================
# Business Rule Tests - Underage Night Shift Restriction
# ============================================================================


def test_minor_cannot_work_night_shift():
    """Test that employees under 18 cannot work night shifts."""
    result = validate_shift("Young Worker", 17, 8, "night", "staff")
    assert result["valid"] is False
    assert "Employees under 18 cannot work night shifts" in result["errors"]


def test_minor_can_work_day_shift():
    """Test that employees under 18 can work day shifts."""
    result = validate_shift("Young Worker", 17, 8, "day", "staff")
    assert result["valid"] is True
    assert "Employees under 18 cannot work night shifts" not in result["errors"]


def test_minor_can_work_evening_shift():
    """Test that employees under 18 can work evening shifts."""
    result = validate_shift("Young Worker", 17, 8, "evening", "staff")
    assert result["valid"] is True
    assert "Employees under 18 cannot work night shifts" not in result["errors"]


def test_exactly_18_can_work_night():
    """Test that employees exactly 18 years old can work night shifts."""
    result = validate_shift("Eighteen", 18, 8, "night", "staff")
    assert result["valid"] is True
    assert "Employees under 18 cannot work night shifts" not in result["errors"]


def test_minor_17_night_shift_rejection():
    """Test that 17-year-old night shift is rejected."""
    result = validate_shift("Minor", 17, 8, "night", "supervisor")
    assert result["valid"] is False
    assert "Employees under 18 cannot work night shifts" in result["errors"]


# ============================================================================
# Business Rule Tests - Consecutive Shift Rest Period
# ============================================================================


def test_insufficient_rest_period():
    """Test that shifts with insufficient rest are rejected."""
    result = validate_shift("Employee", 25, 8, "day", "staff", rest_hours_since_last_shift=4)
    assert result["valid"] is False
    assert any("Insufficient rest period" in error for error in result["errors"])


def test_minimum_rest_period_exactly_8_hours():
    """Test that exactly 8 hours rest is accepted."""
    result = validate_shift("Employee", 25, 8, "day", "staff", rest_hours_since_last_shift=8)
    assert result["valid"] is True
    assert len(result["errors"]) == 0


def test_just_below_minimum_rest_period():
    """Test that 7.9 hours rest is rejected (below 8-hour minimum)."""
    result = validate_shift("Employee", 25, 8, "day", "staff", rest_hours_since_last_shift=7.9)
    assert result["valid"] is False
    assert any("Insufficient rest period" in error for error in result["errors"])


def test_adequate_rest_period():
    """Test that 12 hours rest is accepted."""
    result = validate_shift("Employee", 25, 8, "day", "staff", rest_hours_since_last_shift=12)
    assert result["valid"] is True
    assert len(result["errors"]) == 0


def test_first_shift_no_rest_tracking():
    """Test that zero rest hours (default) doesn't cause rejection (first shift scenario)."""
    result = validate_shift("Employee", 25, 8, "day", "staff", rest_hours_since_last_shift=0)
    # Zero rest hours indicates first shift, not a consecutive shift, so no error
    assert result["valid"] is True
    assert len(result["errors"]) == 0


# ============================================================================
# Overtime Warning Tests
# ============================================================================


def test_overtime_warning_10_plus_hours():
    """Test that shifts over 10 hours generate overtime warning."""
    result = validate_shift("Employee", 25, 10.5, "day", "staff")
    assert result["valid"] is True
    assert len(result["errors"]) == 0
    assert any("Overtime warning" in warning for warning in result["warnings"])


def test_overtime_warning_exactly_11_hours():
    """Test that 11-hour shift generates overtime warning."""
    result = validate_shift("Employee", 25, 11, "day", "staff")
    assert result["valid"] is True
    assert any("Overtime warning" in warning for warning in result["warnings"])


def test_overtime_warning_maximum_12_hours():
    """Test that 12-hour shift generates overtime warning."""
    result = validate_shift("Employee", 25, 12, "day", "staff")
    assert result["valid"] is True
    assert any("Overtime warning" in warning for warning in result["warnings"])


def test_no_overtime_warning_10_hours():
    """Test that exactly 10-hour shift does not generate warning."""
    result = validate_shift("Employee", 25, 10, "day", "staff")
    assert result["valid"] is True
    assert len(result["warnings"]) == 0


def test_no_overtime_warning_below_10_hours():
    """Test that shifts under 10 hours don't generate warning."""
    result = validate_shift("Employee", 25, 9, "day", "staff")
    assert result["valid"] is True
    assert len(result["warnings"]) == 0


# ============================================================================
# Edge Cases and Complex Scenarios
# ============================================================================


def test_multiple_errors_accumulate():
    """Test that multiple validation errors are all reported."""
    result = validate_shift("", 17, 15, "invalid_shift", "invalid_role", rest_hours_since_last_shift=5)
    assert result["valid"] is False
    # Should have multiple errors
    assert len(result["errors"]) >= 3


def test_minor_overtirne_and_rest_validation():
    """Test combination: minor with insufficient rest."""
    result = validate_shift("Young Worker", 17, 11, "day", "staff", rest_hours_since_last_shift=6)
    assert result["valid"] is False
    assert any("Insufficient rest period" in error for error in result["errors"])
    assert any("Overtime warning" in warning for warning in result["warnings"])


def test_valid_complex_scenario():
    """Test a complex valid scenario with maximum constraints."""
    result = validate_shift(
        "John Smith", age=25, shift_hours=12, shift_type="night", role="manager", rest_hours_since_last_shift=10
    )
    assert result["valid"] is True
    assert any("Overtime warning" in warning for warning in result["warnings"])


def test_edge_case_fractional_hours():
    """Test shift with fractional hours."""
    result = validate_shift("Employee", 25, 8.5, "day", "staff")
    assert result["valid"] is True


def test_edge_case_very_small_shift():
    """Test shift with very small duration."""
    result = validate_shift("Employee", 25, 0.25, "day", "staff")
    assert result["valid"] is True


# ============================================================================
# Data Type and Input Validation Tests
# ============================================================================


def test_name_with_special_characters():
    """Test that names with special characters are accepted."""
    result = validate_shift("José García-López", 25, 8, "day", "staff")
    assert result["valid"] is True


def test_name_with_numbers():
    """Test that names with numbers are accepted."""
    result = validate_shift("Agent 007", 25, 8, "day", "staff")
    assert result["valid"] is True


# ============================================================================
# Integration and Real-World Scenarios
# ============================================================================


def test_scenario_morning_shift_coordinator():
    """Test realistic scenario: morning shift coordinator."""
    result = validate_shift("Sarah Chen", 32, 8, "day", "supervisor", rest_hours_since_last_shift=10)
    assert result["valid"] is True
    assert len(result["warnings"]) == 0


def test_scenario_night_shift_manager_overtime():
    """Test realistic scenario: night shift manager with overtime."""
    result = validate_shift("Michael Brown", 40, 11, "night", "manager", rest_hours_since_last_shift=8)
    assert result["valid"] is True
    assert any("Overtime warning" in warning for warning in result["warnings"])


def test_scenario_underage_intern_evening():
    """Test realistic scenario: young intern scheduled evening shift."""
    result = validate_shift("Alex Thompson", 16, 6, "evening", "staff", rest_hours_since_last_shift=12)
    assert result["valid"] is True  # Evening is allowed for minors
    assert len(result["errors"]) == 0


def test_scenario_rejected_fatigue_risk():
    """Test realistic scenario: insufficient rest period detected."""
    result = validate_shift("Emma Davis", 28, 8, "day", "staff", rest_hours_since_last_shift=3)
    assert result["valid"] is False
    assert any("Insufficient rest period" in error for error in result["errors"])