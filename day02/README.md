# Day 2 – Structure-based drug design (small molecules)

[Course overview](../README.md) · [Full program](../PROGRAM.md)

**10 November 2026** · Lectures 09:00–12:00 · Lunch 12:00–13:00 · Workshop 13:00–17:00

Explore the structure-based drug design toolbox, computational hit identification and hit-to-lead optimization, and drug–target molecular interactions. Apply these concepts in a structure-based ligand optimization workshop.

## Day program

| Session | Content | Teacher | Affiliation |
| --- | --- | --- | --- |
| Lecture 4 | The structure-based drug design toolbox<br>Docking, LigPlot, SiteMap etc. | David Gloriam | ILF, UCPH |
| Lecture 5 | Computational hit identification & hit-to-lead optimization<br>Compounds properties being optimized and case story. | Henrik Daver | Lundbeck A/S |
| Lecture 6 | Drug-target molecular interactions<br>Molecular interactions (H-bonds etc.), shape fit and its role in selectivity etc. | David Gloriam | ILF, UCPH |
| Workshop 2 | Structure-based ligand optimization<br>Competition to build the best drug | Kasper Harpsøe, Icaro Simon, Pablo Macho, Jody Pacalon, David Gloriam | ILF, UCPH |

## Workshop: Human vs AI

**Structure-Based Design of Selective 5-HT2A Ligands**

**Draft workshop plan.** The preparation checklist and teaching decisions below remain to be finalized.

[Download the workshop outline (Word)](workshop-outline.docx)

**Tools:** PyMOL, Maestro with LigPrep and Glide, and access to a chatbot. Structure files, software access and loading instructions will be provided for the workshop.

**Central challenge**

Starting from LSD, design three molecules predicted to retain or improve 5-HT2A affinity while increasing selectivity over 5-HT2B. Can human structure-based reasoning outperform AI?

Concept. Students first use PyMOL, aided by chatbots, to interrogate a prepared 5-HT2A-LSD structure. They then compare 5-HT2A and 5-HT2B to formulate binding affinity and selectivity hypotheses, design three compounds themselves, and independently obtain three chatbot-generated designs. All compounds are pooled and docked live with Glide/Maestro. The session ends with a prospective group-vs-group plus human-versus-AI comparison and a discussion of what docking can and cannot tell us.

### Learning objectives

- Interrogate a protein-ligand complex in PyMOL and identify key molecular interactions.
- Use surface properties such as hydrophobicity and electrostatics to reason about ligand binding.
- Compare homologous binding sites and formulate structural hypotheses for subtype selectivity and improving (at least not decreasing) binding affinity.
- Translate structural observations into concrete medicinal chemistry modifications.
- Use chatbots both as scientific copilots and as molecular-design assistants.
- Critically evaluate AI-generated suggestions for chemical and structural plausibility.
- Use docking as a prospective ranking and hypothesis-testing method, not as experimental ground truth.

### Workshop outputs

- Three human-designed candidate ligands per team.
- Three chatbot-generated candidate ligands per team.
- A short structural rationale and predicted affinity/selectivity direction for each submission.
- A live Glide docking leaderboard for 5-HT2A and 5-HT2B.
- A class-level comparison of human and AI design performance.

### Session overview

| Time | Activity | Main concept / output |
| --- | --- | --- |
| 13:00-13:20 | Introduction and PyMOL demo | Challenge, workflow, competition rules |
| 13:20-14:05 | Structural analysis of 5-HT2A-LSD | Molecular recognition and pocket properties |
| 14:05-14:35 | 5-HT2A vs 5-HT2B comparison | Structural basis of selectivity |
| 14:35-14:45 | Break |  |
| 14:45-15:10 | Human molecular design | Three structure-guided candidates |
| 15:10-15:30 | Chatbot molecular design | Three AI-suggested candidates |
| 15:30-15:45 | Submission and predictions | Prospective hypotheses locked in |
| 15:45-16:25 | Live Glide/Maestro docking | 5-HT2A and 5-HT2B prediction |
| 16:25-16:50 | Leaderboard and comparison | Human vs AI performance |
| 16:50-17:00 | Debrief | Interpretation, limitations, next experiment |

> Pedagogical storyline: OBSERVE -> COMPARE -> HYPOTHESIZE -> DESIGN -> PREDICT -> CHALLENGE -> CRITIQUE

### 1. Introduction and challenge (13:00-13:20)

Purpose: establish the scientific problem and explain that the afternoon is a prospective design challenge rather than a software tutorial.

#### Brief conceptual introduction

- 5-HT2A is the desired target, and LSD is the structural starting point.
- 5-HT2B is an important off-target, so the design objective is not only strong predicted 5-HT2A binding but also improved subtype selectivity.
- The workflow follows a medicinal-chemistry decision cycle: structure -> hypothesis -> design -> prediction -> critique.

#### Competition rules

Suggested team size: 3-4 students.

