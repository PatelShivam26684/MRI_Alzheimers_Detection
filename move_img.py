import os
import shutil

def list_patient_dirs(base_dir, folders):
    """
    Get a list of patient directories and associated HDR files in AD and Non_AD directories.
    """
    patient_dirs = {}
    for folder in folders:
        folder_path = os.path.join(base_dir, folder)
        for patient_id in os.listdir(folder_path):
            patient_dir = os.path.join(folder_path, patient_id)
            if os.path.isdir(patient_dir):
                hdr_files = [
                    file for file in os.listdir(patient_dir) if file.endswith('.hdr')
                ]
                patient_dirs[patient_id] = {
                    'directory': patient_dir,
                    'hdr_files': hdr_files,
                }
    return patient_dirs

def find_and_move_img_files(oasis_dir, patient_dirs):
    """
    Search for matching .img files in the oasis_1 structure and move them to the respective patient directories.
    """
    for patient_id, patient_info in patient_dirs.items():
        hdr_files = patient_info['hdr_files']
        dest_dir = patient_info['directory']

        for hdr_file in hdr_files:
            img_file = hdr_file.replace('.hdr', '.img')  # Replace .hdr with .img
            img_found = False

            # Search in oasis_1 structure
            for root, dirs, files in os.walk(oasis_dir):
                if img_file in files:
                    src_img_path = os.path.join(root, img_file)
                    dest_img_path = os.path.join(dest_dir, img_file)

                    # Move the img file
                    shutil.move(src_img_path, dest_img_path)
                    print(f"Moved: {src_img_path} -> {dest_img_path}")
                    img_found = True
                    break

            if not img_found:
                print(f"IMG file not found for: {hdr_file} in patient directory {dest_dir}")

# Define paths
base_dir = "/Users/shivampatel/Research/MRI/Oasis/Data"  # Base directory for AD and Non_AD
folders = ['AD', 'Non_AD']  # Folders to process
oasis_dir = "/Users/shivampatel/Research/MRI/Oasis/Data/oasis_1"  # Directory containing source IMG files

# List patient directories and HDR files in AD and Non_AD
patient_dirs = list_patient_dirs(base_dir, folders)

# Move the IMG files to respective patient directories
find_and_move_img_files(oasis_dir, patient_dirs)