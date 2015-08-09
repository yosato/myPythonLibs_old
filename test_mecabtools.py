import unittest,imp,os
import mecabtools
from pdb import set_trace
imp.reload(mecabtools)

class TestMecabTools(unittest.TestCase):
    def setUp(self):
        self.examplefp=os.getcwd()+'/sometimeswrong.mecab'
        self.errortypes=['head/tail EOS','empty sent','empty line','redundant whitespaces','wrong num of features' ]
        
        self.wrongbits=[
            (0,1,'EOS',self.errortypes[0]),
            (1,2,'会い	動詞,自立,*,*,五段・ワ行促音便,連用形,*,会う,アイ,アイ',self.errortypes[-1]),
            (1,4,'と	助詞,格助詞,引用,*,*,*,と,ト,ト	',self.errortypes[-1]),
            (1,5,'思い 	動詞,自立,*,*,五段・ワ行促音便,連用形,思う,オモイ,オモイ',self.errortypes[1]),
            (2,60,'EOS',self.errortypes[1]),
            (4,104,'私	名詞,代名詞,一般,*,*,*,私,ワタシ,ワタシ',self.errortypes[-1]),
            (5,127,'',self.errortypes[0]),
        ]

        AllLines=open(self.examplefp).read().split('\n')
        WrongInds=[ Wrong[0] for Wrong in self.wrongbits ]
        #set_trace()
        Corrects=[]
        for (Cntr,Line) in enumerate(AllLines):
            if Cntr+1 not in WrongInds:
                Corrects.append(Line)
        self.corrects=Corrects
        
#        self.corrrects=[ Line for (Cntr,Line) in enumerate(AllLines) if Cntr+1 not in WrongInds ]
        

    def test_filter_errors_strict(self):
#        set_trace()
        AllegedWrong,AllegedCorrects=mecabtools.filter_errors(self.examplefp,[7,9],StrictP=True)
        self.assertEqual(AllegedWrong,[self.wrongbits[0]])
        self.assertEqual(AllegedCorrects,[])

    def test_filter_errors_plain(self):
        set_trace()
        AllegedWrong,AllegedCorrects=mecabtools.filter_errors(self.examplefp,[7,9],StrictP=False)
        self.assertEqual(AllegedWrong,self.wrongbits)
#        self.assertEqual(AllegedCorrects,self.corrects)

    def test_filter_errors_recover(self):
        set_trace()
        AllegedWrongs,AllegedCorrects=mecabtools.filter_errors(self.examplefp,[7,9],StrictP=False,Recover=True)
        self.assertEqual(AllegedWrongs,[self.wrongbits[0]])




        

if __name__=='__main__':
    unittest.main()
