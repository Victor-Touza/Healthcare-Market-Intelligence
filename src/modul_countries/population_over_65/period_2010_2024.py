# ========================================================
# VII. POPULATION AGED 65 AND OVER
# ========================================================

# Import required libraries
import pandas as pd


# General pandas configuration for improved data display
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 0)
pd.options.display.float_format = "{:.2f}".format


def load_population_aged_65_and_over():
# ------------------------------------------------------------
# 1. Data loading
# ------------------------------------------------------------
    file_path = "./data/raw/file.csv"
    data_over65 = pd.read_csv(file_path, header=2)


# ------------------------------------------------------------
# 2. Initial dataset cleaning
# ------------------------------------------------------------
# Remove columns with whole NaN values
    data_over65 = data_over65.dropna(axis=1, how='all')

# Rename important columns
    data_over65 = data_over65.rename(columns={"Country Name":"Country", "Country Code":"Country_Code"})

# Identify columns of available years
    available_columns = [c for c in data_over65.columns if c.isdigit()]

# -----------------------------------------------------------------------------------------
# 3. # Function: Calculate the average percentage of the population aged 65 and over (2010-2024)
# -----------------------------------------------------------------------------------------

# 3.1. Calculate the average percentage for the analysis period

    def population_over65_2010_2024(df):
        """
        Calculate the average percentage of the population aged 65 and over for the period 2010-2024.

        """
        year_columns = ['2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', 
                    '2019', '2020', '2021', '2022', '2023', '2024']
    
    # Filter only the columns that actually exist in the dataset
        available_columns = [c for c in year_columns if c in df.columns]
        if not available_columns:
            print("No data for period 2010-2024")
            return None

    # Select the necessary columns and remove rows with no data for those years
        df_filtered = df[["Country", "Country_Code"] + available_columns].dropna(subset = available_columns, how="all")

    # Calculate the average for the analysis period
        df_filtered["2010_2024"] = df_filtered[available_columns].mean(axis=1)
        df_filtered = df_filtered.rename(columns = {"2010_2024":"Population_Over_65_Percentage"})

    # Create the "Period" column
        df_filtered["Period"] = "2010-2024"

    # Rank the countries and retain the top 150
        df_final = df_filtered[
              ["Country", "Country_Code", "Period", "Population_Over_65_Percentage"]
              ].sort_values(by="Population_Over_65_Percentage", ascending=False).head(150)
        return df_final


# ------------------------------------------------------------
# 5. Execute the analysis and display the results
# ------------------------------------------------------------
    df_result = population_over65_2010_2024(data_over65)

    #print("\n=== Top 10 countries with the highest percentage of the population aged 65 and over (2010-2024) ===")
    #print(df_result.head(10))

    return df_result

