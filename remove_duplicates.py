#!/usr/bin/env python3
#! --*--coding=utf8--*--
import os, json, re
from collections import defaultdict

def parse_arguments():
    import argparse
    parser = argparse.ArgumentParser(description='''Remove parallel corpus segments duplicates.''')
    parser.add_argument('--in', type=str, default='', required=True, 
                        help='Input corpus file name (json)')
    parser.add_argument('--out', type=str, default='', required=True, 
                        help='Cleaned output file name in json format')
    parser.add_argument('--discarded', type=str, default='', required=True, 
                        help='Output file name of discarded segments (json)')
    return vars(parser.parse_args())

def main(args):
    infile = args['in']
    outfile = args['out']
    discfile = args['discarded']
    fin = open(infile, 'r', newline='\n')
    fout = open(outfile, 'w')
    fdisc = open(discfile, 'w')
    unique_sent_pairs = set()
    with fin, fout, fdisc:
        for line in fin:
            attrs = json.loads(line)
            stxt = attrs['source']
            ttxt = attrs['target']
            if (stxt, ttxt) not in unique_sent_pairs:
                unique_sent_pairs.add((stxt,ttxt))
                fout.write(json.dumps(attrs, ensure_ascii=False)+'\n')
            else:
                attrs['discarded'] = "DUPLICATE"
                fdisc.write(json.dumps(attrs, ensure_ascii=False)+'\n')

if __name__ == "__main__":
    args = parse_arguments()
    main(args)
