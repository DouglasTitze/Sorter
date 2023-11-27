def moduleLoadedPrint():
    print(f"Module Sucessfully Loaded".center(100,"~"))
    print()

print(f"The system is loading".center(100,"~"))
print()

print(f"Loading Document Preprocessing Module".center(100,"~"))
from Document_preprocessing import *
moduleLoadedPrint()

print(f"Loading Tesseract Module".center(100,"~"))
from Tesseract_OCR import *
moduleLoadedPrint()

print(f"Loading Text Compresion Module".center(100,"~"))
from Compress_text import *
moduleLoadedPrint()

print(f"Loading Model Execution Module".center(100,"~"))
from Model_execution import *
moduleLoadedPrint()

print(f"Loading Helper Functions Module".center(100,"~"))
from Helper_functions import *
moduleLoadedPrint()

print(f"All modules have been sucesfuly loaded".center(100,"~"))