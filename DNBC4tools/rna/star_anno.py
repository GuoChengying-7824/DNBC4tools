import argparse,os,pysam,time
from collections import defaultdict
from multiprocessing import Pool
from DNBC4tools.tools.utils import logging_call
from DNBC4tools.__init__ import _root_dir

parser = argparse.ArgumentParser(description='QC,star and anno')
parser.add_argument('--name',help='sample name', type=str)
parser.add_argument('--outdir',help='output dir, default is current directory', default=os.getcwd())
parser.add_argument('--cDNAfastq1',help='cDNAR1 fastq file, Multiple files are separated by commas.', required=True)
parser.add_argument('--cDNAfastq2',help='cDNAR2 fastq file, Multiple files are separated by commas.', required=True)
parser.add_argument('--oligofastq1',help='oligoR1 fastq file, Multiple files are separated by commas.',required=True)
parser.add_argument('--oligofastq2',help='oligoR2 fastq file, Multiple files are separated by commas.',required=True)
parser.add_argument('--chemistry',metavar='STR',choices=["scRNAv1HT","scRNAv2HT","auto"],help='Chemistry version. Automatic detection is recommended. If setting, needs to be used with --darkreaction, can be "scRNAv1HT", "scRNAv2HT", [default: auto].',default='auto')
parser.add_argument('--darkreaction',metavar='STR',help='Sequencing dark reaction. Automatic detection is recommended. If setting, needs to be used with --chemistry, use comma to separate cDNA and oligo, can be "R1,R1R2", "R1,R1", "unset,unset", etc, [default: auto].', default='auto')
parser.add_argument('--customize',metavar='STR',help='Customize files for whitelist and readstructure in JSON format for cDNA and oligo, use comma to separate cDNA and oligo.')
parser.add_argument('--genomeDir',type=str, help='star index dir.')
parser.add_argument('--gtf',type=str, help='gtf file')
parser.add_argument('--thread',type=int, default=4,help='Analysis threads.')
parser.add_argument('--no_introns',action='store_true',help='Not include intronic reads in count.')
args = parser.parse_args()

detectNreads = 100000
def cDNA_chemistry(seq):
    if len(seq) > 30:
        if seq[0:6] == "TCTGCG" or seq[16:22] == "CCTTCC" or seq[32:37] == "CGATG":
            return "scRNAv2HT"
        elif seq[10:16] == "CCTTCC" or seq[26:31] == "CGATG":
            return "scRNAv1HT"
        else:
            return "Other"
    else:
        return "darkreaction"

def oligo_R1_chemistry(seq):
    if len(seq) > 30:
        if seq[0:6] == "TCTGCG" or seq[16:22] == "CCTTCC":
            return "scRNAv2HT"
        elif seq[10:16] == "CCTTCC":
            return "scRNAv1HT"
        else:
            return "Other"
    else:
        return "darkreaction"

def oligo_R2_reaction(seq):
    if len(seq) > 30:
        if seq[10:16] == "TCTGCG" or seq[26:32] == "CCTTCC":
            return "nodarkreaction"
        else:
            return "Other"
    else:
        return "darkreaction"

def check_cDNA_chemistry(fq1):
    results = defaultdict(int)
    with pysam.FastxFile(fq1) as fq:
        for fastq in range(detectNreads):
            try:
                record = fq.__next__()
            except BaseException as e:
                print("\033[0;31;40mThere is not enough cDNA sequences to automatic identification!\033[0m")
                raise Exception('There is not enough cDNA sequences to automatic identification.')
            seq = record.sequence
            chemistry = cDNA_chemistry(seq)
            if chemistry:
                results[chemistry] += 1
    sorted_counts = sorted(results.items(), key=lambda x: x[1], reverse=True)
    chemistry, read_counts = sorted_counts[0][0], sorted_counts[0][1]
    percent = float(read_counts) / detectNreads
    if chemistry == 'Other':
        raise Exception('The chemistry and darkreaction are unable to be automatically determined.')
    if percent < 0.5:
        print("Valid chemistry read counts percent < 0.5")
        raise Exception('The chemistry and darkreaction are unable to be automatically determined.')
    return chemistry

