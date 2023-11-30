import cv2
import os
import math
import ctypes
import PIL.Image
import cv2
import numpy as np
from wand.image import Image
import pypdfium2.raw as pdfium_c
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

SEPERATOR_PAGES = "*SEPERATOR_PAGES*"
SEPERATOR_EXT = "*SEPERATOR_EXT*"

"""
Convert PDF files to PNG images.
Seperates multi-page documents into multiple PNGs labeled 'SEPERATOR_PAGES0, SEPERATOR_PAGES1, SEPERATOR_PAGES2'.

Input Folder: Documents
Output Folder: NotProcessed
"""

def convertPDF(filepath, output_folder, dpi=300, progress_bar=None):

    pdf = pdfium_c.FPDF_LoadDocument((filepath+"\x00").encode("utf-8"), None)

    # Check page count to make sure it was loaded correctly
    page_count = pdfium_c.FPDF_GetPageCount(pdf)
    assert page_count >= 1

    os.makedirs(output_folder, exist_ok=True)

    scale = dpi / 72.0

    # Load each page and convert it to an image
    for i in range(page_count):
        page = pdfium_c.FPDF_LoadPage(pdf, i)
        width  = math.ceil(pdfium_c.FPDF_GetPageWidthF(page) * scale)
        height = math.ceil(pdfium_c.FPDF_GetPageHeightF(page) * scale)

        # Create a bitmap
        use_alpha = False  # We don't render with a transparent background
        bitmap = pdfium_c.FPDFBitmap_Create(width, height, int(use_alpha))
        pdfium_c.FPDFBitmap_FillRect(bitmap, 0, 0, width, height, 0xFFFFFFFF)

        # Store common rendering arguments
        render_args = (
            bitmap,  # the bitmap
            page,    # the page
            0,       # left start position
            0,       # top start position
            width,   # horizontal size
            height,  # vertical size
            0,       # rotation (as constant, not in degrees!)
            pdfium_c.FPDF_LCD_TEXT | pdfium_c.FPDF_ANNOT,  # rendering flags, combined with binary or
        )

        # Render the page
        pdfium_c.FPDF_RenderPageBitmap(*render_args)

        # Get a pointer to the first item of the buffer
        first_item = pdfium_c.FPDFBitmap_GetBuffer(bitmap)
        # Re-interpret the pointer to encompass the whole buffer
        buffer = ctypes.cast(first_item, ctypes.POINTER(ctypes.c_ubyte * (width * height * 4)))

        # Create a PIL image from the buffer contents
        img = PIL.Image.frombuffer("RGBA", (width, height), buffer.contents, "raw", "RGBA", 0, 1)
        # Save it as a file
        base_name = os.path.splitext(os.path.basename(filepath))[0]
        output_filename = f"{base_name}{SEPERATOR_PAGES}{i}{SEPERATOR_PAGES}{SEPERATOR_EXT}.pdf{SEPERATOR_EXT}.png"
        output_path = os.path.join(output_folder, output_filename)
        img.save(output_path)

        # Free resources
        pdfium_c.FPDFBitmap_Destroy(bitmap)
        pdfium_c.FPDF_ClosePage(page)

        if progress_bar:
            progress_bar.update(1)

    pdfium_c.FPDF_CloseDocument(pdf)


"""
The process is as follows in chronological order:
    Converts images into grayscale
    Changes DPI to 300
    Applies adaptive thresholding
    Dilates then erodes the image
    Removes any borders on the image
    Deskew the image
    Adds a 10 pixel border back on the image

These were the recommended processing per tesseract's documentation.
https://tesseract-ocr.github.io/tessdoc/ImproveQuality.html

Input Folder: NotProcessed
Output Folder: Processed
"""

# 300 DPI is tesseract's ideal DPI
def dpi(np_image):
    with Image.from_array(np_image) as image:
        image.resolution = (300, 300)
        return np.array(image)

# Create border around document
def border(image, thickness=10):
    return cv2.copyMakeBorder(image, thickness, thickness, thickness, thickness, cv2.BORDER_CONSTANT, value=[0, 0, 0])

# Converts image to grayscale then removes noise
def thresholding(image):
    adaptive = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 30)
    return adaptive

# Fixes orientation of image
def deskew(np_image):
    with Image.from_array(np_image) as image:
        image.deskew(0.4 * image.quantum_range)
        return np.array(image)

# Erode then dialtes 
def dilation_erosion(image):
    kernel = np.ones((1, 1), np.uint8) 

    erode = cv2.erode(image, kernel, iterations=1)
    result = cv2.dilate(erode, kernel, iterations=1)

    return result

# https://stackoverflow.com/questions/57858944/opencv-python-border-removal-preprocessing-for-ocr
def remove_borders(image):
    mask = np.zeros(image.shape, dtype=np.uint8)

    cnts = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    cv2.fillPoly(mask, cnts, [255,255,255])
    mask = 255 - mask
    result = cv2.bitwise_or(image, mask)

    return result

# Takes in folder "NotProcssed" processes the images and outputs to folder "Processed"
def process_single_image(input_path, output_path):
    # Read image from input
    image = cv2.imread(input_path)
    grayscale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Process the image
    # changeddpi = dpi(grayscale_image)
    adaptive = thresholding(grayscale_image)
    font = dilation_erosion(adaptive)
    RMborder = remove_borders(font)
    rotImg = deskew(RMborder)

    result = border(rotImg)

    # Write processed image to the output
    cv2.imwrite(output_path, result)

    # Delete the original image
    os.remove(input_path)


def process_pdfs(input_folder='Documents', output_folder='NotProcessed'):
    pdf_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.pdf')]

    # Calculate total number of pages in all PDFs
    total_pages = 0
    for filename in pdf_files:
        filepath = os.path.join(input_folder, filename)
        pdf = pdfium_c.FPDF_LoadDocument((filepath+"\x00").encode("utf-8"), None)
        total_pages += pdfium_c.FPDF_GetPageCount(pdf)
        pdfium_c.FPDF_CloseDocument(pdf)

    # Process PDFs with updated progress bar
    with tqdm(total=total_pages, desc="Converting PDFs to PNGs") as progress:
        for filename in pdf_files:
            filepath = os.path.join(input_folder, filename)
            convertPDF(filepath, output_folder, progress_bar=progress)

def clean_images(input="NotProcessed", output="Processed"):
    input_images = os.listdir(input)

    with ThreadPoolExecutor(max_workers=2) as executor, tqdm(total=len(input_images), desc="Processing Images") as progress:
        futures = []
        for img in input_images:
            filename, file_extension = os.path.splitext(img)
            input_path = os.path.join(input, img)
            output_path = os.path.join(output, f"{filename}{file_extension}")
            future = executor.submit(process_single_image, input_path, output_path)
            futures.append(future)

        for future in futures:
            future.result()
            progress.update(1)