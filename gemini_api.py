import os
import pandas as pd
import time
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_random_exponential
from PIL import Image

api_key = "api_key"
genai.configure(api_key=api_key)

# Initialize the Gemini model
model = genai.GenerativeModel("gemini-2.0-flash-exp")

# Define the output CSV file path
output_csv = "/Users/shivampatel/Research/MRI/Oasis/gemini_official_response.csv"

# Ensure the output CSV exists and has the appropriate columns
if not os.path.exists(output_csv):
    with open(output_csv, 'w', encoding='utf-8') as csvfile:
        csvfile.write("Patient ID,Category,Result\n")

# Load already processed studies
if os.path.getsize(output_csv) > 0:
    processed_studies = pd.read_csv(output_csv)['Patient ID'].tolist()
else:
    processed_studies = []

# Function to check folder size
def get_folder_size(folder_path):
    print(folder_path)
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

# Function to upload files to Gemini API
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def upload_files(file_paths):
    uploaded_files = []
    picture_number = 0
    for file_path in file_paths:
        try:
            print(f"Uploading file: {file_path}")
            uploaded_file = genai.upload_file(file_path, mime_type='image/png')  # Pass the file path directly
            uploaded_files.append(uploaded_file)
            picture_number += 1
            print(f"Successfully uploaded: {file_path}",'picture number: ',picture_number)
        except Exception as e:
            print(f"Error uploading file {file_path}: {e}")
            raise  # Re-raise the exception to trigger retry
    return uploaded_files

# Function to send prompt with locally loaded images
def send_prompt_with_local_images(image_paths, prompt):
    images = [Image.open(img_path) for img_path in image_paths]
    result = model.generate_content([prompt] + images)
    return result.text

# Function to send prompt and images to Gemini API
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def send_prompt_with_uploaded_images(uploaded_files, prompt):
    result = model.generate_content(uploaded_files + ["\n\n", prompt])
    return result.text

# Function to process a study
def process_patient(patient_path):
    # Collect all images recursively in the study directory
    images = []
    for root, _, files in os.walk(patient_path):
        images.extend([os.path.join(root, f) for f in files if f.endswith(('.png', '.jpg', '.jpeg'))])
        #print(images)

    # Check folder size
    folder_size = get_folder_size(patient_path+'/hdr_png_images')
    print(f"Folder size: {folder_size / (1024 * 1024):.2f} MB")

    # Define the prompt
    prompt = (
        "This is a series of MRI images from a patient."
        "Based on the images does the patient have Probable Alzheimer's disease or not?"
        "A) Probable Alzheimer's disease is present\nB) Probable Alzheimer's disease is not present"
        "Answer this question with a single letter ONLY. "
        "For example, if you believe there is evidence of Probable Alzheimer's disease, answer 'A' and NOTHING ELSE. \n"

    )

    # Process based on folder size
    try:
        if folder_size > 19 * 1024 * 1024:  # Greater than 15 MB
            print("Using upload method for large folder size.")
            uploaded_files = upload_files(images)
            response = send_prompt_with_uploaded_images(uploaded_files, prompt)
        else:
            print("Using local file method for small folder size.")
            response = send_prompt_with_local_images(images, prompt)
        return response
    except Exception as e:
        print(f"Error during processing: {e}")
        return "Error"

# Process all studies and collect responses
main_dir = '/Users/shivampatel/Research/MRI/Oasis/Data'
for category in ['AD', 'Non_AD']:
    category_dir = os.path.join(main_dir, category)
    patient_number = 0
    for patient in os.listdir(category_dir):
        if patient in processed_studies:
            print(f"Skipping already processed patient: {patient}")
            patient_number += 1
            continue

        patient_path = os.path.join(category_dir, patient)
        if os.path.isdir(patient_path):
            print(f"Processing patient: {patient} in category {category}")
            result = process_patient(patient_path)
            patient_number += 1
            print(f"Result for patient {patient}: {result}", 'patient number: ',patient_number)

            # Write result to CSV immediately
            with open(output_csv, 'a', newline='', encoding='utf-8') as csvfile:
                csvfile.write(f"{patient},{category},{result}\n")
            #time.sleep(20)

print("All studies processed")