def check_oligo_chemistry(fq1,fq2):
    results_R1 = defaultdict(int)
    with pysam.FastxFile(fq1) as fq:
        for fastq in range(detectNreads):
            try:
                record = fq.__next__()
            except BaseException as e:
                print("\033[0;31;40mThere is not enough oligo sequences to automatic identification!\033[0m")
                raise Exception('There is not enough oligo sequences to automatic identification.')
            seq = record.sequence
            R1chemistry = oligo_R1_chemistry(seq)
            if R1chemistry:
                results_R1[R1chemistry] += 1
    sorted_counts = sorted(results_R1.items(), key=lambda x: x[1], reverse=True)
    R1chemistry, read_counts = sorted_counts[0][0], sorted_counts[0][1]
    percent = float(read_counts) / detectNreads
    if R1chemistry == 'Other':
        raise Exception('The chemistry and darkreaction are unable to be automatically determined.')
    if percent < 0.5:
        print("Valid chemistry read counts percent < 0.5")
        raise Exception('The chemistry and darkreaction are unable to be automatically determined.')
    
    results_R2 = defaultdict(int)
    with pysam.FastxFile(fq2) as fq:
        for fastq in range(detectNreads):
            record = fq.__next__()
            seq = record.sequence
            R2chemistry = oligo_R2_reaction(seq)
            if R2chemistry:
                results_R2[R2chemistry] += 1
    sorted_counts = sorted(results_R2.items(), key=lambda x: x[1], reverse=True)
    R2chemistry, read_counts = sorted_counts[0][0], sorted_counts[0][1]
    percent = float(read_counts) / detectNreads
    if R2chemistry == 'Other':
        raise Exception('The chemistry and darkreaction are unable to be automatically determined.')
    if percent < 0.5:
        print("Valid chemistry read counts percent < 0.5")
        raise Exception('The chemistry and darkreaction are unable to be automatically determined.')

    return R1chemistry,R2chemistry

