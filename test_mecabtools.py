import unittest,imp,os
import mecabtools
from pdb import set_trace
imp.reload(mecabtools)

class TestMecabTools(unittest.TestCase):
    def setUp(self):
        self.examplefp=os.getcwd()+'/sometimeswrong.mecab'
        self.errortypes=['head/tail EOS','empty sent','empty line','redundant whitespaces','wrong num of features' ]
        
        self.alllines=open(self.examplefp).read().split('\n')
        
        self.wrongbits=[
            (1,1,'EOS',self.errortypes[0]),
            (1,2,'会い	動詞,自立,*,*,五段・ワ行促音便,連用形,*,会う,アイ,アイ',self.errortypes[-1]),
            (1,4,'と	助詞,格助詞,引用,*,*,*,と,ト,ト	',self.errortypes[-2]),
            (1,5,'思い 	動詞,自立,*,*,五段・ワ行促音便,連用形,思う,オモイ,オモイ',self.errortypes[-2]),
            (2,60,'EOS',self.errortypes[1]),
            (3,62,'おそらく	一般,*,*,*,*,おそらく,オソラク,オソラク',self.errortypes[-1]),
            (3,64,' ',self.errortypes[2]),
            (4,127,'。\t記号,句点,*,*,*,*,。,。,。',self.errortypes[0]),
        ]

        WrongInds=[ Wrong[0] for Wrong in self.wrongbits ]
        #set_trace()
        Corrects=[]
        for (Cntr,Line) in enumerate(self.alllines):
            if Cntr+1 not in WrongInds:
                Corrects.append(Line)
        self.corrects=Corrects
        
#        self.corrrects=[ Line for (Cntr,Line) in enumerate(AllLines) if Cntr+1 not in WrongInds ]

    def test10_something_wrong(self):
        AllLines=self.alllines
 #      set_trace()
        AllegedErrorType=mecabtools.something_wrong(1,AllLines[0],AllLines[1],[7,9])
        self.assertEqual(AllegedErrorType,self.errortypes[0])

        AllegedErrorType=mecabtools.something_wrong(2,AllLines[1],AllLines[2],[7,9])
        self.assertEqual(AllegedErrorType,self.errortypes[-1])

        AllegedErrorType=mecabtools.something_wrong(4,AllLines[3],AllLines[4],[7,9])
        self.assertEqual(AllegedErrorType,self.errortypes[-2])

        AllegedErrorType=mecabtools.something_wrong(60,AllLines[59],AllLines[60],[7,9])
        self.assertEqual(AllegedErrorType,self.errortypes[1])

        AllegedErrorType=mecabtools.something_wrong(64,AllLines[63],AllLines[64],[7,9])
        self.assertEqual(AllegedErrorType,self.errortypes[2])
        

    def test20_filter_errors_strict(self):
#       set_trace()
        AllegedWrong,AllegedCorrects=mecabtools.filter_errors(self.examplefp,[7,9],StrictP=True)
        self.assertEqual(AllegedWrong,[self.wrongbits[0]])
        self.assertEqual(AllegedCorrects,[])

    def test30_filter_errors_plain(self):
#        set_trace()
        AllegedWrong,AllegedCorrects=mecabtools.filter_errors(self.examplefp,[7,9],StrictP=False)
        self.assertEqual(AllegedWrong,self.wrongbits)
#        self.assertEqual(AllegedCorrects,self.corrects)

    def test40_filter_errors_recover(self):
        #set_trace()
        AllegedWrongs,AllegedCorrects=mecabtools.filter_errors(self.examplefp,[7,9],StrictP=False,Recover=True)
        self.assertEqual(AllegedWrongs,[self.wrongbits[1]]+[self.wrongbits[5]])

    def test50_check_and_remove_errors(self):
        set_trace()
        mecabtools.check_and_remove_errors(self.examplefp,[7,9])



        

if __name__=='__main__':
    unittest.main()
