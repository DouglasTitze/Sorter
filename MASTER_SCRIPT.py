from Load_modules import *

def MASTER_FUNCTION():

    # Create necessary folders
    create_folders()

    # lowerCL, upperCL = get_confidence_levels()
    lowerCL, upperCL = .45, .57
    folderPath = 'Documents'
        
    try:
        process_pdfs(input_folder = folderPath, output_folder='NotProcessed')

        # Any image file type that can be processed by tesseract w/o conversion go to 'NotProcessed'
        allowed_extensions = [".png", ".jpeg", ".jpg", ".tif", ".tiff", ".bmp", ".pnm", ".webp", ".gif"]
        for file_name in os.listdir('Documents'):
            file_extension = os.path.splitext(file_name)[1].lower()
            if any(file_extension == ext for ext in allowed_extensions):
                src = os.path.join('Documents', file_name)
                dest = os.path.join('NotProcessed', file_name)
                shutil.copy(src, dest)

        # Deal with scanner artifacts
        clean_images()

        # transcribe the images
        transcribe_documents()

        # Convert text files to npz format
        compress_text_files()

        # Run the model on the dataset for sorting
        run_model(lowerConfidenceLevel = lowerCL, upperConfidenceLevel = upperCL)

        # Use model output to sort files
        sort_files()

        print("".center(100,"~"))
        input("\n\nYour files have been sucessfully sorted!\nPlease press any button to exit the program.")
        
    except KeyboardInterrupt:
        print("Keyboard interrupt detected")

        # Delete leftovers
        clean_up()

    except Exception as e:
        print(str(e))

        # Delete leftovers
        clean_up()

    # Delete leftovers
    clean_up()

if __name__ == "__main__":
    try: 
        MASTER_FUNCTION()
    except KeyboardInterrupt:
        print("Keyboard interrupt detected")

        # Delete leftovers
        clean_up()
    except Exception as e:
        print(str(e))

        # Delete leftovers
        clean_up()