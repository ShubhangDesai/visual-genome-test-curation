# Visual Genome Test Set Curation
Code used to curate the test set for the Visual Genome dataset.

## Overview

Each time your send a set of images through the AMT pipeline, it is called an "experiment". For example, you may decide to send 10 images through the whole pipeline and call the experiment "10_images". This repo allows you to send these images through the whole pipeline, which consists of 3 stages. Each stage may need to be launched multiple times:

- **Initial launch:** You first send the data through the initial launch of a stage. For example, a stage 1 initial launch on "10_images" would entail showing the 10 images to AMT workers and asking them "How many <s, p, o> are in this image?" for each image. In this example, because we have x tasks per HIT in stage 1, we would launch 1 HIT with 2 assignments, meaning up to 2 workers can work on the HITs.
- **Disagreement launch:** Because we launch 2 assignments for each HIT in the initial launch, we could very well have disagreements. For example, after completing the stage 1 initial launch, say that Worker 1 said image_1 had 3 <s, p, o> while Worker 2 said the same image had 10 <s, p, o>. That's a big difference! We would want to get a third opinion. To that end, we collect all images from the initial launch that had disagreements between workers and send them to AMT again in what's called a disagreement launch. In our exampoe, a stage 1 disagreement launch would show a HIT with 1 task (i.e. image_1) to just 1 worker (i.e. assignments=1). Note: stage 2 cannot have a disagreement launch because of the nature of the task (see Stages: Stage 2 for more info).
- **Relaunches:** In either the initial launch or disagreement launch, a relaunch may be necessary to get acceptable HIT results after a worker fails an attention check (more info on each stage's attention checks in "Stages"). For example, say you run an stage 1 initial launch on "10_images" (recall: up to 2 workers could be working on these HITs). If one of the workers failed an attention check, we would want to relaunch the HIT that they did so that we can get acceptable results. Note: even though it is a relaunch, we would still call this part of the "stage 1 initial launch"! Another note: relaunches can, of course, also happen in the disagreement launch if a worker fails an attention check.

To begin an experiment, you must create a folder in the `data` folder with the experiment's name, and create the `initial_data.json` file. As you send experiment through these launches, the code will incrementally build out other files in the experiment folder. These files keep track of the launch results and change the data as we learn more about it through the AMT HITs. See "data Folder" for more info on these files.

There are various code files that you must interact with in order to successfully send an experiment through the full AMT pipeline. Each file has its own purpose, and they all ultimately touch (i.e. read from or write to) some file in the experiment folder. See "Pipeline" for info on each file.

While it is important that you follow the right steps, don't stress! There are many, many asserts throughout the code that mostly ensure that the steps were followed in the correct order. Even so, it's better to be safe than sorry. See "Workflow" for the detailed steps.



## data Folder

Coming Soon



## Pipeline

Coming Soon



## Workflow

Below is the "psuedocode" for how you should run the various files to send a batch of images (i.e. and experiment) through the pipeline. In summary: for each stage, run the launch, dump the HIT results, and extract the HIT knowledge until no attention checks are failing. For stages 1 and 2, you will have to do this for both an initial launch and a disagreement launch.

```sh
# Stage 1
# -------
do {
    python launch.py --exp_name name --stage 1 --initial_launch --sandbox
    while (there are incomplete HITs) python dump.py --exp_name name --stage 1 --sandbox
    python knowledge.py --exp_name name --stage 1 --sandbox
} while (there are failed attention checks)

do {
    python launch.py --exp_name name --stage 1 --disagreement_launch --sandbox
    while (there are incomplete HITs) python dump.py --exp_name name --stage 1 --sandbox
    python knowledge.py --exp_name name --stage 1 --sandbox
} while (there are failed attention checks)


# Stage 2
# -------
do {
    python launch.py --exp_name name --stage 2 --initial_launch
    while (there are incomplete HITs) python dump.py --exp_name name --stage 2
    python knowledge.py --exp_name name --stage 2
} while (there are failed attention checks)


# Stage 3
# -------
do {
    python launch.py --exp_name name --stage 3 --initial_launch
    while (there are incomplete HITs) python dump.py --exp_name name --stage 3
    python knowledge.py --exp_name name --stage 1
} while (there are failed attention checks)

do {
    python launch.py --exp_name name --stage 3 --disagreement_launch
    while (there are incomplete HITs) python dump.py --exp_name name --stage 3
    python knowledge.py --exp_name name --stage 3
} while (there are failed attention checks)
```



## Other Folders and Files

Coming Soon
