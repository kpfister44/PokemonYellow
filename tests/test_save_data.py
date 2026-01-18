# ABOUTME: Tests for save data serialization and storage
# ABOUTME: Validates round-trip persistence of game state

from pathlib import Path

from src.battle.pokemon import Pokemon
from src.battle.species_loader import SpeciesLoader
from src.battle.stat_stages import StatStages
from src.battle.status_effects import StatusCondition
from src.items.bag import Bag
from src.party.party import Party
from src.save.save_data import SaveData
from src.save.save_storage import load_save_data, save_exists, write_save_data


def _make_pokemon(species_loader: SpeciesLoader) -> Pokemon:
    species = species_loader.get_species("pikachu")
    pokemon = Pokemon(species, 12)
    pokemon.iv_attack = 7
    pokemon.iv_defense = 6
    pokemon.iv_speed = 5
    pokemon.iv_special = 4
    pokemon.iv_hp = pokemon._calculate_hp_iv()
    pokemon.stats = pokemon._calculate_stats()
    pokemon.current_hp = pokemon.stats.hp - 3
    pokemon.moves = ["thunder-shock", "growl"]
    pokemon.move_pp = {
        "thunder-shock": (10, 20),
        "growl": (35, 40)
    }
    pokemon.status = StatusCondition.POISON
    pokemon.status_turns = 2
    pokemon.stat_stages = StatStages(
        attack=1,
        defense=-1,
        speed=2,
        special=0,
        accuracy=-2,
        evasion=1
    )
    pokemon.experience = pokemon.exp_to_next_level - 5
    return pokemon


def test_pokemon_to_dict_round_trip():
    """Pokemon should serialize and deserialize with full fidelity."""
    species_loader = SpeciesLoader()
    pokemon = _make_pokemon(species_loader)

    data = pokemon.to_dict()
    loaded = Pokemon.from_dict(data, species_loader)

    assert loaded.species.species_id == pokemon.species.species_id
    assert loaded.level == pokemon.level
    assert loaded.iv_attack == pokemon.iv_attack
    assert loaded.iv_defense == pokemon.iv_defense
    assert loaded.iv_speed == pokemon.iv_speed
    assert loaded.iv_special == pokemon.iv_special
    assert loaded.iv_hp == pokemon.iv_hp
    assert loaded.stats == pokemon.stats
    assert loaded.current_hp == pokemon.current_hp
    assert loaded.moves == pokemon.moves
    assert loaded.move_pp == pokemon.move_pp
    assert loaded.status == pokemon.status
    assert loaded.status_turns == pokemon.status_turns
    assert loaded.stat_stages == pokemon.stat_stages
    assert loaded.experience == pokemon.experience
    assert loaded.exp_to_next_level == pokemon.exp_to_next_level


def test_party_to_dict_round_trip():
    """Party should serialize and deserialize with order preserved."""
    species_loader = SpeciesLoader()
    party = Party()
    party.add(_make_pokemon(species_loader))
    party.add(Pokemon(species_loader.get_species("rattata"), 3))

    data = party.to_dict()
    loaded = Party.from_dict(data, species_loader)

    assert loaded.size() == party.size()
    assert loaded.pokemon[0].species.species_id == party.pokemon[0].species.species_id
    assert loaded.pokemon[1].species.species_id == party.pokemon[1].species.species_id


def test_bag_to_dict_round_trip():
    """Bag should serialize and deserialize with quantities and order."""
    bag = Bag()
    bag.add_item("potion")
    bag.add_item("antidote")
    bag.add_item("potion")
    bag.add_item("bicycle")

    data = bag.to_dict()
    loaded = Bag.from_dict(data)

    loaded_entries = [(entry.item_id, entry.quantity) for entry in loaded.get_entries()]
    assert loaded_entries == [
        ("potion", 2),
        ("antidote", 1),
        ("bicycle", 1)
    ]


def test_save_data_round_trip():
    """SaveData should serialize and deserialize consistently."""
    species_loader = SpeciesLoader()
    party = Party()
    party.add(_make_pokemon(species_loader))
    bag = Bag()
    bag.add_item("potion")

    save_data = SaveData(
        player_name="PLAYER",
        player_direction="down",
        map_path="assets/maps/pallet_town.tmx",
        player_x=8,
        player_y=13,
        party=party,
        bag=bag,
        defeated_trainers={"pallet_town:boy"},
        collected_items={"pallet_town:pallet_potion"}
    )

    data = save_data.to_dict()
    loaded = SaveData.from_dict(data, species_loader)

    assert loaded.to_dict() == save_data.to_dict()


def test_save_data_normalizes_pokedex_sets():
    """SaveData should normalize pokedex flags into sorted lists."""
    species_loader = SpeciesLoader()
    party = Party()
    bag = Bag()
    reserved_flags = {
        "pokedex_seen": {"bulbasaur", "pikachu"},
        "pokedex_caught": {"pikachu"}
    }

    save_data = SaveData(
        player_name="PLAYER",
        player_direction="down",
        map_path="assets/maps/pallet_town.tmx",
        player_x=8,
        player_y=13,
        party=party,
        bag=bag,
        defeated_trainers=set(),
        collected_items=set(),
        reserved_flags=reserved_flags
    )

    data = save_data.to_dict()

    assert data["flags"]["reserved"]["pokedex_seen"] == ["bulbasaur", "pikachu"]
    assert data["flags"]["reserved"]["pokedex_caught"] == ["pikachu"]


def test_save_storage_round_trip(tmp_path: Path):
    """Save storage should write and read SaveData to JSON."""
    species_loader = SpeciesLoader()
    party = Party()
    party.add(_make_pokemon(species_loader))
    bag = Bag()
    bag.add_item("potion")

    save_data = SaveData(
        player_name="PLAYER",
        player_direction="left",
        map_path="assets/maps/route_1.tmx",
        player_x=5,
        player_y=7,
        party=party,
        bag=bag,
        defeated_trainers=set(),
        collected_items=set()
    )

    save_path = tmp_path / "save.json"
    assert save_exists(save_path) is False

    write_save_data(save_data, save_path)
    assert save_exists(save_path) is True

    loaded = load_save_data(save_path, species_loader)
    assert loaded.to_dict() == save_data.to_dict()
