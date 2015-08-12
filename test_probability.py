from pdb import set_trace

import imp,sys,os,fractions

sys.path.append(os.getenv('HOME')+'/myProgs/var_ngram')

import unittest
import count_ngrams, probability
imp.reload(probability)
imp.reload(count_ngrams)


class TestUniBiStats(unittest.TestCase):
    def setUp(self):
 #       set_trace()
        self.sents=[ 'w1 w2 w3', 
                     'w1 w2 w4', 
                     'w1 w2 w4', 
                     'w1 w2 w5', 

                     'w2 w1 w3', 
                     'w2 w1 w1', 
                     'w2 w1 w5',
                     'w2 w1 w5' ]
        
        self.text='\n'.join(self.sents)
        
        set_trace()
        self.ugrams=probability.DiscDist(probability.list2countdic(count_ngrams.sents2sentunits(self.sents)))
        self.BiStats=probability.BiStats(count_ngrams.collect_nplus1grams(self.text,Level='word'))
#        self.CDs={ Unit1:probability.DiscDist(PostDist) for Unit1,PostDist in self.CDsR.items() }
#        self.BiStats=probability.BiStats(self.CDs)


    def test10_ugram_loop(self):
        UG1,UG2=self.BiStats.ugram_loop()
        ExpectedUG1={('%bos',):8,('w1',):9,('w2',):8,('w3',):2,('w4',):2,('w5',):3}
        ExpectedUG2={'w1':9,'w2':8,'w3':2,'w4':2,'w5':3,'eos%':8}
        self.assertDictEqual(UG1.evtocc,ExpectedUG1)
        self.assertDictEqual(UG2.evtocc,ExpectedUG2)

    def test15_stringify_bistats(self):
        set_trace()
        ExpectedStr=''
        AllegedStr=self.BiStats.stringify_bistats()
        self.assertEqual(ExpectedStr,AllegedStr)
        

    def test02_generate_bigramstat_perunit1(self):
        

        BGsForWd1=self.BiStats.generate_bigramstat_perunit1(('w1',),self.BiStats.conddists[('w1',)])
        AllegedBGForWd1={ ( #BG.unit1, BG.unit1occ, #BG.unit1prob, 
                                           BG.unit2, BG.unit2condocc, #BG.unit2prob,
                                         BG.jointprob)  for BG in BGsForWd1.values() }
        self.assertEqual(len(AllegedBGForWd1),5)
        RealBGForWd1={ ('w1', 1, fractions.Fraction(1,32)),
                       ('w2', 4, fractions.Fraction(4,32)), 
                       ('w3', 1, fractions.Fraction(1,32)), 
                       ('w5', 2, fractions.Fraction(2,32)),
                       ('eos%', 1, fractions.Fraction(1,32))
                                      }
        self.assertEqual(AllegedBGForWd1,RealBGForWd1)

    def test03_generate_bigramstat_perunit1_filtering(self):
        BGsForWd1Filtered=self.BiStats.generate_bigramstat_perunit1('w1',self.BiStats.conddists['w1'],Criteria=[('nmi',0.2)])
        AllegedBGForWd1Filtered={ ( #BG.unit1, BG.unit1occ, #BG.unit1prob, 
                                           BG.unit2, BG.unit2condocc, #BG.unit2prob,
                                         BG.jointprob)  for BG in BGsForWd1Filtered.values() }
        self.assertEqual(len(AllegedBGForWd1Filtered),2)
        RealBGForWd1Filtered={ #('w1', 1, fractions.Fraction(1,32)),
                       ('w2', 4, fractions.Fraction(4,32)), 
                      # ('w3', 1, fractions.Fraction(1,32)), 
                       ('w5', 2, fractions.Fraction(2,32)),
                      # ('eos%', 1, fractions.Fraction(1,32))
                                      }
        self.assertEqual(AllegedBGForWd1Filtered,RealBGForWd1Filtered)


if __name__=='__main__':
    unittest.main()
