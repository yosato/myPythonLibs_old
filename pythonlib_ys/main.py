import re,copy, imp,math, datetime,time,itertools, os, sys, subprocess,pickle,inspect,json

from pdb import set_trace

#timeout = 10
#t = Timer(timeout, print, ['Sorry, times up'])
#t.start()
#prompt = "You have %d seconds to choose the correct answer...\n" % timeout
#answer = input(prompt)
#t.cancel()

def sort_jsons_fromfile(InFP,OutFP=None):
    import ijson
    

def generate_line_reverse(fp, buf_size=8192):
    """a generator that returns a line of a file in reverse order"""
    with open(fp) as fh:
        segment = None
        offset = 0
        fh.seek(0, os.SEEK_END)
        total_size = remaining_size = fh.tell()
        while remaining_size > 0:
            offset = min(total_size, offset + buf_size)
            fh.seek(-offset, os.SEEK_END)
            buffer = fh.read(min(remaining_size, buf_size))
            remaining_size -= buf_size
            lines = buffer.split('\n')
            # the first line of the buffer is probably not a complete line so
            # we'll save it and append it to the last line of the next buffer
            # we read
            if segment is not None:
                # if the previous chunk starts right from the beginning of line
                # do not concact the segment to the last line of new chunk
                # instead, yield the segment first 
                if buffer[-1] is not '\n':
                    lines[-1] += segment
                else:
                    yield segment
            segment = lines[0]
            for index in range(len(lines) - 1, 0, -1):
                if len(lines[index]):
                    yield lines[index]
        yield segment

def readline_reverse(FSr):
    BuffSize=1024
    Cntr=1
    while True:
        # if you hit the beginning, reduce the buff
        CurPos=FSr.tell()
        if CurPos<BuffSize:
            BuffSize=CurPos
           
        FSr.buffer.seek(-1*BuffSize,os.SEEK_CUR)
        FSr.seek(FSr.tell())
        Buff=FSr.read(BuffSize)
        if '\n' in Buff:
            Line=Buff.strip().split('\n')[-1]+'\n'
            break
        else:
            Cntr+=1
            BuffSize+=BuffSize

    return Line
    
def get_nth_line(FP,N):
    Line=None
    with open(FP) as FSr:
        for i in range(N-1):
            FSr.readline()
        Line=FSr.readline()
    return Line

def get_nth_line_reverse(FP,N):
    Line=None
    with open(FP) as FSr:
        FSr.seek(0,2)
        for i in range(N-1):
            readline_reverse(FSr)
        Line=readline_reverse(FSr)
    return Line

def get_nths_lines(FP,TgtLineNums):
    '''
    extract the lines for a particular set of line numbers in a file in that order, by traversing a file stream
    '''
    Lines=[]
    TotalLineCnt=get_linecount(FP)
    with open(FP) as FSr:
        CurPos=CurLineNum=0
        # for each target line num,
        for TgtLineNum in TgtLineNums:
            # you find which of the three is closest, beginning, end or the current position
            ClosestNum,Which=closest(TgtLineNum,[0,CurLineNum,TotalLineCnt])
            # then you move FSr for the diff
            Offset=TgtLineNum-ClosestNum
            Line,FSr=get_nth_line_frompos(FSr,CurPos,Offset)
            CurPos=FSr.tell()
            CurLineNum=CurLineNum+Offset
            Lines.append(Line)
    return Lines        

def get_nth_line_frompos(FSr,CurPos,Offset):
    FSr.seek(CurPos)
    readline_eitherway(FSr,Offset)
    Line=FSr.readline()
    return Line,FSr 

def readline_eitherway(FSr,Offset):
    if Offset>0:
        for i in range(Offset-1):
            FSr.readline()
    else:
        for i in range(Offset):
            readline_reverse(FSr)
    return FSr.readline()
        
def proportions_valid_p(Proportions):
    if any(type(El).__name__!='int' for El in Proportions):
        sys.exit('Proportions have to be integers')
    elif sum(Proportions)!=100:
        sys.exit('Proportions must add to 100')
    else:
        return True

