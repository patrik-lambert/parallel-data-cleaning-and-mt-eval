#/bin/bash

bdir=/home/plambert/src/parallel-data-cleaning-and-mt-eval; mkdir -p $bdir
pushd $bdir
source /home/plambert/soft/venv_parallel_data_cleaning_and_mt_eval/bin/activate

# 0. Installing MT metrics
pip install sacrebleu[ja]
pip install --upgrade pip
pip install unbabel-comet

wdir=$bdir/2-mt-evaluation; mkdir -p $wdir
ref=resources/2-mt-evaluation/reference.txt
src=resources/2-mt-evaluation/source.txt

# 1. Evaluation with automated MT metrics
for system in system1 system2
do
    ln -sf $bdir/resources/2-mt-evaluation/$system.txt $wdir
    mt=$wdir/$system.txt
    
    # Sacrebleu + ChrF
    cat $mt | sacrebleu $ref -l en-ro -m bleu chrf > $mt.SBLEU

    # COMET
    export LD_LIBRARY_PATH=/home/plambert/soft/venv_parallel_data_cleaning_and_mt_eval/lib/python3.8/site-packages/torch/lib/../../nvidia/cublas/lib/libcublas.so.11
    comet-score -s $src -t $mt -r $ref --model wmt20-comet-da --gpus 1 > $mt.comet
done

# 2. Interpretation of results
# Having evaluated system1 and system2 outputs with BLEU, ChrF and COMET, we obtain the following results:
#          BLEU  ChrF  COMET
# system1  35.5  62.0  0.8273
# system2  27.9  55.7  0.6236
#
# For the three metrics, a higher score is better, thus system1 has the best scores. If the difference in scores was small (for example 1 or 2 BLEU/COMET score difference), we wouldn't be able to be conclusive regarding which system is the best, due to the uncertainty in the measurement. However, with 20 BLEU, 7 ChrF and 0.2 COMET point difference, we can safely conclude that system1 is better than system2.
