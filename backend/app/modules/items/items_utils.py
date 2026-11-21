def merge_changes(current: dict, changes: dict) -> dict:
    """Return a new dict with `changes` applied over `current`. Pure: no mutation."""
    return {**current, **changes}
