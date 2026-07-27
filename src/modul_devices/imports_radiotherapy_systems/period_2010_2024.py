#============================================================================================
# VI. IMPORT OF RADIOTHERAPY SYSTEMS
#============================================================================================

# Import required libraries
import os
import numpy as np
import pandas as pd
import pycountry


# General pandas configuration for improved data display
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 0)
pd.options.display.float_format = "{:.2f}".format


def load_radiotherapy_systems():

# -------------------------------------------------------------------
# 1. Creation of a single dataset containing all available datasets
# -------------------------------------------------------------------

    file_path = "./data/raw"
    files = [f for f in os.listdir(file_path) if f.startswith("902214_Radiotherapy_Systems_") and f.endswith(".xlsx")] 


# Load and merge all files

    list_df = []

    for file in files:
    # extract the year from the filename; for example, "902213_Radiotherapy_Systems_2024.xlsx" becomes "2024"
            year = file.split("_")[-1].split(".")[0]
        
        # read the Excel file
            df = pd.read_excel(os.path.join(file_path, file))
        
        # add a column with the year
            df["Year"] = int(year)   
        
        # add the DataFrame to the list
            list_df.append(df)


# Combine all DataFrames into a single one

    df_radiotherapy_systems = pd.concat(list_df, ignore_index=True)


# ------------------------------------------------------------
# 2. Initial dataset cleaning
# ------------------------------------------------------------

# Remove columns that are completely empty (containing only NaN)
    df_radiotherapy_systems = df_radiotherapy_systems.dropna(axis=1, how='all')


# Remove unnecessary columns
    columns_to_remove = [
    "Trade Flow", "Partner", "2nd Partner", "Customs Desc","Transport Mode", 
    "Net Weight (kg)", "Gross Weight", "Qty","Qty Unit","Alternate Quantity", "Alt Qty Unit"
    ]

    df_radiotherapy_systems = df_radiotherapy_systems.drop(columns=columns_to_remove, errors="ignore")


# Rename useful columns    
    df_radiotherapy_systems = df_radiotherapy_systems.rename(columns={
    "Reporter": "Country",
    "Commodity Code":"Product_Code",
    "Trade Value (US$)": "Trade Value 1000USD"
    })
    

# Add a standardized product name
    df_radiotherapy_systems["Product_Name"] = "Radiotherapy Systems"

# Format "Trade Value 1000USD" appropriately
    df_radiotherapy_systems["Trade Value 1000USD"] = (
    df_radiotherapy_systems["Trade Value 1000USD"]
    .str.replace("$", "", regex=False)
    .str.replace(",", "", regex=False)
    .astype(float) / 1000
    )


# ------------------------------------------------------------
# 3. Data transformation
# ------------------------------------------------------------

# Remove rows with missing values in the "Trade Value 1000USD" column
    df_radiotherapy_systems = df_radiotherapy_systems.dropna(subset=["Trade Value 1000USD"])

# Function to retrieve the ISO Alpha-3 country code
    def get_country_code(name):
        try:
            country = pycountry.countries.lookup(name)
            return country.alpha_3
        except LookupError:
            return None  # Return None if the country is not found

# Create the "Country_Code" column
    df_radiotherapy_systems["Country_Code"] = df_radiotherapy_systems["Country"].apply(get_country_code)

# Remove rows with missing values in the "Country_Code" column
    df_radiotherapy_systems = df_radiotherapy_systems.dropna(subset=["Country_Code"])


# Add placeholder columns for variables that will be calculated in later modules
    df_radiotherapy_systems["Units_per_Million_Inhabitants"] = np.nan

    final_columns = [
    "Country",
    "Country_Code",
    "Product_Name",
    "Product_Code",
    "Year",
    "Trade Value 1000USD",
    "Units_per_Million_Inhabitants"
    ]

    df_radiotherapy_systems = df_radiotherapy_systems[final_columns]

    #print(df_radiotherapy_systems.head())


# ------------------------------------------------------------
# 4. Return the transformed dataset
# ------------------------------------------------------------

    return df_radiotherapy_systems

 