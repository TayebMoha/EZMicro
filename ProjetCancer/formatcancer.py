import pandas as pd

# Load the CSV file
file_path = 'cancerSEER.csv'
seer_data = pd.read_csv(file_path)

# Define the list of attributes to rename
colorectal_sites = [
    'Cecum',
    'Appendix',
    'Ascending Colon',
    'Hepatic Flexure',
    'Transverse Colon',
    'Splenic Flexure',
    'Descending Colon',
    'Sigmoid Colon',
    'Large Intestine, NOS',
    'Rectosigmoid Junction',
    'Rectum',
]

# Strip any leading/trailing whitespace and replace with "Colorectal"
seer_data['Site recode ICD-O-3/WHO 2008'] = seer_data['Site recode ICD-O-3/WHO 2008'].str.strip()
seer_data['Site recode ICD-O-3/WHO 2008'] = seer_data['Site recode ICD-O-3/WHO 2008'].replace(colorectal_sites, 'Colorectal')

# Rename "Breast" to "Sein", "Melanoma of the Skin" to "Melanome", and "Lung and Bronchus" to "Poumons"
seer_data['Site recode ICD-O-3/WHO 2008'] = seer_data['Site recode ICD-O-3/WHO 2008'].replace({
    'Breast': 'Sein',
    'Melanoma of the Skin': 'Melanome',
    'Lung and Bronchus': 'Poumons'
})

