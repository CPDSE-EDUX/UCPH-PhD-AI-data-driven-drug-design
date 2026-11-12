# 01 · Warm-up: the databases on the web

**Goal:** see the data the way most people do — on the websites — before you touch any code. Keep these tabs open; you will compare them with what the code returns later.

Open each link, do the search, and note the answer.

## 1. Open Targets Platform

[platform.opentargets.org](https://platform.opentargets.org/)

- Search **semaglutide**. Under *Mechanisms of action*, which protein does it act on, and how (agonist or antagonist)?
- Search **GLP1R** (the target). In *Associated diseases*, which disease has the highest score?

## 2. ChEMBL

[ebi.ac.uk/chembl](https://www.ebi.ac.uk/chembl/)

- Search **sitagliptin**. What is its ChEMBL ID, and what is its highest clinical phase?
- On the sitagliptin page, find its **target** under *Drug mechanisms*. How many bioactivity records does ChEMBL have for that target?

## 3. Open Targets GraphQL browser

[Open the GraphQL browser](https://api.platform.opentargets.org/api/v4/graphql/browser)

Explore the different queries you can run and the fields you can request for drugs, targets and diseases.

## What you take away

The websites are quick for one search, but slow if you want 300 targets or 70 drugs at once. That is what the notebook does for you, starting in the [next step](02-open-targets.md).
