# ========================================================
#  VIII. IMPORT VOLUME
# ========================================================

# Import required libraries
import pandas as pd
import pycountry
import os

# General pandas configuration for improved data display
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 0)
pd.options.display.float_format = "{:.2f}".format


def load_import_volume():
    
# -------------------------------------------------------------------
# 1. Creation of a single dataset containing all available datasets
# -------------------------------------------------------------------

    file_path = "./data/raw"
    files = [f for f in os.listdir(file_path) if f.startswith("WITS-By-HS6Product_") and f.endswith(".xlsx")]

# Load and merge all files

    dataframes = []

    for file in files:
        # Extract the year from the name; for example, "WITS-By-HS6Product_2010.xlsx" becomes "2010"
        year = file.split("_")[-1].split(".")[0]
        
        # Read the Excel file (by default, it uses the first sheet)
        df = pd.read_excel(os.path.join(file_path, file))
        
        # Add a column with the year
        df["Year"] = int(year)
        
        # Store the DataFrame in the list
        dataframes.append(df)


# Concatenate all DataFrames into a single DataFrame
    import_data = pd.concat(dataframes, ignore_index=True)


# ------------------------------------------------------------
# 2. Initial dataset cleaning
# ------------------------------------------------------------
    important_columns = ["Reporter", "Year", "Trade Value 1000USD"]
    import_data = import_data[important_columns]

    import_data = import_data.rename(
            columns={"Reporter": "Country"})


# Function to retrieve the ISO Alpha-3 country code
    def get_country_code(name):
            try:
                country = pycountry.countries.lookup(name)
                return country.alpha_3
            except LookupError:
                return None  # Return None if the country cannot be found

# Create the "Country_Code" column
    import_data["Country_Code"] = import_data["Country"].apply(get_country_code)

# Function to check if an ISO3 code corresponds to a real country
    def is_valid_country(code):
            if code is None:
                return False
            return pycountry.countries.get(alpha_3=code) is not None

#  Keep only valid countries
    import_data = import_data[import_data['Country_Code'].apply(is_valid_country)].copy()


# ------------------------------------------------------------
# 3. Data transformation
# ------------------------------------------------------------

# 3.1. Calculate the average imports for each country over that period
    df_average_import_by_country = (
    import_data
    .groupby("Country", as_index=False)["Trade Value 1000USD"]
    .mean()
    .rename(columns={"Trade Value 1000USD": "Average_Import_Value_1000USD"})
    )

# 3.2. Calculate the relative import index
    df_average_import_by_country["Relative_Import_Index"] = (
    df_average_import_by_country["Average_Import_Value_1000USD"] / df_average_import_by_country["Average_Import_Value_1000USD"].max()
    )
    
    df_average_import_by_country["Relative_Import_Index"] = (df_average_import_by_country["Relative_Import_Index"].round(3)
    )


# 3.3. Merge the aggregated results with the country information
# 3.3.1. Reduce the dataset to one row per country while preserving the most recent record
    import_data = (
    import_data
    .sort_values(["Country", "Year"])
    .groupby("Country", as_index=False)
    .last()
    )

# 3.3.2. Combine both results.
    final_results = import_data.merge(
    df_average_import_by_country,
    on="Country",
    how="right"
    )

# 3.3.3. Create the period variable.
    final_results['Period'] = '2010-2024'

# 3.3.3. Select only the relevant final columns
    final_results = final_results[
    ["Country", "Country_Code", "Period", "Relative_Import_Index"]
    ]


# ------------------------------------------------------------
# 4. Execute the analysis and display the results
# ------------------------------------------------------------
#  Select the 150 countries with the highest import volume

    df_result = final_results.sort_values(by="Relative_Import_Index", ascending=False).head(150)

    #print("\n=== Top 10 countries with the highest import volumes (2010-2024) ===")
    #print(df_result.head(10))

    return df_result


