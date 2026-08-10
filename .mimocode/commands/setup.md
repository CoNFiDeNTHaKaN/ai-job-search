---
description: Profile Onboarding — collect the user's professional information and populate all profile files so /apply works out of the box.
---

You are running the onboarding setup for the AI Job Search framework. Your goal is to collect the user's professional information and populate all profile files so the `/apply` workflow works out of the box.

There are three paths into setup. Step 0 picks the right one; all three converge on Step 3 (file generation) and Step 4 (confirmation).

---

## MANDATORY: Interview Gate Rules (apply to ALL paths, non-negotiable)

- Whenever this workflow says "ask follow-up questions", ask them ONE AT A
  TIME. Ask a single question, then STOP your turn and wait for the user's
  reply. Never print a numbered list of questions expecting batch answers.
- For ANY question that has enumerable answer options (path selection,
  yes/no confirmations, portal choices, conflict resolution
  [keep/replace/manual], role type selection, follow-up questions where
  example options can be offered), you MUST use the interactive question
  tool (the TUI's multiple-choice question prompt, which supports
  single-select, multi-select, and custom/free-text answers). Where the
  user might reasonably want an answer outside the offered options,
  include an "Other (type your own)" style option. Plain-text questions
  are permitted ONLY for genuinely open-ended answers with no sensible
  options to offer (e.g. a salary figure, a free-form description). ONE
  question per tool call. "STOP and wait" means: after the tool call, do
  not continue until the user answers — using the question tool itself
  satisfies the stop-and-wait requirement; it does not violate it.
  Choose the selection mode to match the question: use MULTI-SELECT
  whenever more than one answer can reasonably apply (target role types,
  deal-breakers, portals, technologies, location tiers); use
  single-select only for genuinely exclusive choices (path selection,
  yes/no, keep/replace/manual). Always include an "Other (type your
  own)" option in both modes. TAILOR THE OPTIONS: the options you offer
  must be derived from the candidate's own extracted profile and their
  earlier answers — their actual technologies, domains, industries, and
  role history — not generic boilerplate that could be shown to any
  candidate. Example: for a C#/embedded/aerospace background, "what
  excites you" options should include things like "Embedded/IoT product
  development", "Aerospace & defence domain work", "Cloud architecture
  on Azure", "AI/ML engineering" — not only generic items like "complex
  problem solving" or "team leadership". Generic motivational options
  may appear, but the majority of options must be candidate-specific.
- The "never print a numbered list" rule forbids batching multiple
  QUESTIONS into one message — it does NOT forbid offering multiple
  ANSWER OPTIONS for a single question via the question tool.
- NEVER answer a question on the user's behalf. NEVER fill an answer with
  defaults, assumptions, or values inferred from the CV. Inferred is NOT
  answered.
- If the user replies with a meta-answer ("all questions", "yes", "ok",
  "continue", "answer all now") instead of actual content, treat it as NO
  ANSWER: re-ask the SAME question and stop again. Never offer
  batch-confirmation options such as "All verified", "Confirm all", or
  "Continue" that would resolve multiple unanswered questions at once —
  each question gets its own individual answer.
- Data collection is complete ONLY when every follow-up question has a
  literal answer from the user. Until then: do NOT enter Step 3, do NOT
  write files, do NOT print "Setup complete".
