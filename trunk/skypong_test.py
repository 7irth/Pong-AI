__author__ = 'Tirth'

import unittest
import PongAIvAI
import pygame


class TestSkypong(unittest.TestCase):
    def setUp(self):
        pygame.init()

    def test_ai(self):
        PongAIvAI.init_game()


if __name__ == "__main__":
    unittest.main(exit=False)