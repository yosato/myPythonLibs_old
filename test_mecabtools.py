import unittest,imp,os,copy,re
import mecabtools
from pdb import set_trace
imp.reload(mecabtools)

class TestMecabTools(unittest.TestCase):
    def setUp(self):
        self.examplefp=os.getcwd()+'/sometimeswrong.mecab'
        self.errortypes=['head/tail EOS','empty sent','empty line','redundant whitespaces','wrong num of features' ]
        #set_trace()
#        with open(self.examplefp) as FSr:
#            WholeStr=FSr.read()
#            self.alllines=WholeStr.split('\n')
        self.alllines=open(self.examplefp).read().split('\n')
        self.firstsentlines=self.alllines[1:9]
        self.secondsentlines=self.alllines[10:34]
        self.thirdsentlines=self.alllines[36:77]
        self.firstsentwrongs=[
            (('会い	動詞,自立,*,*,五段・ワ行促音便,連用形,*,会う,アイ,アイ',self.errortypes[-1]),('会い	動詞,自立,*,*,五段・ワ行促音便,連用形,*,会う,アイ,アイ',self.errortypes[-1])),
            (('と	助詞,格助詞,引用,*,*,*,と,ト,ト	',self.errortypes[-2]),'と	助詞,格助詞,引用,*,*,*,と,ト,ト'),
            (('思い 	動詞,自立,*,*,五段・ワ行促音便,連用形,思う,オモイ,オモイ',self.errortypes[-2]),'思い	動詞,自立,*,*,五段・ワ行促音便,連用形,思う,オモイ,オモイ'),
            ((' ',self.errortypes[2]),None),
            ]

        FstSentNoRecover=copy.copy(self.firstsentlines)
        FstSentNoRecover[0]=self.firstsentwrongs[0][0]
        FstSentNoRecover[2]=self.firstsentwrongs[1][0]
        FstSentNoRecover[3]=self.firstsentwrongs[2][0]
        FstSentNoRecover[6]=self.firstsentwrongs[3][0]
        self.fstsentnorecover=FstSentNoRecover
        FstSentRecover=copy.copy(self.firstsentlines)
        FstSentRecover[0]=self.firstsentwrongs[0][0]
        FstSentRecover[2]=self.firstsentwrongs[1][1]
        FstSentRecover[3]=self.firstsentwrongs[2][1]
        FstSentRecover.pop(6)
        self.fstsentrecover=FstSentRecover
        
        self.wrongbits=[
            (1,1,'EOS',self.errortypes[0]),
 
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

    def test10_something_wrong_insideline(self):
        AllLines=self.alllines
        AllegedErrorType=mecabtools.something_wrong_insideline(AllLines[1],[7,9])
        self.assertEqual(AllegedErrorType,self.errortypes[-1])

        AllegedErrorType=mecabtools.something_wrong_insideline(AllLines[3],[7,9])
        self.assertEqual(AllegedErrorType,self.errortypes[-2])

        AllegedErrorType=mecabtools.something_wrong_insideline(AllLines[7],[7,9])
        self.assertEqual(AllegedErrorType,self.errortypes[2])
        
    def test15_filter_errors_sent_norecover(self):
        #set_trace()
        FilteredSent=mecabtools.filter_errors_sent(self.firstsentlines,[7,9],Recover=False)
        self.assertEqual(FilteredSent,self.fstsentnorecover)

    def test15_filter_errors_sent_recover(self):
#        set_trace()
        FilteredSent=mecabtools.filter_errors_sent(self.firstsentlines,[7,9],Recover=True)
        self.assertEqual(FilteredSent,self.fstsentrecover)

    def test20_filter_errors_strict(self):
        set_trace()
        AllegedFilteredSents=mecabtools.filter_errors(self.examplefp,[7,9],StrictP=True)
        RealFilteredSents=[('','empty sent'),
                           self.fstsentnorecover,
                           self.secondsentlines,
                           ('','empty sent'),
                           self.thirdsentlines,
                           ('','tail EOS absent')
                           ]
        self.assertEqual(len(AllegedFilteredSents),len(RealFilteredSents))
        for ASent,RSent in zip(AllegedFilteredSents,RealFilteredSents):
            print(ASent)
            print(RSent)
            self.assertEqual(ASent,RSent)
        

#    def test30_filter_errors_plain(self):
#        set_trace()
#        AllegedWrong,AllegedCorrects=mecabtools.filter_errors(self.examplefp,[7,9],StrictP=False)
#        self.assertEqual(AllegedWrong,self.wrongbits)
#        self.assertEqual(AllegedCorrects,self.corrects)

#    def test40_filter_errors_recover(self):
#        #set_trace()
#        AllegedWrongs,AllegedCorrects=mecabtools.filter_errors(self.examplefp,[7,9],StrictP=False,Recover=True)
#        self.assertEqual(AllegedWrongs,[self.wrongbits[1]]+[self.wrongbits[5]])

#    def test50_check_and_remove_errors(self):
#        set_trace()
#        mecabtools.check_and_remove_errors(self.examplefp,[7,9])



        

if __name__=='__main__':
    unittest.main()
