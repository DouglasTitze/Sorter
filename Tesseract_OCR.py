import os
from time import time
from PIL import Image
import pytesseract
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

SEPERATOR_EXT = "*SEPERATOR_EXT*"

class Converter:
    """
    Contains methods to convert all files, wihtin the input folder, to plain text output
    """

    def __init__(self, folder_path: str = "Documents") -> None:
        """
        Folder path can be input if not inside of the current directory
        """
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        self.folder_path = ""

        # If no path is given, assume Documents folder is within the current directory
        if folder_path == "Documents":
            self.folder_path = os.path.join(self.current_path, folder_path)

        # Otherwise, use the input
        else:
            self.folder_path = folder_path

    def covert_all_files(self) -> None:
        """
        Iterates through the input folder, converts each file into text, and prints their outputs
        """
        inp_files = os.listdir(self.folder_path)

        with ThreadPoolExecutor(max_workers=1) as executor, tqdm(total=len(inp_files), desc="Transcribing Documents") as progress:
            futures = []
            for file_name in inp_files:
                file_path = os.path.join(self.folder_path, file_name)
                future = executor.submit(self.process_file, file_path, file_name)
                futures.append(future)

            for future in futures:
                future.result()
                progress.update(1)

    def process_file(self, file_path: str, file_name: str):
        """
        Process individual file
        """
        timer_start = time()

        # Convert the file into text
        raw_image_text = self._image_to_text(file_path)
        # Write the raw text of the document to a txt file
        self._create_txt_file(file_name, raw_image_text)

        # Delete file from "Processed"
        os.remove(file_path)

        timer_end = time()

    def _image_to_text(self, file_path: str) -> str:
        """
        Returns the files contents as text
        """
        try:
            # Create output to hold the text of the file
            output = ""

            # Save file extension to test for edge case (pdf)
            file_extension = os.path.splitext(os.path.basename(file_path))[1]

            # If the file is a pdf, use its own function
            if file_extension == ".pdf":
                # output = self._pdf_to_text(file_path)
                output = ""
            else:
                # Extract the text from the image, and add it to the output string
                output = pytesseract.image_to_string(Image.open(file_path))

            # Return text from the image
            return output

        except Exception as e:
            raise e

    def _create_txt_file(self, file_name: str, text: str, output_folder_path: str="") -> str:
        # If no custom output folder path is provided, create one relative to the parent of the input folder
        if not output_folder_path:
            output_folder_path = os.path.join(os.path.dirname(self.folder_path), "TextDocuments")

        # Create the folder if it doesn't exist
        if not os.path.exists(output_folder_path):
            os.makedirs(output_folder_path)
        
        splitFileName = os.path.splitext(file_name)
        if file_name.find(".pdf") != -1: mutatedFileName = splitFileName[0] + ".txt"
        else:                            mutatedFileName = splitFileName[0] + SEPERATOR_EXT + splitFileName[1] + SEPERATOR_EXT + ".txt"
        full_txt_path = os.path.join(output_folder_path, mutatedFileName)

        # Write text to the .txt file
        with open(full_txt_path, "a", encoding="utf-8") as f:
            f.write(text)

        return full_txt_path

def transcribe_documents() -> None:
        input_folder = 'Processed'
        converter = Converter(input_folder)
        converter.covert_all_files()