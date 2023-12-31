# Use the Ubuntu 22.04 as the base image
FROM ubuntu:22.04
 
# Set python environment variable
ENV PYTHON_VERSION=3.10

# Maintainer
LABEL maintainer="Douglas Titze <DouglasTitze@gmail.com>"

# Install python + dependencies
RUN apt-get update && apt-get install -y python3.10 
RUN apt-get update && apt-get install -y python3-pip
COPY requirements.txt .
RUN pip install --requirement requirements.txt
RUN rm requirements.txt

# Update + install required packages
RUN apt-get update && apt-get install -y tesseract-ocr
RUN apt-get update && apt-get install -y imagemagick 
RUN apt-get update && apt-get install -y libgl1-mesa-glx 

# Create + move to working directory
RUN mkdir Sorter
WORKDIR /Sorter

# Copy the ML Model into the container
RUN mkdir Model
COPY Model Model

# Copy your Documents into the container
RUN mkdir Documents
COPY Documents Documents

# Copy all the Python scripts into the container
COPY *.py .

# Run the script: Use flag -it when building, because user input is required
# docker build -t img .
# docker run -it img
CMD ["python3.10", "MASTER_SCRIPT.py"]
