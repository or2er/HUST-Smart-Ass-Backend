# SoICT Hackathon 2023: Vietnamese Spoken Language Understanding Challenge

The SoICT Hackathon 2023, organized by sangdv and hosted on AIHUB.ML, is set to be one of the most significant events in the field of artificial intelligence and machine learning. Scheduled to conclude on Oct. 31, 2023, the competition is focused on the theme of "Vietnamese Spoken Language Understanding".

## Overview

The Hackathon aims to tackle the problem of "Understanding Vietnamese spoken language in a smart home context". Participating teams are expected to develop models that can comprehend the intent of a spoken sentence and extract the entities within that sentence in the context of a smart home.

Through research and training of specific models, the teams will output results that include the intent of the sentence and the label of the entities appearing within the sentence.

![Overview](https://soict.hust.edu.vn/wp-content/uploads/hackathon_banner.jpg)
## Data

The VN-SLU dataset provided by the organization committee comprises approximately 10,300 audio files, with a total duration of about 12 hours. The dataset consists of three non-overlapping subsets:
1. **Training data**: This labeled dataset, used for training the model, consists of 7490 audio files.
2. **Public test**: This dataset is used to evaluate the preliminary round.
3. **Private test**: This more challenging dataset will be released in the final round.

The input to the model will be the audio files without labels. Teams will have to output corresponding results and save them to a .jsonl file, which is then converted to a .zip file and submitted to the system.

![Data](https://lookaside.fbsbx.com/lookaside/crawler/media/?media_id=647129277533882)
## Evaluation Criteria

The evaluation criteria is the average of the Intent-F1 and SLU-F1 scores. The higher the average, the more accurate the model is considered to be.

![Evaluation Criteria](https://i.ytimg.com/vi/16NSKI2NpY8/maxresdefault.jpg)
## Rules

Teams must adhere to SoICT Hackathon 2023's general rules. They are allowed to use only the training data set for training their models and are not allowed to interfere or use the public test or private test in any form during the training process.

Datasets without speech (such as noise data, echo data) may be used during the training process and must be shared with other teams. Teams may use pre-trained models, but they are not allowed to use pre-trained models that have been trained for SLU and NLU tasks (in both Vietnamese and other languages).

![Rules](https://soict.hust.edu.vn/wp-content/uploads/inno_day_2023.jpg)
## Prize

The prizes will be awarded based on the committee's review and verification of the contestants' qualification and adherence to the rules, as well as compliance with the requirements for the winning teams.

The SoICT Hackathon 2023 is an excellent opportunity for participants to make their mark in the field of artificial intelligence and machine learning. The challenge provides a platform for coders, researchers, and enthusiasts to collaborate, innovate, and push the boundaries of what's possible in Vietnamese Spoken Language Understanding. 

It's more than just a competition. It's a chance to contribute to the building of a smarter world, together. So gear up and get ready to join the SoICT Hackathon 2023. The journey of 1000km starts here.
