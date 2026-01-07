# ABOUTME: Abstract base class for game states
# ABOUTME: Defines the interface that all states (overworld, battle, menu) must implement

from abc import ABC, abstractmethod


class BaseState(ABC):
    """Abstract base class for all game states."""

    def __init__(self, game):
        """Initialize the state with a reference to the game."""
        self.game = game

    @abstractmethod
    def update(self, dt):
        """
        Update the state logic.

        Args:
            dt: Delta time in seconds since last frame
        """
        pass

    @abstractmethod
    def render(self, renderer):
        """
        Render the state to the screen.

        Args:
            renderer: The Renderer instance to draw with
        """
        pass

    @abstractmethod
    def handle_input(self, input_handler):
        """
        Handle input for this state.

        Args:
            input_handler: The Input instance with current input state
        """
        pass

    def enter(self):
        """Called when entering this state. Override if needed."""
        pass

    def exit(self):
        """Called when exiting this state. Override if needed."""
        pass
