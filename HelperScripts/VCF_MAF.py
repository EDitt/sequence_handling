#!/usr/bin/env python3

#   A script to calculate the minor allele frequency in a VCF file
#   Adapted from Tomo Kono's https://github.com/TomJKono/Misc_Utils/blob/master/VCF_MAF.py
#   Usage: python3 VCF_MAF.py yourSNP.vcf > yourSNP.maf

import sys
import re
import gzip

# User provided input argument
vcf_fp = sys.argv[1]

#   A function to calculate the minor allele frequency
def MAF(x):
    #   get the set of alleles in the list
    genotypes = set(x)
    #   start counting up the frequencies
    freqs = []
    for g in genotypes:
        freqs.append(x.count(g)/float(len(x)))
    return min(freqs)


def vcf_maf_calc(f):
    "Calculate the minor allele frequency."
    for line in f:
        #   ignore header lines
        if line.startswith('##'):
            continue
        #   This defines how many samples in the VCF
        elif line.startswith('#CHROM'):
             print ('Chrom\tPos\tsample_NB\tMinor\tMajor\tMAF')
        else:
            tmp = line.strip().split('\t')
            #   Parse out the relevant information
            chromosome = tmp[0]
            bp_pos = tmp[1]
            ref_allele = tmp[3]
            alt_alleles = tmp[4]
            genotypes = tmp[9:] 
            format = tmp[8].split(':')
            sample_genotypes = [x.split(':') for x in genotypes]
            #   check if AD is not in the format field
            #   if not, then skip it
            if 'AD' not in format:
                notes = 'Missing Genotype Call'
                maf = "NA"
                print (maf)
            else:
                notes = ''
                #   For each sample...
                g_column = []
                for g in genotypes:
                	#   In the genotype string, the first element (separated by :) is the actual genotype call
                    call = g.split(':')[0]
                	#   These are diploid calls, and we are assuming they are unphased
                	#   the are listed in the form allele1/allele2
                	#   with 0 = ref, 1 = alt1, 2 = alt2, and so on...
#                    alleles = call.split('/')
                    alleles = re.split('[/|]', call)
                    individual_call = '' # define a dictionary for all of the alleles 
                    for x in alleles:
                        if x == '.': # ignore the missing data
                            continue
                        else:
                            c = int(x)
                        		#   if it's 0, we just tack on the reference state
                            if c == 0:
                                g_column.append(ref_allele)
                            else:
                            	#   Otherwise, we use it to alternate alleles
                                g_column.append(alt_alleles)
                    #   Then, append that column to the genotype matrix
                    #   If there is no variation in genotype calls (that is, all lines have the same genotype)
                    #   then we don't care about it
                    unique_calls = set(g_column)
                    if len(unique_calls) <= 1:
                        maf = "NA"
                    else:
                        maf = MAF(g_column)
            print ('\t'.join([chromosome, bp_pos, str(int(len(g_column)/2)), ref_allele, alt_alleles, str(maf)]))


#   Start iterating through the file
if "gz" in vcf_fp:
    with gzip.open(vcf_fp, 'rt') as f:
        vcf_maf_calc(f)
else:
    with open(vcf_fp, 'r') as f:
        vcf_maf_calc(f)
