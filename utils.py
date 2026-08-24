def __innings_pitched_fractional_to_decimal(innings_pitched: float) -> float:
    """Converts a fractional innings pitched value to a decimal value (e.g., 3.2 to 3.66666...)."""

    innings_pitched_int = int(innings_pitched)
    innings_pitched_frac = 10 * (innings_pitched - innings_pitched_int)
    ip = innings_pitched_int + innings_pitched_frac / 3

    return ip


def __innings_pitched_decimal_to_fractional(innings_pitched: float) -> float:
    """Converts a decimal innings pitched value to a fractional value (e.g., 3.66666... to 3.2)."""

    innings_pitched_int = int(innings_pitched)
    innings_pitched_frac = int(3 * (innings_pitched - innings_pitched_int))
    ip = innings_pitched_int + innings_pitched_frac / 10

    return ip
