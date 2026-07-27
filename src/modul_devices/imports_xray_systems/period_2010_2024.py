#============================================================================================
# I. IMPORT OF XRAY SYSTEMS
#============================================================================================


# # Import required libraries
import os
import numpy as np
import pandas as pd
import pycountry


# General pandas configuration for improved data display
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 0)
pd.options.display.float_format = "{:.2f}".format


def load_xray_systems():

# -------------------------------------------------------------------
# 1. Creation of a single dataset containing all available datasets
# -------------------------------------------------------------------

        file_path = "./data/raw"
        files = [f for f in os.listdir(file_path) if f.startswith("WITS-By-HS6Product_") and f.endswith(".xlsx")] 


# Load and merge all files

        list_df = []

        for file in files:
        # extract the year from the filename; for example, "WITS-By-HS6Product_2024.xlsx" becomes "2024"
                year = file.split("_")[-1].split(".")[0]
        
        # read the Excel file
                df = pd.read_excel(os.path.join(file_path, file))
        
        # add a column with the year
                df["Year"] = int(year)
        
        # add the DataFrame to the list
                list_df.append(df)


# Combine all DataFrames into a single one

        df_xray_systems = pd.concat(list_df, ignore_index=True)

# ------------------------------------------------------------
# 2. Initial dataset cleaning
# ------------------------------------------------------------

# Remove columns that are completely empty (containing only NaN)
        df_xray_systems = df_xray_systems.dropna(axis=1, how='all')


# Remove unnecessary columns
        columns_to_remove = [
        "TradeFlow", "Partner", "Quantity Unit", "Quantity"
        ]

        df_xray_systems = df_xray_systems.drop(columns=columns_to_remove, errors="ignore")


# ------------------------------------------------------------
# 3. Data transformation
# ------------------------------------------------------------

# Rename useful columns
        df_xray_systems = df_xray_systems.rename(columns={
        "Reporter": "Country",
        "Product Description": "Product_Name",
        "ProductCode": "Product_Code",
        })

        df_xray_systems["Year"] = df_xray_systems["Year"].astype(int)


# Function to retrieve the ISO Alpha-3 country code
        def get_country_code(name):
                try:
                        country = pycountry.countries.lookup(name)
                        return country.alpha_3
                except LookupError:
                        return None  # Return None if the country is not found

# Create the "Country_Code" column
        df_xray_systems["Country_Code"] = df_xray_systems["Country"].apply(get_country_code)
    

# Remove rows with missing values in the "Country_Code" column
        df_xray_systems = df_xray_systems.dropna(subset=["Country_Code"])


# Standardize the product name
        df_xray_systems["Product_Name"] = df_xray_systems["Product_Name"].replace(
            "X-ray tubes", 
            "X-ray systems"
        )


# Add placeholder columns for variables that will be calculated in later modules
        df_xray_systems["Units_per_Million_Inhabitants"] = np.nan

        final_columns = [
        "Country",
        "Country_Code",
        "Product_Name",
        "Product_Code",
        "Year",
        "Trade Value 1000USD",
        "Units_per_Million_Inhabitants"
        ]

        df_xray_systems = df_xray_systems[final_columns]


        print(df_xray_systems.head())


# ------------------------------------------------------------
# 4. Return the transformed dataset
# ------------------------------------------------------------


        return df_xray_systems
