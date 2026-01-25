"""State transitions for workflows."""

from typing import Dict, Any, List, Callable, Optional
from enum import Enum


class StateTransition:
    """Manages state transitions."""
    
    def __init__(self, from_state: str, to_state: str, condition: Callable = None):
        """Initialize a state transition.
        
        Args:
            from_state: Source state.
            to_state: Target state.
            condition: Transition condition function.
        """
        self.from_state = from_state
        self.to_state = to_state
        self.condition = condition
    
    def can_transition(self, current_state: str, context: Dict[str, Any]) -> bool:
        """Check if transition can occur.
        
        Args:
            current_state: Current state.
            context: Transition context.
            
        Returns:
            True if transition is allowed.
        """
        if current_state != self.from_state:
            return False
        
        if self.condition is None:
            return True
        
        return self.condition(context)


class StateMachine:
    """State machine for workflow management."""
    
    def __init__(self, initial_state: str):
        """Initialize the state machine.
        
        Args:
            initial_state: Initial state.
        """
        self.initial_state = initial_state
        self._current_state = initial_state
        self._transitions: List[StateTransition] = []
        self._on_enter_callbacks = {}
        self._on_exit_callbacks = {}
    
    def add_transition(
        self,
        from_state: str,
        to_state: str,
        condition: Callable = None
    ) -> None:
        """Add a state transition.
        
        Args:
            from_state: Source state.
            to_state: Target state.
            condition: Transition condition.
        """
        transition = StateTransition(from_state, to_state, condition)
        self._transitions.append(transition)
    
    def on_enter(self, state: str, callback: Callable) -> None:
        """Register on-enter callback.
        
        Args:
            state: State name.
            callback: Callback function.
        """
        self._on_enter_callbacks[state] = callback
    
    def on_exit(self, state: str, callback: Callable) -> None:
        """Register on-exit callback.
        
        Args:
            state: State name.
            callback: Callback function.
        """
        self._on_exit_callbacks[state] = callback
    
    def transition(self, context: Dict[str, Any]) -> bool:
        """Attempt state transition.
        
        Args:
            context: Transition context.
            
        Returns:
            True if transition occurred.
        """
        for transition in self._transitions:
            if transition.can_transition(self._current_state, context):
                
                exit_callback = self._on_exit_callbacks.get(self._current_state)
                if exit_callback:
                    exit_callback(self._current_state, context)
                
                old_state = self._current_state
                self._current_state = transition.to_state
                
                enter_callback = self._on_enter_callbacks.get(self._current_state)
                if enter_callback:
                    enter_callback(old_state, context)
                
                return True
        
        return False
    
    def get_state(self) -> str:
        """Get current state.
        
        Returns:
            Current state.
        """
        return self._current_state
    
    def reset(self) -> None:
        """Reset to initial state."""
        self._current_state = self.initial_state
    
    def get_possible_transitions(self) -> List[str]:
        """Get possible next states.
        
        Returns:
            List of possible next states.
        """
        possible = []
        for transition in self._transitions:
            if transition.from_state == self._current_state:
                possible.append(transition.to_state)
        return possible
