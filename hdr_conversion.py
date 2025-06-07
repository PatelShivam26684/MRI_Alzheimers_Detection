import nibabel as nib
import numpy as np
import imageio
import os
import shutil
from PIL import Image, ImageSequence


def hdr_to_png(hdr_file, output_dir):
    """
    Convert an HDR file into a series of PNG slices and save them in the output directory.
    """
    # Remove existing output directory if it exists
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    img = nib.load(hdr_file)
    data = img.get_fdata()

    # Normalize the data for 8-bit representation
    data_normalized = (data / np.max(data) * 255).astype(np.uint8)

    os.makedirs(output_dir, exist_ok=True)  # Ensure the output directory exists

    # Save each slice as a separate PNG
    for i in range(data_normalized.shape[2]):  # Loop through the third axis (slices)
        slice_path = os.path.join(output_dir, f"slice_{i:03d}.png")  # Format file name with zero padding
        slice_rgb = np.stack([data_normalized[:, :, i]] * 3, axis=-1)  # Convert to RGB
        slice_rgb = np.squeeze(slice_rgb)  # Remove redundant dimensions

        # Skip all-black images
        if np.max(slice_rgb) == 0:  # All-black image has max pixel value of 0
            print(f"Skipping black image: {slice_path}")
            continue

        imageio.imwrite(slice_path, slice_rgb)  # Save the slice
    print(f"HDR converted and saved to {output_dir}")

def gif_to_png(gif_file, output_dir):
    """
    Convert a GIF file into a series of PNG frames and save them in the output directory.
    """
    # Remove existing output directory if it exists
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    os.makedirs(output_dir, exist_ok=True)  # Ensure the output directory exists
    with Image.open(gif_file) as img:
        for i, frame in enumerate(ImageSequence.Iterator(img)):
            frame_path = os.path.join(output_dir, f"frame_{i:03d}.png")  # Format file name with zero padding
            frame.save(frame_path)  # Save each frame
    print(f"GIF frames converted and saved to {output_dir}")

def process_directories(base_dir, folders):
    """
    Process the AD and Non_AD directories, converting HDR and GIF files to PNGs.
    """
    for folder in folders:
        folder_path = os.path.join(base_dir, folder)
        for patient_id in os.listdir(folder_path):
            patient_dir = os.path.join(folder_path, patient_id)
            if not os.path.isdir(patient_dir):
                continue  # Skip if not a directory

            # Define paths for HDR and GIF files
            hdr_file = None
            gif_file = None
            for file in os.listdir(patient_dir):
                if file.endswith('.hdr'):
                    hdr_file = os.path.join(patient_dir, file)
                elif file.endswith('.gif'):
                    gif_file = os.path.join(patient_dir, file)

            # Create output directories for PNGs
            if hdr_file:
                hdr_output_dir = os.path.join(patient_dir, "hdr_png_images")
                hdr_to_png(hdr_file, hdr_output_dir)

            if gif_file:
                gif_output_dir = os.path.join(patient_dir, "gif_png_images")
                gif_to_png(gif_file, gif_output_dir)

# Define source path and folders
source_path = "/Users/shivampatel/Research/MRI/Oasis/Data"
folders = ['AD', 'Non_AD']

# Process the directories
process_directories(source_path, folders)






