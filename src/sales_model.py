# ============================================================
#  FATHER MODULE: SALES_PREDICTION.PY
# ============================================================
# This script integrates the country-level and device-level
# analytical modules. It generates a complete dataset containing
# the "Sales Index" (SI) to identify the most attractive
# products and countries for commercialization.
# ============================================================

import pandas as pd
import sys
from statsmodels.tsa.holtwinters import Holt
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np



#-----------------------------------------------------------
# 1. Initial setup
#-----------------------------------------------------------

# Project file path
sys.path.append("./src")

# Import the two parent modules
from main_countries import run_main_countries
from main_devices import run_main_devices

# Execute the child modules
df_countries = run_main_countries()
df_devices = run_main_devices()

#-----------------------------------------------------------
# 2. Prepare the datasets
#-----------------------------------------------------------

# Select the required columns
df_countries = df_countries[["Country","Country_Code", "AMI"]]
df_devices = df_devices[["Country_Code","Product_Name","Product_Code","Year","Annual_Product_Index","Global_Product_Index"]]

#-----------------------------------------------------------
# 3. Merge both datasets
#-----------------------------------------------------------

# Create the analysis dataset by merging the country and device datasets
df_analysis = pd.merge(df_devices, df_countries, on="Country_Code", how="inner")

#-----------------------------------------------------------
# 4. Calculate the combined annual and global sales indices
#-----------------------------------------------------------
# The combined index weights both the Attractive Market Index (AMI) and the Global Product Index.
# Relative importance of market attractiveness and product attractiveness
weight_country = 0.6
weight_device = 0.4

# 4.1 Calculate the Annual Sales Index
df_analysis["Annual_Sales_Index"] = (
    weight_country * df_analysis["AMI"] +
    weight_device * df_analysis["Annual_Product_Index"]
).round(4)

# 4.2 Calculate the Global Sales Index
df_analysis["Global_Sales_Index"] = (
    weight_country * df_analysis["AMI"] + weight_device * df_analysis["Global_Product_Index"]
).round(4)

#-----------------------------------------------------------
# 5. Sort and export the final results
#-----------------------------------------------------------

df_analysis = df_analysis.sort_values(by="Global_Sales_Index", ascending=False)

final_columns = [
    "Country",
    "Country_Code",
    "Product_Name",
    "Product_Code",
    "Year",
    "AMI",
    "Annual_Product_Index",
    "Global_Product_Index",
    "Annual_Sales_Index",
    "Global_Sales_Index"
]

df_analysis = df_analysis[final_columns]


# 5.1 Descriptive statistics and outlier detection (CSV + Excel)
# Select the numerical variables of interest
statistics_columns = [
    "AMI",
    "Annual_Product_Index",
    "Global_Product_Index",
    "Annual_Sales_Index",
    "Global_Sales_Index"
]

# 5.1.1 Calculate descriptive statistics
statistics = df_analysis[statistics_columns].describe().T  # Transposed for clarity
statistics["median"] = df_analysis[statistics_columns].median()
statistics["standard deviation"] = df_analysis[statistics_columns].std()

# 5.1.2 Detect outliers using the IQR method
Q1 = df_analysis[statistics_columns].quantile(0.25)
Q3 = df_analysis[statistics_columns].quantile(0.75)
IQR = Q3 - Q1

outliers = ((df_analysis[statistics_columns] < (Q1 - 1.5 * IQR)) | 
            (df_analysis[statistics_columns] > (Q3 + 1.5 * IQR))).sum()

statistics["outliers"] = outliers

# Export the results to CSV (TFM documentation)
statistics.to_csv("descriptive_statistics.csv", index=True)

# Export the results to Excel (visualization and charts)
with pd.ExcelWriter("descriptive_statistics.xlsx") as writer:
    statistics.to_excel(writer, sheet_name="Summary")

print(" Descriptive statistics successfully generated:")
print(" - CSV: descriptive_statistics.csv")
print(" - Excel: descriptive_statistics.xlsx")

#---------------------------------------------------------------------
# 6. PREDICTIVE MODEL OF THE ANNUAL SALES INDEX BY COUNTRY AND PRODUCT
#---------------------------------------------------------------------

# Group data by Country, Product and Year
df_sales_history = (
    df_analysis
    .groupby(["Country", "Product_Name", "Year"])["Annual_Sales_Index"]
    .mean()
    .reset_index()
)

results_metrics = []
results_forecast = []

# Train one model for each Country-Product combination
for (country, product), df_group in df_sales_history.groupby(["Country", "Product_Name"]):

    # Sort observations chronologically
    df_group = df_group.sort_values("Year")

    # ------------------------------------------------------------
    # Split into training and test datasets
    # ------------------------------------------------------------

    train = df_group[df_group["Year"] <= 2021].set_index("Year")
    test = df_group[df_group["Year"] > 2021].set_index("Year")

    # Skip combinations with insufficient training data
    if len(train) < 3:
        continue

    # ------------------------------------------------------------
    # Train Holt's exponential smoothing model
    # ------------------------------------------------------------

    model = Holt(
        train["Annual_Sales_Index"],
        initialization_method="estimated"
    ).fit()

    # ------------------------------------------------------------
    # Evaluate model performance
    # ------------------------------------------------------------

    if len(test) > 0:

        y_pred_test = model.forecast(len(test))

        mae = mean_absolute_error(
            test["Annual_Sales_Index"],
            y_pred_test
        )

        rmse = np.sqrt(
            mean_squared_error(
                test["Annual_Sales_Index"],
                y_pred_test
            )
        )

    else:
        mae = None
        rmse = None

    results_metrics.append({
        "Country": country,
        "Product_Name": product,
        "MAE": round(mae, 4) if mae is not None else None,
        "RMSE": round(rmse, 4) if rmse is not None else None
    })

    # ------------------------------------------------------------
    # Retrain the model using the complete historical series
    # ------------------------------------------------------------

    final_model = Holt(
        df_group.set_index("Year")["Annual_Sales_Index"],
        initialization_method="estimated"
    ).fit()

    # ------------------------------------------------------------
    # Forecast Annual Sales Index for 2025-2027
    # ------------------------------------------------------------

    future_predictions = final_model.forecast(3)

    for year, prediction in zip(
        [2025, 2026, 2027],
        future_predictions
    ):

        results_forecast.append({
            "Country": country,
            "Product_Name": product,
            "Year": year,
            "Predicted_Sales_Index": round(prediction, 4)
        })

#------------------------------------------------------------
# Convert results into DataFrames
#------------------------------------------------------------

df_metrics = pd.DataFrame(results_metrics)
df_forecast = pd.DataFrame(results_forecast)

print("\nPREDICTIVE MODEL PERFORMANCE METRICS BY COUNTRY-PRODUCT COMBINATION:")
print(df_metrics.head())

print("\nSALES INDEX FORECAST (2025-2027):")
print(df_forecast.head())

#------------------------------------------------------------
# Export results
#------------------------------------------------------------

df_metrics.to_csv("predictive_model_metrics.csv", index=False)
df_forecast.to_csv("sales_forecast.csv", index=False)