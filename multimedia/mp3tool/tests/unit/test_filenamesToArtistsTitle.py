import unittest
from helperGeneric import determineArtistAndTitleFromFilename

def getUnittestContentForFunction(name):
        unittestFile = "unittests.json"
        content = getJsonFromFile(unittestFile)

        return content[name]


class TestDetermineArtistAndTitleFromFilename(unittest.TestCase):
    def test_determineArtistAndTitleFromFilename(self):
        content = getUnittestContentForFunction("determineArtistAndTitleFromFilename")
        print(content)
        for myTest in content:

            actual = determineArtistAndTitleFromFilename(filename=myTest["actual"])
            expected = myTest["expected"]
            self.assertEqual(actual, expected)

if __name__ == '__main__':
    unittest.main()