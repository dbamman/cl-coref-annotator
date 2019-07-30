# cl-coref-annotator
Command-line tool for coreference annotation

Run with:

```sh
python3 anno.py 711_allan_quatermain_brat.txt 711_allan_quatermain_brat.ann 711_allan_quatermain_brat.out
```

Input files are brat .ann and .txt files -- it presumes that you've already carried out mention annotations in brat.

* 711\_allan\_quatermain_brat.txt
* 711\_allan\_quatermain_brat.ann

Output file contains links betweens brat mentions and unique entities:

* 711\_allan\_quatermain\_brat.out

Usage:

|Command|Description|
|---|---|
|n|creates new entity|
|n 17|creates new entity for mention 17|
|[enter]|Accept the suggestion above the prompt (e.g., 'T52 0' links mention T52 to entity 0|
|17|links highlighted mention to existing entity 17|
|14 17|links mention T14 to existing entity 17|
|-1|skip the current mention and go on to the next|
|appos 14 18|links mention T14 to mention T18 with apposition relation|
|cop 14 18|links mention T14 to mention T18 with copula relation|
|del 14|deletes annotation for mention T14|
|entities|displays all current entities|
|names|displays all mentions for each entity|
|s tom|search existing entities to find those that contain 'tom'|
|w|save annotations to output file|
|q|quit and save annotations to output file|
|>|advance to next page|
|<|go to previous page|
|name 17 the main narrator|assigns the name 'the main narrator' to entity 17|
|add he 59 0|creates a new mention for the first mention of the word 'he' between mention T59 and T0; use this if you see a pronoun that should be linked in coreference but isn't a linkable candidate mention.|
|add he 59 0 2|creates a new mention for the second mention of the word 'he' between mention T59 and T0; use this if you see a pronoun that should be linked in coreference but isn't a linkable candidate mention.|
