# ABOUTME: Status condition definitions for battle system
# ABOUTME: Defines all Gen 1 status effects (paralysis, burn, freeze, poison, sleep)

from enum import Enum


class StatusCondition(Enum):
    """Pokemon status conditions (Gen 1)."""
    NONE = "none"
    PARALYSIS = "paralysis"
    BURN = "burn"
    FREEZE = "freeze"
    POISON = "poison"
    SLEEP = "sleep"
    BADLY_POISON = "badly-poison"  # Toxic - damage increases each turn