# Define mappings for "Cause of Death" to categorized groups
cause_of_death_mapping = {
    # ORL group
    'Oral Cavity and Pharynx': 'ORL',
    'Lip': 'ORL',
    'Tongue': 'ORL',
    'Salivary Gland': 'ORL',
    'Floor of Mouth': 'ORL',
    'Gum and Other Mouth': 'ORL',
    'Nasopharynx': 'ORL',
    'Tonsil': 'ORL',
    'Oropharynx': 'ORL',
    'Hypopharynx': 'ORL',
    'Other Oral Cavity and Pharynx': 'ORL',
    # Digestive system categories
    'Digestive System': 'Autre Digestif',
    'Esophagus': 'Autre Digestif',
    'Stomach': 'Autre Digestif',
    'Small Intestine': 'Autre Digestif',
    'Colon and Rectum': 'Colorectal',
    'Colon excluding Rectum': 'Colorectal',
    'Rectum and Rectosigmoid Junction': 'Colorectal',
    'Anus, Anal Canal and Anorectum': 'Autre Digestif',
    'Liver and Intrahepatic Bile Duct': 'Autre Digestif',
    'Liver': 'Autre Digestif',
    'Intrahepatic Bile Duct': 'Autre Digestif',
    'Gallbladder': 'Autre Digestif',
    'Other Biliary': 'Autre Digestif',
    'Pancreas': 'Pancreas',
    'Retroperitoneum': 'Autre Digestif',
    'Peritoneum, Omentum and Mesentery': 'Autre Digestif',
    'Other Digestive Organs': 'Autre Digestif',
    # Respiratory system
    'Respiratory System': 'Autre Respiratoir',
    'Nose, Nasal Cavity and Middle Ear': 'Autre Respiratoir',
    'Larynx': 'Autre Respiratoir',
    'Lung and Bronchus': 'Poumons',
    'Pleura': 'Autre Respiratoir',
    'Trachea, Mediastinum and Other Respiratory Organs': 'Autre Respiratoir',
    # Skin categories
    'Skin': 'Autre Peau',
    'Melanoma of the Skin': 'Melanome',
    'Non-Melanoma Skin': 'Autre Peau',
    # Breast
    'Breast': 'Sein',
    # Genital system
    'Female Genital System': 'Gynecologique',
    'Cervix Uteri': 'Gynecologique',
    'Corpus and Uterus, NOS': 'Gynecologique',
    'Corpus Uteri': 'Gynecologique',
    'Uterus, NOS': 'Gynecologique',
    'Ovary': 'Gynecologique',
    'Vagina': 'Gynecologique',
    'Vulva': 'Gynecologique',
    'Other Female Genital Organs': 'Gynecologique',
    'Male Genital System': 'Autre Reproductifs',
    'Prostate': 'Prostate',
    'Testis': 'Autre Reproductifs',
    'Penis': 'Autre Reproductifs',
    'Other Male Genital Organs': 'Autre Reproductifs',
    # Urinary system
    'Urinary System': 'Urologique',
    'Urinary Bladder': 'Urologique',
    'Kidney and Renal Pelvis': 'Urologique',
    'Ureter': 'Urologique',
    'Other Urinary Organs': 'Urologique',
    # Leukemia
    'Leukemia': 'Leucemie',
    'Lymphocytic Leukemia': 'Leucemie',
    'Acute Lymphocytic Leukemia': 'Leucemie',
    'Chronic Lymphocytic Leukemia': 'Leucemie',
    'Other Lymphocytic Leukemia': 'Leucemie',
    'Myeloid and Monocytic Leukemia': 'Leucemie',
    'Acute Myeloid Leukemia': 'Leucemie',
    'Acute Monocytic Leukemia': 'Leucemie',
    'Chronic Myeloid Leukemia': 'Leucemie',
    'Other Myeloid/Monocytic Leukemia': 'Leucemie',
    'Other Leukemia': 'Leucemie',
    'Other Acute Leukemia': 'Leucemie',
    'Aleukemic, Subleukemic and NOS': 'Leucemie',
    # Other cancers
    'Bones and Joints': 'Autres Cancers',
    'Soft Tissue including Heart': 'Autres Cancers',
    'Eye and Orbit': 'Autres Cancers',
    'Brain and Other Nervous System': 'Autres Cancers',
    'Endocrine System': 'Autres Cancers',
    'Thyroid': 'Autres Cancers',
    'Other Endocrine including Thymus': 'Autres Cancers',
    'Lymphoma': 'Autres Cancers',
    'Hodgkin Lymphoma': 'Autres Cancers',
    'Non-Hodgkin Lymphoma': 'Autres Cancers',
    'Myeloma': 'Autres Cancers',
    'Miscellaneous Malignant Cancer': 'Autres Cancers',
    # Miscellaneous
    'Other Cause of Death': 'Non-Cancer',
    'In situ, benign or unknown behavior neoplasm': 'Non-Cancer',
    'Tuberculosis': 'Non-Cancer',
    'Syphilis': 'Non-Cancer',
    'Septicemia': 'Non-Cancer',
    'Other Infectious and Parasitic Diseases including HIV': 'Non-Cancer',
    'Diabetes Mellitus': 'Non-Cancer',
    'Alzheimers (ICD-9 and 10 only)': 'Non-Cancer',
    'Diseases of Heart': 'Non-Cancer',
    'Hypertension without Heart Disease': 'Non-Cancer',
    'Cerebrovascular Diseases': 'Non-Cancer',
    'Atherosclerosis': 'Non-Cancer',
    'Aortic Aneurysm and Dissection': 'Non-Cancer',
    'Other Diseases of Arteries, Arterioles, Capillaries': 'Non-Cancer',
    'Pneumonia and Influenza': 'Non-Cancer',
    'Chronic Obstructive Pulmonary Disease and Allied Cond': 'Non-Cancer',
    'Stomach and Duodenal Ulcers': 'Non-Cancer',
    'Chronic Liver Disease and Cirrhosis': 'Non-Cancer',
    'Nephritis, Nephrotic Syndrome and Nephrosis': 'Non-Cancer',
    'Complications of Pregnancy, Childbirth, Puerperium': 'Non-Cancer',
    'Congenital Anomalies': 'Non-Cancer',
    'Certain Conditions Originating in Perinatal Period': 'Non-Cancer',
    'Symptoms, Signs and Ill-Defined Conditions': 'Non-Cancer',
    'Accidents and Adverse Effects': 'Non-Cancer',
    'Suicide and Self-Inflicted Injury': 'Non-Cancer',
    'Homicide and Legal Intervention': 'Non-Cancer',
    'State DC not available or state DC available but no COD': 'Non-Cancer'
}

# Apply the mapping to the "Cause of Death" column
seer_data['COD to site recode'] = seer_data['COD to site recode'].replace(cause_of_death_mapping)

# Clean and map race categories
race_mapping = {
    'Non-Hispanic White': 'White',
    'Non-Hispanic Black': 'Black',
    'Hispanic (All Races)': 'Hispanic',
    'Non-Hispanic Asian or Pacific Islander': 'Asian/Pacific Islander',
    'Non-Hispanic American Indian/Alaska Native': 'Native American',
    'Non-Hispanic Unknown Race': None
}
seer_data['Race'] = (
    seer_data['Race']
    .replace(race_mapping)
)

# Remove rows with unknown race
seer_data = seer_data.dropna(subset=['Race'])

# Save the updated dataset (optional, specify your desired path)
seer_data.to_csv('updated_cancerSEER.csv', index=False)
