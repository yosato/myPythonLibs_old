import sys,os,imp,re,subprocess,json

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
    import json,myModule
    Response=myModule.ask_filenoexist_execute(FP,Function,ArgsKArgs,Message=Message,TO=TO,DefaultReuse=DefaultReuse,Backup=Backup)
    if Response is False:
        PureJson=json.loads(open(FP,'rt').read())
        Json=dejsonify_diclist(PureJson)
        return Json
    else:
        (Bool,Level)=jsonable_p(Response)
        if not Bool:
            print('not jsonable, only returning the object')
        elif Level=='direct':
            ToJson=Response
        elif Level=='indirect':
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
    print(FP+': counting lines...')
    LineCnt=int(subprocess.check_output(['wc','-l',FP]).split()[0].decode())
    print('...counted')
    return LineCnt
