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


"""
Convert PDF files to PNG images.
Seperates multi-page documents into multiple PNGs labeled '_page0, _page1, _page2'.

Input Folder: Documents
Output Folder: NotProcessed
"""

def convertPDF(filepath, output_folder, dpi=150):

    print("Converting PDF to PNG")
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
        output_filename = "{}_page{}.png".format(base_name, i)
        output_path = os.path.join(output_folder, output_filename)
        img.save(output_path)

        # Free resources
        pdfium_c.FPDFBitmap_Destroy(bitmap)
        pdfium_c.FPDF_ClosePage(page)

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
    kernel = np.ones((3, 3), np.uint8)
    
    # Apply Gaussian blur
    blurred = cv2.GaussianBlur(image, (3, 3), 0)

    # Adaptive thresholding
    _, thresholded = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Opening operation
    opened = cv2.morphologyEx(thresholded, cv2.MORPH_OPEN, kernel)

    # Median filtering
    median_filtered = cv2.medianBlur(opened, 3)

    # Contour detection and drawing
    contours, _ = cv2.findContours(median_filtered, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    result = image.copy()
    for contour in contours:
        cv2.drawContours(result, [contour], -1, (255, 255, 255), 1)

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
    changeddpi = dpi(grayscale_image)
    adaptive = thresholding(changeddpi)
    font = dilation_erosion(adaptive)
    RMborder = remove_borders(font)
    rotImg = deskew(RMborder)

    result = border(rotImg)

    # Write processed image to the output
    cv2.imwrite(output_path, result)
    print(f"\"{os.path.basename(input_path)}\" completed image processing")

    # Delete the original image
    os.remove(input_path)


def process_pdfs(input_folder='Documents', output_folder='NotProcessed'):

    for filename in os.listdir(input_folder):
        if filename.lower().endswith('.pdf'):
            filepath = os.path.join(input_folder, filename)
            convertPDF(filepath, output_folder)

def clean_images(input="NotProcessed", output="Processed"):

    input_images = os.listdir(input)

    with ThreadPoolExecutor(max_workers=1) as executor:
        futures = [executor.submit(process_single_image, os.path.join(input, img), os.path.join(output, f"{os.path.splitext(img)[0]}.png")) for img in input_images]
        for future in futures:
            future.result()