import os
import shutil
import re
from tqdm import tqdm

SEPERATOR_PAGES = "*SEPERATOR_PAGES*"
SEPERATOR_EXT = "*SEPERATOR_EXT*"

def keywordSort(path='TextDocuments'):
    '''
    Responsible for sorting files containin keywords directly in the "Medical" folder before model execution
    '''

    # Set of keywords used to identify medical documents. Add or remove words from the list below.
    medical_keywords = {
        "provider",
        "care plan",
        "physician",
        "eob",
        "dr.",
        "doctor",
        "diagnosis",
        "treatment",
        "symptoms",
        "patient",
        "medical history",
        "medication",
        "allergies",
        "vital signs",
        "laboratory results",
        "lab results",
        "prognosis",
        "physical examination",
        "prescription",
        "prescribed",
        "health record",
        "family history",
        "adverse reactions",
        "anesthesia",
        "discharge summary",
        "immunization",
        "pathology",
        "health insurance",
        "healthcare",
        "chronic condition",
        "acute condition",
        "genetic testing",
        "blood pressure",
        "Heart rate",
        "respiration rate",
        "body temperature",
        "electronic health record",
        "medical imaging",
        "explanation of benefits",
        }

    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    path_to_docs = os.path.join(current_dir, path)

    # Validate the directory is there and is a folder
    if not os.path.exists(path_to_docs) and not os.path.isdir(path_to_docs):
        print(f"This directory does not exist!".center(100,"~"))
        raise Exception
    
    # Extract all files from the directory
    files_in_dir = os.listdir(path_to_docs)

    with tqdm(total=len(files_in_dir), desc="Keywords Processing") as pbar:
        # Iterate through every file in the current folder (financial or medical)
        for file in files_in_dir:
            
            # Check if the file is a txt file, if not continue
            file_path = os.path.join(path_to_docs, file)
            if ".txt" != file_path[-4:]: continue

            try:
                with open(file_path,'r', encoding="utf-8") as f: 
                    # Save the file with its actual extension and not .txt
                    fileName, realExtension, _ = file.split(SEPERATOR_EXT)
                    realFileName = fileName.split(SEPERATOR_PAGES)[0] + realExtension

                    # reading each line    
                    for line in f:
                        # reading each word        
                        for word in line.split():
                            if word in medical_keywords:
                                move_file(realFileName) 
                                os.remove(os.path.join(path_to_docs, file))

                                break
                        else:
                            continue  # only executed if the inner loop did NOT break
                        break  # only executed if the inner loop DID break     
            except:
                print(f"File \"{file}\" failed!")    

            pbar.update(1)            


def move_file(document_name, path="Documents") -> None:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Create a threshold for incorrect directory, if more then this number of documents isn't found in the 
    # input path, then exit the program and notify the user
    THRESHOLD = 2
    # Flagging and sorting medical documents to 'Medical' folder
    destination_folder = 'Medical'

    # Check if the destination folder exists, create it if not
    destination_folder = os.path.join(current_dir, path, destination_folder)
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    # Construct the source and destination paths
    source_path = os.path.join(current_dir, path, document_name)
    destination_path = os.path.join(destination_folder, document_name)
    
    # Try to move documents
    try:
        shutil.move(source_path, destination_path)
        # print(f"Moved {document_name} to {destination_folder.split('/')[-1]}")

    except shutil.Error as e:
        print(f"Error moving {document_name}: {e}")
        if THRESHOLD <= 0:
                print("\n")
                print(f"A lot of documents were not found in \"{path}\"".center(100, "~"))
                print(f"Maybe this was an incorrect path?".center(100, "~"))
                raise Exception
        THRESHOLD -= 1

