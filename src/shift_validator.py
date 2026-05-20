"""
Shift Validator Module

A comprehensive workforce scheduling validation engine for DevOps and Software Testing.
Validates employee shift information against business rules and safety regulations.
"""


def validate_shift(
    name: str,
    age: int,
    shift_hours: float,
    shift_type: str,
    role: str,
    rest_hours_since_last_shift: float = 0,
) -> dict:
    """
    Validates employee shift scheduling against business rules.

    Performs validation checks on:
    - Employee name and age
    - Shift hours and type
    - Employee role
    - Rest periods between consecutive shifts
    - Overtime thresholds

    Args:
        name (str): Employee name (cannot be empty)
        age (int): Employee age in years
        shift_hours (float): Number of hours for the shift (0-12)
        shift_type (str): Type of shift (day, evening, night)
        role (str): Employee role (manager, supervisor, staff)
        rest_hours_since_last_shift (float): Hours since last shift for consecutive shift validation

    Returns:
        dict: Validation result with keys:
            - valid (bool): True if shift passes all validation checks
            - errors (list): List of validation errors (if any)
            - warnings (list): List of validation warnings (non-blocking)

    Examples:
        >>> result = validate_shift("John Doe", 25, 8, "day", "staff")
        >>> result["valid"]
        True
        >>> result["errors"]
        []
    """
    errors = []
    warnings = []

    # 1. Employee name validation
    if not name or not isinstance(name, str) or not name.strip():
        errors.append("Employee name cannot be empty")

    # 2. Shift hours validation
    if shift_hours < 0:
        errors.append("Shift hours cannot be negative")
    elif shift_hours > 12:
        errors.append("Shift hours cannot exceed 12 hours")

    # 3. Valid shift type validation
    valid_shift_types = ["day", "evening", "night"]
    if shift_type not in valid_shift_types:
        errors.append(
            f"Invalid shift type '{shift_type}'. Must be one of: {', '.join(valid_shift_types)}"
        )

    # 4. Valid role validation
    valid_roles = ["manager", "supervisor", "staff"]
    if role not in valid_roles:
        errors.append(
            f"Invalid employee role '{role}'. Must be one of: {', '.join(valid_roles)}"
        )

    # 5. Underage night shift restriction
    if age < 18 and shift_type == "night":
        errors.append("Employees under 18 cannot work night shifts")

    # 6. Consecutive shifts rest period validation
    # Only check rest period if a positive value is provided (indicating consecutive shift)
    if rest_hours_since_last_shift > 0 and rest_hours_since_last_shift < 8:
        errors.append(
            f"Insufficient rest period. Minimum 8 hours required, only {rest_hours_since_last_shift} hours since last shift"
        )

    # 7. Overtime warning (non-blocking)
    if shift_hours > 10:
        warnings.append(
            f"Overtime warning: Shift of {shift_hours} hours exceeds standard 10-hour threshold"
        )

    # Determine overall validity
    is_valid = len(errors) == 0

    return {"valid": is_valid, "errors": errors, "warnings": warnings}