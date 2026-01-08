# ABOUTME: Entry point for Pokemon Yellow game
# ABOUTME: Initializes the game engine and starts in Pallet Town

from src.engine.game import Game
from src.engine import constants
from src.states.overworld_state import OverworldState


def main():
    """Main entry point."""
    print("Starting Pokemon Yellow...")
    print(f"Window size: {constants.WINDOW_WIDTH}x{constants.WINDOW_HEIGHT}")
    print(f"Game resolution: {constants.GAME_WIDTH}x{constants.GAME_HEIGHT} (scaled {constants.SCALE_FACTOR}x)")

    # Create game and initial state (start in Pallet Town)
    game = Game()
    # Start player on path between the houses
    initial_state = OverworldState(game, "data/maps/pallet_town.json", player_start_x=8, player_start_y=13)
    game.push_state(initial_state)

    # Run the game
    try:
        game.run()
    except Exception as e:
        print(f"Error running game: {e}")
        import traceback
        traceback.print_exc()

    print("Game ended.")


if __name__ == "__main__":
    main()