- NEVER RE-ASK AN ALREADY-ANSWERED QUESTION: once the user has answered a
  question (Step 0's path choice included), that answer is final for the
  rest of this session — do not present the same question again, via the
  question tool or otherwise, even after unrelated tool calls, file
  reads, or a pause in the conversation. If you are unsure whether a
  question was already answered, check the conversation above before
  asking — do not ask "just in case." Proceed directly with the recorded
  answer instead.
- CONTACT FIELD VERIFICATION: after extracting any CV or document, check
  each of these fields individually: full name, phone, email, LinkedIn
  URL, GitHub URL, location (city, country). PDF extraction often fails
  on hyperlinked text (LinkedIn/GitHub links embedded as clickable links),
  so a missing value is expected, not an error. Before asking the user,
  attempt automatic recovery: run `pdfinfo -url <file>.pdf` on the source
  PDF — it lists the URLs embedded in link annotations. Map the results
  to fields (`tel:` → phone, `mailto:` → email, a linkedin.com URL →
  LinkedIn, a github.com URL → GitHub) and treat values recovered this
  way as verifiably extracted; show them in the summary marked
  "(recovered from PDF link annotations)". Only for fields STILL
  missing, empty, or uncertain after this step, ask the user — ONE field
  at a time, following the rules above. Never leave a contact field
  blank and never guess or reconstruct a URL: a URL not present in the
  text or the `pdfinfo -url` output must be asked, not invented.
- CURRENT EMPLOYMENT STATUS: never infer this from the most recent CV
  entry (a past contract role does not mean the user is still under
  contract). Always ask explicitly what their current employment status
  is (e.g. actively job-seeking / employed and looking / available
  immediately / notice period) with the interactive question tool
  (single-select + "Other"), even if the CV appears to show an ongoing
  role. This value drives cover-letter tone in `/apply` and must come
  from the user, not from a document.
- JOB SEARCH CONFIGURATION IS MANDATORY, NOT OPTIONAL: wherever this
  workflow says "job search configuration" or references "Section 9",
  that means ALL of the following must each be asked as its own
  question (not bundled, not skipped because other questions were
  answered): target role titles to search for, key skills as search
  terms, target companies (optional), geographic scope, PORTAL SELECTION
  (see below), and CV language. None of these may be filled from the CV
  or from inference — they are follow-up questions like any other and
  fall under every rule above (one at a time, question tool, no
  defaults, checklist-gated).
- PORTAL SELECTION (mandatory sub-question, never skip): explicitly ask
  which job portals fit the user's market, using a MULTI-SELECT question
  tool call. Build the options from what actually exists in
  `.agents/skills/*/SKILL.md` at the time of asking (read them first) —
  list each shipped portal by name with its market (e.g. "linkedin-search
  (global)", "freehire-search (global aggregator)", "jobindex-search
  (Denmark, ships disabled)", etc.), plus an "Other (I'll name a portal
  to add)" option. After the answer: enable any Danish/demo portals the
  user selected (flip `enabled: true` in their `SKILL.md` frontmatter);
  for any market-specific board the user names that is not shipped
  (e.g. a country's local job board, or an English-language-jobs board
  for expats), tell them explicitly: "I can scaffold that with
  `/add-portal <name>` after setup finishes" — do not attempt to
  scaffold a new portal mid-setup, just record the request and mention
  the command. Portals the user does not select stay disabled and cost
  nothing.
- PDF READING: Never read a .pdf file directly with the file read tool —
  the model cannot parse binary PDF content and will fabricate plausible
  text. For every PDF, first convert it with
  `pdftotext -layout <file>.pdf <file>.txt`, then read the .txt. If
  pdftotext output is empty or near-empty, the PDF is likely scanned
  (image-based): tell the user which file could not be read and ask them
  to provide its text (paste it, or supply a text-based PDF) — do NOT
  invent content. Extraction claims must be verifiable: every extracted
  value must literally appear in the converted text. If you cannot point
  to it, it is MISSING and must be asked.

---

## Step 0: Welcome & Choose Path

If `$ARGUMENTS` contains `--section <name>`, skip directly to that section in Path C for an update-only flow. Do not run the path-selection prompt below.

Otherwise, before greeting the user, scan the `documents/` folder. Use the glob tool with `documents/**/*` and count files per subfolder (`cv/`, `linkedin/`, `diplomas/`, `references/`, `applications/`).

Then welcome the user with a single message that lists three paths. The wording changes based on what was found. Per the Interview Gate Rules, present the path choice via the interactive question tool: one single-select question with options "Path A", "Path B", "Path C" (labels adapted from the messages below), using the welcome text as the lead-in. Fall back to printing the message below as plain text only if the question tool is unavailable.

**If `documents/` has files** in one or more subfolders, lead with Path A:

> **Welcome to the AI Job Search setup!**
>
> I'll help you build your professional profile so Claude can evaluate job postings, tailor CVs, write cover letters, and prepare you for interviews.
>
> I see files in your `documents/` folder: [list per subfolder, e.g. "2 in cv/, 1 in linkedin/, 3 in references/"]. Three ways to start:
>
> **Path A: Read my documents folder** (recommended for what you have) - I'll read everything in `documents/`, cross-reference for consistency, and build your profile from real source materials. Idempotent and safe to re-run as you add more documents.
>
> **Path B: Single CV import** - Paste or @-mention a single CV/resume here. I'll extract it and ask follow-up questions for what's missing.
>
> **Path C: Interview mode** - I'll walk you through structured questions section by section.
>
> Which would you like?

**If `documents/` is empty or missing**, surface Path A as a "do this if you have materials" option:

> **Welcome to the AI Job Search setup!**
>
> I'll help you build your professional profile so Claude can evaluate job postings, tailor CVs, write cover letters, and prepare you for interviews.
>
> Three ways to start:
>
> **Path A: Documents folder** (best signal if you have several materials) - Drop your CV / LinkedIn export / diplomas / reference letters in the `documents/` folder, then say "go". I'll read everything and build your profile from it. See `documents/README.md` for the folder layout.
>
> **Path B: Single CV import** - Paste or @-mention a single CV/resume here. I'll extract it and ask follow-up questions for what's missing.
>
> **Path C: Interview mode** - I'll walk you through structured questions section by section. Good if you're starting from scratch.
>
> Which would you like?

Wait for the user's choice. If they pick A but the folder is still empty, tell them what to add (point at `documents/README.md`) and stop.

STEP 0 IS SINGLE-SHOT: once the user has answered this path-selection
question, immediately proceed into that path's steps (Path A / B / C
below) and do not present the path-selection question again for the
rest of this `/setup` run, no matter what other tool calls (reading
skill files, converting or reading the CV, etc.) happen in between.

---

## Path A: Documents Folder

Reads structured documents in `documents/`, cross-references them for consistency, and merges extracted data into the seven profile skill files. Read-before-write and idempotent: changes already present will not be proposed again.

Follow these steps **exactly in order**.

### Step A1: Inventory

Use the glob tool with `documents/**/*` to scan the full tree. Print:

```
## Documents Found

**cv/**: [list files, or "(empty)"]
**linkedin/**: [list files, or "(empty)"]
**diplomas/**: [list files, or "(empty)"]
**references/**: [list files, or "(empty)"]
**applications/**: [list subfolders with their files, or "(empty)"]

I will read these and cross-reference before proposing any changes.
```

If every subfolder is empty, stop and tell the user to populate the folder. Point at `documents/README.md` for the layout.

### Step A2: Read Existing Skill Files

Read these in parallel before extracting anything. You must know what is already there to make the merge intelligent.

- `.claude/skills/job-application-assistant/01-candidate-profile.md`
- `.claude/skills/job-application-assistant/02-behavioral-profile.md`
- `.claude/skills/job-application-assistant/03-writing-style.md`
- `.claude/skills/job-application-assistant/04-job-evaluation.md`
- `.claude/skills/job-application-assistant/05-cv-templates.md`
- `.claude/skills/job-application-assistant/06-cover-letter-templates.md`
- `.claude/skills/job-application-assistant/07-interview-prep.md`

Hold this content in context throughout Path A. Do not re-read.

### Step A3: Parse Documents

Read each document found in Step A1. Process subfolders in this order: `cv/`, `linkedin/`, `diplomas/`, `references/`, `applications/`.

**`cv/` documents:** name, contact (email, phone, LinkedIn, GitHub), education (degree, institution, dates, thesis), work experience (title, company, dates, location, bullets), skills, languages (with any stated proficiency), publications, awards, profile/summary.

**`linkedin/` documents:** About/summary section (full text, used for behavioral inference), work experience, education, skills and endorsements, **Languages section** (language name + self-rated proficiency level, e.g. "Spanish - Native or bilingual proficiency" - a high-confidence structured source, feeds the Language Gate in `04-job-evaluation.md`), certifications, volunteer work, publications, recommendations received (full text). If multiple LinkedIn exports are present, use the most recently modified file.

**`diplomas/` documents:** official degree title and level, institution name (official spelling), graduation date, grade or distinction or GPA if visible.

**`references/` documents:** referee name, title, organization; full text of the letter (extract specific quotes); competency language used.

**`applications/<company>_<role>/` subfolders:**
- `job_posting.md`: role title, company, required skills, experience level, sector, role type
- `cover_letter.tex`: opening structure, body structure, bullet style, closing, recurring phrases
- `cv_draft.tex`: profile statement, section ordering, framing for this role type
- `outcome.md`: status (in_progress/hired/offer_declined/rejected/no_response/interview_only), interview stages, notes. Skip `in_progress` applications for calibration — they have no final signal yet.

After reading, proceed to Step A4 without intermediate output. The user sees a complete picture in Step A6.

### Step A4: Cross-Reference Check

Before mapping anything to skill files, check for inconsistencies:

- Date mismatches between CV / LinkedIn / diploma
- Title mismatches across documents for the same role
- Education mismatches (degree name, graduation date)
- Employer name variations

If inconsistencies are found, present them as a numbered list and wait for the user to resolve each one before continuing:

```
## Cross-Reference Issues Found

These need to be resolved before I continue. For each one, tell me which version is correct.

1. **Role title mismatch - [COMPANY]:**
   CV says: "[TITLE_A]"
   LinkedIn says: "[TITLE_B]"
   Which is correct?

2. ...
```

If no inconsistencies, state "No cross-reference issues found." and continue.

### Step A5: Build Change Sets

For each skill file, compare extracted document content against the current file content from Step A2. Build two buckets.

**Additive changes:** entirely new content not in the skill file in any form. Examples: a certification not in `01-candidate-profile.md`, a new endorsement skill, a referee not yet listed, a new behavioral quote from a reference letter, a new award.

**Conflicting changes:** content that touches something already in a skill file but disagrees. Examples: a different date range for an existing job, a different job title for the same role, a different graduation date than what is recorded.

**Inference rules** (apply when populating from inferred sources):

- **`02-behavioral-profile.md`:** Source is LinkedIn About + recommendation letters. Extract recurring themes, adjectives, phrases about how the candidate works. Add only to "Strongest Behavioral Traits", "How [Candidate] Works Best", or "Management Style Preferences" sections. Do not overwrite existing scored assessments. Always label inferred additions: *[Inferred from LinkedIn About / Reference letter - review before relying on this]*
- **`03-writing-style.md`:** Source is `cover_letter.tex` files. Extract recurring patterns. Add as observations under "## Patterns Observed in Past Applications". Do not modify existing rules. Only add if 2+ cover letters show a genuine pattern.
- **`04-job-evaluation.md`:** Source is `job_posting.md` + `outcome.md` pairs. If an application reached interview or offer: note role type and sector as a confirmed strong-fit signal. If 2+ applications repeat a no-response or rejection pattern: note it. Add findings under "## Calibration from Past Applications". Do not modify the existing scoring framework.
- **`05-cv-templates.md`:** Source is `cv_draft.tex` files. Extract any profile statement that does not already appear in templates. Label with: *[Used for: <company>_<role>]*. **Ground before extracting:** archived drafts are tailored outputs, not source documents - verify every factual claim in an extracted statement (titles, employers, metrics, technologies) against `01-candidate-profile.md` and drop or correct any claim the profile does not support, keeping only the framing. A tailored draft that drifted must never become a template future applications start from.
- **`06-cover-letter-templates.md`:** Source is `cover_letter.tex` files. Extract opening patterns, bullet structures, closing formulations. Add only what is structurally distinct from existing templates.
- **`07-interview-prep.md`:** Source is CV bullets, LinkedIn descriptions, reference letter quotes. Identify achievements not yet covered by an existing STAR example. Do NOT draft full STAR examples. Add stubs under "## STAR Candidates (Complete Manually)":

```markdown
### [Achievement title]
**Source:** [CV / LinkedIn / Reference letter - role/company]
**What happened:** [one sentence]
**Why it matters:** [interview question types this could answer]
**S/T/A/R stub:**
- Situation:
- Task:
- Action:
- Result:
```

### Step A6: Present and Confirm Changes

Present the full change set before writing anything.

**Additive changes** (single grouped list, organized by target file):

```
## Proposed Additive Changes

### 01-candidate-profile.md
- [ ] New certification: [title], [issuer], [date] - extracted from LinkedIn
- [ ] New reference: [name, title, company]
  Quote: "[relevant quote]"

### 02-behavioral-profile.md
- [ ] New behavioral observation [labeled as inference]: "[phrase]"

[and so on per file]
```

Then ask:

> **Apply all additive changes?** These add new content without touching anything already in the files.
> Reply **yes** to apply all, or list the numbers you want to skip.

Wait for the response. Apply only the confirmed items.

**Conflicting changes** (one at a time):

```
## Conflict 1 of [N]: Job title - [COMPANY]

**Current in 01-candidate-profile.md:**
[TITLE_A] - [COMPANY] ([START]-[END])

**Proposed (from LinkedIn export):**
[TITLE_B] - [COMPANY] ([START]-[END])

Options:
  [keep] Keep the existing text
  [replace] Replace with the version from the document
  [manual] I'll edit this myself - skip for now
```

Wait for the user's choice on each conflict. If no conflicts, state "No conflicting changes found." and skip this section.

### Step A7: Write Confirmed Changes and Fill Gaps

Apply the confirmed changes with the edit tool. Make targeted edits only. Do not rewrite entire files. State which changes were applied per file. If a file has no confirmed changes, state "No changes made to [filename]."

Documents cover skills, experience, education, references, and behavioral signal. They do not cover everything `/apply` and `/scrape` need. After the writes, ask follow-up questions for gaps:

- Any contact field (full name, phone, email, LinkedIn URL, GitHub URL, location) that could not be extracted from the documents or is uncertain — per the Contact Field Verification rule, ask for each missing field individually; hyperlinked URLs often fail PDF extraction
- Career goals and target role types
- What excites the user in their next role
- Deal-breakers and must-haves
- Current employment status (per the CURRENT EMPLOYMENT STATUS rule — never inferred from the CV)
- Languages you work in professionally, with proficiency levels (only if not already extracted from `cv/` or `linkedin/` above) - this feeds the Language Gate in `04-job-evaluation.md`, so ask directly rather than skipping it
- Salary expectations / baseline (optional)
- Commute or location constraints (if not visible from CV)
- Job search configuration, asked as its own set of questions per the JOB SEARCH CONFIGURATION and PORTAL SELECTION rules above (role titles, key skills, target companies, geographic scope, portal selection, CV language) — use the fuller question wording from Path C Section 9 below, but these are mandatory here too, not skippable

Follow the Interview Gate Rules: one question per turn, wait for each
answer, no defaults. Use the interactive question tool with selectable
options (plus an "Other" option) for every follow-up question above where
options can be offered — e.g. role types, deal-breakers, portals, location
tiers; keep plain text only for open-ended items like a salary figure.
Before leaving this step, print a checklist of every
follow-up question above with the user's literal answer beside it. If any
entry is empty or inferred, go back and ask that question. Only when every
entry has a real answer, continue.

POST-ANSWER REVISION: the seven skill files were written from documents
BEFORE these answers existed. After the checklist passes, revisit the
files the answers affect and reconcile them — in particular: the
role-type profile statements in `05-cv-templates.md` (their target-role
headers and emphasis must match the user's stated target roles, not just
the CV's past), the career goals and motivation filters in
`04-job-evaluation.md`, and any Status/Constraints lines. State which
files were revised.

Then proceed to Step 3 to populate the non-skill files (`CLAUDE.md`, `cv/main_example.tex`, `.claude/skills/job-scraper/search-queries.md`). Step 3 will detect that the seven skill files are already populated and skip those substeps.

---

## Path B: Single CV Import

If the user provides a single CV/resume:

1. Read the document thoroughly.
2. Extract all structured information: name, contact, education, experience, skills, languages, publications, awards.
3. Present a summary of what was extracted. In the summary, list the contact fields (full name, phone, email, LinkedIn URL, GitHub URL, location) each with its extracted value or "MISSING". For every MISSING or uncertain field, ask the user for it one at a time (Interview Gate Rules) before moving on — hyperlinked LinkedIn/GitHub URLs and contact details frequently fail to extract from PDFs even when the CV is ATS-compliant.
4. Ask follow-up questions for gaps (behavioral profile, career goals, deal-breakers, current employment status [per the CURRENT EMPLOYMENT STATUS rule], languages and proficiency levels if not already extracted, salary expectations, references, and job search configuration per the JOB SEARCH CONFIGURATION and PORTAL SELECTION rules above). Follow the Interview Gate Rules: one question per turn, wait for each answer, no defaults.
5. GATE: Before proceeding, print a checklist of every follow-up question with the user's literal answer beside it. If any entry is empty or inferred, go back and ask that question. Only when every entry has a real answer, proceed.
6. Proceed to Step 3 (file generation).

---

## Path C: Interview Mode

Walk through each section conversationally. Ask questions naturally, not as a form. Let the user answer in their own words and you'll structure the data. Per the Interview Gate Rules: one question at a time, and use the interactive question tool with selectable options (plus an "Other" option) wherever the question has enumerable answers.

### Section 1: Identity & Contact
Ask about:
- Full name
- Location (city, country)
- Phone, email, LinkedIn, GitHub
- What languages they work in professionally, and roughly what level in each (native, fluent, conversational, a CEFR letter like B2 - whatever's natural for them to describe, doesn't need to be precise). Worth explaining why: a posting requiring a language they don't list at all gets auto-excluded later by the Language Gate, while one asking for a higher level in a language they do list gets flagged for their own judgment instead of silently passed or rejected - so it's worth being honest here rather than optimistic.
- Current employment status
- Family/commute constraints (if any)

### Section 2: Education
For each degree:
- Level (PhD, MSc, BSc, etc.), field, institution, years
- Thesis topic (if applicable)
- Key coursework or topics

Also ask about certifications (online courses, professional certs).

### Section 3: Professional Experience
For each role (most recent first):
- Job title, company, dates, location
- Key responsibilities (3-5 bullets)
- Key achievements or projects
- Technologies/tools used

Also ask about independent projects, freelance work, or side projects.

### Section 4: Technical Skills
- Programming languages + proficiency level
- ML/AI frameworks and tools
- Domain expertise
- Software tools and platforms
- Any other technical skills

### Section 5: Publications & Awards (optional)
- Peer-reviewed papers, conference presentations
- Hackathons, competitions, awards
- Skip if not applicable

### Section 6: Behavioral Profile (optional)
If they have a formal assessment (PI, DISC, Myers-Briggs, StrengthsFinder):
- Ask them to describe or share the results

If not, ask behavioral questions:
- "What work environments do you thrive in?"
- "What drains your energy at work?"
- "How do you prefer to work in teams?"
- "How do you make decisions, quickly or deliberately?"
- "What's your communication style?"
- Synthesize answers into a behavioral profile

### Section 7: Career Goals & Preferences
- Target roles and industries
- What excites you in work
- Deal-breakers and must-haves
- Salary expectations/baseline (optional)
- What environments to avoid
- Commute/location constraints

### Section 8: References (optional)
For each reference:
- Name, title, company, email, phone
- Relationship to the user

### Section 9: Job Search Configuration
This section generates the search queries that power `/scrape`. Use the information from Sections 1, 4, and 7 to build targeted queries.

Ask about:
- **Role titles to search for:** "What job titles should I search for? For example: Data Scientist, ML Engineer, Geophysicist." Collect 3-8 specific titles.
- **Key skills as search terms:** "Which of your skills are most likely to appear in job postings?" Pick 3-5 that are distinctive and searchable.
- **Target companies (optional):** "Are there specific companies you'd like to monitor for openings?"
- **Geographic scope:** "Which cities or regions should I search in? How far are you willing to commute?" Use this to define the location filter tiers (ideal, acceptable, borderline, too far).
- **Job portals:** Read `.agents/skills/*/SKILL.md` first, then ask via a MULTI-SELECT question tool call listing every shipped portal by name and market (e.g. "linkedin-search (global)", "freehire-search (global aggregator)", "jobindex-search (Denmark, ships disabled)", "jobbank-search (Denmark, ships disabled)", "jobdanmark-search (Denmark, ships disabled)", "jobnet-search (Denmark, ships disabled)"), plus "Other (I'll name a portal to add)". **Then act on the answer:** for any Danish/demo portal the user selected, edit its `SKILL.md` and set `enabled: true` in the frontmatter; leave unselected ones disabled - they cost nothing while disabled and can be enabled later by flipping the flag. If the user selects "Other" or names a market-specific board that is not shipped (a country's local job board, an English-language-jobs board for expats, etc.), do NOT scaffold it now - tell them explicitly: "I can scaffold that with `/add-portal <name>` after setup finishes," record what they asked for, and move on. Websearch/`site:` queries remain the fallback for portals without a CLI skill.
- **CV language:** "Should your CVs be written in English (the default, accepted in most markets), or in your market's language?" Record the answer as a `CV language: <language>` line in CLAUDE.md's Identity section. Cover letters always match each posting's language automatically; this setting governs the CV only. If the user is unsure, keep English and note they can re-run `/setup --section search` to change it.

**Important:** Also suggest role types the user may not have considered, based on their skill profile. For example:
- If they have strong Python + domain expertise: "Have you considered roles like 'Technical Consultant' or 'Solutions Engineer' in your domain?"
- If they have ML + a specific industry: "Companies in adjacent industries also hire for these skills. Should I include searches for [adjacent sector]?"
- If they have project management experience alongside technical skills: "Would you also want to search for 'Technical Project Manager' or 'Team Lead' roles?"

This proactive suggestion step helps users discover career paths they might not have considered.

---

## Step 3: Generate Profile Files

PRECONDITION: the Interview Gate checklist has passed — every follow-up question has a literal user answer. If not, STOP and return to the questions. MECHANICAL GATE — the literal FIRST output of Step 3, before any file is written or any template text is drafted, MUST be this checklist:

```
## Interview Gate Checklist (must pass before file generation)

| Question | User's literal answer |
|---|---|
| Career goals and target role types | [answer or MISSING] |
| What excites the user in their next role | [answer or MISSING] |
| Deal-breakers and must-haves | [answer or MISSING] |
| Current employment status | [answer or MISSING] |
| Languages and proficiency levels | [answer or MISSING] |
| Salary expectations (optional — "skipped" counts as answered) | [answer or MISSING/skipped] |
| Commute or location constraints | [answer or MISSING] |
| Job search: target role titles | [answer or MISSING] |
| Job search: key skills as search terms | [answer or MISSING] |
| Job search: target companies (optional) | [answer or MISSING/skipped] |
| Job search: geographic scope | [answer or MISSING] |
| Job search: portal selection | [answer or MISSING] |
| Job search: CV language | [answer or MISSING] |
```

If ANY row shows MISSING, Step 3 is forbidden: go back and ask that question (one at a time, interactive question tool). A value inferred from the CV or filled by you is MISSING, not an answer. Only when every row holds a literal user answer (or an explicit user "skip" on optional rows), generate or finish populating the following files. **For Path A**, the seven skill files are already populated by Step A7; check each before writing and skip if its content is no longer placeholder text.

### 1. Update `CLAUDE.md`
Replace all `[PLACEHOLDER]` tokens with the user's actual information. Keep the structure, workflow, and verification checklist intact.

### 2. Populate `01-candidate-profile.md` *(Path B and C; skip if Path A populated it)*
Write the full candidate profile with structured sections: Identity (including Languages, with levels), Education, Professional Experience, Independent Projects, Technical Skills, Publications, Awards, References.

### 3. Populate `02-behavioral-profile.md` *(Path B and C; skip if Path A populated it)*
Write the behavioral profile based on assessment results or synthesized answers.

### 4. Update `04-job-evaluation.md` *(Path B and C; skip if Path A populated it)*
Replace skill match areas with the user's actual skills:
- Strong match areas: [their primary skills]
- Moderate match areas: [their secondary skills]
- Weak match areas: [skills they lack]

Update career goals and motivation filters with their actual preferences.

### 5. Update `05-cv-templates.md` *(Path B and C; skip if Path A populated it)*
Add role-specific profile statement templates based on their background.

### 6. Update `07-interview-prep.md` *(Path B and C; skip if Path A populated it)*
Create STAR examples from their actual experience (at least 3-4 examples). Path A leaves STAR stubs under "## STAR Candidates (Complete Manually)" rather than full examples; if any stubs are present, mention them in Step 4 so the user knows to flesh them out.

### 7. Update `cv/main_example.tex`
Replace placeholder personal data with their actual name, contact info, and add their education and most recent experience entries.

### 8. Generate `.claude/skills/job-scraper/search-queries.md`
Replace all placeholder tokens in the search queries file with the user's actual information from Section 9 (or the equivalent follow-up questions in Path A's Step A7):
- Replace `[YOUR_PRIMARY_ROLE_TYPE]`, `[YOUR_PRIMARY_JOB_TITLE]`, etc. with actual role titles
- Replace `[YOUR_KEY_SKILL]`, `[YOUR_DOMAIN_KEYWORD_1]`, etc. with actual skills and domain terms
- Replace `[YOUR_CITY]`, `[YOUR_COUNTRY]`, `[YOUR_REGION]` with actual location
- Fill in the location filter tiers (ideal, acceptable, borderline, too far) based on commute constraints
- Organize queries into priority categories matching the user's career direction:
  - Priority 1: Their strongest/most desired role direction
  - Priority 2: Their domain expertise
  - Priority 3: Adjacent roles they could pivot into
  - Priority 4: Broader roles (wider net)
- PORTAL CONSISTENCY: only write `site:<domain>` query templates for
  portals the user actually selected in the Job Search Configuration
  answers (or portals they asked you to `/add-portal` later, listed as
  "not yet added"). Do not write query templates targeting a disabled or
  unselected portal's domain — if a Danish demo portal stays disabled,
  its domain must not appear in any `site:` line. `linkedin.com/jobs` and
  `freehire.me` can appear by default since their CLIs run regardless.
- LANGUAGE COVERAGE: per this file's own "Language scope" section, write
  each priority category in EVERY language listed in CLAUDE.md's
  Languages table, not only English — this is not optional even if the
  user's CV is in English.

---

## Step 4: Confirm & Next Steps

Present a summary:

> **Setup complete!** Here's what was generated:
>
> - `CLAUDE.md` - Your full candidate profile
> - `.claude/skills/job-application-assistant/01-candidate-profile.md` - Structured profile
> - `.claude/skills/job-application-assistant/02-behavioral-profile.md` - Behavioral assessment
> - `.claude/skills/job-application-assistant/04-job-evaluation.md` - Personalized evaluation framework
> - `.claude/skills/job-application-assistant/05-cv-templates.md` - CV templates with your profile statements
> - `.claude/skills/job-application-assistant/07-interview-prep.md` - STAR examples from your experience
> - `cv/main_example.tex` - Your LaTeX CV template
> - `.claude/skills/job-scraper/search-queries.md` - Job search queries for `/scrape`
>
> **Privacy note:** the files above now contain your personal data and are *tracked by git*.
> A GitHub fork of the template is always public (forks of public repos cannot be made
> private), so do not push these commits to a fork. Keep them local, or push to a private
> repository instead - see SETUP.md section 8 for the private-remote setup.
>
> **Try it out:**
> - Run `/scrape` to search for matching jobs right now
> - Run `/apply` with a job posting URL to see the full application workflow
> - Run `/setup --section search` later to update your search queries as your priorities evolve

If Path A left any STAR stubs in `07-interview-prep.md`, also note:

> Path A flagged [N] STAR candidate stubs in `07-interview-prep.md` that need your situation/task/action/result details before you use them in interviews.

---

## Design Principles

- Three onboarding paths converge on the same skill files. Step 0 picks the right path based on what's in `documents/`. Steps 3 and 4 are shared.
- Path A is read-before-write and idempotent. Re-running it as documents are added does not duplicate or overwrite existing content; conflicts are surfaced for explicit resolution.
- Path A labels inferred behavioral or style additions so the user can review them critically before relying on them.
- Each section in Path C is a natural conversation, not a form. The user can skip optional sections.
- Synthesize answers into structured formats (the user does not need to know markdown or LaTeX).
- Can be re-run with `--section <name>` to update specific sections (e.g., `/setup --section search` to reconfigure job search queries without re-doing the full profile).
- Section 9 (search) in Path C, and the equivalent follow-up questions in Path A, proactively suggest role types the user may not have considered.
- At the end, suggest running `/scrape` and `/apply` with a test job posting.
