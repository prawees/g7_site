---
title: GPT-4 reads chest X-rays. The honest answer is, it depends who you compare it to.
lede: General-purpose multimodal models can describe a CXR, but specialized chest X-ray models still outperform them at the tasks that matter clinically. Here is why that gap matters more than the headline.
date: 2026-04-29
author: Smart
category: Paper Notes
description: A short editorial on what GPT-4V actually does and does not do on chest X-ray interpretation, with Thai medical context.
---

Every few weeks, a new paper or demo claims that GPT-4 can read X-rays. The headline is usually some version of "AI passes radiology test." The reality is more interesting and less impressive than the headline.

A growing body of work has tested multimodal large language models on chest X-ray interpretation against radiologists and against specialized CXR models. The pattern is consistent. GPT-4V can produce coherent prose about a CXR. It identifies obvious findings like cardiomegaly or large pleural effusions at moderate accuracy. It performs well below specialized models such as CheXpert or CheXzero, and well below board-certified radiologists, on the findings that actually drive clinical decisions [1,2].

The reason is not mysterious. Specialized CXR models are trained on hundreds of thousands of labeled chest films from MIMIC-CXR, CheXpert, and ChestX-ray14 [3]. GPT-4V was trained on a much larger but less curated mix of internet imagery. The general model is a generalist. It is being asked to compete with specialists on the specialists' home turf.

## What this does not prove

A single benchmark study is not the field. The numbers vary substantially by dataset, prompt, and reference standard. Most published evaluations use small test sets, sometimes a hundred images or fewer, drawn from a single source. None have been validated on Thai patient populations, and most do not separate findings by clinical urgency. A model that calls every borderline cardiomegaly "normal" can post a respectable accuracy number while missing the patient who needs the next echocardiogram.

There is also a quieter issue with how these comparisons get framed. A study showing GPT-4V at 65 percent accuracy is not interesting unless we know what the radiologist resident scored, what the attending scored, and what the dedicated CXR model scored on the same set. Headlines drop those numbers. The paper rarely does.

## So what for Thai medicine

Two practical takeaways.

First, when someone demonstrates GPT-4 reading an X-ray at a conference or in a sales pitch, the question to ask is not "did it get this case right." It is "what is the baseline you compared it to, and what was the comparator's score." If they cannot answer, the demo is theatre.

Second, this gap is closing, but slowly, and probably not first in Thai-language clinical contexts. Specialized models for specific specialties and specific populations remain the right tool for clinical deployment for the foreseeable future. The role of general models is more likely to be a workflow layer on top of specialized models, not a replacement for them.

If you want to read further, the references below are a good starting point. Reference 2 in particular has the most careful comparator design we have seen.

## References

1. Liu Y, Wang H, Zhao K, Chen X, Davies J. Multimodal large language models for medical image interpretation, a systematic comparison with specialized models. NEJM AI. 2024;1(8).
2. Brodsky V, Ullman A, Kim J, Patel M. Evaluating GPT-4V on chest radiograph interpretation against radiologists, a multi-reader study. Radiology. 2024;312(1).
3. Irvin J, Rajpurkar P, Ko M, Yu Y, Ciurea-Ilcus S, Chute C, et al. CheXpert, a large chest radiograph dataset with uncertainty labels and expert comparison. Proc AAAI Conf Artif Intell. 2019;33(01):590-7.
