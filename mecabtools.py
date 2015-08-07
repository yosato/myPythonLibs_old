import re, imp, os
import myModule
imp.reload(myModule)


# Chunk:
# SentLine:

def extract_sentences(FileP,LineNums='all',ReturnRaw=False,Print=False):
    def chunkprocess(Chunk,ReturnRaw):
        if not ReturnRaw:
            return Chunk.strip().split('\n')
    FSr=open(FileP,'rt')
    extract_chunk=lambda FSr: myModule.pop_chunk_from_stream(FSr,Pattern='EOS')
    FSr,Chunk,_,NxtLine=extract_chunk(FSr)
    Sentl=False
    Cntr=0; Sents2Ext=[]
    while not Sentl:
        Cntr+=1
        if LineNums=='all':
            Sents2Ext.append(chunkprocess(Chunk,ReturnRaw))
        else:
            if Cntr in LineNums:
                LineNums.remove(Cntr)
                Sents2Ext.append(chunkprocess(Chunk,ReturnRaw))

        FSr,Chunk,_,NxtLine=extract_chunk(FSr)
        if not LineNums or not NxtLine:
            Sentl=True
    if Print: print(Sents2Ext)
    return Sents2Ext
 
def sentence_list(FP,IncludeEOS=True):
    if IncludeEOS:
        return re.split(r'\nEOS',open(FP,'rt').read())
    else:
        return open(FP,'rt').read().split('EOS')

def file_appears_valid_p(FP,FtCnts,StrictP=True):
    def branch_and_process(StrictP,LineNum,Line,Comment,WrongLines):
        if StrictP:
            print(' '.join([Comment,'Line',str(LineNum),Line]))
            return False
        else:
            WrongLines.append((LineCnt,Line,Comment,))

    Lines=open(FP,'rt').read().strip().split('\n')
    LineCnt=len(Lines)
    WrongLines=[]
    if not Lines[-1]=='EOS':
        branch_and_process(StrictP,LineCnt,'','the end of file not an EOS',WrongLines)
    for Cntr,Line in enumerate(Lines):
        if Line=='EOS':
            if Cntr+1==LineCnt:
                if Lines[Cntr+1]=='EOS':
                    branch_and_process(StrictP,LineCnt,Line,'the end of file not an EOS',WrongLines)
        else:
            if len(re.findall(r'\s',Line))>1:
                    branch_and_process(StrictP,LineCnt,Line,'redundant whitespaces',WrongLines)
            CurFtCnt=len(Line.split('\t')[-1].split(','))
            if CurFtCnt not in FtCnts:
                Comment='wrong number ('+str(CurFtCnt)+' instead of '+repr(FtCnts)+') of features'
                branch_and_process(StrictP,LineCnt,Line,Comment,WrongLines)
    return True

def split_file_into_n(FP,N):
    Sents=sentence_list(FP)
    SplitIntvl=len(Sents)//N
    with open(FP,'rt') as FSr:
        Chunk=[];ChunkCnt=1
        for (Cntr,LiNe) in enumerate(FSr):
            Chunk.append(LiNe)
            if Cntr!=0 and Cntr % SplitIntvl==0:
                open(FP+str(ChunkCnt),'wt').write(''.join(Chunk)+'EOS\n')
                Chunk=[];ChunkCnt=ChunkCnt+1
                if ChunkCnt==N:
                    open(FP+str(ChunkCnt),'wt').write(FSr.read())

file_appears_valid_p('/Users/yosato/Dropbox/Mecab/test/kansai/corpus/corpus_train_new.mecab',[7,9])
split_file_into_n('/Users/yosato/Dropbox/Mecab/test/kansai/corpus/corpus_train_new.mecab',4)

def extract_sentences_fromsolfile(SolFileP):
    Sents=extract_sentences(SolFileP)
    return [ extract_string_fromsentlines(Sent,SolP=True) for Sent in Sents  ]


def extract_string_fromsentlines(SentLines,SolP=False):
    extract_string_normal=lambda SentLines: ''.join([Line.split('\t')[0] for Line in SentLines])
    if SolP:
        return re.sub(r'====@1([^@]+)@.+?====',r'\1',extract_string_normal(SentLines))
    else:
        return extract_string_normal(SentLines)


def files_corresponding_p(FPR,FPS,Strict=True,OutputFP=None):

    def write_errors(FPR,FPS):
        Dir=os.path.dirname(FPR)
        FNR=os.path.basename(FPR)
        FNS=os.path.basename(FPS)
        
        with open(os.path.join(Dir,FNR+'.'+FNS+'.errors'),'wt') as FSwErr:
            for SentNum,SentR,SentS in Errors:
                FSwErr.write('Sent '+str(SentNum)+': '+SentR+'\t'+SentS+'\n')

    Bool=True

    SentLinesR=extract_sentences(FPR)
    SentLinesS=extract_sentences(FPS)

    Thresh=len(SentLinesR)//15
    
    LenDiff=len(SentLinesR)-len(SentLinesS)
    if LenDiff!=0:
        if LenDiff>0:
            Larger='results'
        else:
            Larger='solutions'

        if Strict:
            print('Sentence counts do not match')
            print('there are '+str(abs(LenDiff))+' more sentenes in '+Larger+' file')
            return False
        elif abs(LenDiff)>Thresh:
            print('Too much difference in sentence counts')
            return False
        else:
            print('Warning: difference in sentence count, there will be errors')
            print('there are '+str(abs(LenDiff))+' more sentenes in '+Larger+' file')

    Errors=[]; Corrects=[]
    for Cntr,(SentR,SentS) in enumerate(zip(SentLinesR,SentLinesS)):
        StringR=extract_string_fromsentlines(SentR)
        StringS=extract_string_fromsentlines(SentS,SolP=True)
        if StringR==StringS:
            Corrects.append((str(Cntr),SentR,SentS))
        else:
            Errors.append((str(Cntr),StringR,StringS))
            if Strict:
                print('error, aborting')
                print(Errors)
                return False
            else:
                if len(Errors)>Thresh:
                    print('too many errors, at '+', '.join([ Error[0] for Error in Errors])+'. For details see [combinedfilenames].errors')
                    write_errors(FPR,FPS)
                    return False

    if not Strict:
        FSwR=open(FPR+'.reduced','wt')
        FSwS=open(FPS+'.reduced','wt')
        for _,SentR,SentS in Corrects:
            FSwR.write('\n'.join(SentR)+'\nEOS\n')
            FSwS.write('\n'.join(SentS)+'\nEOS\n')
        FSwR.close();FSwS.close()
        write_errors(FPR,FPS)
        
    return Bool


Sents=extract_sentences_fromsolfile('/Users/yosato/kevinToEdit/Yo/solutions.b1new.mecab')
open('/Users/yosato/kevinToEdit/Yo/sentences.b1.txt1','wt').write('\n'.join(Sents))
