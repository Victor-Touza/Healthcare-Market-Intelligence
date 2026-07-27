#===========================================================
# III. COUNTRIES WITH THE HIGHEST GDP PER CAPITA
#===========================================================

# Import required libraries
import pandas as pd
import pycountry


# General pandas configuration for improved data display
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 0)
pd.options.display.float_format = "{:.2f}".format


def load_countries_gdp_per_capita():
# ------------------------------------------------------------
# 1. Data loading
# ------------------------------------------------------------
        file_path = "./data/raw/file.csv"
        data_gdp_per_capita = pd.read_csv(file_path)

# ------------------------------------------------------------
# 2. Initial dataset cleaning
# ------------------------------------------------------------

# 2.1. Remove rows that do not correspond to real countries
        data_gdp_per_capita = data_gdp_per_capita[data_gdp_per_capita["Code"].notna()]

# Function to check if an ISO3 code corresponds to a real country
        def is_valid_country(country_code):
                return pycountry.countries.get(alpha_3=country_code) is not None

# Filter only valid countries
        data_gdp_per_capita = data_gdp_per_capita[data_gdp_per_capita['Code'].apply(is_valid_country)].copy()

# 2.2. Rename and select the required columns
        data_gdp_per_capita = data_gdp_per_capita.rename(
        columns={
        "Entity":"Country",
        "Year":"Year",
        "Code":"Country_Code",
        "GDP per capita, PPP (constant 2021 international $)":"GDP_Per_Capita_PPP"}
        )

        data_gdp_per_capita = data_gdp_per_capita[["Country", "Country_Code", "Year", "GDP_Per_Capita_PPP"]]

# 2.3. Remove rows where "GDP_Per_Capita_PPP" is empty.
        data_gdp_per_capita = data_gdp_per_capita.dropna(subset=["GDP_Per_Capita_PPP"])


# ------------------------------------------------------------------------------
#  3. Calculate GDP average (2010-2024)
# ------------------------------------------------------------------------------

# 3.1. Select the data corresponding to the desired time period.
        data_period = data_gdp_per_capita[
        (data_gdp_per_capita["Year"] >= 2010) & (data_gdp_per_capita["Year"] <= 2024)
        ]


# 3.2. Group by each country and calculate the average GDP for that country.        
        df_average_gdp_by_country = (
                        data_period
                        .groupby("Country", as_index=False)["GDP_Per_Capita_PPP"]
                        .mean()
                        .rename(columns={"GDP_Per_Capita_PPP": "GDP_Per_Capita_Average"})
                        )

# Keep only the most recent record for each country so that the DataFrame contains one row per country.
        data_period = data_period.sort_values(["Country", "Year"])
        latest_country_data = data_period.groupby("Country", as_index=False).last()


# Create final dataframe with the whole information.
        final_results = latest_country_data.merge(df_average_gdp_by_country, on = "Country", how = "left")

# Create the "Period" column
        final_results["Period"] = "2010-2024"

# Round values for presentation purposes
        final_results["GDP_Per_Capita_Average"] = final_results["GDP_Per_Capita_Average"].round(2)

        final_results = final_results[["Country", "Country_Code", "Period", "GDP_Per_Capita_Average"]]

        df_results = final_results.sort_values(by="GDP_Per_Capita_Average", ascending=False).head(150)


# ------------------------------------------------------------
# 4. Execute the analysis and display the results
# ------------------------------------------------------------
#         
        #print("\n=== TOP 10 countries with the highest GDP per capita (2010-2024) ===")
        #print(df_results.head(10))

        return df_results


