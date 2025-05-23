from fastapi.responses import HTMLResponse
import random
import joblib
import pandas as pd
from catboost import CatBoostClassifier
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

# Charger le dataset


# Préparer la colonne "Age" : Nettoyage et regroupement
def process_age_column():
    df = pd.read_csv("updated_cancerSEER.csv")
    # Convertir "Age" en numérique, en remplaçant "90+ years" par 90
    df['Age'] = df['Age'].str.replace(" years", "").replace("90+", "90").astype(int)
    # Ajouter une colonne "Age Group"
    bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    labels = ["0–10", "11–20", "21–30", "31–40", "41–50", "51–60", "61–70", "71–80", "81–90", "90+"]
    df['Age Group'] = pd.cut(df['Age'], bins=bins, labels=labels, right=False)
    return df

df = process_age_column()

# Configuration des templates
templates = Jinja2Templates(directory="templates")

@app.get("/dashboard", response_class=HTMLResponse)
def home(request: Request):
    # Données pour le graphique de répartition par groupe d'âge
    age_group_data = df.groupby(["Age Group", "Sex"]).size().reset_index(name="Count")

    # Données pour le graphique bar chart (répartition par sexe et année)
    bar_data = df.groupby(["Yeardiag", "Type", "Sex"]).size().reset_index(name="Count")


    # Données pour le line chart (évolution des cas par cancer avec split homme/femme)
    line_chart_data = df.groupby(["Yeardiag", "Type", "Sex"]).size().reset_index(name="Count")

    # Données pour le graphique par type de cancer et âge
    cancer_age_data = df.groupby(["Type", "Age Group"]).size().reset_index(name="Count")

    ethnicity_totals = df.groupby("Race")["Type"].count()

    # Calculate percentage for each combination of Race and Type
    ethnicity_cancer_data = (
        df.groupby(["Race", "Type"])
        .size()
        .reset_index(name="Count")
    )

    # Normalize by total cases per ethnicity
    ethnicity_cancer_data["Percentage"] = (ethnicity_cancer_data["Count"] / ethnicity_cancer_data["Race"].map(ethnicity_totals)) * 100

    # Ensure Age is a string before applying .str operations
    df["Age"] = df["Age"].astype(str)

    # Replace " years" and handle "90+" appropriately, then convert to numeric
    df["Age"] = df["Age"].str.replace(" years", "", regex=False).replace("90+", "90")
    df["Age"] = pd.to_numeric(df["Age"], errors="coerce")  # Convert to numeric and handle invalid values
    # Filter out rows where the cause of death is "Alive"
    box_plot_data = df[df["COD"] != "Alive"][["Age", "COD"]]
    # Group by Type and COD to calculate counts
    vital_status_data = df.groupby(["Type", "COD"]).size().reset_index(name="Count")

    # Optionally, calculate percentages for visualization (if needed)
    type_totals = vital_status_data.groupby("Type")["Count"].sum()
    vital_status_data["Percentage"] = (vital_status_data["Count"] / vital_status_data["Type"].map(type_totals)) * 100

    # Group by Race and COD (vital status) to calculate counts
    vital_status_ethnicity_data = df.groupby(["Race", "COD"]).size().reset_index(name="Count")

    # Optionally, calculate percentages for each ethnicity
    ethnicity_totals = vital_status_ethnicity_data.groupby("Race")["Count"].sum()
    vital_status_ethnicity_data["Percentage"] = (vital_status_ethnicity_data["Count"] /vital_status_ethnicity_data["Race"].map(ethnicity_totals)) * 100

    # Group by year of diagnosis and cancer type, then calculate average age
    line_graph_data = df.groupby(["Yeardiag", "Type"])["Age"].mean().reset_index()

    # Rename columns for clarity (optional)
    line_graph_data.columns = ["Year", "CancerType", "AverageAge"]

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "age_group_data": age_group_data.to_dict(orient="records"),
            "line_chart_data": line_chart_data.to_dict(orient="records"),
            "cancer_age_data": cancer_age_data.to_dict(orient="records"),
            "ethnicity_cancer_data": ethnicity_cancer_data.to_dict(orient="records"),
            "box_plot_data": box_plot_data.to_dict(orient="records"),
            "vital_status_data": vital_status_data.to_dict(orient="records"),
            "vital_status_ethnicity_data": vital_status_ethnicity_data.to_dict(orient="records"),
            "line_graph_data": line_graph_data.to_dict(orient="records"),
        },
    )

