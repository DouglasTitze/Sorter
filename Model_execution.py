import tensorflow as tf
import numpy as np
import os
SEPERATOR_CONFIDENCE = "*SEPERATOR_CONFIDENCE*"


# This function is responsible for executing the model to sort provided documents
def run_model(lowerConfidenceLevel, upperConfidenceLevel):

    # Seperator between file name and confidence value

    # Current directory to load the model
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Load the model and its saved weights and biases for execution
    model = tf.keras.models.load_model(os.path.join(current_dir, 'Model'))
    # Load the documents that need to be sorted (in text format with their file names as labels)
    new_loaded_data = np.load('texts_as.npz')
    
    new_data = new_loaded_data['data'] # new_data elements (text to be classified)
    file_names = new_loaded_data['labels'] # file labels (name of original file)

    predictions = model.predict(new_data).astype("float") # Predictions made on each file
    confidence_levels = tf.nn.sigmoid(predictions) # Set predictions between 0-1 for classification

    # Open a file to writethe model output - used for organizing files in correct folders
    outputFile = open("ML_OUT.txt", "w", encoding="utf-8")

    # Display the predictions (Medical or Non-medical folder with corresponding file name)
    for file_name, prediction in zip(file_names, confidence_levels):
        prediction = prediction[0].numpy()
        if prediction < lowerConfidenceLevel: 
            outputFile.write(f"{file_name}{SEPERATOR_CONFIDENCE}Non-medical (CL:{prediction})\n")
        elif prediction > upperConfidenceLevel:  
            outputFile.write(f"{file_name}{SEPERATOR_CONFIDENCE}Medical (CL:{prediction})\n")
        else: 
            outputFile.write(f"{file_name}{SEPERATOR_CONFIDENCE}Unknown (CL:{prediction})\n")