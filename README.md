# Repository Structure and Contents
### Documents
- This directory is used to store all documents that the system will sort.
### Model
- This directory contains the pre-trained model used for the binary classification of documents. In this directory, you will find assets, variables, fingerprints, and Keras metadata used for the model and the saved model.
### Compress_text.py
- This file combines multi-page documents back into one text file and compresses these text files into a single npz file, which is fed to the model in Model_execution.
### Dockerfile
- This file is used to set up and install external dependencies in the docker container environment.
### Document_preprocessing.py
- This file converts PDF documents to PNG images, separates multi-page documents into multiple images, and removes noise and small artifacts from documents to improve OCR accuracy. 
### Helper_functions.py
- This file contains an assortment of helper functions used throughout the repository.
- get_confidence_levels - This function is where you are able to set the **admin password** and the default **confidence values**.
### Keyword_identifier.py
- This file contains a set of medical keywords that are used to scan files in text form. If any keyword is found in the text file, it will immediately be moved to the `Medical` folder.
### Load_modules.py
- This file loads all required modules into the environment, outputting a message to the console to let the user know these modules are loading.
### MASTER_SCRIPT.py
- This script executes the entire system workflow to properly preprocess and sort documents.
### Model_execution.py
- This file runs the model on the npz file generated from Compress_text.py, outputting a file of fileName, confidence value pairs. This file is then fed into a helper function to sort the documents within the container.
### requirements.txt
- This file contains all required Python libraries for the system to execute.
### Tesseract_OCR.py
- This file contains methods for Tesseract OCR recognition, converting PNG, JPG, and JPEG (PDFs are duplicated and converted to png before this step) documents to text files.

# Required Software
- Docker Desktop Application [https://docs.docker.com/get-docker/]

# Changing CPU Usage
In both files, `Tesseract_OCR.py` and `Document_preprocessing.py`, you are able to specify the maximum number of logical processors that you would like our system to use when parallelizing document processing. The higher the number, the more documents can be processed and transcribed concurrently. You can change this number by searching for `max_workers=` and replacing the value after the `=` with your desired number.

# Usage Instructions
1. Install the Docker Desktop Application using the link in the `Required Software` section.
2. Place all files that require sorting in the `Documents` directory within the `Sorter` repository.
3. Using your local machine's terminal, set the current directory to where the `Sorter`repository is stored.
4. Run the following command to build the docker image
```terminal
docker build -t img .
```
5. Run the following command to run the docker image and sort the files.
```terminal
docker run -it img
```
- It must be run with the -it flag to allow for user interaction, or you can comment line 10 and uncomment line 11 to allow it to run without user interaction.
