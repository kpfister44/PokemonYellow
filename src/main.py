# ABOUTME: Entry point for Pokemon Yellow game
# ABOUTME: Initializes the game engine and starts in Pallet Town

from src.engine.game import Game
from src.engine import constants
from src.states.title_menu_state import TitleMenuState


def main():
    """Main entry point."""
    print("Starting Pokemon Yellow...")
    print(f"Window size: {constants.WINDOW_WIDTH}x{constants.WINDOW_HEIGHT}")
    print(f"Game resolution: {constants.GAME_WIDTH}x{constants.GAME_HEIGHT} (scaled {constants.SCALE_FACTOR}x)")

    # Create game and initial state
    game = Game()
    initial_state = TitleMenuState(game)
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
