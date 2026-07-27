# ==========================================================================================
# II. ANALYSIS OF COMPLIANCE WITH THE INTERNATIONAL HEALTH REGULATIONS (IHR)
# ==========================================================================================

# Import required libraries
import pandas as pd
import numpy as np
import pycountry

# General pandas configuration for improved data display
pd.options.display.float_format = "{:.2f}".format


def load_health_regulation_compliance():

# ------------------------------------------------------------
# 1. Data loading
# ------------------------------------------------------------
# Load each dataset individually according to its source.
    file_path_2021_2024 = "./data/raw/file.csv"
    health_regulations_2021_2024 = pd.read_csv(file_path_2021_2024)

    file_path_2018_2020 = "./data/raw/file.csv"
    health_regulations_2018_2020 = pd.read_csv(file_path_2018_2020)

    file_path_2010_2017 = "./data/raw/file.csv"
    health_regulations_2010_2017 = pd.read_csv(file_path_2010_2017)


# ------------------------------------------------------------
# 2. Initial dataset cleaning
# ------------------------------------------------------------

# Remove columns that are completely empty
    health_regulations_2021_2024 = health_regulations_2021_2024.dropna(axis=1, how='all')
    health_regulations_2018_2020 = health_regulations_2018_2020.dropna(axis=1, how='all')
    health_regulations_2010_2017 = health_regulations_2010_2017.dropna(axis=1, how='all')

   
# Remove columns that are not relevant for the analysis
    columns_to_remove_2021_2024 = [
        "IND_ID",
        "IND_CODE",
        "IND_UUID",
        "IND_PER_CODE",
        "DIM_GEO_CODE_TYPE",
        "DIM_TIME_TYPE",
        "DIM_PUBLISH_STATE_CODE",
        "DIM_GEO_CODE_M49"
        ]

    health_regulations_2021_2024 = health_regulations_2021_2024.drop(columns_to_remove_2021_2024, axis=1)


    columns_to_remove_2010_2020 = [
        "IndicatorCode",
        "ValueType",
        "ParentLocationCode",
        "Location type",
        "Period type",
        "IsLatestYear",
        "Value",
        "FactValueTranslationID",
        "FactComments",
        "Language",
        "ParentLocation",
        "SpatialDimValueCode",
        "DateModified"
    ]

    health_regulations_2018_2020 = health_regulations_2018_2020.drop(columns_to_remove_2010_2020, axis=1)

    health_regulations_2010_2017 = health_regulations_2010_2017.drop(columns_to_remove_2010_2020, axis=1)


# ------------------------------------------------------------------------------------------------------
# 3. Concatenate the three datasets into a single DataFrame
#-------------------------------------------------------------------------------------------------------

# Rename columns

    health_regulations_2021_2024 = health_regulations_2021_2024.rename(
        columns = {
            "IND_NAME": "Regulation",
            "GEO_NAME_SHORT": "Country",
            "DIM_TIME":"Year",
            "INDEX_N": "Index_N"
        }
    )

    health_regulations_2018_2020 = health_regulations_2018_2020.rename(
        columns = {
            "Indicator": "Regulation",
            "Location": "Country",
            "Period":"Year",
            "FactValueNumeric": "Index_N"
        }
    )


    health_regulations_2010_2017 = health_regulations_2010_2017.rename(
        columns = {
            "Indicator": "Regulation",
            "Location": "Country",
            "Period":"Year",
            "FactValueNumeric": "Index_N"
        }
    )

# Concatenate the three DataFrames
    health_regulations = pd.concat(
    [health_regulations_2010_2017, health_regulations_2018_2020, health_regulations_2021_2024],
    ignore_index = True
    )


# ------------------------------------------------------------
# 4. Data cleaning and filtering based on the Index_N variable
# ------------------------------------------------------------

# Remove rows with missing Index_N values
    health_regulations = health_regulations[health_regulations["Index_N"].notna()]

# Round Index_N values to two decimal places
    health_regulations["Index_N"] = health_regulations["Index_N"].round(2)

# Keep only countries with an Index_N score above 60 (high level of health regulation compliance)
    health_regulations = health_regulations[health_regulations["Index_N"] > 60]

# Ensure that the year column is numeric
    health_regulations["Year"] = health_regulations["Year"].astype(int)

# Sort the data by country and year (from the most recent to the oldest)
    health_regulations = health_regulations.sort_values(["Country", "Year"], ascending=[True, False])

# Add the ISO Alpha-3 country code
# Function to retrieve the ISO Alpha-3 country code
    def get_country_code(name):
        try:
            country = pycountry.countries.lookup(name)
            return country.alpha_3
        except LookupError:
            return None  # if the country is not found

# Create the new "Country_Code" column
    health_regulations["Country_Code"] = health_regulations["Country"].apply(get_country_code)

# Create the "Period" column
    health_regulations["Period"] = "2010-2024"


# ------------------------------------------------------------------------------
# 5. Function: Calculate the average compliance index (2010-2024)
# ------------------------------------------------------------------------------

# Select data within the required time period
    health_regulations_2010_2024 = health_regulations[
    (health_regulations["Year"] >= 2010) & (health_regulations["Year"] <= 2024)
    ]

# Calculate the average Index_N value over the selected period

    index_n_average = (
    health_regulations_2010_2024
    .groupby("Country", as_index=False)["Index_N"]
    .mean()
    .round(2)
    .rename(columns={"Index_N": "Index_N_average"})
    )

    health_regulations_2010_2024 = health_regulations_2010_2024.merge(
     index_n_average, 
     on = "Country", 
     how = "left"
     )


# Create a summary dataset by country
    df_health_regulation = (
    health_regulations_2010_2024[["Country", "Country_Code", "Period", "Index_N_average"]]
    .drop_duplicates()
    .reset_index(drop=True)
    )

# ------------------------------------------------------------
# 6. Execute the analysis and display the results
# ------------------------------------------------------------
    #print("=== TOP 10 countries with the highest Index_N (2010-2024) ===")
    #print(df_health_regulation.head(10))


    return df_health_regulation
