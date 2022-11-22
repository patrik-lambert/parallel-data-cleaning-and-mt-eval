#/bin/bash

download-resources(){
    # manually save assignment.zip
    unzip assignment.zip
    mv assignment resources
    rm assignment.zip

    python3.8 -m venv /home/plambert/soft/venv_parallel_data_cleaning_and_mt_eval
    source /home/plambert/soft/venv_parallel_data_cleaning_and_mt_eval/bin/activate
}

clean-encoding(){
    /home/plambert/soft/venv_parallel_data_cleaning_and_mt_eval/bin/python -m pip install ftfy
    python clean_encoding.py --in resources/1-data-cleaning/noisy-corpus.json --out 1-data-cleaning/noisy-corpus.fix.json --discarded 1-data-cleaning/noisy-corpus.fix.discarded.json
}

length-filter(){
    python length_filter.py --in 1-data-cleaning/noisy-corpus.fix.json --out 1-data-cleaning/noisy-corpus.fix.len.json --discarded 1-data-cleaning/noisy-corpus.fix.len.discarded.json --threshold 3
}

remove-duplicates(){
    python remove_duplicates.py --in 1-data-cleaning/noisy-corpus.fix.len.json --out 1-data-cleaning/noisy-corpus.fix.len.dup.json --discarded 1-data-cleaning/noisy-corpus.fix.len.dup.discarded.json
}

langid-filtering(){
    pip install fasttext-wheel
    wget https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin -O resources/1-data-cleaning/lid.176.bin
    python langid_filtering.py --in 1-data-cleaning/noisy-corpus.fix.len.dup.json --out 1-data-cleaning/noisy-corpus.clean.json --discarded 1-data-cleaning/noisy-corpus.fix.len.dup.lid.discarded.json --s de --t en --fasttext-model resources/1-data-cleaning/lid.176.bin
}
##########################################
bdir=/home/plambert/src/parallel-data-cleaning-and-mt-eval; mkdir -p $bdir
pushd $bdir

# 0 download resources
# download resources and create python environment 
download-resources

wdir=$bdir/1-data-cleaning; mkdir -p $wdir
# 1. Encoding cleaning:

# * remove characters which are not proper UTF-8 from the corpus,
# * recover characters which may have been corrupted due to encoding issues.
# * remove empty lines
# * remove long enoung sentences in which target is a copy of source (according to Khayrallah and Koehn 2018,
#   shallow RNN-based NMT models are very sensitive to this type of noise)
# * remove pairs of HTML tag/closing tag
# The encoding cleaning step may also avoids execution crashes in the subsequent steps of the pipeline.
# We use the python ftfy fix-text() function for this purpose.
# Note that we disable some normalisation features, because we are not sure they would be enabled at test time.
#
# We created a python script which reads the json file and applies ftfy fix_text() + filters described above
clean-encoding

# 2. length filter
# Done at character level because the input is not tokenized, and tokenization is not part of the "cleaning" stage,
# thus we don't tackle it here.
# Note that the proposed methods doesn't take into account the difference in average length of each language.
# Refined strategies could take this into account.
length-filter

# 3. Deduplication
# We load the corpus in memory for simplicity, but there are methods to collect counts on disk, e.g. sqlite
# This method removes duplicated segment pairs. We could also implement several de-duplication logics,
# for example one removing segments having the same source side, or a logic respect the word distributions (if segment A-B occurs 9 times, and segment A-C occurs 1 time, removing the duplicates would modify the probability distribution, thus we don't remove duplicates in this case).
remove-duplicates

# 4. langid filtering
# Here we use fasttext to perform language identification and filter out segment pairs not having the expected language
# pair. According to https://modelpredict.com/language-identification-survey#benchmark-results,
# fasttext is the best public tool in a number of language pairs and domains.
langid-filtering

# 5. Further work
# After langid filtering, we obtain the corpus 1-data-cleaning/noisy-corpus.clean.json, which is the result of this work.
# There are still many misaligned sentence pairs. These could be filtered out with more computing-intensive methods,
# such as dual conditional cross-entropy filtering (https://aclanthology.org/W18-6478/), which requires forced decoding
# of the whole corpus with a source-target and a target-source NMT models. An even better solution would be to include
# these scores in a machine translation quality estimation system having more features. Other possibilities include
# taking the cosine of multilingual embedding vectors, such as in LASER. However, several recent papers have reported
# dual conditional cross-entropy was better (e.g. Herold et al., ACL 2022), and the corpora built with LASER contain 25%
# of rubish. Thus I think methods such as LASER are good to detect segment pair candidates, but not for a refined
# filtering.
