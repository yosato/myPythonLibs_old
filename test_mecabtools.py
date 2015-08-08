import unittest,imp,sys,os
import mecabtools

class TestMecabTools(unittest.TestCase):
    def setUp(self):
        self.examplefp='exampleForTest.mecab'
        if os.path.isfile(self.examplefp):
            self.examplestr=open(self.examplefp).read()
        else:
            self.examplestr=[
                ''
                ]
    def test_file_valid_p(self):
        

if __name__=='__main__':
    unittest.main()