def split_list_proportions(List,Proportions):
    if proportions_valid_p(Proportions):
        PrvCutPoint=0;Slices=[]
        for Prop in Proportions[:-1]:
            CurCutPoint=int(PrvCutPoint+len(List)//(100/Prop))
            Slices.append(List[PrvCutPoint:CurCutPoint])
            PrvCutPoint=CurCutPoint
        Slices.append(List[PrvCutPoint:])
    return Slices
        
def find_insert_point_byattr(ToInsert,Objs,Attr):
    import bisect
    Keys=[ Obj.__dict__[Attr] for Obj in Objs ]
    return bisect.bisect_left(Keys,ToInsert)





class MyEncoder(json.JSONEncoder):
    def default(self,o):
        return o.__dict__
    
def obj2json(Obj):
    return MyEncoder().encode(Obj)

def mean(Stats):
    return sum(Stats)/len(Stats)

def variance(Stats):
    Mean=mean(Stats)
    return sum((Stat-Mean)**2 for Stat in Stats)
    
def stdev(Stats):
    Var=variance(Stats)
    return math.sqrt(Var/len(Stats))

def stddev(Stats):
    return stdev(Stats)

def harmonic_mean(OrgNums):
    Nums=copy.copy(OrgNums)
    Sum=0
    while Nums:
        Sum=Sum+(1/Nums.pop(0))
    HM=len(OrgNums)/Sum
    return HM 


def rank_list_of_tuples(LofTs,Thresh=float('inf'),EqualNorm=True):
    LofTs=sorted(LofTs,key=lambda x:x[0],reverse=True)
    PrvScore=None;Rank=0;NewLofTs=[];Equals=0
    for (CurScore,CurVal) in LofTs:
        if CurScore != PrvScore:
            if EqualNorm:
                Rank=Rank+Equals+1
                Equals=0
            else:
                Rank=Rank+1
        else:
            if EqualNorm:
                Equals=Equals+1
        if Rank>Thresh:
            break
        NewLofTs.append((Rank,CurVal,))
        PrvScore=CurScore

    return NewLofTs

def prompt_loop_bool(Prompt,Interact=False,Default=False,TO=10,DefaultSuppress=False):
    import threading,select, sys, platform
    Sent=False
    if Default:
        DefStr='yes'
    else:
        DefStr='no'
    AddStr=''
    if not DefaultSuppress:
        AddStr=AddStr+"[default ("+DefStr+")]"
    FullPrompt=Prompt+" Enter '[Yy](es)' or '[Nn](o)' "+AddStr+": "
    while not Sent:
        if not Interact:
            print(FullPrompt+' Default value is taken if you do nothing for %d secs) ' %TO )
            SysName=platform.system()
            if SysName=='Linux' or 'Darwin':
                (StdIn,_,_)=select.select([sys.stdin],[],[],TO)
                if StdIn:
                    YesNoStr=StdIn[0].readline().strip()
                else:
                    YesNoStr=''
                    DefaultSuppress=False
            else:
                YesNoStr=DefStr
        else:
            YesNoStr=input(Prompt+" Enter [Yy](es) or [Nn](o) "+AddStr+": ")
        YesNoBool=yesno2bool(YesNoStr)
        if (YesNoBool=='' and DefaultSuppress) or YesNoBool==None:
            print("You don't seem to have entered [Yy](es) or [Nn](o). Try again")
        else:
            Sent=True
            if YesNoBool=='':
               YesNoBool=Default

    return YesNoBool

def time_and_record(FSw,Message=''):
    import datetime
    Now=datetime.datetime.now()
    output_stdout_fs('['+Now.strftime('%Y/%m/%d %H:%M')+'] '+Message,FSwLog=FSw)

def output_stdout_fs(Stuff,FSwLog=None,Prefix=''):
    sys.stdout.write(Prefix+Stuff+'\n')
    if not FSwLog:
        print('log filepath not specified, ignoring the file output')
    else:
        FSwLog.write(Prefix+Stuff+'\n')

def choose_randomly(List,Num=1):
    import random
    return List[random.randint(0,len(List)-1)]

def number_lines(FP,Ext='numbered',ExtRepl=False):
    if ExtRepl:
        OutputFP=change_ext(FP,Ext)
    else:
        OutputFP=FP+'.'+Ext
    FSw=open(OutputFP,'wt')
    for (Cntr,Line) in enumerate(open(FP,'rt')):
        NewLine='\t'.join([str(Cntr+1),Line])
        FSw.write(NewLine)
    FSw.close()

def ask_filenoexist_execute_pickle(FP,Function,ArgsKArgs,Message='Use the old file',TO=10,DefaultReuse=True,Backup=True):
    Response=ask_filenoexist_execute(FP,Function,ArgsKArgs,Message=Message,TO=TO,DefaultReuse=DefaultReuse,Backup=Backup)
    if Response:
        dump_pickle(Response,FP)
        return Response,False
    else:
        Pickle=load_pickle(FP)
        return Pickle,True

def jsonable_p(Obj,DirectP=True):
    JsonableAtoms=[ 'str', 'int', 'float' ]
#    JsonableCollects=[ 'dict', 'list' ]
#    IndirectlyJsonableCollects=[ 'tuple', 'set' ]
    if type(Obj).__name__ in JsonableAtoms:
        return True,DirectP
    else:
        if isinstance(Obj,dict):
            Obj=list(Obj.keys())+list(Obj.values())
        elif isinstance(Obj,tuple) or isinstance(Obj,set):
            Obj=list(Obj)
            DirectP=False
        if isinstance(Obj,list):
            List=Obj
            for El in List:
                (ObjP,DirectP)=jsonable_p(El,DirectP)
                if not ObjP:
                    return False,DirectP
            return True,DirectP
        else:
            return False,DirectP

def diclist_halfjsonable2jsonable(DicList):
    if isinstance(DicList,dict):
        dic_halfjsonable2jsonable(DicList)
    elif isinstance(DicList,list):
        list_halfjsonable2jsonable(DicList)


def diclist_jsonable2halfjsonable(DicListStr):
    if isinstance(DicList,dict):
        dic_jsonable2halfjsonable(DicList)
    elif isinstance(DicList,list):
        list_jsonable2halfjsonable(DicList)



def dic_halfjsonable2jsonable(Dic):
    NewItems=[]
    for Key,Value in Dic.items():
        if isinstance(Key,Tuple):
            NewKey=stringify_halfjsonablecollection(Key)
        else:
            NewKey=Key
        Type=type(Value).__name__
        if Type=='list' or Type=='dict':
            NewVal=diclist_halfjsonable2jsonable(Value)
        elif Type=='tuple':
            stringify_halfjsonablecollection(Value)
        else:
            NewVal=Val
        NewItems.append(NewKey,NewVal)
    return {}.update(NewItems)

def dic_jsonable2halfjsonable(Dic):
    NewItems=[]
    for Key,Value in Dic.items():
        if isinstance(Key,Tuple):
            NewKey=destringify_halfjsonablecollection(Key)
        else:
            NewKey=Key
        Type=type(Value).__name__
        if Type=='list' or Type=='dict':
            NewVal=diclist_jsonable2halfjsonable(Value)
        elif Type=='tuple':
            destringify_halfjsonablecollection(Value)
        else:
            NewVal=Val
        NewItems.append(NewKey,NewVal)
    return {}.update(NewItems)


def list_halfjsonable2jsonable(L):
    NewL=[]
    for El in L:
        Type=type(Value).__name__
        if Type=='list' or Type=='dict':
            NewL.append(diclist_halfjsonable2jsonable(El))
        elif Type=='tuple':
            NewL.append(stringify_halfjsonablecollection(El))
        else:
            NewL.append(El)

    return NewL

def list_jsonable2halfjsonable(L):
    NewL=[]
    for El in L:
        Type=type(Value).__name__
        if Type=='list' or Type=='dict':
            NewL.append(diclist_jsonable2halfjsonable(El))
        elif Type=='tuple':
            NewL.append(destringify_halfjsonablecollection(El))
        else:
            NewL.append(El)

    return NewL


def stringify_halfjsonablecollection(HalfJsonable):
    Els=[]
    for El in HalfJsonable:
        if isinstance(El,str):
            Els.append(El)
        else:
            Els.append(type(El).__name__+'|;|'+str(El))

    return type(HalfJsonable).__name__+'|;|'+'|-|'.join(Els)

def destringify_halfjsonablecollection(StringifiedTuple):
    Type,StEls=StringifiedTuple.split('|:|')[0]
    Els=[]
    for StEl in StEls.split('|-|'):
        if '/=/' in StEl:
            Type,St=StEl.split('|-|')
            if Type=='int':
                Els.append(int(St))
            elif Type=='float':
                Els.append(float(St))
        else:
            Els.append(StEl)
    if Type=='set':
        return set(Els)
    elif Type=='tuple':
        return tuple(Els)



def ask_filenoexist_execute_json(FP,Function,ArgsKArgs,Message='Use the old file',TO=10,DefaultReuse=True,Backup=True):
    import json
    Response=ask_filenoexist_execute(FP,Function,ArgsKArgs,Message=Message,TO=TO,DefaultReuse=DefaultReuse,Backup=Backup)
    if Response is False:
        Json=json.loads(open(FP,'rt').read())
        Object=dejsonify_diclist(Json)
        return Object,False
    else:
        (Bool,DirectP)=jsonable_p(Response)
        if not Bool:
            print('not jsonable, only returning the object')
        elif DirectP:
            ToJson=Response
        else:
            ToJson=jsonify_diclist(Response)
        open(FP,'wt').write(json.dumps(ToJson))
        return Response,True

def ask_filenoexist_execute(FPs,Function,ArgsKArgs,Message='Use the old file',TO=10,DefaultReuse=True,Backup=True):
    if type(FPs).__name__=='str':
        FPs=[FPs]
    FileExistP=check_exist_paths(FPs)
    RedoIt=not DefaultReuse
    if not FileExistP:
        RedoIt=True
    else:
        if prompt_loop_bool(Message+' i.e. '+str(FPs)+'?',TO=TO,Default=DefaultReuse):
            RedoIt=False
        else:
            RedoIt=True
    
    if Backup and FileExistP and RedoIt:
        for FP in FPs:
            if os.path.getsize(FP)>10000:
                print('backing up '+FP)
                run_stuff_exit(['cp',FP,FP+'.bak'])
    if RedoIt:
        if type(ArgsKArgs).__name__!='tuple' or type(ArgsKArgs[0]).__name__!='list' or type(ArgsKArgs[1]).__name__!='dict':
            sys.exit('arg arg needs to be tuple(list,dict)')
        else:
            (Args,KArgs)=ArgsKArgs
            Return=Function(*Args,**KArgs)
            return Return
            #if Return:
            #    return Return
            #else:
            #    return None
        return True
    return False


def dicval_sum(Dic):
    return sum(Dic.values())

def increment_diccount(OrgDic,Key,Step=1,Inset=True):
    if not Inset:
        import copy
        Dic=copy.copy(OrgDic)
    else:
        Dic=OrgDic
    if Key in Dic.keys():
        Dic[Key]=Dic[Key]+Step
    else:
        Dic[Key]=Step
    if not Inset:
        return Dic

def create_percentage_milestones(UnitCnt):
    Milestones=[]
    Interval=100/UnitCnt
    for i in range(1,UnitCnt):
        Milestones.append(i*Interval)
    return Milestones


def run_stuff_exit(CmdLst,Shell=False,StdOut=False):
    from subprocess import Popen,PIPE
    if StdOut:
        (StdOut,Err)=Popen(CmdLst,stderr=PIPE,stdout=PIPE,shell=Shell).communicate()
    else:
        (_,Err)=Popen(CmdLst,stderr=PIPE,shell=Shell).communicate()
    if Err:
        sys.exit(Err)
    if StdOut:
        return StdOut.decode('utf-8')


def prepare_progressconsts(Tgt,TgtType='filename'):
    import datetime
    Type=type(Tgt).__name__
    if Type=='list' or Type=='dict':
        TgtType='iter'
    elif Type=='str' and len(Tgt)>10000:
        TgtType='str'
    if TgtType=='filename':
        Cnt=get_linecount(Tgt)
    elif TgtType=='iter' or TgtType=='str':
        Cnt=len(Tgt)
    print('process starting')    
    return (Cnt,datetime.datetime.now(),)

def return_stack():
    import inspect
    Stack=inspect.stack()
    if len(Stack)>=3:
        return (Stack[2][1], Stack[2][3],Stack[3][1], Stack[3][3])
    else:
        return (Stack[2][1],Stack[2][3])


def progress_counter(Milestones,ProgressConsts,Current,Unit='',Interval=2):
    (Target,StartTime)=ProgressConsts
    OrgProgress=Current/Target
    Progress=OrgProgress*100
    TimeNow=datetime.datetime.now()
    SecondsPassed=(TimeNow-StartTime).seconds
    MinutesPassed=SecondsPassed/60

    if Milestones==None and SecondsPassed>50:
        print(return_stack())
        print('Progress pre-warning: '+str(SecondsPassed)+' secs passed and '+'{0:.2f}'.format(Progress)+'% done.')
        if OrgProgress==0:
            OrgProgress=0.0001
        DurEstimate=MinutesPassed/OrgProgress
        if DurEstimate>120:
            MilestoneUnits=200
        if DurEstimate>60:
            MilestoneUnits=100
        elif DurEstimate>30:
            MilestoneUnits=50
        elif DurEstimate>10:
            MilestoneUnits=10
        else:
            MilestoneUnits=5
        Milestones=create_percentage_milestones(MilestoneUnits)
        
        print('Rough estimate of total duration '+'{0:.2f}'.format(DurEstimate)+' mins. You will be alerted again at '+str(Milestones[1])+'%')
        if DurEstimate>30:
            print('Have a cup of tea...')
        time.sleep(Interval)

    elif Milestones:
        if Progress>Milestones[0]:
            print(return_stack())
            print(str(Current)+' out of '+str(Target)+' '+Unit+' or '+str(Milestones[0])+'% done. Time taken so far: '+str((TimeNow-StartTime).seconds//60)+' mins')

            Milestones=Milestones[1:]
            time.sleep(Interval)
    return Milestones

def exist_paths_p(FPs):
    return check_exist_paths(FPs)

def warnprint(Str):
    print(return_stack())
    print(Str)

def check_exist_paths(FPs):
    import os
    for FP in FPs:
        if not os.path.exists(FP):
            warnprint(FP+' does not exist')
            Bool=False
            if os.path.isdir(os.path.dirname(FP)):
                print('... but the upper dir exists')
            else:
                print('... nor the upper fot')
        else:
            Bool=True
    return Bool

#def do_something_and_comeback_fs(FS,FuncOrMethod):
#    CurPos=FS.tell()
#    Return=Func(FS)
#    FS.seek(CurPos)
#    return Return

def get_endpos_fs(FS):
    CurPos=FS.tell()
    LstPos=FS.seek(0,2)
    FS.seek(CurPos)
    return LstPos

#def get_last_pos_fs(FS):
#    return do_something_and_comeback_fs(FS,)


def change_stem(FP,Addition):
    StExt=get_stem_ext(FP)
    return StExt[0]+Addition+'.'+StExt[1]

def indicate_loop_progress(Var,Interval,Message='progress',Increment=1):
    if Var%Interval==0:
        print(Message+': '+str(Var))
    return Var+Increment
    
def human_readable_num(Num):
#    '{}'.format()
    
    if Num<1000:
        NumStr=str(Num)
    elif Num<1000000:
        NumStr=str(Num//10000)+'T '+str(Num)[-2:]
    elif Num<1000000000:
        NumStr=str(Num//1000000)+'M '+str(Num)[-5:-2]+'T '+str(Num)[-2:]
    return NumStr


def process_ifnotexist(FP,FuncN,Args,PickleP=False,FileVar=''):
    RealFP=FP+FileVar
    if not os.path.isfile(RealFP):
        Res=FuncN(*Args)
    else:
        if prompt_loop_bool('Do you want to use the old file?'):
            Res=load_pickle(RealFP)
        else:
            Res=FuncN(*Args)
#            print('pickling...'+'('+FP+')')
 #           dump_pickle_check(Res,FP+'.pickle')
        
#    return Res

def first_same_ind(L1,L2):
    for Ind,E1,E2 in enumerate(zip(L1,L2)):
        if E1==E2:
            return Ind
    return None

def put_spaces_around_chars(Str,Chars=[],Types=['sym']):
#    SpChars=["+","(",")","*",".","\\",'&']
#    import re
#    Res=Str
#    NewCharL=[ ' '+Char+' ' if (identify_type_char=='cjksym' or Char in Chars)
#              else Char for Char in Str ]
    NewChars=[]
    for Char in Str:
        Type=identify_type_char(Char)
        if Type in Types or Char in Chars:
            NewChars.append(' '+Char+' ')
        else:
            NewChars.append(Char)
#            Res=re.sub(r'\%s'%Char,r' %s '%Char,Res)
#        else:
#            Res=re.sub(r'%s'%Char,r' %s '%Char,Res)
    return ''.join(NewChars)


def remove_duplicates_list(seq):
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if x not in seen and not seen_add(x)]    


def split_list_bylen(List):
    D={}
    for El in List:
        Len=len(El)
        if Len not in D.keys():
            D.update([(Len,[El])])
        else:
            D[Len].append(El)
    return D

def sort_by_keys(D):
    L=[]
    Keys=sorted(list(D.keys()))
    for Key in Keys:
        L.append(D[Key])
    return L
        

def complementary_lists(List,Cond):
    CondYes=[]; CondNo=[]
    for El in List:
        if Cond:
            CondYes.append(El)
        else:
            CondNo.append(El)
    return CondYes, CondNo
        
    

    
def replace_byindex(OrgStr,StartInd,EndInd,Str2RepWith):
    NewStr=OrgStr[:StartInd]+Str2RepWith+OrgStr[EndInd:]
    return NewStr

def first_index_regex(Str,Regex,Start=0):
    import re
    Substr=Str[Start:]
    if re.search(Regex,Substr):
        StartInd=re.search(Regex,Substr).start()+Start
        EndInd=re.search(Regex,Substr).end()+Start
    else:
        return None
    return (StartInd,EndInd)

#def find_all_str(Str,TgtStr):

def f_score(Prec,Rec):
    return 2*((Prec*Rec)/(Prec+Rec))

def file_exists_prompt_loop_bool(Prompt,FP,Default=True,TO=10):
    from os import path
    if path.isfile(FP):
        return prompt_loop_bool(Prompt,Default=Default,TO=TO)
    else:
        return False

def closest(TgtNum,OrgNums,Sorted=False):
    ''' returns the number in a list that is closest to the given number, as well as its position in the list
        if there are the same values in the list pick the first one,
        or if there are two number with the same distance, pick the smaller one

    '''
    # if the same number is in the list, that's the one
    if TgtNum in OrgNums:
        Closest=TgtNum

    # otherwise sort your list if not done yet,
    if not Sorted:
        Nums=sorted(OrgNums)
        
    Top=Nums[0];Tail=Nums[-1]
    # tgt could just be smaller than any in the list (then the top is what you want)
    if TgtNum<Top:
        Closest=Top
    # or may be larger than any
    elif TgtNum>Tail:
        Closest=Tail
    # othrewise check for each num     
    else:
        MinDiff=float('inf')
        for Num in Nums:
            Diff=abs(TgtNum-Num)
            if Diff<MinDiff:
                MinDiff=Diff
                Closest=Num

    return Closest, OrgNums.index(Closest)


def larger(Num1,Num2):
    if Num1>Num2:
        return Num1
    elif Num2>Num1:
        return Num2
    else:
        return None
        
        
            
def strlist2str(StrL,Joiner):
    if all([ type(El)==str for El in StrL]):
        return Joiner.join(StrL)
    else:
        print('Each element in the list needs to be a string'); exit()
#        return None

def all_indices(List,Tgt):
    return [i for i, x in enumerate(List) if x == Tgt]

def abs_diff(Num1,Num2):
    return abs(Num1-Num2)

def close_p(Num1,Num2,Whatisclose):
    return abs_diff(Num1,Num2)<=Whatisclose


def increment_dicts(D1,D2):
    NewD={}
    D1Keys=set(D1.keys()); D2Keys=set(D2.keys())
    CommonKeys=D1Keys.intersection(D2Keys)
    D1OnlyKeys=D1Keys-D2Keys
    D2OnlyKeys=D2Keys-D1Keys
    for CommonKey in CommonKeys:
        Sum=D1[CommonKey]+D2[CommonKey]
        NewD.update([(CommonKey,Sum)])
    for D1OnlyKey in D1OnlyKeys:
        NewD.update([(D1OnlyKey,D1[D1OnlyKey])])

    for D2OnlyKey in D2OnlyKeys:
        NewD.update([(D2OnlyKey,D2[D2OnlyKey])])
#    for RestKey in RestKeys:
        
        
    return NewD


def chunk_file_bysize(SrcFP,Size,DstDir='.'):
    import os,subprocess
    SrcFN=os.path.basename(SrcFP)
    #DstFPs=[]
    FileSize=os.path.getsize(SrcFP)
    if FileSize>Size*2:
        NumChunks=FileSize//Size
        DstFPs=split_file(SrcFP,NumChunks,DstDir=DstDir)
     #   DstFPs.extend(DstFPs)
    else:
        DstFPs=[DstDir+'/'+SrcFN]
        if DstDir!='.':
            subprocess.call(['cp',SrcFP,DstDir] )
    
    return DstFPs
    

def chunk_files_bysize(FPs,Size,DstDir='.'):
    import os
    CumSize=0; TmpFPs=[]
    for FP in FPs:
        if os.path.getsize(FP)>Size*2:
            FN=os.path.basename(FP)
            SplitFPs=chunk_file_bysize(FN,Size,Dir=Dir)
            TmpFPs.extend(SplitFPs)
        else:
            TmpFPs.append(FP)
    
    Chunks=chunks(TmpFPs,5)
            
    return Chunks
            

def split_file(SrcFP,NumFiles,DstDir='.'):
    FSr=open(SrcFP,encoding='utf-8')
    Lines=FSr.readlines()
    LineCnt=len(Lines)
    NumLPerF=LineCnt // NumFiles
    
    SetsOfLines=chunks(Lines,NumLPerF)
    if len(SetsOfLines)!=NumFiles:
        if len(SetsOfLines)-1==NumFiles:
            LastTwoTogether=SetsOfLines.pop(-2)+SetsOfLines.pop(-1)
            SetsOfLines.append(LastTwoTogether)
        else:
            print("something's wrong"); exit()
    
    SrcFN=os.path.basename(SrcFP)
    (TgtFNStem,FileExt)=get_stem_ext(SrcFN)
    DstFPs=[]
    Cntr=0
    for SetOfLines in SetsOfLines:
        Cntr+=1
        FP=DstDir+'/'+TgtFNStem+'_'+str(Cntr)+'of'+str(NumFiles)+'.'+FileExt
        FSw=open(FP,'tw',encoding='utf-8')
        FSw.write(''.join(SetOfLines))
        FSw.close()
        DstFPs.append(FP)
    
    return DstFPs


def overall_filesize(FPs):
    import os
    return sum([ os.path.getsize(FP) for FP in FPs ])







def glue_els(L,Step):
    return [ ''.join(L[i:i+Step]) for i in range(0,len(L),Step) ]   

def hex_chr(HexStr):
    Int=int('0x'+HexStr,16)
    Chr=chr(Int)
    return Chr

def check_pickle(FN):
    if not FN.endswith('.pickle'):
        FN=FN+'.pickle'
    return FN
    
        
def flatten_tuple(Tuple):
    List=[]
    for El in Tuple:
        if type(El).__name__=='tuple':
           for SubEl in El:
               List.append(SubEl)
        else:
            List.append(El)
    return tuple(List)


def flatten_list(l):
    return [item for sublist in l for item in sublist ]

def flatten_list_r(L):
    IntL=flatten_list(L)
    Inds=find_type(IntL,list)
    if Inds:
        for Ind in Inds:
            flatten_list(IntL[Ind])
    return L

def replace_linenumbers(OldFP,NewFP,LCPairs):
#    import linecache
    Lines=open(OldFP,encoding='utf-8').readlines()
    for LInd,Correction in LCPairs:
        if Correction:
            Lines[LInd]=Correction
        else:
            Lines.pop(LInd)
    FSw=open(NewFP,'tw',encoding='utf-8')
    FSw.write(''.join(Lines))
    FSw.close



def len_above_thresh_inlist(L,Thresh):
    ATs=[]
    for El in L:
        if len(El)>Thresh:
            ATs.append(El)
    return ATs


def file_exists_save_open(FN,Type='t'):
    if os.path.isfile(FN):
        FS=open(FN,Type)
    return FS

def find_type(L,Type):
    Inds=[]; Ind=0
    for El in L:
        Ind+=1
        if isinstance(El,Type):
            Inds.append(Ind)
    return Inds

def load_pickle(FN):
    import pickle
    
    FN=check_pickle(FN)
    Pr=open(FN,'rb')
    print(FN+': loading...')
    Stuff=pickle.load(Pr)
    print(' loaded')
    Pr.close()
    return Stuff

def write_strlist_asline(L,FN):
    if all([ isinstance(El,str) for El in L ]):
        FSw=open(FN,'wt')
        for El in L:
            FSw.write(El+'\n')
        FSw.close()
    else:
        print("There are non-str elements, aborting"); exit()

def dump_pickle(Stuff,FN):
    dump_pickle_check(Stuff,FN)
def dump_pickle_check(Stuff,FN):
    FN=check_pickle(FN)
    print(FN+': pickling...')
    Pw=open(FN,'bw')        
    pickle.dump(Stuff,Pw)
    Pw.close()
#    Stuff=load_pickle(FN)
    print(' pickled')
#    print(Stuff)
    
def in_ranges(TgtNum,Ranges):
    Val=False
    for Range in Ranges:
        if len(Range)!=2:
            print('[in_ranges] you need two values for a range'); exit()
        else:
            (Fst,Snd)=Range
            HexP= (type(Fst).__name__ == 'str' and type(Snd).__name__ == 'str' and 
                   len(Fst)==4 and len(Snd)==4 )
            Cond=((type(Fst).__name__ == 'int' and type(Snd).__name__ == 'int') or
                 HexP )
            if not Cond:
                print('[myModule.in_ranges] format wrong'); exit()
        if HexP:
            LB=int(Range[0],16); UB=int(Range[1],16)
        else:
            LB=Range[0]; UB=Range[1]
            
        if TgtNum >= LB and TgtNum <= UB:
            Val=True
            break
    return Val



def xor(Bool1,Bool2):
    return (Bool1 or Bool2) and not (Bool1 and Bool2)

def chunk_list(List,ChunkSize,ChunkCnt=None,Overlap=0):
    Chunks=[]
    ListLen=len(List)
    Conds=[ xor(ChunkSize,ChunkCnt)]
    if not all(Conds):
        print('conds not met'); exit()
    if ChunkCnt:
        ChunkSize=ListLen//ChunkCnt
    else:
        ChStartInd=0; ChEndInd=ChunkSize
        while ChEndInd <= ListLen:
            Chunks.append(List[ChStartInd:ChEndInd])
            ChStartInd=ChStartInd+ChunkSize-Overlap
            ChEndInd=ChStartInd+ChunkSize
    return Chunks

def chunk(L,N,O=0): 
     return [ L[Cntr-(N-O):(Cntr-(N-O))+N] for Cntr,El in enumerate(L) if Cntr<len(L)-N and L[Cntr-(N-O):(Cntr-(N-O))+N] ]
def chunks(OrgList,N,Overlap=0,Remnant=True):
    """successive n-sized chunks with an optional overlap"""
    import copy
    List=copy.deepcopy(OrgList)
    Len=len(OrgList)
    Chunks=[]
    if Overlap>N:
        print("You can't do the overlap value bigger than the step"); exit()
    Chunk=[]
    while len(List)>=N:
        for El in List[0:N]:
            Chunk.append(El)
        Chunks.append(Chunk)
        Chunk=[]
        List=List[N-Overlap:]
    if Remnant:
        Chunks.append(List)
    return Chunks

def set_debug():
    global Debug
    Debug=True

def get_debug():
    return Debug

def iter2strs(Iter,Delim):
    Str=''
    for El in Iter:
        Str=Str+str(El)+Delim
    return Str

def numStr_p(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def all_true(Iter):
    Cum=True
    Cntr=0
    for Bool in Iter:
        if not Iter[Cntr]:
            break
        Cntr=Cntr+1
    return Cum


def reverse_keyval(Dict):
   RevDict={}
   RevDictVals=[]
   for Key in list(Dict.keys()):
      RevDictVals.append((Dict[Key],Key))
   RevDict.update(RevDictVals)
   return RevDict


def gen_cartesian_prod(LofTups):
    CumProd=[]
    PrevProd=[()]
    for Tup in LofTups:
        for El in Tup:
            for PrevTup in PrevProd:
                PrevL=list(PrevTup)
                PrevL.append(El)
                NewTup=tuple(PrevL)
                CumProd.append(NewTup)

        PrevProd=CumProd
        CumProd=[]

    return PrevProd

gen_cartesian_prod([(1,2),(3,),(4,5,6)])

choice=None

def prob2logit(Prob):

      return math.log(Prob/(1-Prob))

def logit2prob(Logit):
    NegLogit=-Logit
    return 1/(1+math.exp(NegLogit))

def coeffs2probs_ord(IntCoeffs):
    Int=IntCoeffs[0]
    CoeffLs=copy.deepcopy(IntCoeffs[1:])
    Probs=[]

    (CL1,CL2)=CoeffLs
    CL1.append(0)
    CL2.append(0)
    
    for Coeff1 in CL1:
        for Coeff2 in CL2:
            Logit=Int+Coeff1+Coeff2
            Prob=logit2prob(Logit)
            Probs.append(Prob)

    return Probs


def rlinput(Prefill='aaa'):
#    defaultText = 'I am the default value'
    readline.set_startup_hook(lambda: readline.insert_text(Prefill))
    res = input('Edit this:')
    print(res)

#def rlinput(Prompt, Prefill=''):
 #  readline.set_startup_hook(lambda: readline.insert_text(Prefill))
  # try:
   #   return eval(input(Prompt))
  # finally:
   #    readline.set_startup_hook()

#give a list of dics and a pair of key/val, you fetch the ones that have that value 
def collect_rightdics(Dics,TgtKey,TgtVal):
    RightDics=[]
    for Dic in Dics:
        if Dic[TgtKey]==TgtVal:
            RightDics.append(Dic)
    
    return RightDics

def collect_nths(LofCols,N):
    TgtL=[]
    for Col in LofCols:
        TgtL.append(Col[N-1])
    return TgtL

def powersets(SupS):
    PSet=set()
    for i in range(len(SupS)+1):
        SetToAdd=set(itertools.combinations(SupS, i))
        PSet=PSet.union(SetToAdd)
    return PSet

def randpick_from_list(L):
    import random
    return L[random.randint(0,len(L)-1)]

def partition(OrgCol):
    Parts=[]
    for i in range(math.floor((len(OrgCol)/2)+1)):
        Combs=list(itertools.combinations(OrgCol, i))
        for Comb in Combs:
            Compl=compl(OrgCol,Comb)
            if len(Comb)>=len(Compl):
                Comb1=Comb
                Comb2=Compl
            else:
                Comb2=Comb
                Comb1=Compl
            Pair=[Comb1,Comb2]
            if Pair not in Parts:
                Parts.append(Pair)
    return Parts

def compl(WholeL,Tuple):
    ComplL=[]
    for El in WholeL:
        if El not in Tuple:
            ComplL.append(El)
    return tuple(ComplL)


# given a list of strings, output 'a, b, c, .... 'conj' n'
def select_prompt(OrgOpts,Conj,Numbered=False):
    SelPr=""
    Punc=', '
    Len=len(OrgOpts)
    Cntr=0
    Sent=False
    while not Sent:
        Cntr=Cntr+1

        if Len == 0:
            Sent=True

        else: 
          CurOpt=OrgOpts[Cntr-1]

          if Numbered:
              NumStr=str(Cntr)+'. '
          else:
              NumStr=''

          if type(CurOpt).__name__!='str':
              CurStr=str(CurOpt)
          else:
              CurStr=CurOpt

          if Len == 1:
              Sent=True
              SelPr=NumStr+CurStr
          else:
              if Cntr == Len:
                  Sent=True
                  SelPr=SelPr+' '+Conj+' '

              if Cntr>=Len-1:
                  Punc=''

              SelPr=SelPr+NumStr+CurStr+Punc

    return SelPr

def merge_countdics(Dic1,Dic2):
    NewDic={}
    Only1=set(Dic1.keys())-set(Dic2.keys())
    Only2=set(Dic2.keys())-set(Dic1.keys())
    for Key,Cnt in Dic1.items():
        if Key in Only1:
            NewDic[Key]=Dic1[Key]
        else:
            NewDic[Key]=Dic1[Key]+Dic2[Key]
    for Key in Only2:
        NewDic[Key]=Dic2[Key]
    return NewDic
            



def merge_lists(Ls):
    LToExtend=copy.deepcopy(Ls[0])
    for L in Ls[1:]:
        LToExtend.extend(L)
    return LToExtend

def peek_next_line(FS):
    OrgP=FS.tell()
    NxtL=FS.readline()
    FS.seek(OrgP, 0)
    return NxtL

# convert all sorts of yes-no's to True and False, if nothing is entered, return '', if not convertible, return None
def yesno2bool(Str):
    LowerStr=Str.strip().lower().replace("'",'')
    if LowerStr=='yes' or LowerStr=='y' or LowerStr=="'yes'" or LowerStr=="'y'":
        Final=True
    elif LowerStr=='no' or LowerStr=='n':
        Final=False
    elif LowerStr=='':
        Final=''
    else:
        Final=None

    return Final
        


def prompt_loop_fn(Prompt='filename',Ext='',Dir='.'):
    Sent=False
    while not Sent:
        FNStem=input(Prompt+' (extension "'+Ext+'", directory "'+Dir+'", or say "exit" to exit): ')

        if FNStem=='exit':
            Sent=True
            FullDir=None
 
        else:
            if Ext:
                DotExt='.'+Ext
            else:
                DotExt=''
            FN=FNStem+DotExt
            FullDirCand=Dir+'/'+FN

            if not os.path.exists(FullDirCand):
                print("The specified file ("+FullDirCand+") doesn't exist. Try again")
                FullPath=None

            else:
                Sent=True
                FullPath=FullDirCand

    return (FullPath,FNStem,FN)

def same_upto(LorStr1,LorStr2):
    Ind=0
    for Pair in zip(LorStr1,LorStr2):
        if not Pair[0]==Pair[1]:
            break
        Ind=Ind+1

    return Ind

def twostrs_middiff(Str1,Str2):
    Len1=len(Str1); Len2=len(Str2)
    TopSameUpTo=same_upto(Str1,Str2)
    Tail1=Str1[TopSameUpTo:][::-1]; Tail2=Str2[TopSameUpTo:][::-1]
    TailSameUpTo=same_upto(Tail1,Tail2)
    MidDiff=(Str1[TopSameUpTo:Len1-(TailSameUpTo)],Str2[TopSameUpTo:Len2-(TailSameUpTo)])            
    return (MidDiff,(TopSameUpTo,TailSameUpTo))

def prompt_loop_fs(Prompt,Path='',WR='r'):
    Path=prompt_loop_fn(Prompt)
    FS=open(Path,WR)
    return FS



def prompt_loop1(Prompt,Type):
    Input=input(Prompt+": ").strip()
    if Type=='int':
        Val=int(Input)
    return Val 

def create_numlist(NofNs,StartNum=1,Interval=1):
    Cntr=StartNum
    Nums=[]
    for i in range(NofNs):
        Nums.append(Cntr)
        Cntr=Cntr+Interval
    return Nums

def list_num_print(L):
    Cntr=0
    Str=''
    for E in L:
        Cntr=Cntr+1
        Str=Str+str(Cntr)+': '+str(E)+', '

    print(Str)

    return Str


def lower_strs(OrgL):
    L=copy.deepcopy(OrgL)
    NewEs=[]
    for E in L:
        if type(E).__name__=='str':
            NewE=E.lower()
        else:
            NewE=str(E)
        NewEs.append(NewE)
    return NewEs

def str2num(Str):
    if numStr_p(Str):
        NumStr=int(Str)
    else:
        NumStr=Str
    return NumStr



def stringify_list(OrgL):
#    L=copy.deepcopy(OrgL)
    NewL=[]
    for E in L:
        if type(E).__name__!='str':
            NewE=str(E)
        else:
            NewE=E
        NewL.append(NewE)
    return NewL
    
def prompt_loop_list(Prompt,OrgSelectOps,Default=None,ReturnSingleEl=False,Numbered=False,MsgSuppress=False,AtLeast=1,AtMost=100):
    Choices=[]
    # return single el implies there's only a single el
    if ReturnSingleEl:
        AtLeast=1
        AtMost=1

    # if there's no choice
    if len(OrgSelectOps) == 0:
        print('Nothing to choose from, returning an empty list')
        Choices=[]
    # if there's only one choice
    elif len(OrgSelectOps) == 1:
        OnlyChoice=OrgSelectOps[0]
        if prompt_loop_bool(Prompt+"\nOnly one option, "+OnlyChoice+", is it your choice?"):
            Choices=[OnlyChoice]
        else:
            Choices=[]
    # normal case: more than one option
    else:
        Choices=prompt_loop_list2(Prompt,OrgSelectOps,Default,Numbered,MsgSuppress,AtLeast,AtMost)

    if ReturnSingleEl:
        Choices=Choices[0]

    return Choices

def prompt_loop_list2(Prompt,SelOps,Default,Numbered,MsgSuppress,AtLeast,AtMost):
    #first the prompt message created
    if not MsgSuppress: 
        SelectPrompt=select_prompt(SelOps,'or',Numbered=Numbered)

        Msg=" Please choose from the following\n"
        if Default==None:
            AddMsg=''
        else:
            AddMsg=' (Default='+str(Default)+')'

        if AtLeast != 1 and AtMost != 1:
            AddMsg=AddMsg+"\nFor multiple options, separate them with comma(s)."
        if AtLeast == 0:
            AddMsg=AddMsg+" For no option, say 'none'"
    
        Msg=Msg+SelectPrompt+AddMsg

    else:
        Msg=' Your option'

    Choices=[] 
    NumChoice=len(SelOps)
    # needed to allow lower case input
    LStrSelOps=lower_strs(SelOps)
    Sent=False
    while not Sent:
        # wrong input keeps the loop running
        WrongInput=False
        # notice we lower-case the input
        Answers=input(Prompt+Msg+": " ).lower().strip().split(',')
        AnswerCnt=len(Answers)
        # if nothing is inputted you flag error or take the default
        if Answers==['']:
            if Default==None:
                print('You need to enter at least one option')
                WrongInput=True
            else:
                Choices=[Default]
        else:
            # if the answer is 'none' return empty list or flag error if disallowed
            if Answers==['none']:
                if AtLeast==0:
                    Choices=[]
                else:
                    print('You have to choose at least one option.')
                    WrongInput=True

            elif AnswerCnt < AtLeast or AnswerCnt > AtMost:
                print('You entered either too few or too many answers.')
                WrongInput=True

            # below's the normal list case
            else:
                # numbering allows the user to pick the corresponding num
                if Numbered:
                    for Answer in Answers:
                        if numStr_p(Answer):
                            AnswerNum=int(Answer)
                            # just to exclude out-of-range input error
                            if AnswerNum > 0 or AnswerNum <= AnswerCnt:
                                Choices.append(SelOps[AnswerNum-1])
                            else:
                                print('You entered the wrong number(s).')
                                WrongInput=True
                        # we'd also allow text input. remember we're handling lower case strings!
                        elif Answer in LStrSelOps:
                            Choices.append(same_ind_el(Answer,LStrSelOps,SelOps))
                        else:
                            print("There is no such option.")
                            WrongInput=True
            # if un-numbered
                else:
                    for Answer in Answers:
                        if Answer in LStrSelOps:
                            Choices.append(same_ind_el(Answer,LStrSelOps,SelOps))
                        else:
                            print("There is no such option.")
                            WrongInput=True

        if WrongInput:
            print("Wrong or no input. Try again")
        else:
            Sent=True

    return Choices

def same_ind_el(OrgE,OrgL,TgtL):
    return TgtL[OrgL.index(OrgE)]

def split_re_inclusive(Str,Delims=r'([!?\n。]+)'):
    import re
    # you will get the bracketed content as well this way
    SplitsWithDelims=re.split(r'(%s)'%Delims,Str)
    # and you need to get those bits
    SplitPairs=chunk_list(SplitsWithDelims,ChunkSize=2)
    SplitStrs=[ Pair[0]+Pair[1] for Pair in SplitPairs ]
    return SplitStrs


##==============================
## TEXTPROC
####


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
        if in_ranges(ord(Char), Ranges):
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


###
## fileproc
##

def dedup_totalidenticals(FPIn,FPOut=None,Min=80,WindowSize=50000):
    if not FPOut:
        FPOut=FPIn+'.dedup'
    Seen=[]; Sentl=False
    with open(FPIn) as FSr:
        with open(FPOut,'wt') as FSw:
            while not Sentl:
                LiNe=FSr.readline()
                if not LiNe:
                    Sentl=True
                    continue
                Line=LiNe.strip()
                if Line and len(Line)>Min and Line in Seen:
                    print('dup found, "'+Line+'" at earlier by '+str(WindowSize-Seen.index(Line)))
                    
                else:
                    if Line:
                        Seen.append(Line)
                    if len(Seen)>WindowSize:
                        Seen.pop(0)
                    FSw.write(LiNe)


class JsonManip:
    def __init__(self,FP,Stuff):
        if FP.endswith('.json'):
            FP=FP+'.json'
        self.fp=FP
        self.stuff=Stuff
    def encode_stuff_if_nec(self,Stuff):
        return Stuff.__dict__
    def decode_stuff_if_nec(self,FP):
        PureJ=json.loads(FP)
        Decoded=dejsonify_diclist(PureJ)
        return Decoded
    def dump_json(self):
        with open(FP,'wt') as FSw:
            try:
                json.dumps(self.stuff,FSw)
            except TypeError:
                json.dumps(self.serialise_stuff_if_nec(self.stuff))

def jsonable_p(Obj,DirectP=True):
    JsonableAtoms=[ 'str', 'int', 'float' ]
#    JsonableCollects=[ 'dict', 'list' ]
#    IndirectlyJsonableCollects=[ 'tuple', 'set' ]
    if type(Obj).__name__ in JsonableAtoms:
        return True,DirectP
    else:
        if isinstance(Obj,dict):
            Obj=list(Obj.keys())+list(Obj.values())
        elif isinstance(Obj,tuple) or isinstance(Obj,set):
            Obj=list(Obj)
            DirectP=False
        if isinstance(Obj,list):
            List=Obj
            for El in List:
                (ObjP,DirectP)=jsonable_p(El,DirectP)
                if not ObjP:
                    return False,DirectP
            return True,DirectP
        else:
            return False,DirectP


            

def jsonify_diclist(DicList):
    if isinstance(DicList,dict):
        return jsonify_dic(DicList)
    elif isinstance(DicList,list):
        return jsonify_list(DicList)


def dejsonify_diclist(DicList):
    if isinstance(DicList,dict):
        return dejsonify_dic(DicList)
    elif isinstance(DicList,list):
        return dejsonify_list(DicList)



def jsonify_dic(Dic):
    NewItems=[]
    for Key,Value in Dic.items():
        if isinstance(Key,tuple):
            NewKey=stringify_halfjsonable(Key)
        else:
            NewKey=Key
        Type=type(Value).__name__
        if Type=='list' or Type=='dict':
            NewVal=jsonify_diclist(Value)
        elif Type=='tuple':
            NewVal=stringify_halfjsonable(Value)
        else:
            NewVal=Value
        NewItems.append((NewKey,NewVal,))
    Dict={}
    Dict.update(NewItems)
    return Dict

def dejsonify_dic(Dic):
    NewItems=[]
    for Key,Value in Dic.items():
        if Key.startswith('tuple|:|'):
            NewKey=destringify_halfjsonable(Key)
        else:
            NewKey=Key
        Type=type(Value).__name__
        if Type=='list' or Type=='dict':
            NewVal=dejsonify_diclist(Value)
        elif Type=='str' and (Value.startswith('tuple|:|') or Value.startswith('set|:|')):
            NewVal=destringify_halfjsonable(Value)
        else:
            NewVal=Value
        NewItems.append((NewKey,NewVal,))
    Dict={}
    Dict.update(NewItems)
    return Dict


def jsonify_list(L):
    NewL=[]
    for El in L:
        Type=type(El).__name__
        if Type=='list' or Type=='dict':
            NewL.append(jsonify_diclist(El))
        elif Type=='tuple':
            NewL.append(stringify_halfjsonable(El))
        else:
            NewL.append(El)

    return NewL

def dejsonify_list(L):
    NewL=[]
    for El in L:
        Type=type(Value).__name__
        if Type=='list' or Type=='dict':
            NewL.append(dejsonify_diclist(El))
        elif Type=='tuple':
            NewL.append(destringify_halfjsonable(El))
        else:
            NewL.append(El)

    return NewL


def stringify_halfjsonable(HalfJsonable):
    Els=[]
    for El in HalfJsonable:
        if isinstance(El,str):
            Els.append(El)
        else:
            Els.append(type(El).__name__+'|;|'+str(El))

    return type(HalfJsonable).__name__+'|:|'+'|-|'.join(Els)

def destringify_halfjsonable(StringifiedTuple):
    Type,StEls=StringifiedTuple.split('|:|')
    Els=[]
    for StEl in StEls.split('|-|'):
        if '/=/' in StEl:
            Type,St=StEl.split('|-|')
            if Type=='int':
                Els.append(int(St))
            elif Type=='float':
                Els.append(float(St))
        else:
            Els.append(StEl)
    if Type=='set':
        return set(Els)
    elif Type=='tuple':
        if Els==['']:
            return ()
        return tuple(Els)



def ask_filenoexist_execute_json(FP,Function,ArgsKArgs,Message='Use the old file',TO=10,DefaultReuse=True,Backup=True):
    import json
    Response=ask_filenoexist_execute(FP,Function,ArgsKArgs,Message=Message,TO=TO,DefaultReuse=DefaultReuse,Backup=Backup)
    if Response is False:
        PureJson=json.loads(open(FP,'rt').read())
        Json=dejsonify_diclist(PureJson)
        return Json
    else:
        (Bool,DirectP)=jsonable_p(Response)
        if not Bool:
            print('not jsonable, only returning the object')
        elif DirectP:
            ToJson=Response
        else:
            ToJson=jsonify_diclist(Response)
        open(FP,'wt').write(json.dumps(ToJson))
        return Response


    
    

        












def filelines2list(FP,Num=False):
    L=[]
    for Line in open(FP):
        if Num:
            L.append(int(Line.strip()))
        else:
            L.append(Line.strip())
    return L

def extract_lines_numbers(FP,Nums,Delete=False,StdOut=True):
    if not StdOut:
        FSw=open(FP+'_extlines','wt')
    for Cntr,Line in enumerate(open(FP)):
        if Delete:
            Cond=Cntr+1 not in Nums
        else:
            Cond=Cntr+1 in Nums
        if Cond:
            if StdOut:
                sys.stdout.write(Line)
            else:
                FSw.write(Line)
    if not StdOut:
        FSw.close()

def filelines_extract(LineFP,FP,Delete=False,StdOut=False):
    Lines=filelines2list(LineFP,Num=True)
    extract_lines_numbers(FP,Lines,Delete=Delete,StdOut=StdOut)

def change_ext(FP,NewExt):
    return get_stem_ext(FP)[0]+'.'+NewExt

def get_stem_ext(FN):
    if '.' in FN:
        Matches=re.match(r'(..*)\.(..*)',FN).groups()
    else:
        Matches=(FN,'')
    return Matches

def get_linecount(FP):
    FSr=open(FP)
    Cnt=0
    print('get_linecount, '+FP+': counting lines...')
    while True:
        if Cnt!=0 and Cnt%1000000==0:
            print('get_linecount: quite a few lines... now '+str(Cnt)+' and still going')
        if FSr.readline():
            Cnt+=1
        else:
            break
    return Cnt


