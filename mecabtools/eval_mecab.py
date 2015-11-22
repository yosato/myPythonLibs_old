import os, sys, copy, re, imp, datetime
import myModule
import mecabtools

imp.reload(myModule)
imp.reload(mecabtools)

Debug=False

class WdParse:
    def __init__(self,Line,SPos):
        Wd,Rest=Line.split('\t')
        self.word=Wd
        self.sequence=Wd
        self.startpos=SPos
        self.leninchar=len(self.word)
        self.endpos=SPos+self.leninchar
        Fts=Rest.split(',')
        self.pos=Fts[0]
        self.otherfeats=Fts[1:]
    
class AmbSols:
    def __init__(self,Sols):
        (WffP,Seq)=self.wff_check(Sols)
        if not WffP:
            sys.exit('invalid solution set')
        else:
            self.sequence=Seq
            self.leninchar=len(Seq)
            self.leninwd=len(Sols)
            self.solutions=Sols


    def wff_check(self,OrgSols):
        Bool=True; Fst=True; Sentl=False
        Sols=copy.deepcopy(OrgSols)
        while not Sentl:
            if Fst:
                Fst=False
            else:
                if PrvSeq!=''.join([Wd.word for Wd in Sol]):
                    Bool=False
                    break
            if Sols:
                Sol=Sols.pop(0)
                PrvSeq=''.join([Wd.word for Wd in Sol])
            else:
                Sentl=True
        return Bool,PrvSeq
   
def main0(ResFP,SolFP):
    Strict=False
    if not mecabtools.files_corresponding_p(ResFP,SolFP,Strict=Strict):
        sys.exit('result and solutions do not seem aligned')

    if not Strict:
        ResFPRed=ResFP+'.reduced'; SolFPRed=SolFP+'.reduced'
        exist_and_new_p=lambda FP: os.path.isfile(FP) and (datetime.datetime.fromtimestamp(os.path.getctime(FP))-datetime.datetime.now()).seconds<180
        if exist_and_new_p(ResFP) and exist_and_new_p(SolFP):
            FPR=ResFP+'.reduced'; FPS=SolFP+'.reduced'

    ResSentsRaw=mecabtools.extract_sentences(ResFP)
    SolSentsRaw=mecabtools.extract_sentences(SolFP)

    process_sentsraw=lambda SentsRaw: [process_chunk(SentRaw) for SentRaw in SentsRaw]
    SentPairs=zip(process_sentsraw(ResSentsRaw),process_sentsraw(SolSentsRaw))
    Scores=score_sents(SentPairs)

    return calculate_fscore(Scores)


def calculate_fscore(Scores):
    Score,[RCnt,SCnt]=Scores
    L1Den=sum(Score)
    L2Den=Score[1]+Score[2]
    L3Den=Score[2]
    round5_pair=lambda Pair: (round(Pair[0],8),round(Pair[1],8),round((Pair[0]+Pair[1])/2,8))
    L1=round5_pair((L1Den/RCnt,L1Den/SCnt))
    L2=round5_pair((L2Den/RCnt,L2Den/SCnt))
    L3=round5_pair((L3Den/RCnt,L3Den/SCnt))
    return (('Level1',L1),('Level2',L2),('Level3',L3))


def score_sents(SentPairs):
    CumScores=([0,0,0],[0,0,0],[0,0]);Cntr=0
    for ResSent,SolSent in SentPairs:
        Cntr+=1
        if Debug:  print('Sent '+str(Cntr))
        Scores=score_sent(ResSent,SolSent)
        CumScores=cumulate_scores(CumScores,Scores)
        if Debug: print(CumScores)
    return CumScores

