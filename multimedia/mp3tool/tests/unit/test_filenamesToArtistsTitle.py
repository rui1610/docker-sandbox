import unittest
from helperGeneric import determineArtistAndTitleFromFilename
from helperJson import getJsonFromFile

def getUnittestContentForFunction(name):
        unittestFile = "tests/unit/unittests.json"
        content = getJsonFromFile(unittestFile)

        return content[name]


class TestDetermineArtistAndTitleFromFilename(unittest.TestCase):
    def test_determineArtistAndTitleFromFilename(self):
        content = getUnittestContentForFunction("determineArtistAndTitleFromFilename")

        for myTest in content:
            actual = determineArtistAndTitleFromFilename(filename=myTest["input"])
            expected = myTest["expected"]
            self.assertEqual(actual, expected)

if __name__ == '__main__':
    unittest.main()