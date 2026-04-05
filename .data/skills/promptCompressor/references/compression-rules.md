# Compression Rules — Full Catalog

## Phrase Replacements (applied first)

| Verbose Phrase               | Replacement |
| ---------------------------- | ----------- |
| in order to                  | to          |
| as well as                   | and         |
| due to the fact that         | because     |
| in the case of               | for         |
| at this point in time        | now         |
| on the other hand            | however     |
| in addition to               | besides     |
| a large number of            | many        |
| a small number of            | few         |
| is able to                   | can         |
| are able to                  | can         |
| was able to                  | could       |
| make sure that               | ensure      |
| make sure to                 | ensure      |
| in the event that            | if          |
| with respect to              | regarding   |
| take into account            | consider    |
| it is important to note that | note:       |
| it should be noted that      | note:       |
| for the purpose of           | to          |
| in the process of            | while       |
| on a regular basis           | regularly   |
| at the present time          | now         |
| for the most part            | mostly      |
| in the near future           | soon        |
| in the context of            | in          |
| with regard to               | regarding   |
| in terms of                  | in          |
| as a result of               | from        |
| prior to                     | before      |

## Word Removal Sets

### Articles (always removed)

`a`, `an`, `the`

### Auxiliaries (always removed)

`is`, `are`, `was`, `were`, `am`, `be`, `been`, `being`, `have`, `has`, `had`, `do`, `does`, `did`

### Intensifiers (always removed)

`very`, `quite`, `rather`, `somewhat`, `really`, `extremely`, `essentially`, `particularly`, `especially`

### Fillers (always removed)

`currently`, `basically`, `actually`, `simply`, `just`, `certainly`, `definitely`, `obviously`, `clearly`, `literally`

## Preserved Words (never removed)

### Negations

`not`, `no`, `never`, `without`, `nor`, `neither`

### Uncertainty qualifiers

`may`, `might`, `could`, `seems`, `appears`

### Critical prepositions

`from`, `with`, `must`

## Before/After Examples

| Before                                                              | After                                      | Reduction |
| ------------------------------------------------------------------- | ------------------------------------------ | --------- |
| "The system was designed to process data efficiently"               | "system designed process data efficiently" | 43%       |
| "In order to make sure that the results are accurate"               | "To ensure results accurate"               | 58%       |
| "It is very important to note that this is basically a simple tool" | "note: simple tool"                        | 73%       |
| "The model has been trained on a very large dataset"                | "model trained on large dataset"           | 40%       |
| "There are currently 42 items in the list"                          | "42 items list"                            | 65%       |
| "The API is able to handle extremely high loads"                    | "API can handle high loads"                | 38%       |
