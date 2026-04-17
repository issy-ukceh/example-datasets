# Sample dataset fromt the lepmon project

<img src="media/Lepmon#SN010030_TH_J_2025-07-02_T_2330.jpg" alt="RangeX example image" width="300"/>

## Media folder contents
The folder `media` contains the raw data as they are uploaded from the camera: one run from one nights moth observation. Here: Juky 2nd 2025 between 9:04 pm till 5:34 am next day.

### Files:
 - *.jpg: raw images from the camera device
 - Lepmon#SN010030_TH_J_2025-07-02_T_2102.csv: metadata about each image, including abiotic sensoric and trechnical measurements
 - Lepmon#SN010030_TH_J_2025-07-02_T_2102.log: lofgile of the run
 - Lepmon#SN010030_TH_J_2025-07-02_T_2102_Kameraeinstellungen: Camera settings


## Raw labels folder contents

**Work in Progress**

The processed files (`raw_labels`) is a csv file in the following structure:
- Links to cropped image in iiif-format. 
- AI prediction with GBIF-ID
- AI localisation flag moth/non moth
- Track number and the amount of cropped images coantining the same organism
- Human generated taxonomic assignment
- Flag by an expert confirming the identification
- Timestamp of identification
- Name and version of the AI model used for prediction