#!/usr/bin/env python3
#! --*--coding=utf8--*--
import os, json, re
from ftfy import fix_text

def parse_arguments():
    import argparse
    parser = argparse.ArgumentParser(description='''Clean parallel corpus:
    - applies ftfy to clean invalid characters, encoding errors, etc.
    - removes empty lines
    - removes pairs of tag/closing-tag
    - filters out sentences in which the target is a copy of the source 
                        and both sides have at least 20 characters.''')
    parser.add_argument('--in', type=str, default='', required=True, 
                        help='Input corpus file name (json)')
    parser.add_argument('--out', type=str, default='', required=True, 
                        help='Cleaned output file name in json format')
    parser.add_argument('--discarded', type=str, default='', required=True, 
                        help='Output file name of discarded segments (json)')
    return vars(parser.parse_args())

def strip_tags(html,pattern):
    # remove only pairs of tag/closing-tag
    m = pattern.search(html)
    while m:
        old = m.group(0)
        new = m.group(2)
        html = html.replace(old, new)
        m = pattern.search(html)
    html = re.sub(r'<img [^>]*alt="([^"]*)"[^>]*>',r'\1', html)
    html = re.sub(r'<!--','',html)
    html = re.sub(r'-->','',html)
    html = re.sub(r"\s+"," ", html)
    html = html.strip() 
    return html

def is_verbatim(stext, ttext):
    return len(stext)>=20 and len(ttext)>=20 and stext==ttext

def clean(sraw, traw, pattern_tags):
    # Apply fix_text
    stxt = fix_text(sraw.strip(), fix_character_width=False, uncurl_quotes=False, fix_latin_ligatures=False).replace('\n',' ')
    ttxt = fix_text(traw.strip(), fix_character_width=False, uncurl_quotes=False, fix_latin_ligatures=False).replace('\n',' ')
    # Strip tags
    sclean = strip_tags(stxt, pattern_tags)
    tclean = strip_tags(ttxt, pattern_tags)
    # Apply fix_text a second time as one time is not enough in some cases
    scleantxt = fix_text(sclean, fix_character_width=False, uncurl_quotes=False, fix_latin_ligatures=False)
    tcleantxt = fix_text(tclean, fix_character_width=False, uncurl_quotes=False, fix_latin_ligatures=False)
    scleantxt = re.sub(r"\s+"," ", scleantxt)
    tcleantxt = re.sub(r"\s+"," ", tcleantxt)
    return scleantxt.strip(), tcleantxt.strip()

def main(args):
    pattern_tags = re.compile('<([A-Za-z][^> ]*)[^>]*>([^<]*)<\/\\1>')

    infile = args['in']
    outfile = args['out']
    discfile = args['discarded']
    fin = open(infile, 'r', newline='\n')
    fout = open(outfile, 'w')
    fdisc = open(discfile, 'w')
    with fin, fout:
        for line in fin:
            attrs = json.loads(line)
            sraw = attrs['source']
            traw = attrs['target']
            # apply fix_text and remove tags
            stxt, ttxt = clean(sraw, traw, pattern_tags)
            # remove empty lines
            if (not stxt or not ttxt):
                attrs['discarded'] = "EMPTY LINE"
                fdisc.write(json.dumps(attrs, ensure_ascii=False)+'\n')
                continue
            # remove pairs in which target is copy of source
            if is_verbatim(stxt, ttxt):
                attrs['discarded'] = "VERBATIM"
                fdisc.write(json.dumps(attrs, ensure_ascii=False)+'\n')
                continue
            attrs['source'] = stxt
            attrs['target'] = ttxt
            fout.write(json.dumps(attrs, ensure_ascii=False)+'\n')

if __name__ == "__main__":
    args = parse_arguments()
    main(args)
