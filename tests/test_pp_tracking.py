# ABOUTME: Tests for PP tracking in Pokemon
# ABOUTME: Validates PP initialization, usage, and display

import pytest
from src.battle.pokemon import Pokemon
from src.battle.species_loader import SpeciesLoader


@pytest.fixture
def species_loader():
    """Fixture for SpeciesLoader."""
    return SpeciesLoader()


@pytest.fixture
def pikachu(species_loader):
    """Fixture for a test Pikachu."""
    species = species_loader.get_species("pikachu")
    return Pokemon(species, 5)


def test_pp_initialized_correctly(pikachu):
    """PP should be initialized to max PP for each move."""
    # Pikachu should have at least one move
    assert len(pikachu.moves) > 0

    for move_id in pikachu.moves:
        current_pp, max_pp = pikachu.get_move_pp(move_id)
        assert current_pp == max_pp
        assert max_pp > 0


def test_use_move_pp_deducts_correctly(pikachu):
    """Using a move should deduct 1 PP."""
    move_id = pikachu.moves[0]
    current_pp, max_pp = pikachu.get_move_pp(move_id)

    success = pikachu.use_move_pp(move_id)

    assert success is True
    new_current_pp, new_max_pp = pikachu.get_move_pp(move_id)
    assert new_current_pp == current_pp - 1
    assert new_max_pp == max_pp  # Max PP shouldn't change


def test_use_move_pp_multiple_times(pikachu):
    """Should be able to use PP multiple times until depleted."""
    move_id = pikachu.moves[0]
    current_pp, max_pp = pikachu.get_move_pp(move_id)

    # Use PP 3 times
    for _ in range(3):
        success = pikachu.use_move_pp(move_id)
        assert success is True

    new_current_pp, _ = pikachu.get_move_pp(move_id)
    assert new_current_pp == current_pp - 3


def test_use_move_pp_fails_when_zero(pikachu):
    """Should return False when trying to use a move with 0 PP."""
    move_id = pikachu.moves[0]
    current_pp, max_pp = pikachu.get_move_pp(move_id)

    # Deplete all PP
    for _ in range(current_pp):
        success = pikachu.use_move_pp(move_id)
        assert success is True

    # Should fail now
    final_pp, _ = pikachu.get_move_pp(move_id)
    assert final_pp == 0

    success = pikachu.use_move_pp(move_id)
    assert success is False

    # PP should still be 0
    final_pp, _ = pikachu.get_move_pp(move_id)
    assert final_pp == 0


def test_use_move_pp_nonexistent_move(pikachu):
    """Should return False for a move the Pokemon doesn't have."""
    success = pikachu.use_move_pp("nonexistent-move")
    assert success is False


def test_get_move_pp_nonexistent_move(pikachu):
    """Should return (0, 0) for a move the Pokemon doesn't have."""
    current_pp, max_pp = pikachu.get_move_pp("nonexistent-move")
    assert current_pp == 0
    assert max_pp == 0


def test_pp_persists_between_uses(pikachu):
    """PP should persist as the Pokemon is used."""
    move_id = pikachu.moves[0]

    # Use PP once
    pikachu.use_move_pp(move_id)
    pp_after_first, _ = pikachu.get_move_pp(move_id)

    # Use PP again
    pikachu.use_move_pp(move_id)
    pp_after_second, _ = pikachu.get_move_pp(move_id)

    # Should be decremented by 2 total
    assert pp_after_second == pp_after_first - 1
