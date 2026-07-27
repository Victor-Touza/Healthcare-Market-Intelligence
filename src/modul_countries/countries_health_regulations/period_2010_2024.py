# ========================================================
#  I. ANALYSIS OF COUNTRIES WITH NATIONAL HEALTH REGULATIONS
# ========================================================

# Import required libraries
import pandas as pd


# General pandas configuration for improved data display
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 0)
pd.options.display.float_format = "{:.2f}".format


def load_national_health_regulations():
# ------------------------------------------------------------
# 1. Data loading
# ------------------------------------------------------------
# Load the CSV file containing information on national health policies
    file_path = "./data/raw/file.csv"
    national_health_regulations = pd.read_csv(file_path)

# ------------------------------------------------------------
# 2. Initial dataset cleaning
# ------------------------------------------------------------
# Remove columns that are completely empty
    national_health_regulations = national_health_regulations.dropna(axis=1, how='all')

# Remove columns that are not relevant for the analysis
    columns_to_remove = [
        'Indicator',
        'IndicatorCode',
        'ParentLocation',
        'ValueType',
        'Location type',
        'Language',
        'ParentLocationCode',
        'Period type',
        'FactComments',
        'IsLatestYear',
        'DateModified'
    ]

    national_health_regulations = national_health_regulations.drop(columns_to_remove, axis=1)


# ----------------------------------------------------------------
# 3. Filter countries with an active national health policy
# ----------------------------------------------------------------
# Remove rows where the "Value" column contains "No data"
    national_health_regulations = national_health_regulations[~national_health_regulations["Value"].isin(["No data"])]

# Remove rows with missing values in the "FactValueTranslationID" column
    national_health_regulations = national_health_regulations[national_health_regulations["FactValueTranslationID"].notna()]


# ------------------------------------------------------------
# 4. Correct text values in the "Value" column
# ------------------------------------------------------------
# Standardize category labels
    national_health_regulations["Value"] = national_health_regulations["Value"].replace({
        "Yes": "Yes, but it is not part of the National Health Program",
        "Yes, but is not part of the National Health Program":
            "Yes, but it is not part of the National Health Program"
    })


# ------------------------------------------------------------
# 5. # Filter data by analysis period
# ------------------------------------------------------------
# Define the analysis period
    time_range = range(2010, 2025)

    df_period = national_health_regulations[national_health_regulations["Period"].isin(time_range)].copy()

    # Sort the data to ensure that .last() returns the most recent record for each country.
    df_period = df_period.sort_values(by=["Location", "Period"])

    # Keep the most recent record for each country
    df_latest = df_period.groupby("Location", as_index=False).last()

    # Assign a label to the analysis period
    df_latest["Period"] = "2010_2024"

    selected_columns = ['Location', 'SpatialDimValueCode', 'Period', 'Value', 'FactValueTranslationID']
    df_latest = df_latest[selected_columns]

# ------------------------------------------------------------
# 6. Prepare the final dataset
# ------------------------------------------------------------
# Select the columns required for the final analysis
    national_health_regulations = df_latest.copy()

# Rename columns for improved clarity
    df_result = national_health_regulations.rename(columns={
        "Location": "Country",
        "SpatialDimValueCode":"Country_Code",
        "Value":"Health_Regulation_Status",
        "FactValueTranslationID":"Health_Regulation_Code"
    })

# ------------------------------------------------------------
# 7. Execute the analysis and display the results
# ------------------------------------------------------------

    #print("\n=== Overview of countries with an active national health policy (2010-2024) ===")
    #print(df_result.head(10))

    return df_result

