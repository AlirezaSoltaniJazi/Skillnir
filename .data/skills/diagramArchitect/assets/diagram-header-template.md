# Diagram Header Template

Paste at the top of every diagram. All five fields are mandatory.

## Mermaid (`%%` comments, then accessibility lines after the diagram keyword)

```text
%% Title: <Noun phrase>
%% Question: <The ONE question this diagram answers>
%% Audience: <Who reads it>
%% Source of truth: <path/to/your/file.ext :: Symbol>  (or "N/A — conceptual")
%% Last verified: YYYY-MM-DD
<diagram keyword, e.g. flowchart LR>
    accTitle: <Short title>
    accDescr: <One or two sentences describing the diagram>
```

## PlantUML (`'` comments, then title + caption)

```text
@startuml <name>.<type>
' Title: <Noun phrase>
' Question: <The ONE question this diagram answers>
' Audience: <Who reads it>
' Source of truth: <path/to/your/file.ext :: Symbol>  (or "N/A — conceptual")
' Last verified: YYYY-MM-DD
title <Short title>
caption <One-sentence summary>
...
@enduml
```

## Field Rules

| Field            | Rule                                                                                 |
| ---------------- | ------------------------------------------------------------------------------------ |
| Title            | Noun phrase, matches the doc heading                                                 |
| Question         | One question. Two questions → two diagrams                                           |
| Audience         | Named role(s); drives vocabulary and abstraction level                               |
| Source of truth  | File path + symbol the diagram was derived from; append `(INFERRED steps: N)` if any |
| Last verified    | Date the diagram was last checked against the source — bump only after re-checking   |
