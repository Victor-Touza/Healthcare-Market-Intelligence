# ========================================================
#  VI. PERCENTAGE OF GDP ALLOCATED TO HEALTHCARE
# ========================================================

import pandas as pd
import pycountry

# General pandas configuration for improved data display
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 0)
pd.options.display.float_format = "{:.2f}".format


def load_health_expenditure_percentage_gdp():

# ------------------------------------------------------------
# 1. Data loading
# ------------------------------------------------------------
    file_path = "./data/raw/file.csv"
    health_expenditure_gdp = pd.read_csv(file_path, header=2)


# ------------------------------------------------------------
# 2. Initial dataset cleaning
# ------------------------------------------------------------
# Validate country codes and rename columns

# Function to check if an ISO3 code corresponds to a real country.
    def is_valid_country(country_code):
            return pycountry.countries.get(alpha_3=country_code) is not None

# Filter only valid countries
    health_expenditure_gdp = health_expenditure_gdp[health_expenditure_gdp['Country Code'].apply(is_valid_country)].copy()

# Rename the columns
    health_expenditure_gdp = health_expenditure_gdp.rename(columns={"Country Name":"Country", "Country Code":"Country_Code"})


# -----------------------------------------------------------------------------------------
# 3. Function: calculate the average percentage of GDP allocated to healthcare for 2010-2024
# -----------------------------------------------------------------------------------------

# 3.1. Function to calculate the average healthcare expenditure.

    def calculate_average_health_expenditure(df):
        """
        Calculate the average healthcare expenditure as a percentage of GDP for the period 2010-2024.

        """
        year_columns = ['2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', 
                    '2019', '2020', '2021', '2022', '2023', '2024']
    
    # Filter only the columns that actually exist in the dataset.
        existing_columns = [c for c in year_columns if c in df.columns]
        if not existing_columns:
            print("No data for period 2010-2024")
            return None

    # Select the necessary columns and remove rows with no data for those years.
        df_filtered = df[["Country", "Country_Code"] + existing_columns].dropna(subset = existing_columns, how="all")

    # Calculate the average for the period.
        df_filtered["2010_2024"] = df_filtered[existing_columns].mean(axis=1)
        df_filtered = df_filtered.rename(columns = {"2010_2024":"Health_Expenditure_Percentage_GDP"})

    # Create the "Period" column
        df_filtered["Period"] = "2010-2024"

    # Sort countries by healthcare expenditure and retain the top 150.
        df_final = df_filtered[
              ["Country", "Country_Code", "Period", "Health_Expenditure_Percentage_GDP"]
              ].sort_values(by="Health_Expenditure_Percentage_GDP", ascending=False).head(150)
        return df_final


# ------------------------------------------------------------
# 4. Execute the analysis and display the results
# ------------------------------------------------------------
    df_result = calculate_average_health_expenditure(health_expenditure_gdp)

    #print("\n=== Top 10 countries with the highest healthcare expenditure as a percentage of GDP (2010-2024) ===")
    #print(df_result.head(10))

    return df_result
