import numpy as np
import os
import re
SEPERATOR_PAGES = "*SEPERATOR_PAGES*"
SEPERATOR_EXT = "*SEPERATOR_EXT*"


def append_files(file_path):
    pattern = re.compile(r'(.+)\*SEPERATOR_PAGES\*(\d+).*\.txt')
    filenames = [os.path.join(file_path, f) for f in os.listdir(file_path) if pattern.match(f)]
    base_files = {}

    for fname in filenames:
        match = pattern.match(os.path.basename(fname))
        base_name, page_num = match.group(1), int(match.group(2))
        
        if base_name not in base_files or page_num < base_files[base_name][1]:
            base_files[base_name] = (fname, page_num)

    for base_name, (base_filename, _) in base_files.items():
        with open(base_filename, "a+", encoding="utf-8") as f:
            f.seek(0)
            content = f.read()
            if not content.endswith('\n'):
                f.write('\n')
        
        with open(base_filename, "a", encoding="utf-8") as outfile:
            for fname in sorted(
                [f for f in filenames if pattern.match(os.path.basename(f)).group(1) == base_name and f != base_filename],
                key=lambda x: int(pattern.match(os.path.basename(x)).group(2))
            ):
                with open(fname, "r", encoding="utf-8") as infile:
                    outfile.write(infile.read().strip() + "\n")
                print(f"Appended file: {fname}")
                os.remove(fname)

def convert_texts_to_npz(txtFolder="TextDocuments"):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    path_to_docs = os.path.join(current_dir, txtFolder)

    # Validate the directory is there and is a folder
    if not os.path.exists(path_to_docs) and not os.path.isdir(path_to_docs):
        print(f"This directory does not exist!".center(100,"~"))
        raise Exception

    txt_file_names = []
    txt_contents = []

    # Extract all files from the directory
    files_in_dir = os.listdir(path_to_docs)

    # Iterate through every file in the current folder (financial or medical)
    for file in files_in_dir:
        
        # Check if the file is a txt file, if not continue
        file_path = os.path.join(path_to_docs, file)
        if ".txt" != file_path[-4:]: continue
        
        # Add all of the data of the file to the txt_contents and file name to txt_file_names
        all_text = "" 
        try:
            with open(file_path,'r', encoding="utf-8") as f: all_text += f.readline()

            # Save the file with its actual extension and not .txt
            fileName, realExtension, _ = file.split(SEPERATOR_EXT)
            realFileName = fileName.split(SEPERATOR_PAGES)[0]
            
            txt_file_names.append(realFileName + realExtension)
            txt_contents.append(all_text)
        except:
            print(f"File \"{file}\" failed!")

    # Save the arrays as a compressed numpy dataset 
    current_dir = os.path.dirname(os.path.abspath(__file__))
    save_path = os.path.join(current_dir,'texts_as.npz')
    np.savez_compressed(save_path, data=txt_contents,labels=txt_file_names)

def compress_text_files():
    documents_path = os.path.join(os.getcwd(), "TextDocuments")
    append_files(documents_path)
    convert_texts_to_npz()