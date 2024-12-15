from dataclasses import dataclass
import random
import time
from typing import Dict, Tuple

@dataclass
class KeyTransition:
    base_delay: float
    variability: float

class TransitionType:
    SAME_FINGER = 0.12
    ADJACENT_FINGER = 0.08
    ALTERNATING_HAND = 0.06
    COMMON_PAIR = 0.05
    DIAGONAL_STRETCH = 0.11
    VERTICAL_STRETCH = 0.10
    CROSS_HAND = 0.13
    LONG_STRETCH = 0.14

class VirtualKeyCode:
    # Map common keys to codes
    A = 'a'
    S = 's'
    D = 'd'
    F = 'f'
    H = 'h'
    G = 'g'
    Z = 'z'
    X = 'x'
    C = 'c'
    V = 'v'
    B = 'b'
    Q = 'q'
    W = 'w'
    E = 'e'
    R = 'r'
    T = 't'
    Y = 'y'
    U = 'u'
    I = 'i'
    O = 'o'
    P = 'p'
    N = 'n'
    M = 'm'
    K = 'k'
    J = 'j'
    L = 'l'

class TypingPatternMap:
    def __init__(self):
        self.key_relationships = self._build_key_relationships()

    def _build_key_relationships(self) -> Dict[str, Dict[str, KeyTransition]]:
        relationships = {}
        
        # Left hand mappings
        relationships[VirtualKeyCode.Q] = {
            VirtualKeyCode.A: KeyTransition(TransitionType.VERTICAL_STRETCH, 0.02),
            VirtualKeyCode.Z: KeyTransition(TransitionType.LONG_STRETCH, 0.03),
            VirtualKeyCode.W: KeyTransition(TransitionType.ADJACENT_FINGER, 0.02)
        }

        relationships[VirtualKeyCode.W] = {
            VirtualKeyCode.S: KeyTransition(TransitionType.VERTICAL_STRETCH, 0.02),
            VirtualKeyCode.X: KeyTransition(TransitionType.LONG_STRETCH, 0.02),
            VirtualKeyCode.E: KeyTransition(TransitionType.ADJACENT_FINGER, 0.02)
        }

        # Common bigrams
        relationships[VirtualKeyCode.T] = {
            VirtualKeyCode.H: KeyTransition(TransitionType.COMMON_PAIR, 0.01),
            VirtualKeyCode.E: KeyTransition(TransitionType.COMMON_PAIR, 0.01)
        }

        relationships[VirtualKeyCode.H] = {
            VirtualKeyCode.E: KeyTransition(TransitionType.COMMON_PAIR, 0.01)
        }

        # Difficult combinations
        relationships[VirtualKeyCode.Z] = {
            VirtualKeyCode.P: KeyTransition(TransitionType.LONG_STRETCH, 0.03),
            VirtualKeyCode.O: KeyTransition(TransitionType.LONG_STRETCH, 0.03)
        }

        relationships[VirtualKeyCode.B] = {
            VirtualKeyCode.Y: KeyTransition(TransitionType.CROSS_HAND, 0.03),
            VirtualKeyCode.U: KeyTransition(TransitionType.DIAGONAL_STRETCH, 0.03)
        }

        # Add more mappings for complete coverage
        for key in vars(VirtualKeyCode).keys():
            if not key.startswith('_'):
                if getattr(VirtualKeyCode, key) not in relationships:
                    relationships[getattr(VirtualKeyCode, key)] = {}

        return relationships

    def get_transition_delay(self, from_key: str, to_key: str) -> float:
        if from_key in self.key_relationships and to_key in self.key_relationships[from_key]:
            transition = self.key_relationships[from_key][to_key]
            return transition.base_delay + random.uniform(-transition.variability, transition.variability)
        return TransitionType.ALTERNATING_HAND + random.uniform(-0.015, 0.015)

    def analyze_transition(self, from_key: str, to_key: str) -> str:
        delay = self.get_transition_delay(from_key, to_key)
        has_mapping = (from_key in self.key_relationships and 
                      to_key in self.key_relationships[from_key])
        
        return f"""
        Transition Analysis:
        From key: {from_key}
        To key: {to_key}
        Delay: {delay:.3f}s
        Has explicit mapping: {has_mapping}
        """