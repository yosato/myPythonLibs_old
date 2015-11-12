import unittest,os,imp,timeit,datetime
import main as myModule
imp.reload(myModule)
from pdb import set_trace

class TestJsonRelated(unittest.TestCase):
    def setUp(self):
        self.jsonFPSmall=os.path.join(self.testDir,'sampleJsonSmall.json')
        self.jsonFPLarge=os.path.join(self.testDir,'sampleJsonLarge.json')
    def sort_jsons_fromfile(self):
        set_trace()
        Before=datetime.datetime.now()
        myModule.sort_jsons_fromfile(self.jsonFPLarge,OutFP=self.jsonFPLarge+'.sorted')
        After=datetime.datetime.now()
        self.assertTrue(After-Before.seconds<20)
        self.assertEqual()
        
        

class TestFileRelated(unittest.TestCase):
    def setUp(self):

        self.testDir=os.path.join(os.getenv('HOME'),'links/corpora_mine_test')
        self.testFP=os.path.join(self.testDir,'sample.txt')
        self.testLines1='aaa\niii\nuuu\neee\nooo\n'
        self.testLines2='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\niiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii\nuuu\neeeeeeeeeeee\nooooooooo\n'
        self.largeFP=os.path.join(self.testDir,'sampleLarge.txt')

    def test_readline_reverse(self):
        
        for TestLines in (self.testLines1,self.testLines2):
            open(self.testFP,'wt').write(self.testLines)
            FSr=open(self.testFP,'rt')
            FSr.readline();FSr.readline();FSr.readline()
            LstLine=myModule.readline_reverse(FSr)
            FSr.close()
            self.assertEqual(LstLine,'uuu')
    def test_readline_reverse_speed(self):
        set_trace()
        B4=datetime.datetime.now()
        myModule.get_nth_line(self.largeFP,20000)
        After=datetime.datetime.now()
        Time1=After-B4
#        myTimer1=timeit.Timer("myModule.get_nth_line(,20000)","import main as myModule")
 #       Time1=myTimer1.timeit()
        B4=datetime.datetime.now()
        myModule.get_nth_line_reverse(self.largeFP,20000)
        After=datetime.datetime.now()
        Time2=After-B4
        
        self.assertTrue(Time2-Time1>0.1)
        
        
    def test_get_nths_lines(self):
        #set_trace()
        open(self.testFP,'wt').write(self.testLines1)
        AllegedLines=myModule.get_nths_lines(self.testFP,[3,5,2])
        self.assertEqual(AllegedLines,['uuu','ooo','iii'])
           
            

if __name__=='__main__':
    unittest.main()
