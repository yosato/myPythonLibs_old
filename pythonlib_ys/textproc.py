import imp,re,sys,os,subprocess
imp.reload(pythonlib_ys)
from pythonlib_ys import main


def identify_chartype(Char):
    return identify_type_char(Char)

def identify_type_char(Char):
    TCMap={'num': [(48,57,),(65296,65305,)],
           'roman': [('0041','005a',),('0061','0077',),('ff21','ff3a',),('ff41','ff5a',)],
           'asciisym': [('0000','002f',),('007b','00bb'), (58,64,),(91,96,),(123,126,)],#ascii symbols
           'cjksym':[(8192,8303,),(8591,8597,),(9632, 9983,),('3000','3004',),('3008','303f',),(65280,65519,)],
        'shape':[('25a0','25ff')],
           'han': [(19968, 40959,),('f900','faff'),('3005','3006')],
           'hiragana': [('3040','309f',)],
        'katakana': [('30a0','30ff',)],
        'hangul': [('AC00','D7AF',)], 
        'jamo': [('1100','11FF',),('3130','318f',)],
        'ws': [('0009','0009',),('000A','000D',),('0020','0020',),('3000','3000',)],
     }

    for (Type,Ranges) in TCMap.items():
        if main.in_ranges(ord(Char), Ranges):
            return Type
    return 'unknown'

def upto_first_diff(Str1,Str2):
    for Cntr,(Char1,Char2) in enumerate(zip(Str1,Str2)):
        if not Char1==Char2:
            return Cntr
    return Cntr
           

def string_sharerate(Str1,Str2):
    IndF=upto_first_diff(Str1,Str2)
    IndB=upto_first_diff(Str1[IndF:][::-1],Str2[IndF:][::-1])
    Min=min([len(Str1),len(Str2)])
    return (IndF+IndB)/Min

Rate=string_sharerate('aiueo','aiuEEo')
        
        

def at_least_one_of_chartypes_p(Str,Types,UnivTypes=[]):
    Bool=False
    Types.extend(UnivTypes)
    for Char in Str:
        CharType=identify_type_char(Char)
        if CharType in Types:
            Bool=True; break
    return Bool


def of_chartypes_p(Char,Types,UnivTypes=[]):
    Types.extend(UnivTypes)
    CharType=identify_type_char(Char)
    return CharType in Types

def all_of_types_p(Str,Types,UnivTypes=['ws']):
    all_of_chartypes_p(Str,Types,UnivTypes=UnivTypes)

def all_of_chartypes_p(Str,Types,UnivTypes=['ws']):

    Bool=True

    for Char in Str:
        if not of_chartypes_p(Char,Types+UnivTypes):
            Bool=False; break
    return Bool


#def all_roman(Str):
#    return all( identify_type_char(Char)=='roman' or \
#                identify_type_char(Char)=='ws' or \
#                identify_type_char(Char)=='num' or \
#                identify_type_char(Char)=='sym' for Char in Str)
             

def identify_type_wd(Wd):
    if all( identify_type_char(Char)=='num' for Char in Wd):
        Val='num'
    elif all( identify_type_char(Char)=='sym' for Char in Wd):
        Val='sym'
    elif all( identify_type_char(Char)=='others' for Char in Wd):
        Val='others'
    else:
        Val= 'mixed'      
    return Val

def identify_type_wd_loose(Wd):
    Val='others'
    if any( identify_type_char(Char)=='jp' for Char in Wd):
        Val='jp'
    if all( identify_type_char(Char)=='roman' for Char in Wd):
        Val='roman'
    return Val



def escape_sp_chars(Pattern):
    SpChars=['$', '?', '+', '*', '{', '}', '[', ']', '(', ')','^','|','.']
    if chr(92) in Pattern:
        Pattern=Pattern.replace(chr(92),chr(92)+chr(92))
    if any([ (Char in SpChars) for Char in Pattern ]):
        for SpChar in SpChars:
            Pattern=Pattern.replace(SpChar,chr(92)+SpChar)
    return Pattern

