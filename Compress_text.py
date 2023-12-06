import numpy as np
import os
SEPERATOR_PAGES = "*SEPERATOR_PAGES*"
SEPERATOR_EXT = "*SEPERATOR_EXT*"


# Removes the pattern resulting from the conversion of PDF to PNG
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
    convert_texts_to_npz()