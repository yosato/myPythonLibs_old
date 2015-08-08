import unittest,imp,sys,os
import mecabtools
from pdb import set_trace
imp.reload(mecabtools)

class TestMecabTools(unittest.TestCase):
    def setUp(self):
        self.examplefp_wrong=os.getcwd()+'/sometimeswrong.mecab'
        self.errortypes=['head/tail EOS','empty sent','empty line','redundant whitespaces','wrong num of features' ]
        self.wrongbits=[
            (1,1,'会い	動詞,自立,*,*,五段・ワ行促音便,連用形,*,会う,アイ,アイ',self.errortypes[0]),
            (3,1,'と	助詞,格助詞,引用,*,*,*,と,ト,ト	',self.errortypes[1]),
            (4,1,'思い 	動詞,自立,*,*,五段・ワ行促音便,連用形,思う,オモイ,オモイ',self.errortypes[1]),
            (61,2,'EOS',self.errortypes[2]),
        ]
        self.examplefp_correct='correct.mecab'

    def test_filter_errors(self):
        set_trace()
        AllegedWrong,_=mecabtools.filter_errors(self.examplefp_wrong,[7,9],StrictP=False)
        self.assertEqual(AllegedWrong,self.wrongbits)
        

if __name__=='__main__':
    unittest.main()