@app.get("/", response_class=HTMLResponse)
def context(request: Request):
    return templates.TemplateResponse("context.html", {"request": request})


# Load the trained CatBoost model (Using joblib)
model = joblib.load("best_model.pkl")

# List of expected columns (Ensures correct feature alignment)
expected_features = [
    'Age', 'Sex', 'Type_Colorectal', 'Type_Melanome', 'Type_Pancreas', 'Type_Poumons', 'Type_Prostate', 'Type_Sein', 'Race_Asian/Pacific Islander', 'Race_Black', 'Race_Hispanic', 'Race_Native American', 'Race_White'
]


# Define the expected input format
class PatientData(BaseModel):
    Age: int
    Sex: str  # "Male" or "Female"
    CancerType: str  # e.g., "Sein" (Breast Cancer)
    Race: str  # e.g., "White"


# Mapping for categorical encoding
sex_mapping = {"Male": 1, "Female": 0}
cancer_mapping = {
    "Melanome": "Type_Melanome",
    "Pancreas": "Type_Pancreas",
    "Poumons": "Type_Poumons",
    "Prostate": "Type_Prostate",
    "Sein": "Type_Sein",
    "Colorectal": "Type_Colorectal"
}
race_mapping = {
    "Black": "Race_Black",
    "Hispanic": "Race_Hispanic",
    "Native American": "Race_Native American",
    "White": "Race_White",
    "Asian/Pacific Islander": "Race_Asian/Pacific Islander"
}


# Preprocess input data function
def preprocess_input(data: PatientData):
    # Initialize an empty row with default values
    input_data = {col: False for col in expected_features}

    # Assign values based on user input
    input_data["Age"] = data.Age
    input_data["Sex"] = sex_mapping.get(data.Sex, 0)  # Default to Female if unknown

    # Activate the corresponding cancer type
    if data.CancerType in cancer_mapping:
        input_data[cancer_mapping[data.CancerType]] = True

    # Activate the corresponding race
    if data.Race in race_mapping:
        input_data[race_mapping[data.Race]] = True

    # Convert to a DataFrame
    input_df = pd.DataFrame([input_data])

    return input_df


@app.post("/predict/")
def predict_lifestatus(patient: PatientData):
    # Preprocess the input
    input_df = preprocess_input(patient)

    # Get model's expected feature names
    model_features = model._feature_names  # ✅ Extract feature names from saved model

    # Ensure input features match the expected order
    missing_features = set(model_features) - set(input_df.columns)
    if missing_features:
        print("Model features:", model._feature_names)  # Print all expected features
        print("Input Data Columns:", input_df.columns.tolist())  # Print input columns
        raise ValueError(f"Missing features in input data: {missing_features}")

    # Reorder DataFrame correctly
    input_df = input_df[model_features]

    # Get probability predictions using CatBoost
    proba = model.predict_proba(input_df)[0]  # Returns [prob_alive, prob_dead]

    return {
        "Probability_Alive": round(proba[0] * 100, 2),  # Convert to percentage
        "Probability_Dead": round(proba[1] * 100, 2)
    }


# Route for ML page
@app.get("/ml-model")
def ml_page(request: Request):
    cancer_types = ["Melanome", "Pancreas", "Poumons", "Prostate", "Sein", "Colorectal"]
    races = ["Black", "Hispanic", "Native American", "White", "Asian/Pacific Islander"]

    return templates.TemplateResponse("ml_model.html", {
        "request": request,
        "cancer_types": cancer_types,
        "races": races
    })