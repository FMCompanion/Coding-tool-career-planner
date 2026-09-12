# FM Companion Career Planner v1

## Purpose
Career Planner turns normalized save facts + user career preferences into a persistent managerial roadmap.

It is intentionally parser-agnostic. The existing private Labs remain ground truth for decoded FM data. Career Planner consumes normalized values and never decodes `.fm` binaries itself.

## Main product surfaces
1. **Career Route** — dynasty, journeyman, youth developer, stepping-stone, fallen giant, trophy hunter, realistic climb.
2. **Stay or Leave** — deterministic recommendation with evidence.
3. **Current Project Milestones** — what should be completed before reassessing.
4. **Next Move Profile** — target club level and non-negotiables.
5. **Club Finder Brief** — structured search criteria for the existing Club Finder.
6. **Long-Term Path** — destination profile rather than a fabricated specific job.
7. **AI Q&A** — explain the roadmap, not invent save facts.

## Integration architecture

```text
FM save / user profile
   ↓
normalized manager + club context
   ↓
Career Planner deterministic engine
   ↓
Career plan / next-move brief
   ↓
Club Finder candidate list (optional)
   ↓
Career-fit ranking
   ↓
ChatGPT explanation / Q&A
```

## High-value questions
- Should I leave this club now?
- What should I achieve before moving?
- Am I ready for a Champions League club?
- What type of club should I target next?
- Which of these job offers best fits my career?
- Build me a realistic five-season career path.
- I want a journeyman save — where should I go next?

## Confidence boundary
Inputs such as manager reputation, club level, achievements, tenure and job offers may be absent until their source is wired in. Missing fields stay missing. The deterministic engine must never infer an unseen offer or unseen reputation value.
