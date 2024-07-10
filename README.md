# FIGNEWS-2024

## Framing the Israel War on Gaza: A Shared Task on News Media Narratives

### Introduction and Motivation

In response to the evolving landscape of media representation and discourse surrounding the Gaza-Israel 2023-2024 war, we propose an innovative shared task aimed at delving into the intricate nuances of bias and double standards prevalent in news articles. This initiative seeks to explore diverse perspectives, cultures, and languages, fostering a comprehensive understanding of the events through the lens of major news outlets across the globe. This shared task seeks to unravel the layers of bias and propaganda within news articles in multiple languages, fostering a collaborative exploration of media narratives surrounding one of the most critical moments in recent history.


The overarching objective is to establish a shared corpus for comprehensive annotation across various layers, crafting annotation guidelines shaped by the diverse range of conflicting discourses around this sensitive topic. This endeavor seeks to bring to light both challenges and commendable aspects within the data and to foster a collaborative community. Furthermore, it aspires to nurture the growth of the next generation of Natural Language Processing (NLP) researchers, equipping them with the skills to engage directly with raw data sources.

You can find more details about this shared task at the [FIGNEWS homepage](https://sites.google.com/view/fignews/home).

The full dataset (including the original and machin translated text lines) can be found on the [CAMeL Lab Hugging Face page](https://huggingface.co/datasets/CAMeL-Lab/FIGNEWS-2024).

### Description of this repository

This repository contains the data and guidelines submitted by the participating teams, as well as a script to calculate metrics both across and within teams. The folder structure is as follows:
```
|- data
    |- FIGNEWS-2024-ALL-CLEAN.tsv
    |- guidelines
|- get_metrics.py
|- LICENSE
|- README.md
|- requirements.txt
```
- **data/FIGNEWS-2024-ALL-CLEAN.tsv** contains all the data collected from the participating teams
- **data/guidelines** contains the guidelines for participating teams
- **get_metrics.py** is the script that is used to generate metrics such as the Cohen's Kappa and the F1 score within and across teams
- **LICENSE** is the MIT License
- **README** is this document
- **requirements.txt** file containing dependencies

### Getting metrics

After selecting your virtual environment, install the required packages:
```
pip install -r requirements.txt
```

You can then obtain the data metrics by running the following:
```
python get_metrics.py -i data/FIGNEWS-2024-ALL-CLEAN.tsv -o [output/dir/of/your/choice]
```

### Shared Task Organizers

Wajdi Zaghouani, Hamad Bin Khalifa University (Qatar)

Mustafa Jarrar, Birzeit University (Palestine)

Nizar Habash, New York University Abu Dhabi (UAE)

Houda Bouamor, Carnegie Mellon University (Qatar)

Imed Zitouni, Google (USA)

Mona Diab, Carnegie Mellon University (USA)

Samhaa R. El-Beltagy, Newgiza University (Egypt)

Muhammed AbuOdeh, New York University Abu Dhabi (UAE)