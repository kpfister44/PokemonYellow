# ABOUTME: Main game engine with game loop and state management
# ABOUTME: Handles initialization, state transitions, and frame timing

import pygame
from src.engine import constants
from src.engine.renderer import Renderer
from src.engine.input import Input


class Game:
    """Main game engine that manages the game loop and states."""

    def __init__(self):
        """Initialize the game engine."""
        pygame.init()

        # Core systems
        self.renderer = Renderer()
        self.input = Input()
        self.clock = pygame.time.Clock()

        # State management
        self.state_stack = []
        self.running = False

    def push_state(self, state):
        """
        Push a new state onto the stack.
        The new state becomes the active state.
        """
        if self.state_stack:
            self.state_stack[-1].exit()
        self.state_stack.append(state)
        state.enter()

    def pop_state(self):
        """
        Pop the current state from the stack.
        Returns to the previous state.
        """
        if self.state_stack:
            state = self.state_stack.pop()
            state.exit()
        if self.state_stack:
            self.state_stack[-1].enter()

    def change_state(self, state):
        """
        Replace the current state with a new one.
        """
        if self.state_stack:
            self.state_stack[-1].exit()
            self.state_stack.pop()
        self.state_stack.append(state)
        state.enter()

    def get_current_state(self):
        """Get the currently active state."""
        if self.state_stack:
            return self.state_stack[-1]
        return None

    def run(self):
        """Start the main game loop."""
        self.running = True

        while self.running:
            # Calculate delta time
            dt = self.clock.tick(constants.FPS) / 1000.0  # Convert to seconds

            # Handle events
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

            # Update input
            self.input.update(events)

            # Get current state
            current_state = self.get_current_state()
            if current_state:
                # Handle input, update, and render
                current_state.handle_input(self.input)
                current_state.update(dt)
                current_state.render(self.renderer)

            # Present the frame
            self.renderer.present()

        # Clean up
        self.quit()

    def quit(self):
        """Clean up and quit the game."""
        pygame.quit()
