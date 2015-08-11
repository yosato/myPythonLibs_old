import imp,sys,math,copy,collections,fractions
import myModule
imp.reload(myModule)
Debug=1

if Debug:
    from pdb import set_trace

__author__ = 'yosato'

class EquivalEqual:
    def __init__(self):
        def __eq__(self,Tgt):
            if type(self)!=type(Tgt):
                return False
                for Attr, Val in self.__dict__():
                    if Tgt.__dict__[Attr]!=Val:
                        return False
            return True

# use this guy for unigrams. to be used for posthoc dist also.
class DiscDist(EquivalEqual):
    '''
      discrete distribution of one random var. from occurrences, you mainly get marginal prob.
      obligatory input: normally a dict representing {evt:occ} 
    '''
    def __init__(self,EvtProbPairsOrEvtOccPairs,Occs={},TotalOccs=0):
        super().__init__()
        if not EvtProbPairsOrEvtOccPairs or type(list(EvtProbPairsOrEvtOccPairs.values())[0]).__name__=='int':
            self.evtocc=EvtProbPairsOrEvtOccPairs
            self.occs=[ Occ for Occ in self.evtocc.values() ]
            self.totalocc=sum(self.occs)
            EvtProbPairs=self.evtocc2evtprob()
        else:
            EvtProbPairs=EvtProbPairsOrEvtOccPairs
            self.evtocc=Occs
            self.totalocc=TotalOccs
        self.evtprob=EvtProbPairs
        self.probs=[ Probs for Probs in self.evtprob.values() ]
      #  self.sum_check()
     #  self.evtprob=EvtProbPairs

    def filter_evts(self,Thresh):
        if type(Thresh).__name__=='int':
            Items=self.evtocc.items()
        elif type(Thresh).__name__=='float':
            Items=self.evtprob.items()
        return { Evt:Occ  for (Evt,Occ) in Items if Occ>Thresh }
            
    def evtocc2evtprob(self):
        return { Evt:fractions.Fraction(Occ,self.totalocc) for Evt,Occ in self.evtocc.items() }
        
    def format_check(self,EvtProbPairs):
        Bool=True
        for Evt,Prob in EvtProbPairs:
            if not type(Evt).__name__!='str' or not type(Prob).__name__!='float':
                return False
        return Bool
    def sum_check(self):
        if sum(self.probs)==1:
            return True
        else:
            return False

