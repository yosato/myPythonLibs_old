import os,subprocess,re

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




def get_featval_board(BoardFP,Lang,Feat):
    CmdStem=' '.join(['perl $MYSCRIPT_RESOURCES_DIR/tools/LMBE/edit_board.pl', BoardFP, '-l', Lang])

    Cmd=' '.join([CmdStem,'-r','-f',Feat])
#    cmd_getfeat=lambda Feat: ' '.join([CmdStem, ' -r ', ' -f ', Feat])
#    execute_cmd_getfeat=lambda Cmd: subprocess.Popen(Cmd, shell=True,stdout=subprocess.PIPE).communicate()[0].decode().strip()

    Val=subprocess.Popen(Cmd, shell=True,stdout=subprocess.PIPE).communicate()[0].decode().strip()

#        Proc=subprocess.Popen(CmdSte,,shell=True,stdout=subprocess.PIPE)
    #Val=execute_cmd_getfeat(cmd_getfeat(Feat))
    return Val

