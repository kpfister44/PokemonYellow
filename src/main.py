# ABOUTME: Entry point for Pokemon Yellow game
# ABOUTME: Initializes the game engine and starts with a test state

from src.engine.game import Game
from src.engine import constants
from src.states.base_state import BaseState


class TestState(BaseState):
    """Simple test state to verify the engine works."""

    def __init__(self, game):
        super().__init__(game)
        self.counter = 0
        self.input_text = "Press arrow keys, Z, X, or Enter"

    def update(self, dt):
        """Update test state."""
        self.counter += 1

    def render(self, renderer):
        """Render test state."""
        # Clear screen with Game Boy light green
        renderer.clear(constants.COLOR_LIGHTEST)

        # Draw a test rectangle that changes position
        x = 50 + (self.counter % 100)
        y = 50
        renderer.draw_rect(constants.COLOR_DARKEST, (x, y, 20, 20))

        # Draw text area (placeholder - we'll implement text rendering later)
        renderer.draw_rect(constants.COLOR_DARK, (10, 110, 140, 24), 2)

    def handle_input(self, input_handler):
        """Handle input for test state."""
        # Just print what keys are pressed
        if input_handler.is_just_pressed("a"):
            print("A button pressed!")
        if input_handler.is_just_pressed("b"):
            print("B button pressed!")
        if input_handler.is_just_pressed("start"):
            print("Start button pressed!")

        direction = input_handler.get_direction()
        if direction is not None:
            direction_names = {
                constants.DIR_UP: "UP",
                constants.DIR_DOWN: "DOWN",
                constants.DIR_LEFT: "LEFT",
                constants.DIR_RIGHT: "RIGHT"
            }
            if input_handler.is_just_pressed("up") or \
               input_handler.is_just_pressed("down") or \
               input_handler.is_just_pressed("left") or \
               input_handler.is_just_pressed("right"):
                print(f"Direction: {direction_names[direction]}")


def main():
    """Main entry point."""
    print("Starting Pokemon Yellow...")
    print(f"Window size: {constants.WINDOW_WIDTH}x{constants.WINDOW_HEIGHT}")
    print(f"Game resolution: {constants.GAME_WIDTH}x{constants.GAME_HEIGHT} (scaled {constants.SCALE_FACTOR}x)")

    # Create game and initial state
    game = Game()
    initial_state = TestState(game)
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
