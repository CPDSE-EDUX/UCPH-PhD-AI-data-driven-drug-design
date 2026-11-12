# Workshop 5: Data analysis using AI/ML

## Intro & Warm-up

> **What will happen?** Over four rounds, you’ll build machine learning models that answer real drug discovery questions and in the last round you’ll score the molecules you designed on day 2. For each round you get a **seed script**: it covers loading the data and help you steer how you will build the models. The models help us relate some molecular properties to . Your job is to build these model and assess their abilities. You will be helped by Claude in this task. You can. use the tasks descriptions and the different tips in the seed files to prompt Claude and let it write the code. After each round, we look at the results together and show you one possible solution.
> {: .tip }

In this final workshop, we try to bind together the activities from this week. You’ll compute features introduced in the *Data processing / preparation* lecture earlier today. **GPCRdb** comes from the database lecture on day 1, and at the end, you will score the **5-HT2A** molecules you designed and docked on day 2.

You'll be working in the Claude code app (or VScode if you are already familiar). 

### How each round works

1. **Open the seed 1-4.** Each script is divided into tasks, which corresponds to a specific modelling step.
2. **Understand the task.** The task text has questions and tips to help you understand the role of that step, but it has no code ready. Figure out what needs to be done, how you can do it, and with the help of Claude, generate the related code to execute that task.
3. **We regroup.** We go through the results together, discuss what they mean, and show a (possible) solution.



### Before you start

Open the Claude app, and prepare the working folder. For this, download the following set up:

[Workshop data (ZIP)](downloads/workshop_day5.zip)

It contains a `requirements.txt` to load all the necessery libraries, the LIT-PCBA ALDH1 data, the `your_designs/` folder, containing the molecules you designed on day 2, and the seed scripts. Once the folder downloaded and added to Claude, you (or Claude) can start the virtual environment with the following command:

<div class="prompt-actions"><button class="button secondary" type="button" data-copy-target="setup-commands">Copy commands</button><span data-copy-status aria-live="polite"></span></div>

<pre id="setup-commands"><code>unzip workshop_day5.zip
cd workshop_data
python -m venv .venv
.venv/bin/pip install -r requirements.txt</code></pre>


## The workshop in 4 rounds

We have 13:00–16:30, so roughly 45 minutes per round including the discussion. Rounds 1 is a warm up, you learn about classifiers in an *ideal* context. In 2 you learn about regression. In rounds 3, you train a classifier and regression model on 5HT2A ligand data, and in round 4 you apply the models from rounds 2 and 3 to evaluate the molecules you designed.


### Round 0

A test round to see that everything works for you. Open the round 1 seed and run the cells above the first task — the imports and the data loading. You should see the molecule counts print.

| Tasks |
| --- |
| • Create the environment and install the requirements.<br>• Run the loading cells of the round 1 seed.<br>• Confirm you see `107,237 molecules, 5,363 actives` or similar.<br>• Ask Claude to explain one thing in the file you don’t recognise. |



### Round 1 - Classification

Virtual screening is a needle-in-a-haystack problem. The modelling problem we'll have to deal with is: a model that classifies *everything* as inactive would scores 95% accuracy. It would look good, but be completely useless. So how do we build a useful model to classify active and inactive molecules?

This round is about measuring the thing you actually care about: **how many real hits sit in the slice of the library you could afford to buy.** That is the enrichment factor.


| Tasks |
| --- |
| • Featurize the molecules: descriptors and ECFP4 fingerprints.<br>• Split the data into training-validating sets.<br>• Train a random forest on descriptors, on fingerprints, and on both.<br>• Evaluate the three models.<br>• Visualise the results.<br>


### Round 2 - Regression

In the [OpenADMET CYP challenge](https://openadmet.ghost.io/take-me-heme-binding-modes-wrapping-up-the-cyp-inhibition-challenge/) we want to predict the pIC50 at which a compound inhibits each of four cytochrome P450 isoforms (1A2, 2C9, 2D6, 3A4). Inhibit these and you cause drug–drug interactions, so this is a liability you want to predict before you ever make the compound.

We build a deliberately simple regressor on the challenge’s own train/test split, so you can eventually look at the leaderboard and see how your model performs.

Make sure to save the model in a file, we'll reuse it in round 4, to test the possible toxicity of your compounds.

| Tasks |
| --- | 
| • Featurize both splits.<br>• Inspect the data.<br>• Train one regressor per isoform. Which CYP is hardest, and why?<br>• Use regression metrics against a mean baseline: can you beat it?<br>• Save the `cyp.joblib` for round 4.<br>

### Round 3 - Case study: 5-HT2A

Now your own target. We pull the measured ligands of the human 5-HT2A receptor straight from [GPCRdb](https://gpcrdb.org/), the resource from day 1. GPCRdb lists measured ligands, so there are **no inactives in it**, the weakest thing in there still binds. We therefore cannot build the active/inactive classifier from round 1. What we can do is split the known ligands at a potency threshold and ask a different, answerable question: potent or weak?

You'll build two models from this data:

1. a **classifier** to answer: is the molecule a potent or weak binder?
2. a **regressor** to predict the molecule's binding affinity, pKi

Save both models for round 4.

| Tasks |
| --- |
| • Inspect the data. <br>• Train the classifier at a potency threshold of your choosing. <br>• Train the pKi regressor. <br>• Evaluate the results of the models. <br>• Save `5ht2a_classifier.joblib`, `5ht2a_regressor.joblib` and the reference ligands for round 4.<br>

### Round 4 - Score your own designs

Everything comes together. We have added the molecules you designed in `your_designs/workshop_designs.smi`, one per line as `SMILES<tab>name`. The seed loads the models you trained in rounds 2 and 3.
How can you use the models you built to evaluate new molecules, such as your designs?

The models give you predictions on:
- how likely is the molecule to be **potent or weak** at 5-HT2A
- **affinity**, pKi, of 5-HT2A
- **CYP inhibition** across all four isoforms
- **how novel** your structure is against the 5-HT2A ligand set (using the Tanimoto similarity measure)

| Task |
| --- | 
| • Featurize the new compounds.<br>• Compute novelty of your designs.<br> • Make predictions from your models.

<div class="workshop-banner"><div><strong>Reference material</strong><span>Where these datasets and benchmarks come from.</span></div><div><a class="button secondary" href="https://drugdesign.unistra.fr/LIT-PCBA/">LIT-PCBA ↗</a> <a class="button secondary" href="https://huggingface.co/datasets/openadmet/cyp-challenge-train-test">OpenADMET CYP ↗</a> <a class="button secondary" href="https://gpcrdb.org/">GPCRdb ↗</a> <a class="button secondary" href="https://www.rdkit.org/docs/">RDKit docs ↗</a></div></div>