Each team submits six molecules: G#H1-G#H3 (human-designed) and G#AI1-G#AI3 (chatbot-generated).

Important: students remain responsible for deciding whether the chatbot proposals are chemically and structurally plausible.

#### PyMOL demo

Keep the demonstration short and task-oriented. Show only the operations needed for the exercise and provide a cheat sheet so that the workshop does not become a syntax exercise.

### 2. Structural investigation of 5-HT2A-LSD (13:20-14:05)

Students fetch a 5-HT2A-LSD complex and use PyMOL to investigate why LSD binds. Chatbots are explicitly allowed as copilots for generating PyMOL commands and helping interpret observations.

#### Required analyses

- Identify ionic interactions, hydrogen bonds, aromatic interactions, hydrophobic contacts and shape complementarity.
- Inspect polar versus hydrophobic regions of the binding site.
- Identify solvent-exposed regions and available cavities around LSD.
- Display the binding-pocket surface.
- Color or otherwise represent the surface by hydrophobicity.
- Display an electrostatic-potential representation or an equivalent electrostatic view.

#### Example chatbot use

"I have a 5-HT2A receptor-LSD complex loaded in PyMOL. Help me identify residues within 4 A of LSD and display them as sticks."

"How can I display the molecular surface and color the binding pocket according to hydrophobicity?"

"Based on these contacts and pocket properties, what structural features might be exploitable to increase ligand affinity?"

#### Mini-deliverable

Each team records three observations in an Observation -> Design consequence format. The emphasis is on turning structural inspection into a testable medicinal-chemistry hypothesis.

| Structural observation | Possible design consequence |
| --- | --- |
| Hydrophobic cavity adjacent to one part of LSD | Consider a small hydrophobic substituent. |
| Polar feature close to an accessible ligand position | Consider a group capable of a favorable polar interaction. |
| Tightly packed region around the ligand | Avoid additional steric bulk in that direction. |

### 3. Structural basis of 5-HT2A / 5-HT2B selectivity (14:05-14:35)

Students fetch and align a 5-HT2B structure to 5-HT2A and inspect the region around the ligand. They use structural superimposition to identify opportunities for subtype-selective design.

- Non-conserved binding-site residues.
- Differences in side-chain orientation.
- Differences in local pocket shape or volume.
- Potential steric conflicts in 5-HT2B that may be tolerated in 5-HT2A.
- Differences in polarity or hydrophobicity that could be exploited.

Required conclusion: each team formulates one affinity hypothesis and one selectivity hypothesis before designing compounds.

| Hypothesis | Statement |
| --- | --- |
| Affinity hypothesis | "Modification X should improve 5-HT2A binding because..." |
| Selectivity hypothesis | "Modification Y should be better accommodated by 5-HT2A than 5-HT2B because..." |

### 4. Human medicinal chemistry vs AI design (14:45-15:30)

The design phase deliberately separates human structure-based reasoning from chatbot-generated ideas so that the two approaches can be compared prospectively.

#### A. Human design (14:45-15:10)

Each team designs three LSD analogues based on its own structural analysis. Ideally the three designs represent different hypotheses rather than minor variants of the same idea.

- H1 - affinity-driven design: optimize an interaction or fill available space.
- H2 - selectivity-driven design: exploit a 5-HT2A / 5-HT2B structural difference.
- H3 - combined design: attempt to improve both affinity and selectivity.

Each molecule is built directly in Maestro using the 2D-builder, students should also provide the modification relative to LSD, the expected benefit, a structural rationale, and the expected direction of 5-HT2A / 5-HT2B selectivity.

#### B. Chatbot design (15:10-15:30)

Students then ask a chatbot to independently propose three molecules with the same design objective. Do not prescribe a single "perfect" prompt. Different prompting strategies are part of the experiment.

- Provide LSD as the starting ligand.
- State the desired target (5-HT2A) and off-target (5-HT2B).
- Provide relevant structural observations discovered during the workshop.
- Ask for concrete, chemically interpretable modifications and a rationale.

AI quality-control question: "Would I actually dock this molecule? Why or why not?" Students should reject or revise clearly implausible suggestions before submission.

### 5. Submission and prospective predictions (15:30-15:45)

Teachers collect all designs in a shared form or spreadsheet. The predictions should be locked before any docking result is revealed.

| Team | Origin | ID | SMILES / structure | Main hypothesis | Expected effect |
| --- | --- | --- | --- | --- | --- |
| Team 4 | Human | G#H2 | ... | Exploit subtype pocket difference | 2A affinity up; selectivity up |
| Team 4 | AI | G#AI1 | ... | Chatbot rationale | 2A affinity up; selectivity up |

Each team should also nominate one compound as "our predicted winner" before seeing docking results.

### 6. Live Glide / Maestro docking (15:45-16:25)

Pool the submitted molecules and run a live docking demonstration for the full ligand set (all groups) while the students prepare the protein plus ligands, calculate grids and dock their own compounds. The live component should focus on ligand preparation, docking, result inspection and interpretation.

