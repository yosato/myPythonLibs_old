import sys,os,imp,re,subprocess

#imp.reload(myModule)

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