def score_sent(ResSent,SolSent):

    def score_sent_iter(ResSent,SolSent,CumScores):
        if isinstance(SolSent[0],AmbSols):
            Triple=handle_ambcase(SolSent,ResSent)
        else:
            if not aligned_ressol_p(ResSent[0],SolSent[0]):
                Triple=next_aligned(ResSent,SolSent)
            else:
                Triple=handle_simplecase(ResSent,SolSent)
        NResSents,NSolSents,Scores=Triple
        NScores=cumulate_scores(CumScores,Scores)
        return NResSents,NSolSents,NScores

    def handle_ambcase(OrgSolSent,OrgResSent):
        SolAmb=OrgSolSent[0]

        Score,ChosenReading=score_amb(SolAmb,OrgResSent)

        # you decide how many resunit to remove
        SolSeqLenInChars=SolAmb.leninchar
        NewResSent,ConsumedResUnitCnt=closest_smaller(OrgResSent,SolSeqLenInChars)

        if not ChosenReading:
            SolCnt=len(SolAmb.solutions[0])
        else:
            SolCnt=len(ChosenReading)
        ElCnts=[ConsumedResUnitCnt,SolCnt]

        return NewResSent,OrgSolSent[1:],(Score,ElCnts)

    def handle_simplecase(ResSent,SolSent):
        Score=[0,0,0]
        SolEntry=SolSent.pop(0);ResEntry=ResSent.pop(0)
        Bit=compare_entries(ResEntry,SolEntry)
        Score[Bit-1]=Score[Bit-1]+1
        
        return ResSent,SolSent,(Score,[1,1])

    CumScores=([0,0,0],[0,0,0],[0,0])
    while ResSent and SolSent:
        if Debug:
            print('Doing with result "'+ResSent[0].sequence+'" against solution "'+SolSent[0].sequence+'"')
        ResSent,SolSent,CumScores=score_sent_iter(ResSent,SolSent,CumScores)
        if Debug:  print(CumScores)
            
    return CumScores


def compare_entries(E1,E2):
    if E1.startpos!=E1.startpos or E1.endpos!=E2.endpos:
        return 0
    else:
        WdP=E1.word==E2.word
        PosP=E1.pos==E2.pos
        OthersP=E1.otherfeats==E2.otherfeats
        if all([WdP,PosP,OthersP]):
            return 3
        elif WdP and PosP and not OthersP:
            return 2
        elif WdP and not PosP:
            return 1


def highest_scores(ScoresL):
    Prv=ScoresL[0]
    for Cur in ScoresL[1:]:
        Highest=higher_scores(Cur,Prv)
    return Highest

def higher_lor(Scores1,Scores2):
    if Scores1==[0,0,0] and Scores2==[0,0,0]:
        return None
    elif Scores1[-1]>Scores2[-1]:
        return 'left'
    elif Scores1[-2]>Scores2[-2]:
        return 'left'
    elif Scores1[-3]>Scores2[-3]:
        return 'left'
    return 'right'

def bitwise_add(Iter1,Iter2):
    return [ Tup[0]+Tup[1] for Tup in zip(Iter1,Iter2) ]

def score_amb(SolAmb,ResSent):
    def score_reading(SolReading,ResSent):    
        # word level
        ScoreP=[0,0,0]
        for WdCntr,SolEntry in enumerate(SolReading):
            ResEntry=ResSent[WdCntr]
            Bit=compare_entries(ResEntry,SolEntry)
            if not Bit:
                break
            else:
                ScoreP[Bit-1]=ScoreP[Bit-1]+1

        return ScoreP

    Highest=[0,0,0]
    ChosenReading=None
    # reading level
    for Reading in SolAmb.solutions:
        # score a reading, and compare
        Score=score_reading(Reading,ResSent)
        if higher_lor(Highest,Score)=='right':
            Highest=Score
            ChosenReading=Reading

    return Highest,ChosenReading

def aligned_ressol_p(ResEl,SolEl):
    if isinstance(SolEl,AmbSols):
        for Seq in SolEl.values():
            for Wd in Seq:
                if Wd.startpos==ResEl.startpos:
                    return True
                else:
                    break
    elif SolEl.startpos==ResEl.startpos and SolEl.endpos==ResEl.endpos:
        return True
    return False

