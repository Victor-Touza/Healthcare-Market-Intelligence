# ============================================================
#  FATHER MODULE: MAIN_COUNTRIES.PY
# ============================================================
# This script integrates the child-level (country-specific) analytical modules
# for a given period. It generates a complete dataset containing the
# "Attractive Market Index" (AMI) by country.
# ============================================================

def run_main_countries():
    import pandas as pd
    import sys
    from sklearn.preprocessing import MinMaxScaler
    import pycountry
    from importlib import import_module

#--------------------------------------------------------------------------------------------
# 1. Data loading
#--------------------------------------------------------------------------------------------

# Proyect file path
    modules_path = "./src"

# Add the route to the system to enable the import of child modules
    sys.path.append(modules_path)


# ------------------------------------------------------------
# 2. Importing child modules
# ------------------------------------------------------------

# Build the import paths based on the selected period.
# Connect the individual programs.
# Define the folder names (child modules).
    child_modules = {
    "health_regulations": f"modul_countries.countries_health_regulations.period_2010_2024",
    "regulation": f"modul_countries.countries_health_regulation_compliance.period_2010_2024",
    "gdp_per_capita": f"modul_countries.gdp_per_capita.period_2010_2024",
    "healthcare": "modul_countries.health_expenditure_gdp.period_2010_2024",
    "physicians": f"modul_countries.physicians_per_1000_inhabitants.period_2010_2024",
    "over65": f"modul_countries.population_over_65.period_2010_2024",
    "rd_expenditure": f"modul_countries.rd_expenditure_gdp.period_2010_2024",
    "import_volume": f"modul_countries.import_volume.period_2010_2024"
    }

# Import each module and execute its main function
    df_health_regulations = import_module(child_modules["health_regulations"]).load_national_health_regulations()
    df_regulation = import_module(child_modules["regulation"]).load_health_regulation_compliance()
    df_gdp_per_capita = import_module(child_modules["gdp_per_capita"]).load_countries_gdp_per_capita()
    df_gdp_healthcare = import_module(child_modules["healthcare"]).load_health_expenditure_percentage_gdp()
    df_physicians = import_module(child_modules["physicians"]).load_physicians_per_1000_inhabitants()
    df_over65 = import_module(child_modules["over65"]).load_population_aged_65_and_over()
    df_rd_expenditure = import_module(child_modules["rd_expenditure"]).load_rd_expenditure_percentage_gdp()
    df_import_volume = import_module(child_modules["import_volume"]).load_import_volume()



#--------------------------------------------------------------------------------------------
# 3. Merge the DataFrames into a complete dataset.
#--------------------------------------------------------------------------------------------

# First dataframe (base)
    df_final = df_health_regulations.copy()

# List of dataframes to join
    lista_dataframes = [
    df_regulation,
    df_gdp_per_capita,
    df_gdp_healthcare,
    df_physicians,
    df_over65,
    df_rd_expenditure,
    df_import_volume
    ]

#  Combine all the dataframes progressively.
    for df in lista_dataframes:
        df = df.drop(columns=["Country", "Period"], errors="ignore")
        df_final = pd.merge(df_final, df, on="Country_Code", how="outer")


# Recover the names of countries lost during the "merge" operation.
# a) Function to get the country name from the ISO3 code.

    def name_country(code, current_name):
        if current_name == 0 or pd.isna(current_name):
            try:
                return pycountry.countries.get(alpha_3=code).name
            except:
                return "Unknown"
        else:
            return current_name

# b) Apply the function to the "Country" column
    df_final["Country"] = df_final.apply(lambda row: name_country(row["Country_Code"], row["Country"]), axis=1)


# Recover the period lost during the "merge" operation.
# df_final["Period"] = "2010-2024"


# Sort by country
    df_final = df_final.sort_values(by="Country").reset_index(drop=True)


#--------------------------------------------------------------------------------------------
# 4. Clean the resulting dataset
#--------------------------------------------------------------------------------------------

# Fill in nulls where necessary.
    df_final = df_final.fillna(0).infer_objects(copy=False)

# Reorder the main columns (you can adapt this based on your actual names)
    final_columns = [
    "Country",
    "Country_Code",
    "Period",
    "Health_Regulation_Status",
    "Health_Regulation_Code",
    "Index_N_average",
    "GDP_Per_Capita_Average",
    "Health_Expenditure_Percentage_GDP",
    "Physicians_Per_1000_Inhabitants",
    "Population_Over_65_Percentage",
    "RD_Expenditure_Percentage_GDP",
    "Relative_Import_Index"
    ]

    df_final = df_final[final_columns]



#--------------------------------------------------------------------------------------------
# 5. Normalization
#--------------------------------------------------------------------------------------------

# Create a copy to standardize
    df_standard = df_final.copy()

    cod_legislation = {
    'No': 0,
    'Yes, but it is not part of the National Health Program': 1,
    'Yes, and it is part of the National Health Program/Plan or Policy': 2
    }

    df_standard["Health_Regulation_Status_cod"] = df_standard["Health_Regulation_Status"].map(cod_legislation)

# Replace nulls with 0 in the legislation coding
    df_standard["Health_Regulation_Status_cod"] = df_standard["Health_Regulation_Status_cod"].fillna(0)


# Select numerical variables to scale.
    num_variables = [
        "Health_Regulation_Status_cod",
        "Index_N_average",
        "GDP_Per_Capita_Average",
        "Health_Expenditure_Percentage_GDP",
        "Physicians_Per_1000_Inhabitants",
        "Population_Over_65_Percentage",
        "RD_Expenditure_Percentage_GDP",
        "Relative_Import_Index"
    ]

# We keep only the "Health_Regulation_Status_cod" variable.
#df_standard["Health_Regulation_Status_cod"] = df_standard["Health_Regulation_Status"].map(cod_legislation)

# We convert numeric columns that might have remained as 'object'
    df_standard[num_variables] = df_standard[num_variables].apply(pd.to_numeric, errors="coerce")

    scaler = MinMaxScaler()
    df_standard[num_variables] = scaler.fit_transform(df_standard[num_variables])



#--------------------------------------------------------------------------------------------
# 6. Calculate the AMI (Attractive Market Index) index.
#--------------------------------------------------------------------------------------------

# Define variable weights for the AMI

    weights = {
    "Health_Regulation_Status_cod": 0.15,
    "Index_N_average": 0.20,
    "GDP_Per_Capita_Average": 0.15,
    "Health_Expenditure_Percentage_GDP": 0.10,
    "Physicians_Per_1000_Inhabitants": 0.10,
    "Population_Over_65_Percentage": 0.10,
    "RD_Expenditure_Percentage_GDP": 0.10,
    "Relative_Import_Index": 0.10
    }

# Create a column with name AMI (acronym for "Attractive Market Index") with the final assessment.

# Calculate AMI
    df_standard["AMI"] = (
    df_standard[list(weights.keys())] * pd.Series(weights)
    ).sum(axis=1)


# ------------------------------------------------------------
# 7. Selection of the most attractive countries
# ------------------------------------------------------------
    df_countries = df_standard.sort_values(by="AMI", ascending=False).head(20)
    df_countries = df_countries[["Country_Code", "Country", "Period", "AMI"]]

# ------------------------------------------------------------
# 8. Final result
# ------------------------------------------------------------

    #print("\nTOP 20 MORE ATTRACTIVE COUNTRIES")
    #print(df_countries)

    return df_countries
