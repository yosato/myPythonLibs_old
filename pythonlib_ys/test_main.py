import unittest,os,imp
import main
imp.reload(main)
from pdb import set_trace

class TestFileRelated(unittest.TestCase):
    def setUp(self):

        self.testDir=os.path.join(os.getenv('HOME'),'links/corpora_mine_test')
        self.testFP=os.path.join(self.testDir,'sample.txt')
        self.testLines1='aaa\niii\nuuu\neee\nooo\n'
        self.testLines2='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\niiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii\nuuu\neeeeeeeeeeee\nooooooooo\n'
        self.largeFP=os.path.join(self.testDir,'sampleLarge.txt')
    def test_readline_reverse(self):
        set_trace()
        for TestLines in (self.testLines1,self.testLines2):
            open(self.testFP,'wt').write(self.testLines)
            FSr=open(self.testFP,'rt')
            FSr.readline();FSr.readline();FSr.readline()
            LstLine=main.readline_reverse(FSr)
            FSr.close()
            self.assertEqual(LstLine,'uuu')
    def test_readline_reverse_speed(self):
        main.get_nth_line()
        FSr=open(self.largeFP)
        for FSr.readlines()
        FSr.close()
        
        
    def test_get_nths_lines(self):
        set_trace()
        open(self.testFP,'wt').write(self.testLines1)
        AllegedLines=main.get_nths_lines(self.testFP,[3,5,2])
        self.assertEqual(AllegedLines,['uuu','ooo','iii'])
           
            

if __name__=='__main__':
    unittest.main()
