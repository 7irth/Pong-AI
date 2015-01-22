__author__ = 'Tirth'

import unittest
import PongAIvAI
import pygame
import skypong


class TestSkypong(unittest.TestCase):
    def setUp(self):
        pass

    def test_ai(self):
        pygame.init()
        PongAIvAI.init_game()

        score = skypong.score
        print str(score) + '!'

        if score[0] == 1:  # therefore we're on the right side
            self.assertGreater(score[1][1], score[1][0])
        else:
            self.assertGreater(score[2][0], score[2][1])


if __name__ == "__main__":
    unittest.main(exit=False)