import math

def round_to_price_ending(p: float, ending: float = 0.99, policy: str = "down") -> float:
    """
    Snap to a specific ending (e.g., .99) with an explicit policy.

    policy:
      - "down": floor then add ending; if that exceeds p, step down one int.
      - "nearest": choose whichever (down/up) is closer to p; ties -> up.
      - "up": ceil then add ending; if that is below/equal to p, step up one int.

    Returns price rounded to 2 decimals.
    """
    base = math.floor(p)
    down = base + ending
    if down > p:
        down = max(ending, base - 1 + ending)

    up_base = math.ceil(p)
    up = up_base + ending
    if up <= p:
        up = up_base + 1 + ending

    if policy == "down":
        snapped = down
    elif policy == "up":
        snapped = up
    elif policy == "nearest":
        snapped = down if (p - down) <= (up - p) else up
    else:
        snapped = down  # default safe behavior

    return round(snapped, 2)

def clamp(x: float, lo: float, hi: float) -> float:
    return min(max(x, lo), hi)
