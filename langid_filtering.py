#!/usr/bin/env python3
#! --*--coding=utf8--*--
import os, json, re
import fasttext

def parse_arguments():
    import argparse
    parser = argparse.ArgumentParser(description='''Remove parallel corpus segments in which the source side or the target side are not of the expected language.''')
    parser.add_argument('--in', type=str, default='', required=True, 
                        help='Input corpus file name (json)')
    parser.add_argument('--out', type=str, default='', required=True, 
                        help='Cleaned output file name in json format')
    parser.add_argument('--discarded', type=str, default='', required=True, 
                        help='Output file name of discarded segments (json)')
    parser.add_argument('--s', type=str, default='', required=True, 
                        help='Source language code')
    parser.add_argument('--t', type=str, default='', required=True, 
                        help='Target language code')
    parser.add_argument('--fasttext-model', type=str, default='', required=True, 
                        help='Fasttext pretrained language model')
    return vars(parser.parse_args())

class Langid:
    """
    Class object for Language Identification
    """
    def __init__(self, model_path):
        """
        Initializing class objects
        """
        self.fasttext_model = fasttext.load_model(model_path)

    def classify(self, text):
        label_string, score_array = self.fasttext_model.predict(text, k=1)
        _cls = label_string[0][-2:]
        _score = score_array[0]
        return _cls, _score

def main(args):
    infile = args['in']
    outfile = args['out']
    discfile = args['discarded']
    fin = open(infile, 'r', newline='\n')
    fout = open(outfile, 'w')
    fdisc = open(discfile, 'w')
    LANGID = Langid(args['fasttext_model'])
    with fin, fout, fdisc:
        for line in fin:
            attrs = json.loads(line)
            stxt = attrs['source']
            ttxt = attrs['target']
            src_class, src_score = LANGID.classify(stxt)
            trg_class, trg_score = LANGID.classify(ttxt)
            if src_class == args['s'] and trg_class == args['t']:
                fout.write(json.dumps(attrs, ensure_ascii=False)+'\n')
            else:
                attrs['discarded'] = "LANGID"
                fdisc.write(json.dumps(attrs, ensure_ascii=False)+'\n')

if __name__ == "__main__":
    args = parse_arguments()
    
    main(args)