class BiStats(EquivalEqual):
    '''
      embracing stuff, given plural conddists, churn out various stats including
      joint probabilities, mutual information and pointwise counterpart
    '''
    def __init__(self,CDsR,Criteria=[],U2Grams=[],SentCnt=None,UThresh=1):
        # for conddists, we accept the raw dict or DiscDist for postdists, and keep them both for different attributes.
        # special case for unigrams
        if CDsR and type(list(CDsR.values())[0]).__name__=='int':
            self.rawconddists={ ():{U1:PD} for (U1,PD) in CDsR.items() }
        else:
            self.rawconddists={ ((U1,) if type(U1).__name__=='str' else U1):PD for (U1,PD) in CDsR.items() }
        Items=self.rawconddists.items()
        if Items:
            self.n=len(list(Items)[0][0])+1
        else:
            self.n=0
        self.conddists={ U1:DiscDist(PostDist) for U1,PostDist in Items }
        self.orgbgcount=sum(PostDist.totalocc for PostDist in self.conddists.values())
        self.eossym='eos%'
        self.bossym='%bos'
        if SentCnt:
            self.sentcnt=SentCnt
        else:
            self.sentcnt=self.sum_allpostdists(self.pick_cds_unit1_satisfies_f(self.conddists,(lambda X: self.bossym in X)))
        if U2Grams:
            self.u2grams=U2Grams
        else:
            self.u2grams=self.find_u2grams()
        self.u1grams=self.find_u1grams()

        self.filteredbistats=self.generate_filteredbigramstats(Criteria=Criteria,UThresh=UThresh)
        IndBiStats={}
        for U1,PostDist in self.filteredbistats.items():
            for U2,SpecBG in PostDist.items():
                IndBiStats[(U1,U2)]=SpecBG
        self.sortedbistats=sorted(IndBiStats.items(),key=lambda x:(x[1].nmi,x[0]),reverse=True)
        if self.orgbgcount==0:
            self.filterrate=1
        else:
            self.filterrate=1-(len(self.sortedbistats)/self.orgbgcount)
    def stringify_topranked_bistats(self,Thresh=100):
        Str=''
        pdb.set_trace()
        for Cntr,(BG,BS) in enumerate(self.sortedbistats):
            if Cntr>Thresh:
                break
            else:
                Str=Str+'\n'+repr(BG)+'\t'+repr(BS.mis)

    def pick_cds_unit1_satisfies_f(self,CDs,F):
        return { Unit1:PostDist for Unit1,PostDist in CDs.items() if F(Unit1) }        

    def sum_allpostdists(self,CDs):
        return sum([ PostDist.totalocc for PostDist in CDs.values() ])
        
    def find_u1grams(self):
        U1Raw={}
        if not self.conddists:
            return DiscDist({})
        for (Unit1,Unit2Dist) in self.conddists.items():
            #if Cntr%1000==0: print(Cntr)
            myModule.increment_diccount(U1Raw,Unit1,Step=Unit2Dist.totalocc,Inset=True)
        return DiscDist(U1Raw)

    def find_u2grams(self):
        Unit2Occs={}
        for Unit2Dist in self.conddists.values():
            for Unit2,Occ in Unit2Dist.evtocc.items():
                myModule.increment_diccount(Unit2Occs,Unit2,Step=Occ,Inset=True)
        return DiscDist(Unit2Occs)
            

    def generate_filteredbigramstats(self,Criteria=[],UThresh=1):
        print('filtering bistats, of which unit1s number '+str(len(self.conddists)))
        FBiStats={}#; RawBGs=[]
        for Cntr,(Unit1,PostDist) in enumerate(self.conddists.items()):
            if Cntr!=0 and Cntr%2000==0: print(str(Cntr)+' unit1s done')
            (U1PostDists,_RawBG)=self.generate_fbigramstat_perunit1(Unit1,PostDist,Criteria,UThresh=UThresh)
            if U1PostDists:
                FBiStats[Unit1]=U1PostDists
                #RawBGs.extend(RawBG)
        return FBiStats#,RawBGs

    # this is for one conddist. that is only one unit1, which can be a compound, plus postdist of singleton unit2s
    def generate_fbigramstat_perunit1(self,Unit1,PostDist,Criteria=[],UThresh=1):
        BGsPerUnit1={}; RawBGsPerUnit1=[]
        Unit1Stats=(self.u1grams.evtocc[Unit1],self.u1grams.totalocc)
        Unit2VarOcc=PostDist.totalocc

        for Unit2,Unit2Occ in PostDist.evtocc.items():
            if Unit2 in self.u2grams.evtocc.keys():
                Unit2Prob=self.u2grams.evtprob[Unit2]
                Unit2Stats=(Unit2Occ,Unit2VarOcc,Unit2Prob)
                BGStat=SpecBiGram(Unit1,Unit1Stats,Unit2,Unit2Stats)

                if (BGStat.unit1occ<=UThresh and BGStat.unit2condvarocc<=UThresh) or (Criteria and not self.bgstat_criteria_met_p(BGStat,Criteria)):
                    pass
                else:
                    BGsPerUnit1[Unit2]=BGStat
                    RawBGsPerUnit1.append(myModule.flatten_tuple(Unit1)+(Unit2,))

        return BGsPerUnit1,RawBGsPerUnit1

    def generate_trigramstat(self):
        BiNowUni={}; TriNowBis=[]
        # first you need (u1,u2) figures
        PostDist={}
        for Wd1,BiStats in self.filteredbistats.items():
            if not BiStats:
                Wd12Occ=0
            else:
                for Wd2,Wd12Stat in BiStats.items():
#                    PostDist[Wd12Stat.unit2]=Wd12Stat.unit2condocc
                    Wd12Occ=Wd12Stat.unit2condvarocc
  #          generate_bigramstat_p
#                BiNowUni[(Wd1,Wd2,)]=Wd12Stat.jointprob
  #              if Wd2 in self.bistats.keys():
    #                for Wd3,BiStat in self.bistats[Wd2].items():
      #                  BiWd3GivenWd12=self.bistats[Wd2][Wd3]
        #                Wd3OccGivenWd12=BiWd3GivenWd12.unit2condocc
          #              Wd3VarOccGivenWd12=BiWd3GivenWd12.unit2varocc
            #            TriNowBi=BiGram((Wd1,Wd2,),Wd12Stat.Wd3,)
              #          TriNowBis.append(TriNowBi)
        #BiNowUni=DiscDist(BiNowUni)
        #Hi=UniBiStats(TriNowBis,BiNowUni)
        return BiNowUni,TriNowBis

    def get_raw_pairs(self):
        Pairs=[]
        for U1,U2Dist in self.conddists.items():
            for U2 in U2Dist.evtocc.keys():
                Pairs.append((U1,U2,))
        return Pairs

    def bgstat_criteria_met_p(self,BGStat,Criteria,BoolOp='or'):
        for Att,Val in Criteria:
            if BGStat.__dict__[Att]>Val:
                if BoolOp=='or':
                    return True
            else:
                if BoolOp=='and':
                    return False
        if BoolOp=='or':
            return False
        elif BoolOp=='and':
            return True

    def filter_bgstats(self):
        return [ BGStat for BGStat in self.bgstats if self.bgstat_criteria_met_p(BGStat) ]
            

        

