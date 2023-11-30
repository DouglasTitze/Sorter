import os
import re
import time
import shutil

SEPERATOR_CONFIDENCE = "*SEPERATOR_CONFIDENCE*"

def create_folders() -> None:
    folders = ["Processed", "NotProcessed", "TextDocuments"]
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)

def clean_up() -> None:
    '''
    Deletes leftover folders and files
    '''
    print("\nDeleting Excess Files")

    # Sleep to attempt to allow threads to terminate
    time.sleep(1)

    directories = ["NotProcessed","Processed","processed_texts","TextDocuments","__pycache__"]
    for directory in directories:
        # Continue if the directory does not exist
        if not os.path.exists(directory): continue

        try:
            # Remove a directory if empty
            os.rmdir(directory)
            print(f"Deleted directory: {directory}")
        except OSError as e:
            # If the directory is not empty, delete it and its contents
            shutil.rmtree(directory)
            print(f"Recursively deleted directory: {directory}")

    # Delete specific files
    files_to_delete = ["texts_as.npz", "ML_OUT.txt"]
    for file_to_delete in files_to_delete:
        try:
            os.remove(file_to_delete)
            print(f"Deleted file: {file_to_delete}")
        except OSError as e:
            print(f"Unable to delete file: {file_to_delete} - {e}")

def get_confidence_levels() -> (int, int):
    lowerCL = 0.15
    upperCL = 0.85
    
    PASSWORD = "1234"
    inpPassword = input("Please enter an administrator password to edit confidence levels: ")

    if PASSWORD == inpPassword:
        userLowerCL = input("Please enter your desired lowerConfidenceLevel for documents to be classified as Non-Medical: ")
        try:
            userLowerCL = float(userLowerCL)
            if userLowerCL <= 0 or userLowerCL > lowerCL:
                print(f"Your lowerConfidenceLevel is out of the acceptable range, it has been set to the deafault ({lowerCL}).")
            else:
                lowerCL = userLowerCL
        except:
            print("Your input was invalid\nTerminating program")
            exit()

        userUpperCL = input("Please enter your desired upperConfidenceLevel for documents to be classified as Non-Medical: ")
        try:
            userUpperCL = float(userUpperCL)
            if userUpperCL >= 1 or userUpperCL < upperCL:
                print(f"Your upperConfidenceLevel is out of the acceptable range, it has been set to the deafault ({upperCL}).")
            else:
                upperCL = userUpperCL
        except:
            print("Your input was invalid\nTerminating program")
            exit()

    return lowerCL, upperCL

def sort_files(path="Documents") -> None:
    # Name of the ML output file
    ML_OUT = "ML_OUT.txt"

    # Create a threshold for incorrect directory, if more then this number of documents isn't found in the 
    # input path, then exit the program and notify the user
    THRESHOLD = 2

    # Read the input file
    with open(ML_OUT, "r", encoding="utf-8") as file:
        # Read each line from the file
        for line in file:
            # Remove trailing and beginning spaces from the line (NEED THIS OR ELSE \n WILL BE IN EACH LINE)
            line = line.strip()

            # Extract names
            document_name, destination_folder = line.split(SEPERATOR_CONFIDENCE)

            destination_folder, CL = destination_folder.split(" (")

            # Check if the destination folder exists, create it if not
            destination_folder = os.path.join(path, destination_folder)
            if not os.path.exists(destination_folder):
                os.makedirs(destination_folder)

            # Construct the source and destination paths
            source_path = os.path.join(path, document_name)
            destination_path = os.path.join(destination_folder, document_name)

            # Try to move documents
            try:
                shutil.move(source_path, destination_path)
                print(f"Moved {document_name} to {destination_folder.split()[-1]} ({CL}")

            except shutil.Error as e:
                print(f"Error moving {document_name}: {e}")
                if THRESHOLD <= 0:
                        print("\n")
                        print(f"A lot of documents were not found in \"{path}\"".center(100, "~"))
                        print(f"Maybe this was an incorrect path?".center(100, "~"))
                        raise Exception
                THRESHOLD -= 1
                