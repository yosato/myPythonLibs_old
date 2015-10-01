import os,subprocess,re,collections

class LMBEExp:
    def __init__(self,ExpDirRt,Lang,ExpName,CorporaDirRt,BoardFP=None,LogFP=''):
        self.lang=Lang
        self.expname=ExpName
        self.expdirrt=ExpDirRt
        self.expdir=os.path.join(self.expdirrt,self.lang,self.expname)
        self.corporadirrt=CorporaDirRt
        self.corporadirlang=self.corporadirrt+'/'+self.lang
        self.logfp=LogFP
        if not BoardFP:
            BoardFP=os.path.join(self.expdir,'board_'+self.expname+'.csv')
        self.boardfp=BoardFP
        GitDir=os.getenv('MYSCRIPT_RESOURCES_DIR')
        if GitDir:
            CmdDirPath=GitDir+'/tools/LMBE'
        else:
            CmdDirPath=os.getenv('HOME')+'/projects/MyScript_Resources/tools/LMBE'
        self.cmddirpath=CmdDirPath
 
    def generate_newboard(self,OrgBoardFP,NewFeatsVals):
        NewBoardFP=os.path.join(self.expdirrt,self.lang,self.expname,'board_'+self.expname+'.csv')

        CmdForSingleLang=' '.join(['python3', os.getenv('HOME')+'/yo/myProgs/iroiro_py/extract_lang_board.py', OrgBoardFP, self.lang, '>', NewBoardFP  ])
        SingleLangExtractProc=subprocess.Popen(CmdForSingleLang,shell=True)
        SingleLangExtractProc.wait()

        CmdStem=' '.join(['perl', self.cmddirpath+'/edit_board.pl', OrgBoardFP, '-l', self.lang, '-o', self.boardfp])
        
        CmdAddStr=''
        for (Feat,Val) in NewFeatsVals.items():
            CmdAddStr=CmdAddStr+' -f '+Feat+'='+Val
        
        Cmd=CmdStem+' '+CmdAddStr

        Proc=subprocess.Popen(Cmd,shell=True)
        Return=Proc.wait()

        return Return
    def run_exp(self,Stages):
        ShellCmd=' '.join([self.cmddirpath+'/LMBE.pl', self.lang, '-x', self.expdir, '-c', self.boardfp, '-'+Stages])
        Proc=subprocess.Popen(ShellCmd,shell=True)
        Proc.communicate()


def get_allfeatsvals_lang_board(BoardFP,Lang):
    Cmd=' '.join(['perl $MYSCRIPT_RESOURCES_DIR/tools/LMBE/edit_board.pl', BoardFP, '-l', Lang, '-r'])
    EBoardOutputAll=subprocess.Popen(Cmd, shell=True,stdout=subprocess.PIPE).communicate()[0].decode().strip()
    AllFsVsList=[ (Line.strip().split()[1],Line.strip().split()[-1] ) for Line in EBoardOutputAll.split('\n') ]
    AllFsVsList=[ (F,'') if V=="''" else (F,V) for (F,V) in AllFsVsList ]
    AllFsVs=collections.OrderedDict(AllFsVsList)
    AllFsVs.update()
    return AllFsVs

def get_featsvals_board(BoardFP,Langs,Feats):
    FsVsLangs=get_allfeatsvals_langs_board(BoardFP,Langs)
    Filtered=collections.OrderedDict()
    for Lang in Langs:
        for Feat in Feats:
            Filtered[Lang][Feat]=FsVsLangs[Lang][Feat]
    return Filtered

def stringify_allfeatsvals_lang_board(Lang,FsVs):
    Str='lg_code;'+Lang+'\n'
    for F,V in FsVs.items():
        Str=Str+F+';'+V+'\n'
    return Str


AsmissibleLangs=['fr_FR','fr_FR_lite']

class FsVsLang:
    def __init__(self,Lang,FsVs):
        self.lang=Lang
        self.feats_vals=FsVs
    def stringify_feats_vals(self,VOnly=False):
        Str=''
        for F,V in self.FsVs:
            if VOnly:
                Str2Add=V
            else:
                Str2Add=F+';'+V
            Str=Str+Str2Add+'\n'
        return Str
            

class BoardFsVs:
    def __init__(self,FsVsLangs,AdmissibleLangs,AdmissibleFts):
        self.admissible_feats=AdmissibleFts
        self.admissible_langs=AdmissibleLangs
        self.populate_featsvals(FsVsLangs)
    def populate_featsvals(self,FsVsLangs):
        ValidFsVsLangs=collections.OrderdDict()
        for Lang,FsVs in FsVsLangs.items():
            ValFsVs=collections.OrderedDict()
            InputFts=list(FsVs.keys())
            for AdmissibleFt in AdmissibleFts:
                if AdmissibleFt in InputFts:
                    InputFts.remove(AdmissibleFt)
                    ValFsVs[AdmissibleFt]=FsVs[AdmissibleFt]
                else:
                    ValFsVs[AdmissibleFt]=''
            if InputFts:
                print('these alleged features are not admissible')
                print(InputFts)
            ValidFsVsLangs[Lang]=ValFsVs
        self.feats_vals=ValidFsVsLangs

        

            