> Recommended live workflow: Submitted structures -> LigPrep -> 5-HT2A Glide docking -> 5-HT2B Glide docking -> scores + pose inspection -> leaderboard

- Show enough of Maestro to explain what LigPrep, the receptor grid and Glide are doing.
- Dock to both 5-HT2A and 5-HT2B so the class can assess the stated selectivity objective.
- Inspect poses as well as scores; a favorable score with an implausible pose should be discussed, not celebrated uncritically.
- Emphasize that GlideScore is a model-dependent ranking quantity, not an experimental affinity measurement.

Simple selectivity metric: GlideScore(5-HT2B) - GlideScore(5-HT2A). Under the usual negative-score convention, a more positive value indicates a stronger predicted preference for 5-HT2A. Treat this as a teaching metric rather than a validated quantitative free-energy prediction. Consider calculating Ki and fold-change.

### 7. Leaderboard and Human vs AI comparison (16:25-16:50)

Use the competition to motivate discussion, but keep the scientific interpretation central. A useful format is to award separate rankings for predicted 5-HT2A binding and predicted subtype selectivity.

| Challenge | Ranking | Interpretation |
| --- | --- | --- |
| Affinity challenge | Gold / Silver / Bronze | Best predicted 5-HT2A docking scores |
| Selectivity challenge | Gold / Silver / Bronze | Best predicted preference for 5-HT2A over 5-HT2B |
| Overall design award | Optional | Strong performance on both criteria plus a plausible pose |

Compare human and AI molecules not only by the winners but also at class level. Depending on time, summarize median 5-HT2A score, predicted selectivity, number of implausible poses and chemical diversity. A simple scatter plot of 5-HT2A docking score versus predicted selectivity could be generated on the fly if convenient.

### 8. Debrief (16:50-17:00)

Close with a short whole-class discussion. The questions below should make explicit what was learned about both structure-based design and AI-assisted drug discovery.

1. Did docking support your original structural hypothesis? If not, why might that be?
1. Did the chatbot propose anything useful that the human team did not think of?
1. Did the chatbot also propose chemically or structurally questionable ideas?
1. Which evidence would you trust most when structure, docking and AI disagree?
1. What experiment would you perform next to test the best hypothesis?

> Key methodological message: Winning the docking competition does not mean that a team designed the highest-affinity ligand. It means that the molecule scored best according to this particular computational model.

### Instructor preparation checklist

- Prepared and cleaned 5-HT2A-LSD structure for all students.
- Prepared 5-HT2B structure aligned to 5-HT2A for the selectivity exercise.
- PyMOL session files or clearly defined loading instructions.
- Short PyMOL cheat sheet covering selections, sticks, surfaces, labels, distances, hydrophobicity and electrostatic visualization.
- Chatbot access confirmed for students; decide whether any model(s) should be recommended or whether model choice is open.
- Shared submission form/spreadsheet with fixed fields and unique team/compound IDs.
- Validated LigPrep workflow and pre-generated Glide grids for both receptors.
- Test docking on a small set of representative LSD analogues to estimate live runtime.
- Fallback precomputed docking results in case the live calculation is too slow or fails.
- A simple script or spreadsheet formula for calculating the selectivity metric and generating the leaderboard.
- Optional small prizes or symbolic Gold/Silver/Bronze awards.

### Suggested instructor roles during the session

| Role | Main responsibility |
| --- | --- |
| Lead instructor | Introduces the challenge, coordinates timing and leads the final scientific discussion. |
| PyMOL / structural support | Helps students with structural analysis, visualization and receptor superimposition. |
| Medicinal chemistry support | Challenges design rationales and checks whether proposed modifications are interpretable. |
| AI / prompting support | Helps students use chatbots productively without turning suggestions into unquestioned answers. |
| Docking operator | Collects submissions, prepares ligands, runs live Glide docking and produces the leaderboard. |

### Points to agree among teachers before the course

- Exact 5-HT2A and 5-HT2B structures and protonation/state preparation used for the exercise.
- How much receptor-specific information should be revealed versus discovered by students.
- Whether students may make any chemical modification or should remain within a defined LSD analogue space.
- Whether the AI designs must be accepted verbatim or may be rejected/revised after student quality control.
- Docking protocol and scoring/ranking rules, including handling of multiple protonation states or stereoisomers.
- Whether medals are awarded separately for affinity and selectivity, or whether an additional overall prize is used.
- How to communicate docking limitations so the competition remains engaging without implying experimental validation.

### Core take-home messages

- AI can act as a scientific copilot for interacting with complex software and structural data.
- AI can also generate molecular hypotheses, but those hypotheses still require chemical and structural judgement.
- Strong drug-design decisions integrate structural reasoning, chemical knowledge and computational predictions.
- Affinity and selectivity are distinct design objectives and should be evaluated separately.
- Docking provides model-dependent evidence. The goal is to formulate better testable hypotheses, not to generate the lowest score.
