# Coding tool - career planner

Reference implementation for **FM Companion Career Planner**.

## Product principle

**Use real save facts + explicit manager preferences to plan a credible career. Never invent job offers, club interest, reputation or achievements.**

Career Planner sits above the existing Labs. It does not decode `.fm` binaries itself.

## What v1 does

- classifies the selected career route;
- scores how mature the current club project is;
- scores manager readiness for a move;
- gives a deterministic **stay / leave / explore** recommendation;
- creates current-job milestones;
- creates a realistic next-club profile;
- generates a structured Club Finder search brief;
- ranks supplied Club Finder/job candidates for career fit;
- maintains a long-term destination profile;
- provides an AI coaching layer for Q&A.

## Architecture

```text
FM Companion normalized save context
        +
user career preferences
        ↓
Career Planner
        ↓
Stay / leave decision
Current project milestones
Next move profile
Club Finder search brief
Long-term career path
        ↓
Optional Club Finder candidates
        ↓
Career-fit ranking
        ↓
ChatGPT explanation / Q&A
```

## Example questions

- Should I leave my club now?
- What do I need to achieve before moving?
- What level of club should I target next?
- Which of these job offers is best for my career?
- Give me a realistic five-season path.
- I want a journeyman career — what kind of move should I make next?

## Public-repo safety

This repository contains **no FM26 binary reverse-engineering internals**. Those remain in the private parser/Lab repositories. Career Planner only consumes normalized input contracts.

See `docs/CAREER_PLANNER_V1.md` and `contracts/career_plan.schema.json`.
