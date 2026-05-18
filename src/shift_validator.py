def validate_shift(hours_worked, break_minutes, consecutive_days, role):
    """
    Validates employee shift safety and returns a risk classification.
    """

    if hours_worked < 0 or break_minutes < 0 or consecutive_days < 0:
        raise ValueError("Values cannot be negative")

    if role not in ["staff", "manager", "admin"]:
        raise ValueError("Invalid role")

    if hours_worked > 14:
        return "REJECTED"

    if consecutive_days > 6:
        return "HIGH_RISK"

    if break_minutes < 20:
        return "WARNING"

    return "VALID"