class SpecBiGram(EquivalEqual):
    '''
      Unit1 varoccurrence (total occs for that random var) 
      posthoc conditional distribution (Unit2|Unit1) 
      single Unit1, with discdist.
    '''
    def __init__(self,Unit1,Unit1Stats,Unit2,Unit2Stats):
        self.unit1=Unit1
        self.unit2=Unit2
        self.unit12=list(Unit1)+[Unit2]
        self.unit1occ=Unit1Stats[0]
        self.unit1varocc=Unit1Stats[1]
        self.unit1prob=fractions.Fraction(self.unit1occ, self.unit1varocc)
        self.unit2condocc=Unit2Stats[0]
        self.unit2condvarocc=Unit2Stats[1]
        self.unit2condprob=fractions.Fraction(self.unit2condocc, self.unit2condvarocc)
        self.jointprob=self.unit1prob*self.unit2condprob

        self.mis=all_mis(self.unit1prob,Unit2Stats[2],self.jointprob)
        self.nmi=self.mis[1][1]

        #BiStatsPerUnit1[Wd2]=BiStat(Wd1Prob,Wd2Prob,PostDist,Joint,MIs)

    def render_raw(self,OccOrProb='occ'):
        if OccOrProb=='prob':
            ToReturn=self.conddist.evtprob
        elif OccOrProb=='occ':
            ToReturn=self.conddist.evtocc
        return (self.unit1,ToReturn,)

    










    
def rawfile2objs(RawFPWdPerLine,OutputFP=None):
    if not OutputFP:
        OutputFP=RawFPWdPerLine+'.occ'
    UniDict={}; BiDict={}; Prv=''
    for Wd in open(RawFPWdPerLine):
        myModule.increment_dictcnt(UniDict,Wd)
        if Prv in BiDict.keys():
            myModule.increment_dictcnt(BiDict[Prv])
        else:
            BiDict[Prv]={Wd:1}
        
    myUGs=DiscDist(UniDict)
    myBGStats=[]
    for Wd,Dict in BiDict.items():
        myBGStats.append(BiStat(Wd,Dict))

    return myUGs,myBGStats
        

def bit_required(Prob):
    Bit= math.log(Prob,2)
    return Bit

def remove_adjust_distribution(OrgDist,Items2Remove):
    Prob2Remove=0
    DiscDist=copy.deepcopy(OrgDist)
#    (NonSeenCnt,SmthdProb)=copy.copy(OrgSmthedDist[1])
    for Item in Items2Remove:
        Prob2Remove=Prob2Remove+DiscDist[Item]
        del DiscDist[Item]
    Coeff=1+(Prob2Remove/1)
    NewDiscDist={}
    for (Key,Prob) in DiscDist.items():
        NewDiscDist[Key]=Prob*Coeff
#    NewSmthd=(NonSeenCnt,SmthdProb*Coeff)
    Val=check_sumzero(NewDiscDist)
    return NewDiscDist

def check_sumzero(Dist):
    return sum(Dist.values())


def info_gain(Entropy1,Item,Dist):
    Entropy2=entropy(remove_adjust_distribution(Dist,[Item]))
    return Entropy2,Entropy1-Entropy2


def entropy(DiscDist):
    NEntropy=0
#    DiscDist,Smoothed=SmoothedDiscDist
    for _EventName,Prob in DiscDist.items():
        NEntropy=NEntropy+entropy_moto(Prob)
#    (Cnt,Prob)=Smoothed
#    Entropy=Entropy+(entropy_moto(Prob)*Cnt)

    return -NEntropy

def mutual_info_unit(Marg1,Marg2,Joint):
    return pw_mutual_info(Marg1,Marg2,Joint)*Joint

def all_mis(M1,M2,Joint):
    M1=float(M1); M2=float(M2); Joint=float(Joint)
    if Joint==1:
        PWMI=MI=NPWMI=NMI=0
    else:
        PWMI=pw_mutual_info(M1,M2,Joint)
        NPWMI=PWMI/-bit_required(Joint)
        MI=mutual_info_unit(M1,M2,Joint)
        NMI=MI/-entropy_moto(Joint)
    return (MI,NMI),(PWMI,NPWMI)

def normalised_pwmi_mi(Marg1,Marg2,Joint):
    PWMI=pw_mutual_info(Marg1,Marg2,Joint)
    NPWMI=-(PWMI/bit_required(Joint))
    NMIUnit=-(Joint/(Joint*bit_required(Joint)))
    return NPWMI,NMIUnit

def normalised_mutual_info_unit(Marg1,Marg2,Joint):
    return mutual_info_unit(Marg1,Marg2,Joint)/-entropy_moto(Joint)

def entropy_moto(Prob):
    return Prob*bit_required(Prob)

def pw_mutual_info(Marg1,Marg2,Joint):
    PWMI=bit_required(Joint/(Marg1*Marg2))
    return PWMI

def pw_mutual_info2(Marg1,Marg2,Cond2given1):
    Joint=Cond2given1*Marg1
    PWMI=bit_required(Joint/(Marg1*Marg2))
    return PWMI

def normalised_pwmi(Marg1,Marg2,Joint):
    return pw_mutual_info(Marg1,Marg2,Joint)/-bit_required(Joint)


def condprob_fromjoint(Joint,MargGiven):
    return Joint/MargGiven
