# 02 · Open Targets from Python

**Goal:** follow one thread through Open Targets — a drug, its target, and the disease most linked to that target — all from the notebook.

Open the notebook ([Colab link on the workshop home](index.md)) and work through **Part A**. This page explains what each step is for; the notebook holds the code and the results.

## The idea

In the warm-up you ran queries in the GraphQL browser and pressed ▶. The notebook sends **the same kind of query** to the same address. The one new idea is a **variable**: a placeholder like `$id` that Python fills in, so one query works for any drug, target or disease.

**The thread in Part A:** semaglutide (a diabetes and obesity drug) → its target GLP1R → the disease most strongly associated with GLP1R, type 2 diabetes.

## The steps

- **A1 · Name → ID.** Databases use IDs, not names. A `search` query turns a name into an ID: ChEMBL IDs for drugs, Ensembl IDs for targets, EFO/MONDO IDs for diseases. ✏️ Here you make your first edit: swap in another drug name.
- **A2 · A drug.** Everything Open Targets knows about semaglutide: its type, highest clinical stage, mechanism of action (which target, and how), and every indication. The result is one table, plus a chart of indications by clinical stage.
- **A3 · A target.** For GLP1R: its class, UniProt ID, tractability (which kinds of drug can reach it), subcellular location, the drugs acting on it, and the diseases most associated with it.
- **A4 · A disease.** For type 2 diabetes: its description, the drugs and candidates for it, and the targets most associated with it. The approved-drug list is where you meet **sitagliptin**, which you follow into ChEMBL next.

## Reading the colours in the notebook

Each step is marked: 🔎 *What this query does* (blue), 📊 *What you get* (green), ▶ *Your turn* (red). Follow the red lines — they tell you exactly what to run or change.

Next: [B · ChEMBL from Python](03-chembl.md).