def cDNA_para():
    cDNA_in1 = open('%s/01.data/cDNAin1'%args.outdir,'w')
    cDNA_in2 = open('%s/01.data/cDNAin2'%args.outdir,'w')
    
    cDNA_chemistry_list = []
    for fastq1 in args.cDNAfastq1.strip().split(','):
        cDNA_in1.write(os.path.abspath(fastq1)+'\n')
        if args.customize or (args.darkreaction != 'auto' and args.chemistry != 'auto'):
            pass
        else:
            chemistry = check_cDNA_chemistry(fastq1)
            cDNA_chemistry_list.append(chemistry)
    cDNA_in1.close()
    for fastq2 in args.cDNAfastq2.strip().split(','):
        cDNA_in2.write(os.path.abspath(fastq2)+'\n')
    cDNA_in2.close()
    cDNA_conf = open('%s/01.data/cDNA_para'%args.outdir,'w')
    cDNA_conf.write('in1=%s/01.data/cDNAin1'%args.outdir+'\n')
    cDNA_conf.write('in2=%s/01.data/cDNAin2'%args.outdir+'\n')
    
    if args.customize:
        cDNAConfig = args.customize.strip().split(',')[0]
    elif args.darkreaction != 'auto' and args.chemistry != 'auto':
        if args.darkreaction.strip().split(',')[0] == 'R1':
            cDNAConfig = '%s/config/scRNA_beads_darkReaction.json'%_root_dir
        elif args.darkreaction.strip().split(',')[0] == 'unset':
            if args.chemistry == 'scRNAv1HT':
                cDNAConfig = '%s/config/scRNAv1HT/scRNA_beads_noDarkReaction_v1.json'%_root_dir
            if args.chemistry == 'scRNAv2HT':
                cDNAConfig = '%s/config/scRNAv2HT/scRNA_beads_noDarkReaction_v2.json'%_root_dir
        else:
            print('\033[0;31;40mUnable to parse parameter in cDNA!\033[0m')
            raise Exception('Unable to parse parameter in cDNA!')
    else:
        if len(set(cDNA_chemistry_list)) != 1 :
            print('\033[0;31;40mmultiple chemistry found in cDNA!\033[0m')
            raise Exception('The chemistry and darkreaction are unable to be automatically determined in cDNA.')
        else:
            print('\033[0;32;40mThe chemistry(darkreaction) automatically determined in cDNA : %s\033[0m'%(cDNA_chemistry_list[0]))
            if cDNA_chemistry_list[0] == 'darkreaction':
                cDNAConfig = '%s/config/scRNA_beads_darkReaction.json'%_root_dir
            if cDNA_chemistry_list[0] == 'scRNAv2HT':
                cDNAConfig = '%s/config/scRNAv2HT/scRNA_beads_noDarkReaction_v2.json'%_root_dir
            if cDNA_chemistry_list[0] == 'scRNAv1HT':
                cDNAConfig = '%s/config/scRNAv1HT/scRNA_beads_noDarkReaction_v1.json'%_root_dir

    cDNA_conf.write('config=%s'%cDNAConfig+'\n')
    cDNA_conf.write('cbdis=%s/01.data/cDNA_barcode_counts_raw.txt'%args.outdir+'\n')
    cDNA_conf.write('report=%s/01.data/cDNA_sequencing_report.csv'%args.outdir+'\n')
    cDNA_conf.write('adapter=%s/config/adapter.txt'%_root_dir+'\n')
    cDNA_conf.close()
    return cDNAConfig
    
def oligo_para():
    oligo_conf = open('%s/01.data/oligo_para'%args.outdir,'w')
    oligo_R1 = []
    oligo_R2 = []
    oligo_R1_list = []
    oligo_R2_list = []
    for i in range(len(args.oligofastq1.strip().split(','))):
        fastq1 = os.path.abspath(args.oligofastq1.strip().split(',')[i])
        fastq2 = os.path.abspath(args.oligofastq2.strip().split(',')[i])
        oligo_R1.append(fastq1)
        oligo_R2.append(fastq2)
        if args.customize or (args.darkreaction != 'auto' and args.chemistry != 'auto'):
            pass
        else:
            R1chemistry,R2chemistry = check_oligo_chemistry(fastq1,fastq2)
            oligo_R1_list.append(R1chemistry)
            oligo_R2_list.append(R2chemistry)
    oligo_conf.write('in1=%s'%",".join(oligo_R1)+'\n')
    oligo_conf.write('in2=%s'%",".join(oligo_R2)+'\n')
    if args.customize:
        oligoConfig = args.customize.strip().split(',')[1]
    elif args.darkreaction != 'auto' and args.chemistry != 'auto':
        if args.darkreaction.strip().split(',')[1] == 'R1':
            oligoConfig= '%s/config/scRNA_oligo_R2_noDarkReaction.json'%_root_dir
        elif args.darkreaction.strip().split(',')[1] == 'R1R2':
            oligoConfig= '%s/config/scRNA_oligo_darkReaction.json'%_root_dir
        elif args.darkreaction.strip().split(',')[1] == 'unset':
            if args.chemistry == 'scRNAv1HT':
                oligoConfig = '%s/config/scRNAv1HT/scRNA_oligo_noDarkReaction_v1.json'%_root_dir
            if args.chemistry == 'scRNAv2HT':
                oligoConfig = '%s/config/scRNAv2HT/scRNA_oligo_noDarkReaction_v2.json'%_root_dir
        else:
            print('\033[0;31;40mUnable to parse parameter in oligo!\033[0m')
            raise Exception('Unable to parse parameter in oligo!')
    else:
        if len(set(oligo_R1_list)) != 1 or len(set(oligo_R2_list)) != 1:
            print('\033[0;31;40mmultiple chemistry found in oligo!\033[0m')
            raise Exception('The chemistry and darkreaction are unable to be automatically determined in oligo.')
        else:
            print('\033[0;32;40mThe chemistry(darkreaction) automatically determined in oligoR1 : %s\033[0m'%(oligo_R1_list[0]))
            print('\033[0;32;40mThe chemistry(darkreaction) automatically determined in oligoR2 : %s\033[0m'%(oligo_R2_list[0]))
            if oligo_R1_list[0] == 'darkreaction' and oligo_R2_list[0] == 'darkreaction':
                oligoConfig = '%s/config/scRNA_oligo_darkReaction.json'%_root_dir
            elif oligo_R1_list[0] == 'darkreaction' and oligo_R2_list[0] == 'nodarkreaction':
                oligoConfig = '%s/config/scRNA_oligo_R2_noDarkReaction.json'%_root_dir
            elif oligo_R1_list[0] == 'scRNAv2HT':
                oligoConfig = '%s/config/scRNAv2HT/scRNA_oligo_noDarkReaction_v2.json'%_root_dir
            elif oligo_R1_list[0] == 'scRNAv1HT':
                oligoConfig = '%s/config/scRNAv1HT/scRNA_oligo_noDarkReaction_v1.json'%_root_dir

    oligo_conf.write('config=%s'%oligoConfig+'\n')
    oligo_conf.write('cbdis=%s/01.data/Index_barcode_counts_raw.txt'%args.outdir+'\n')
    oligo_conf.write('report=%s/01.data/Index_sequencing_report.csv'%args.outdir+'\n')
    oligo_conf.write('outFq=%s/01.data/Index_reads.fq.gz'%args.outdir+'\n')
    oligo_conf.write('threads=%s'%args.thread+'\n')
    oligo_conf.close()