def pop_chunk_from_stream(FSr,Pattern='\t',Type='delim',IncludeDelim=False,FstIgnore=False,ForwardInclude=''):
    '''
    given a stream, return four things
    1 the shifted stream, the chunk removed
    2 chunk, that's a usually multi-line string up to the delim or regex
    3 line count of a chunk
    4 the next line
    three types
    1 delim delimiter, fixed str
    2 regex, pattern delimiter
    3 cont, for continued pattern like sorted list of strings. i.e.
      AA\t ...
      AA\t ...
      AA\t ...
      BB\t ...
      'pattern' here is the column separator, and use the str up to the separator
    '''
    Chunk=''
    PrevPos=0;LineCnt=0
    Line=FSr.readline()
    if Line:
        if Type=='delim':
            Cond2AccumF=(lambda Line,Pattern: (Line!='' and Line.strip()!=Pattern))
        elif Type=='regex':
            Cond2AccumF=(lambda Line,Pattern: (Line!='' and not re.match(r'%s'%Pattern,Line.strip()))) 
        elif Type=='cont':
            # you may have dots and things for continued pattern to use
            Pattern=escape_sp_chars(Pattern)
            Pattern=Line.split(Pattern)[0]+'\t'
            Cond2AccumF=(lambda Line,Pattern: (Line!='' and re.match(r'^%s'%Pattern,Line.strip())))

        if FstIgnore and LineCnt==0:
            ContinueP=True
        else:
            ContinueP=Cond2AccumF(Line,Pattern)

        while ContinueP:
           # print(Line)
            LineCnt=LineCnt+1
            Chunk=Chunk+Line
#            if Type=='cont':
#                PrevPos=FSr.tell()
            Line=FSr.readline()
            ContinueP=Cond2AccumF(Line,Pattern)

        # for a chunk with a delimiter you might want to include it 
        if IncludeDelim:
            Chunk=Chunk+Line
        if ForwardInclude:
            Chunk=ForwardInclude+Chunk
            

        LineCnt=LineCnt+1
                
    return FSr,Chunk,LineCnt,Line

def string_pop(Str,Pos,End=0):
    End=Pos+1
    Popped=Str[Pos:End]
    Rest=Str[:Pos]+Str[End:]
    return (Popped,Rest)
    
def split_str_into_sents(Str):
    import re
    SentPuncts=re.split(r'([!?。]\s+)',Str)
    Len=len(SentPuncts)
    Sents=[ SentPunct+SentPuncts[Ind+1] for (Ind,SentPunct) in enumerate(SentPuncts) if Ind%2==0 and Ind<Len-1 ]
    return Sents

def upto_first(Str,Up2What):
    NewSubStr=''
    for Char in Str:
        if Char==Up2What:
            return NewSubStr
        else:
            NewSubStr=NewSubStr+Char
    return NewSubStr

def all_hiragana(Str):
    Proc=subprocess.Popen(['kakasi_utf8.sh',Str,'-JH','-KH'],stdout=subprocess.PIPE)
    (StdOut,_)=Proc.communicate()
    return StdOut.decode().strip()


def change_ext(FP,NewExt):
    return get_stem_ext(FP)[0]+'.'+NewExt

def render_kana(Wd):
    Cmd='echo '+Wd+' | kakasi -i utf8 -o utf8 -JH'
    Proc=subprocess.Popen(Cmd,shell=True,stdout=subprocess.PIPE)
    Reading=Proc.communicate()[0].decode().strip()
    return Reading

def render_katakana(Wd):
    Str=''
    for Char in Wd:
        CharT=identify_type_char(Char)
        if CharT=='han':
            Str=Str+subprocess.Popen(['/home/yosato/links/myProgs/scripts/kakasi_utf8.sh',Orth,'-JK -HK']).communicate()[0].decode()
        elif CharT=='hiragana':
            Str=Str+kana2kana(Char)
        elif CharT=='katakana':
            Str=Str+Char
        else:
            sys.exit('disallowed char')
    return Str

def is_kana(Char):
    CharT=identify_type_char(Char)
    return CharT=='hiragana' or CharT=='katakana'
 
def kana2kana_wd(Str):
    NewWd=''
    for Ind,Char in enumerate(Str):
        CharT=identify_type_char(Char)
        if CharT != 'hiragana' and CharT != 'katakana':
            print('Non-kana is contained')
            return None
        elif Ind!=0 and CharT!=PrvCharT:
            print('hiragana and katakana are mixed. may not make sense, this conversion, though we will do it')
        NewWd=NewWd+kana2kana(Char)
        PrvCharT=CharT
    return NewWd
    
def kana2kana(Char):
    KanaCand=identify_type_char(Char)
    if KanaCand=='hiragana':
        ConvKana=chr(ord(Char)+96)
    elif KanaCand=='katakana':
        ConvKana=chr(ord(Char)-96)
    else:
        print('This is not a kana')
        ConvKana=None
    return ConvKana
