# ABOUTME: Tests for Pokedex ordering and visibility logic
# ABOUTME: Validates list ordering, visibility states, and measurement formatting

from dataclasses import dataclass

from src.ui.pokedex_screen import (
    format_height_feet_inches,
    format_weight_pounds,
    get_species_in_dex_order,
    get_visibility_state
)


@dataclass
class FakeSpecies:
    species_id: str
    number: int


def test_species_order_by_dex_number():
    """Species list should order by dex number ascending."""
    species_by_id = {
        "mew": FakeSpecies("mew", 151),
        "bulbasaur": FakeSpecies("bulbasaur", 1),
        "ivysaur": FakeSpecies("ivysaur", 2)
    }

    ordered = get_species_in_dex_order(species_by_id)

    assert [species.species_id for species in ordered] == [
        "bulbasaur",
        "ivysaur",
        "mew"
    ]


def test_visibility_state_prioritizes_caught():
    """Caught status should take priority over seen."""
    seen = {"pikachu"}
    caught = {"pikachu"}

    assert get_visibility_state("pikachu", seen, caught) == "caught"


def test_visibility_state_seen_when_not_caught():
    """Seen status should apply when not caught."""
    seen = {"pikachu"}
    caught = set()

    assert get_visibility_state("pikachu", seen, caught) == "seen"


def test_visibility_state_unseen():
    """Unseen status should apply when not in any set."""
    seen = set()
    caught = set()

    assert get_visibility_state("pikachu", seen, caught) == "unseen"


def test_format_height_feet_inches():
    """Height formatting should match Yellow display."""
    assert format_height_feet_inches(7) == "2'04\""


def test_format_weight_pounds():
    """Weight formatting should match Yellow display."""
    assert format_weight_pounds(69) == "15.2LB."
