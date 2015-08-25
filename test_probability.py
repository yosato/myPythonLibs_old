from pdb import set_trace

import imp,sys,os,fractions,copy

sys.path.append(os.getenv('HOME')+'/myProgs/var_ngram')

import unittest
import count_ngrams, probability
imp.reload(probability)
imp.reload(count_ngrams)


class TestNPlus1GramStats(unittest.TestCase):
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
        UGsR=count_ngrams.collect_nplus1grams(self.sents,None)
        self.unistats=probability.NPlus1GramStats(UGsR)
        U2Grams=self.unistats.u2grams
        BGsR=count_ngrams.collect_nplus1grams(self.sents,self.unistats)
        self.bistats=probability.NPlus1GramStats(BGsR,U2Grams=U2Grams)

    def test10_ugram_loop(self):
#        set_trace()
        UG1=self.bistats.find_u1grams()
        UG2=self.bistats.find_u2grams()
        ExpectedUG1={('%bos',):8,('w1',):9,('w2',):8,('w3',):2,('w4',):2,('w5',):3}
        ExpectedUG2={'w1':9,'w2':8,'w3':2,'w4':2,'w5':3,'eos%':8}
        self.assertDictEqual(UG1.evtocc,ExpectedUG1)
        self.assertDictEqual(UG2.evtocc,ExpectedUG2)

    def test20_generate_fbigramstat_perunit1_nofilter(self):
#        set_trace()
        BGsForWd1=self.bistats.generate_fbigramstat_perunit1(('w1',),self.bistats.conddists[('w1',)],Threshs=([],0))
                                                                      
        AllegedBGForWd1={ ( BG.unit2, BG.unit2condocc, BG.jointprob) for BG in BGsForWd1[0].values() }
        self.assertEqual(len(AllegedBGForWd1),5)
        RealBGForWd1={ ('w1', 1, fractions.Fraction(1,32)),
                       ('w2', 4, fractions.Fraction(4,32)), 
                       ('w3', 1, fractions.Fraction(1,32)), 
                       ('w5', 2, fractions.Fraction(2,32)),
                       ('eos%', 1, fractions.Fraction(1,32))
                                      }
        self.assertEqual(AllegedBGForWd1,RealBGForWd1)

    def test22_generate_bigramstat_perunit1_filter(self):
#        set_trace()
        BiStatsFilter=copy.deepcopy(self.bistats)
        BGsForWd1Filtered=BiStatsFilter.generate_fbigramstat_perunit1(('w1',),self.bistats.conddists[('w1',)],Threshs=([('nmi',0.2)],1,))
        AllegedBGForWd1Filtered={ ( BG.unit2, BG.unit2condocc, BG.jointprob)  for BG in BGsForWd1Filtered[0].values() }
        self.assertEqual(len(AllegedBGForWd1Filtered),3)
        RealBGForWd1Filtered={ #('w1', 1, fractions.Fraction(1,32)),
                       ('w2', 4, fractions.Fraction(4,32)), 
                       ('w3', 1, fractions.Fraction(1,32)), 
                       ('w5', 2, fractions.Fraction(2,32)),
                      # ('eos%', 1, fractions.Fraction(1,32))
                                      }
        self.assertEqual(AllegedBGForWd1Filtered,RealBGForWd1Filtered)

    def test24_generate_filteredstats(self):
        set_trace()
        BiStatsFilter=copy.deepcopy(self.bistats)
        BGsForWd1Filtered=BiStatsFilter.generate_filteredstats(Threshs=([('nmi',0.2)],1,))
        AllegedBGForWd1Filtered={ ( BG.unit2, BG.unit2condocc, BG.jointprob)  for BG in BGsForWd1Filtered[0].values() }
        self.assertEqual(len(AllegedBGForWd1Filtered),3)
        RealBGForWd1Filtered={ #('w1', 1, fractions.Fraction(1,32)),
                       ('w2', 4, fractions.Fraction(4,32)), 
                       ('w3', 1, fractions.Fraction(1,32)), 
                       ('w5', 2, fractions.Fraction(2,32)),
                      # ('eos%', 1, fractions.Fraction(1,32))
                                      }

        

if __name__=='__main__':
    unittest.main()