def sol_seqlen_inchar(SolDict):
    SolSeq0=SolDict[1]
    return sum([ len(SolWd[1]) for SolWd in SolSeq0 ])


def next_aligned(ResSent,SolSent):
        # the first element each is guaranteed to be different, so pop them
        SolSent.pop(0);SolRedCnt=1
        ResSent.pop(0);ResRedCnt=1
        # then we rely on the res position and word to find aligned equiv
        ResPosWds=[ (ResEl.startpos,ResEl.word) for ResEl in ResSent ]

        while SolSent:
            if isinstance(SolSent[0],AmbSols):
                break
            else:
                # then we try to see for each solel whether it has the equiv in res
                SolPosWd=SolSent[0].startpos,SolSent[0].word

                if SolPosWd in ResPosWds:
                    # and delete the bits up to there
                    ResRedCnt=ResRedCnt+ResPosWds.index(SolPosWd)
                    ResSent=ResSent[ResRedCnt-1:]
                    break
                else:
                    SolRedCnt+=1
                    SolSent.pop(0)
                    if SolSent and isinstance(SolSent[0],AmbSols):
                        break
            
        return ResSent,SolSent,([0,0,0],[ResRedCnt,SolRedCnt])
        
def closest_smaller(ResSent,SolLenInChars):
        CurResPos=ResSent[0].startpos
        GoalPos=CurResPos+SolLenInChars
        ResUnitCnt = 0
        while CurResPos<=GoalPos:
            ResUnitCnt+=1
            if len(ResSent)>ResUnitCnt+1:
                CurEl=ResSent[ResUnitCnt+1]
                CurResPos=CurEl.startpos
            else:
                break
        ResUnitCnt2Reduce=ResUnitCnt-1
        return ResSent[ResUnitCnt2Reduce:],ResUnitCnt2Reduce



#====

def cumulate_scores(Scores1,Scores2):
    PScores,ElCnts=zip(Scores1,Scores2)
    return (bitwise_add(PScores[0],PScores[1]),bitwise_add(ElCnts[0],ElCnts[1]))


def process_chunk(SolLines):

    def amb_miniloop(Lines, OrgPos):
        Ambs=[];CurNum=-1
        Line=Lines.pop(0)
        while Line!='====':
            if Line.startswith('@'):
                Pos=OrgPos
                CurNum+=1
                Ambs.append([])
            else:
                WdP=WdParse(Line,OrgPos)
                Ambs[CurNum].append(WdP)
                Pos=Pos+WdP.leninchar
            Line=Lines.pop(0)
        return Lines,AmbSols(Ambs),Pos

    Sentl=False
    Els=[]; Pos=0; Fst=True
    while not Sentl:
        if Fst:
            Fst=False
        else:
            if Line=='====':
                SolLines,Ambs,Pos=amb_miniloop(SolLines,Pos)
                Els.append(Ambs)
            else:
                WdP=WdParse(Line,Pos)
                Els.append(WdP)
                Pos=Pos+WdP.leninchar
           
        if not SolLines:
            Sentl=True
        else:
            Line=SolLines.pop(0)
    return Els

def main():
    Args=sys.argv
    if len(Args)!=3:
        sys.exit('we need two args, result and solution filepaths')
    
    FPs=Args[1:3]

    if not all([ os.path.isfile(FP) for FP in FPs ]):
        sys.exit('one of the files not found')

    Scores=main0(Args[1],Args[2])
    
    print('\t'.join(['','Precision','Recall','\tFScore']))
    for Level,PRF in Scores:
        P=PRF[0];R=PRF[1];F=PRF[2]
        print('\t'.join([Level,str(P),str(R),str(F)]))
    
    

if __name__=='__main__':
    main()
