# Systematically Adapting Machine Translation for Grammatical Error Correction

If using this code or its results, please cite
```
@InProceedings{napoles-callisonburch:2017:BEA,
  author    = {Napoles, Courtney  and  Callison-Burch, Chris},
  title     = {Systematically Adapting Machine Translation for Grammatical Error Correction},
  booktitle = {Proceedings of the 12th Workshop on Innovative Use of NLP for Building Educational Applications},
  month     = {September},
  year      = {2017},
  address   = {Copenhagen, Denmark},
  publisher = {Association for Computational Linguistics},
  pages     = {345--356},
  url       = {http://www.aclweb.org/anthology/W17-5039}
}
```
## Requirements

- python2
- python libraries:
  - py-enchant (1.6.8)
  - nltk (3.0.5)
  - scipy (0.15.1)
  - inflect (0.2.5)
  - kenlm
  - numpy (1.11.0)
- Stanford tagger (3.5.0)
- fast_align
- Joshua (6.0.5)
- morpha, morphg (1.0.4)
- RASP M2 scorer
- English language model (not supplied)

Set environmental variables `JOSHUA`, `M2_HOME`, `MORPH_HOME`, `FASTALIGN`, `STANFORD_HOME` to parent directories of each tool

## Instructions

**1. Prepare parallel corpus/corpora**

To prepare a corpus given two parallel files, `PREFIX.err` and `PREFIX.corr`, call
 ```
 ./prepare_corpus.sh PREFIX corpus-name
 ```
This will tokenize and tag the texts and generate the token-level alignment. Corpora will be saved in `data/corpus-name/`

**2. Generate morphological analysis**
```
./generate_morpha_lookup.sh -d store data/*/*.vocab
```
This creates the file `store/vocab` and `store/vocab.morph`, a unique list of all of the vocab across in the corpus/corpora and the morphological analysis.

**3. Augment grammar with artificial rules**
```
./create_artificial_rules.sh data/corpus-name/ path/to/lm
```
Generates spelling and morphological rules and saves them to `data/corpus-name/[spelling|morph]-rules.gz`

**4. Calculate GEC-specific features**
```
./calculate_gec_features.sh grammar.gz [grammar1.gz ...]
```
Calculates features for each grammar and saves the new grammar file to `grammar.gec-features.gz`

**5. Recase and normalize output**
```
python recase.py data/corpus/corpus-name.tok.err.pos candidate.txt >> candidate.cased
```
Recases lower-case candidate sentences by comparing it to the proper nouns in the sentence

**6. Analyze parallel sentences**
```
./compare_edits.sh -i data/corpus/corpus-name.tok.err -c candidate.txt
```
Performs analysis of sentence pairs and writes to `candidate-source.parallel.analysis`

## Contents ##

```
├── README.md
├── data
│   └── test            # final correct test set references
│       └── unprocessed # original test set references
├── results             # system results and Joshua configuration
├── scripts             # system results and Joshua configuration
└── src                 # Joshua customizations
```

## Errata
The results presented in the paper were calculated on an earlier version of the JFLEG test set (commit #) which has since been processed for correcting errors present in the annotations (commit # ). We will be submitting errata to the ACL anthology (stay tuned), and have included both the earlier, the unprocessed test set and the final, processed test set in `data/test`. The original results were as follows and are incorrect for comparison with other systems reporting results on the JFLEG test set.

|--------------|------|------|------|-------|
| System       | GLEU | P    | R    | F_0.5 |
|--------------|------|------|------|-------|
| Sp. baseline | 55.5 | 57.7 | 16.6 | 38.4  |
| MT baseline  | 54.8 | 56.7 | 14.6 | 36.0  |
| SMEC+morph   | 57.9 | 54.7 | 44.2 | 52.3  |
| SMEC-morph   | 58.3 | 55.9 | 41.1 | 52.2  |
| YB16         | 58.4 | 59.4 | 35.3 | 52.3  |
| Human        | 62.1 | 67.0 | 52.9 | 63.6  |
|--------------|------|------|------|-------|

The newer, correct results are

|--------------|------|------|------|-------|
| System       | GLEU | P    | R    | F_0.5 |
|--------------|------|------|------|-------|
| Sp. baseline | 47.1 | 58.4 | 17.4 | 39.7  |
| MT baseline  | 45.9 | 58.4 | 15.3 | 37.4  |
| SMEC+morph   | 54.2 | 57.4 | 44.6 | 54.3  |
| SMEC-morph   | 53.9 | 58.2 | 42.0 | 54.1  |
| YB16         | 51.9 | 60.7 | 35.5 | 53.2  |
| Human        | 62.4 | 68.8 | 62.9 | 67.5  |
|--------------|------|------|------|-------|

These results should be considered the final results. Systems scored higher when evaluated on the original, unprocessed test set because there were more errors present in that test set and so candidate sentences had greater overlap with those references.

## Notes
Stay tuned for our additions to Joshua (namely an adapted GLEU metric for parameter optimization). Feel free to email me if you'd like them now.

-----
Contact napoles@cs.jhu.edu with any questions.

Last updated: 2017-09-07
