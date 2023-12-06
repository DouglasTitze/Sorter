import os
import shutil
import re
from tqdm import tqdm

SEPERATOR_PAGES = "*SEPERATOR_PAGES*"
SEPERATOR_EXT = "*SEPERATOR_EXT*"


def keywordSort(path='TextDocuments'):

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

    append_files(path_to_docs)
    
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


def append_files(file_path):
    # Recognize pattern resulting from conversion of PDF to PNG
    pattern = re.compile(r'(.+)\*SEPERATOR_PAGES\*(\d+).*\.txt')
    
    # List all files that match the pattern
    filenames = [os.path.join(file_path, f) for f in os.listdir(file_path) if pattern.match(f)]
    base_files = {}

    # Get base file name for each set of files to be merged 
    for fname in filenames:
        match = pattern.match(os.path.basename(fname))
        base_name, page_num = match.group(1), int(match.group(2))
        
        if base_name not in base_files or page_num < base_files[base_name][1]:
            base_files[base_name] = (fname, page_num)

    total_files = len(filenames) - len(base_files)

    pbar = tqdm(total=total_files, desc="Appending files")

    # Iterate over each base file and append content from other files with the same base name
    for base_name, (base_filename, _) in base_files.items():
        # Opens base file for read/write
        with open(base_filename, "a+", encoding="utf-8") as f:
            f.seek(0)
            content = f.read()
            if not content.endswith('\n'):
                f.write('\n')
        
        # Opens base file to get appended to
        with open(base_filename, "a", encoding="utf-8") as outfile:
            for fname in sorted(
                [f for f in filenames if pattern.match(os.path.basename(f)).group(1) == base_name and f != base_filename],
                key=lambda x: int(pattern.match(os.path.basename(x)).group(2))
            ):
                # Read from each file and append its content to the base file
                with open(fname, "r", encoding="utf-8") as infile:
                    outfile.write(infile.read().strip() + "\n")

                # Remove file queue when all files are appended
                os.remove(fname)
                pbar.update(1)

    pbar.close()
