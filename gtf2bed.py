#!/bin/env python3

# This file converts Cufflinks .gtf file to .bed file.
import sys;
import re;

if len(sys.argv)<2:
	print('This script converts Cufflinks predictions (.GTF) into .BED annotations.\n');
	print('Usage: gtf2bed {OPTIONS} [.GTF file]\n');
	print('Options:');
	print('-c color\tSpecify the color of the track. This is a RGB value represented as "r,g,b". Default 255,0,0 (red)');
	print('\nNote:');
	print('1\tOnly "exon" and "transcript" are recognized in the feature field (3rd field).');
	print('2\tIn the attribute list of .GTF file, the script tries to find "gene_id", "transcript_id" and "FPKM" attribute, and convert them as name and score field in .BED file.'); 
	print('Author: Wei Li (li.david.wei AT gmail.com)');
	sys.exit();

color='255,0,0'


for i in range(len(sys.argv)):
	if sys.argv[i]=='-c':
		color=sys.argv[i+1];



def printbedline(estart,eend,field,nline):
	try:
		estp=estart[0]-1;
		eedp=eend[-1];
		# use regular expression to get transcript_id, gene_id and expression level
		geneid=re.findall(r'gene_id \"([\w\.]+)\"',field[8])
		transid=re.findall(r'transcript_id \"([\w\.]+)\"',field[8])
		fpkmval=re.findall(r'FPKM \"([\d\.]+)\"',field[8])
		if len(geneid)==0:
			print('Warning: no gene_id field ',file=sys.stderr);
		else:
			geneid=geneid[0];
		if len(transid)==0:
			print('Warning: no transcript_id field',file=sys.stderr);
			transid='Trans_'+str(nline);
		else:
			transid=transid[0];
		if len(fpkmval)==0:
			print('Warning: no FPKM field',file=sys.stderr);
			fpkmval='100';
		else:
			fpkmval=fpkmval[0];
		fpkmint=round(float(fpkmval));
		print(field[0]+'\t'+str(estp)+'\t'+str(eedp)+'\t'+transid+'\t'+str(fpkmint)+'\t'+field[6]+'\t'+str(estp)+'\t'+str(eedp)+'\t'+color+'\t'+str(len(estart))+'\t',end='');
		seglen=[eend[i]-estart[i]+1 for i in range(len(estart))];
		segstart=[estart[i]-estart[0] for i in range(len(estart))];
		strl=str(seglen[0]);
		for i in range(1,len(seglen)):
			strl+=','+str(seglen[i]);
		strs=str(segstart[0]);
		for i in range(1,len(segstart)):
			strs+=','+str(segstart[i]);
		print(strl+'\t'+strs);
	except ValueError:
		print('Error: non-number fields at line '+str(nline),file=sys.stderr);
				




estart=[];
eend=[];
# read lines one to one
nline=0;
prevfield=[];
for lines in open(sys.argv[-1]):
	field=lines.strip().split('\t');
	nline=nline+1;
	if len(field)<9:
		print('Error: the GTF should has at least 9 fields at line '+str(nline),file=sys.stderr);
		continue;
	if field[1]!='Cufflinks':
		print('Warning: the second field is expected to be \'Cufflinks\' at line '+str(nline),file=sys.stderr);
	if field[2]!='exon' and field[2] !='transcript':
		print('Error: the third filed is expected to be \'exon\' or \'transcript\' at line '+str(nline),file=sys.stderr);
		continue;
	if field[2]=='exon':
		try:	
			est=int(field[3]);
			eed=int(field[4]);
			estart+=[est];
			eend+=[eed];
		except ValueError:
			print('Error: non-number fields at line '+str(nline),file=sys.stderr);
	if field[2]=='transcript':
		# A new transcript record, write
		if len(estart)!=0:
			printbedline(estart,eend,prevfield,nline);
		prevfield=field;
		estart=[];
		eend=[];
# the last record
if len(estart)!=0:
	printbedline(estart,eend,field,nline);
