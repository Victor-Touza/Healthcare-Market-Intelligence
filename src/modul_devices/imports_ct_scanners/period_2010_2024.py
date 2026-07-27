#============================================================================================
# IV. IMPORT OF CT-SCANNERS.
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


def load_ct_scanners():

# -------------------------------------------------------------------
# 1. Creation of a single dataset containing all available datasets
# -------------------------------------------------------------------

    file_path = "./data/raw"
    files = [f for f in os.listdir(file_path) if f.startswith("902212_ct_scanners_") and f.endswith(".xlsx")] 


# Load and merge all files

    list_df = []

    for file in files:
    # extract the year from the filename; for example, "902212_ct_scanners_2010.xlsx" becomes "2010"
            year = file.split("_")[-1].split(".")[0]
        
        # Read the Excel file
            df = pd.read_excel(os.path.join(file_path, file))

        # Add a column with the year
            df["Year"] = int(year)
        
        # Add the DataFrame to the list
            list_df.append(df)


# Combine all DataFrames into a single DataFrame

    df_ct_scanners = pd.concat(list_df, ignore_index=True)

    #print(df_ct_scanners.head(5))


# ------------------------------------------------------------
# 2. Initial dataset cleaning
# ------------------------------------------------------------

# Remove columns that are completely empty (containing only NaN)
    df_ct_scanners = df_ct_scanners.dropna(axis=1, how='all')


# Remove unnecessary columns
    columns_to_remove = [
    "Trade Flow", "Partner", "2nd Partner", "Customs Desc","Transport Mode", 
    "Net Weight (kg)", "Gross Weight", "Qty","Qty Unit","Alternate Quantity", "Alt Qty Unit"
    ]

    df_ct_scanners = df_ct_scanners.drop(columns=columns_to_remove, errors="ignore")


# Rename useful columns  
    df_ct_scanners = df_ct_scanners.rename(columns={
    "Reporter": "Country",
    "Commodity Code": "Product_Code",
    "Trade Value (US$)": "Trade Value 1000USD"
    })
    


# Rename the product description
    df_ct_scanners["Product_Name"] = "CT Scanners"

# Format the "Trade Value 1000USD" column

    df_ct_scanners["Trade Value 1000USD"] = (
    df_ct_scanners["Trade Value 1000USD"]
    .str.replace("$", "", regex=False)
    .str.replace(",", "", regex=False)
    .astype(float) / 1000
    )


# ------------------------------------------------------------
# 3. Data transformation
# ------------------------------------------------------------

# Remove rows with missing values in the "Trade Value 1000USD" column
    df_ct_scanners = df_ct_scanners.dropna(subset=["Trade Value 1000USD"])

# Function to retrieve the ISO Alpha-3 country code
    def get_country_code(name):
        try:
            country = pycountry.countries.lookup(name)
            return country.alpha_3
        except LookupError:
            return None  # Return None if the country is not found

# Create the "Country_Code" column
    df_ct_scanners["Country_Code"] = df_ct_scanners["Country"].apply(get_country_code)

# Remove rows with missing values in the "Country_Code" column
    df_ct_scanners = df_ct_scanners.dropna(subset=["Country_Code"])

# Add placeholder columns for variables that will be calculated in later modules
    df_ct_scanners["Units_per_Million_Inhabitants"] = np.nan

    final_columns = [
    "Country",
    "Country_Code",
    "Product_Name",
    "Product_Code",
    "Year",
    "Trade Value 1000USD",
    "Units_per_Million_Inhabitants"
    ]

    df_ct_scanners = df_ct_scanners[final_columns]

    #print(df_ct_scanners.head())


# ------------------------------------------------------------
# 4. Return the transformed dataset
# ------------------------------------------------------------

    return df_ct_scanners

