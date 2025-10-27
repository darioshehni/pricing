import math

def round_to_price_ending(p: float, ending: float = 0.99) -> float:
    """
    Snap price to a .99-like ending.
    Example: 101.23 -> 100.99 (floor then add ending)
    """
    base = math.floor(p)
    snapped = base + ending
    if snapped > p:
        snapped = max(ending, base - 1 + ending)  # go down one integer if necessary
    return round(snapped, 2)

def clamp(x: float, lo: float, hi: float) -> float:
    return min(max(x, lo), hi)
