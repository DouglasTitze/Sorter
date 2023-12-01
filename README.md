# Repository Structure and Contents
## Documents
- This directory is used to store all documents that will be sorted by the system.
## Model
- This directory contains the pretrained model used for the binary classification of documents. In this directory you will find assets, variables, fingerprint, and keras metadataand used for the model as well as the saved model.
## Compress_text.py
- This file splits up multi-page documents, converting documents to textfiles, and compressing the text documents into a single npz file.
## Dockerfile
- This file is used to setup and install external dependencies in the docker container environment.
## Document_preprocessing.py
- This file converts PDF documents to PNG inages, separates multipage documents into multiple images, and removes noise and small artifacts from documents to improve OCR accuracy. 
## Helper_functions.py
- This file contains an assortment of helper functions used throughout the repository.
## Load_modules.py
- This file loads all required modules into the environment, outputting a message t the console to let the user know these modules are loading.
## MASTER_SCRIPT.py
- This script executes the entire system workflow to properly preprocess and sort documents.
## Model_execution.py
- This file runs the model on the npz file generated from Compress_text.py, classifying documents and placing them into folders based on the user selected confidence interval.
## requirements.py
- This file contains all required dependencies for the system to execute.
## Tesseract_OCR.py
- This file contains methods for Tesseract OCR recognition, converting PNG documents to text files.

# Required Software
- Docker Desktop Aplication [https://docs.docker.com/get-docker/]

# Usage Instructions
1. Install Docker Desktop Application using the link provided under the `Required Software` section.
2. Place all files that require sorting in the `Documents` directory within the `Sorter` repository.
3. Using your local machines terminal, set the current directory to the location where the `Sorter`repository is stored.
4. Run the following command to build the docker image
```
docker build -t img .
``` 
5. Run the following command to run the docker image and sort the files
```
docker run img
```

