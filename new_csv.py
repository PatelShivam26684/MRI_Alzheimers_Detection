import os
import pandas as pd
import numpy as np
import glob

df = pd.read_excel('/Users/shivampatel/Research/MRI/Oasis/Data/oasis_2_data.xlsx')

print(df['CDR'].value_counts())


no_duplicate_df = df.loc[df.groupby('Subject ID')['CDR'].idxmax()]
print('noduplicates: ', no_duplicate_df['CDR'].value_counts())

# Filter patients with CDR of 2 and 1
patients_with_cdr_2 = no_duplicate_df[no_duplicate_df['CDR'] == 2]['MRI ID'].tolist()
patients_with_cdr_1 = no_duplicate_df[no_duplicate_df['CDR'] == 1]['MRI ID'].tolist()

# Prioritize CDR = 2 and add CDR = 1 to make up 50 patients
selected_patients = patients_with_cdr_2 + patients_with_cdr_1
selected_patients = selected_patients[:20]  # Ensure no more than 50 patients

# Define the source and destination directories
source_dir = '/Users/shivampatel/Research/MRI/Oasis/Data/oasis_2'
dest_dir = '/Users/shivampatel/Research/MRI/Oasis/Data/AD'

# Ensure the destination directory exists
os.makedirs(dest_dir, exist_ok=True)

# Iterate over selected patients
for patient_id in selected_patients:
    # Use glob to find the T88_111 directory for the patient
    patient_dirs = glob.glob(f"{source_dir}/OAS2_RAW_PART*/{patient_id}/PROCESSED/MPRAGE/T88_111")

    if patient_dirs:
        # Use the first match (assuming there's only one relevant directory)
        patient_path = patient_dirs[0]

        # Check for HDR and GIF files
        hdr_file = None
        gif_file = None
        for file in os.listdir(patient_path):
            if file.endswith('_masked_gfc.hdr'):
                hdr_file = file
            if file.endswith('_masked_gfc_tra_90.gif'):
                gif_file = file

        # Only proceed if both files are found
        if hdr_file and gif_file:
            # Create a subdirectory for the patient in the destination directory
            dest_patient_dir = os.path.join(dest_dir, patient_id)
            os.makedirs(dest_patient_dir, exist_ok=True)

            # Move the HDR file
            shutil.move(
                os.path.join(patient_path, hdr_file),
                os.path.join(dest_patient_dir, hdr_file)
            )

            # Move the GIF file
            shutil.move(
                os.path.join(patient_path, gif_file),
                os.path.join(dest_patient_dir, gif_file)
            )

            print(f"Moved files for patient {patient_id} to {dest_patient_dir}")
    else:
        print(f"No directory found for patient {patient_id} in T88_111")

print(f"Files moved successfully for {len(selected_patients)} patients.")


#df.to_csv('/Users/shivampatel/Research/MRI/Oasis/Data/oasis_1/oasis_1_edited.csv',index=False)



#df = df[~df['MRI ID'].isin(folders)]

#df.to_csv('/Users/shivampatel/Research/MRI/Oasis/Data/data.csv', index=False)
