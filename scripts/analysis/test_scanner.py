import unittest
import os
import re
from scanner import LoreScanner

class TestLoreScanner(unittest.TestCase):
    def setUp(self):
        self.scanner = LoreScanner()
        self.test_content = """
        小金正趴在一片玉米叶上。小玉正忙着看书。
        他们在回声山谷遇到了黑焰。
        小彩拿出了阳光露珠。
        """
    
    def test_extract_characters(self):
        characters = self.scanner.extract_characters(self.test_content)
        self.assertIn("小金", characters)
        self.assertIn("小玉", characters)
        self.assertIn("黑焰", characters)
        self.assertIn("小彩", characters)

    def test_extract_locations(self):
        locations = self.scanner.extract_locations(self.test_content)
        self.assertIn("回声山谷", locations)

    def test_extract_items(self):
        items = self.scanner.extract_items(self.test_content)
        self.assertIn("阳光露珠", items)

if __name__ == '__main__':
    unittest.main()