def cDNA_qcstaranno():
    cDNAConfig = cDNA_para()
    cDNA_star_cmd = '%s/soft/scStar --outSAMattributes singleCell --outSAMtype BAM Unsorted --genomeDir %s --outFileNamePrefix %s/01.data/ --stParaFile %s/01.data/cDNA_para --outSAMmode NoQS --runThreadN %s --limitOutSJcollapsed 10000000 --limitIObufferSize 350000000'\
        %(_root_dir,args.genomeDir,args.outdir,args.outdir,args.thread)
    cDNA_anno_cmd = ['%s/soft/Anno -I %s/01.data/Aligned.out.bam -a %s -L %s/01.data/cDNA_barcode_counts_raw.txt -o %s/01.data -c %s -m chrM -B %s --anno 1 '\
        %(_root_dir,args.outdir,args.gtf,args.outdir,args.outdir,args.thread,cDNAConfig)]
    if args.no_introns:
        pass
    else:
        cDNA_anno_cmd += ['--intron']
    cDNA_anno_cmd = ' '.join(cDNA_anno_cmd)
    return cDNA_star_cmd,cDNA_anno_cmd

def oligo_qc():
    oligo_para()
    oligo_qc_cmd = '%s/soft/parseFq %s/01.data/oligo_para'%(_root_dir,args.outdir)
    return oligo_qc_cmd

if __name__ == '__main__':
    cDNA_star_cmd,cDNA_anno_cmd = cDNA_qcstaranno()
    oligo_qc_cmd = oligo_qc()
    time.sleep(10)
    mission = [oligo_qc_cmd,cDNA_star_cmd]
    pool = Pool(2)
    for i in mission:
        pool.apply_async(logging_call,(i,'data',args.outdir,))
    pool.close()
    pool.join()
    logging_call(cDNA_anno_cmd,'data',args.outdir)