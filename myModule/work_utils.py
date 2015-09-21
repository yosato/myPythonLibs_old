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
 
    def adapt_board(self,OrgBoardFP,NewFeatsVals,NewBoardFP):
        NewBoardFP=os.path.join(self.expdirrt,self.lang,self.expname,'board_'+self.expname+'.csv')

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


def get_allfeatsvals_langs_board(BoardFP,Langs):
    FsVsLangs=collections.OrderedDict()
    for Lang in Langs:
        FsVsLangs[Lang]=get_allfeatsvals_lang_board(BoardFP,Lang)
    return FsVsLangs

def get_allfeatsvals_lang_board(BoardFP,Lang):
    Cmd=' '.join(['perl $MYSCRIPT_RESOURCES_DIR/tools/LMBE/edit_board.pl', BoardFP, '-l', Lang, '-r'])
    EBoardOutputAll=subprocess.Popen(Cmd, shell=True,stdout=subprocess.PIPE).communicate()[0].decode().strip()
    AllFsVs=collections.OrderedDict()
    AllFsVs.update([ (Line.strip().split()[1],Line.strip().split()[-1] ) for Line in EBoardOutputAll.split('\n') ])
    return AllFsVs

def get_featsvals_board(BoardFP,Langs,Feats):
    FsVsLangs=get_allfeatsvals_langs_board(BoardFP,Langs)
    Filtered=collections.OrderedDict()
    for Lang in Langs:
        for Feat in Feats:
            Filtered[Lang][Feat]=FsVsLangs[Lang][Feat]
    return Filtered


    Cmd=' '.join([CmdStem,'-r','-f',Feat])
#    cmd_getfeat=lambda Feat: ' '.join([CmdStem, ' -r ', ' -f ', Feat])
#    execute_cmd_getfeat=lambda Cmd: subprocess.Popen(Cmd, shell=True,stdout=subprocess.PIPE).communicate()[0].decode().strip()

    Val=subprocess.Popen(Cmd, shell=True,stdout=subprocess.PIPE).communicate()[0].decode().strip()

#        Proc=subprocess.Popen(CmdSte,,shell=True,stdout=subprocess.PIPE)
    #Val=execute_cmd_getfeat(cmd_getfeat(Feat))
    return FeatsVals

