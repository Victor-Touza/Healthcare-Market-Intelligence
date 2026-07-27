# ========================================================
#  V. NUMBER OF PHYSICIANS PER 1,000 INHABITANTS
# ========================================================

# ------------------------------------------------------------
# 1. Import required libraries
# ------------------------------------------------------------
import pandas as pd

# General pandas configuration for improved data display
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 0)
pd.options.display.float_format = "{:.2f}".format


def load_physicians_per_1000_inhabitants():

# ------------------------------------------------------------
# 2. Data loading
# ------------------------------------------------------------
    file_path = "./data/raw/file.csv"
    physicians_data = pd.read_csv(file_path, header=2)


# ------------------------------------------------------------
# 3. Initial dataset cleaning
# ------------------------------------------------------------
# Rename columns
    physicians_data = physicians_data.rename(columns={"Country Name": "Country", "Country Code": "Country_Code"})

# Remove columns that are completely empty
    physicians_data = physicians_data.dropna(axis=1, how='all')

# Identify the available year columns
    available_columns = [c for c in physicians_data.columns if c.isdigit()]
    #print("\nAvailable Columns:", available_columns)


# ----------------------------------------------------------------------------
# 4. Function: calculate the average number of physicians per thousand inhabitants (2010-2024)
# ----------------------------------------------------------------------------
    def calculate_average_physicians(df):
        """
        Calculate the average number of physicians per 1,000 inhabitants for the 2010-2024 period. 
        It returns a DataFrame containing the 150 countries with the highest averages.
            """
        year_columns = ['2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', 
                    '2019', '2020', '2021', '2022', '2023', '2024']
        
        # Filter only the columns that actually exist in the dataset.
        existing_columns = [c for c in year_columns if c in df.columns]
        if not existing_columns:
            print("No data for period 2010-2024")
            return None

        # Select the required columns and remove countries without data for the selected period.
        df_final = df[["Country", "Country_Code"] + existing_columns].dropna(subset=existing_columns, how="all")



        # Calculate the average number of physicians during the analysis period.
        df_final["2010_2024"] = df_final[existing_columns].mean(axis=1)
        df_final = df_final.rename(columns={"2010_2024":"Physicians_Per_1000_Inhabitants"})

        # Create the "Period" column
        df_final["Period"] = "2010-2024"

        ## Sort the countries by the average number of physicians and keep the top 150.
        df_final = df_final[
            ["Country", "Country_Code", "Period", "Physicians_Per_1000_Inhabitants"]
            ].sort_values(by="Physicians_Per_1000_Inhabitants", ascending=False).head(150)
        
        return df_final


# ------------------------------------------------------------
# 5. Execute the analysis and display the results
# ------------------------------------------------------------
    df_result = calculate_average_physicians(physicians_data)

    #print("\n=== countries with the highest number of physicians per 1,000 inhabitants (2010-2024) ===")
    #print(df_result.head(10))
    return df_result
