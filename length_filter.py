#!/usr/bin/env python3
#! --*--coding=utf8--*--
import os, json, re

def parse_arguments():
    import argparse
    parser = argparse.ArgumentParser(description='''Remove parallel corpus segments in which the source/target or 
    target/source length ratio is larger than a threshold.''')
    parser.add_argument('--in', type=str, default='', required=True, 
                        help='Input corpus file name (json)')
    parser.add_argument('--out', type=str, default='', required=True, 
                        help='Cleaned output file name in json format')
    parser.add_argument('--discarded', type=str, default='', required=True, 
                        help='Output file name of discarded segments (json)')
    parser.add_argument('--threshold', type=float, default=3.0, required=True, 
                        help='Threshold for length ratio')
    return vars(parser.parse_args())

def main(args):
    threshold = args['threshold']
    infile = args['in']
    outfile = args['out']
    discfile = args['discarded']
    fin = open(infile, 'r', newline='\n')
    fout = open(outfile, 'w')
    fdisc = open(discfile, 'w')
    with fin, fout, fdisc:
        for line in fin:
            attrs = json.loads(line)
            sraw = attrs['source']
            traw = attrs['target']
            slen = float(len(sraw.replace(" ", "")))
            tlen = float(len(traw.replace(" ", "")))
            ratio = slen/tlen
            if ratio<1:
                ratio = tlen/slen
            if ratio > threshold:
                attrs['discarded'] = "LENGTH RATIO"
                fdisc.write(json.dumps(attrs, ensure_ascii=False)+'\n')
            else:
                fout.write(json.dumps(attrs, ensure_ascii=False)+'\n')

if __name__ == "__main__":
    args = parse_arguments()
    main(args)
