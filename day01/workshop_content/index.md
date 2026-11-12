# Workshop 1: Hunt for drug, target and disease data

**Day 1 workshop**

Collect drug, target and disease data **with code**, so that a search you would otherwise click through by hand can be repeated for any drug, target or disease and rerun when the databases are updated. You then apply the same steps to a disease of your own choosing, possibly from your own research.

No Python experience is needed. All the code is written for you; you run each cell and change a few marked words.

## Run it in Google Colab

The whole workshop is one Jupyter notebook. Open it in Google Colab (nothing to install) and save your own copy:

1. **[Open the notebook in Google Colab](https://colab.research.google.com/github/CPDSE-EDUX/UCPH-PhD-AI-data-driven-drug-design/blob/main/day01/workshop_content/downloads/Workshop1_hunt_for_data.ipynb)**
2. Sign in with a Google account.
3. **File → Save a copy in Drive**, and work in that copy.

Prefer to run it on your own machine? Download the [notebook file](downloads/Workshop1_hunt_for_data.ipynb) and open it in Jupyter.

## Before you begin

- A laptop and a Google account, so you can run the notebook in Colab.
- Optional: if you want to work on a disease from your own research in [Part D](05-your-project.md), note its name and two or three proteins you already know are involved.

## What you will do

The notebook is one continuous story: each step uses a result from the step before.

| Step | What you do |
| --- | --- |
| [Warm-up: the databases on the web](01-warm-up.md) | Look up a drug, a target and a disease on the websites, no code |
| [A · Open Targets from Python](02-open-targets.md) | Follow a thread: semaglutide → its target GLP1R → type 2 diabetes |
| [B · ChEMBL from Python](03-chembl.md) | Sitagliptin → its target DPP4 → potent compounds → similar molecules |
| [C · Worked example](04-worked-example.md) | Find new targets for type 2 diabetes, step by step |
| [D · Your group project](05-your-project.md) | Repeat Part C for a disease of your choice and present three candidate targets |

## Databases used

Open Targets (targets, diseases, associations and drugs) and ChEMBL (measured bioactivities and chemical similarity), reached through their public APIs. Both are introduced in the morning lecture.

## Where to find help

- **Open Targets:** [GraphQL API documentation](https://platform-docs.opentargets.org/data-access/graphql-api) · [GraphQL browser](https://api.platform.opentargets.org/api/v4/graphql/browser) · [Community forum](https://community.opentargets.org/)
- **ChEMBL:** [API documentation](https://www.ebi.ac.uk/chembl/api/data/docs) · [Python client](https://github.com/chembl/chembl_webresource_client) · [web interface](https://www.ebi.ac.uk/chembl/)
- **Tools:** [pandas](https://pandas.pydata.org/docs/user_guide/10min.html) · [RDKit](https://www.rdkit.org/docs/GettingStartedInPython.html) · [Google Colab introduction](https://colab.research.google.com/notebooks/basic_features_overview.ipynb)
