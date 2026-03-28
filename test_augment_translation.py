import unittest
from augment_translation import normalize_cloze

class TestAugmentTranslation(unittest.TestCase):
    def test_normalize_cloze_simple(self):
        self.assertEqual(normalize_cloze("{{c1::apple}}"), "apple")
        self.assertEqual(normalize_cloze("{{c2::banana}}"), "banana")

    def test_normalize_cloze_with_hint(self):
        self.assertEqual(normalize_cloze("{{c1::apple::fruit}}"), "apple")
        self.assertEqual(normalize_cloze("{{c10::banana::yellow}}"), "banana")

    def test_normalize_cloze_mixed(self):
        text = "I like {{c1::apple}} and {{c2::banana::fruit}}."
        expected = "I like apple and banana."
        self.assertEqual(normalize_cloze(text), expected)

    def test_normalize_cloze_no_cloze(self):
        self.assertEqual(normalize_cloze("No cloze here."), "No cloze here.")

if __name__ == "__main__":
    unittest.main()
