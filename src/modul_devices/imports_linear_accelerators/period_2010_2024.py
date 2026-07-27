#============================================================================================
# VII. IMPORT OF LINEAR ACCELARATORS
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


def load_linear_accelerators():

# -------------------------------------------------------------------
# 1. Creation of a single dataset containing all available datasets
# -------------------------------------------------------------------

    file_path = "./data/raw"
    files = [f for f in os.listdir(file_path) if f.startswith("902290_Linear_Accelerators_") and f.endswith(".xlsx")] 


# Load and merge all files

    list_df = []

    for file in files:
    # extract the year from the filename; for example, "902290_Linear_Accelerators_2024.xlsx" becomes "2024"
            year = file.split("_")[-1].split(".")[0]
        
        # read the Excel file
            df = pd.read_excel(os.path.join(file_path, file))
        
        # add a column with the year
            df["Year"] = int(year)
        
        # add the DataFrame to the list
            list_df.append(df)


# Combine all DataFrames into a single one
    df_accelerators = pd.concat(list_df, ignore_index=True)


# ------------------------------------------------------------
# 2. Initial dataset cleaning
# ------------------------------------------------------------

# Remove columns that are completely empty (containing only NaN)
    df_accelerators = df_accelerators.dropna(axis=1, how='all')


# Remove unnecessary columns
    columns_to_remove = [
    "Trade Flow", "Partner", "2nd Partner", "Customs Desc","Transport Mode", 
    "Net Weight (kg)", "Gross Weight", "Qty","Qty Unit","Alternate Quantity", "Alt Qty Unit"
    ]

    df_accelerators = df_accelerators.drop(columns=columns_to_remove, errors="ignore")


# Rename useful columns     
    df_accelerators = df_accelerators.rename(columns={
    "Reporter": "Country",
    "Commodity Code":"Product_Code",
    "Trade Value (US$)": "Trade Value 1000USD"
    })
    

# Add a standardized product name
    df_accelerators["Product_Name"] = "Linear Accelerators"

# Format the "Trade Value 1000USD" column
    df_accelerators["Trade Value 1000USD"] = (
    df_accelerators["Trade Value 1000USD"]
    .str.replace("$", "", regex=False)
    .str.replace(",", "", regex=False)
    .astype(float) / 1000
    )


# ------------------------------------------------------------
# 3. Data transformation
# ------------------------------------------------------------

# Remove rows with missing values in the "Trade Value 1000USD" column
    df_accelerators = df_accelerators.dropna(subset=["Trade Value 1000USD"])

# Function to retrieve the ISO Alpha-3 country code
    def get_country_code(name):
        try:
            country = pycountry.countries.lookup(name)
            return country.alpha_3
        except LookupError:
            return None  # Return None if the country is not found

# Create the "Country_Code" column
    df_accelerators["Country_Code"] = df_accelerators["Country"].apply(get_country_code)


# Remove rows with missing values in the "Country_Code" column
    df_accelerators = df_accelerators.dropna(subset=["Country_Code"])


# Add placeholder columns for variables that will be calculated in later modules.
    df_accelerators["Units_per_Million_Inhabitants"] = np.nan

    final_columns = [
    "Country",
    "Country_Code",
    "Product_Name",
    "Product_Code",
    "Year",
    "Trade Value 1000USD",
    "Units_per_Million_Inhabitants"
    ]

    df_accelerators = df_accelerators[final_columns]

    #print(df_accelerators.head())


# ------------------------------------------------------------
# 4. Return the transformed dataset
# ------------------------------------------------------------

    return df_accelerators
