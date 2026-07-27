# ============================================================
#  FATHER MODULE: MAIN_DEVICES.PY
# ============================================================
# This script integrates all device-level modules into a single dataset.
# It calculates both the Annual Product Index and the Global Product Index
# for each country-product combination.
# ============================================================

def run_main_devices():
    import pandas as pd
    import sys
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
        "c_arms_systems": f"modul_devices.imports_c_arm_systems.period_2010_2024",
        "ultrasound_systems": f"modul_devices.imports_ultrasound_systems.period_2010_2024",
        "xray_systems": f"modul_devices.imports_xray_systems.period_2010_2024",
        "linear_accelerators": f"modul_devices.imports_linear_accelerators.period_2010_2024",
        "mammography_systems": f"modul_devices.imports_mammography_systems.period_2010_2024",
        "radiotherapy_systems": f"modul_devices.imports_radiotherapy_systems.period_2010_2024",
        "mri_systems": f"modul_devices.imports_mri_systems.period_2010_2024",
        "ct_scanners": f"modul_devices.imports_ct_scanners.period_2010_2024"
    }


# Import each module and execute its main function
    df_c_arms_systems = import_module(child_modules["c_arms_systems"]).load_c_arms()
    df_ultrasound_systems = import_module(child_modules["ultrasound_systems"]).load_ultrasound_systems()
    df_xray_systems = import_module(child_modules["xray_systems"]).load_xray_systems()
    df_linear_accelerators = import_module(child_modules["linear_accelerators"]).load_linear_accelerators()
    df_mammography_systems = import_module(child_modules["mammography_systems"]).load_mammography_systems()
    df_radiotherapy_systems = import_module(child_modules["radiotherapy_systems"]).load_radiotherapy_systems()
    df_mri_systems = import_module(child_modules["mri_systems"]).load_mri_scanners()
    df_ct_scanners = import_module(child_modules["ct_scanners"]).load_ct_scanners()


#--------------------------------------------------------------------------------------------
# 3. Combine all device datasets into a single DataFrame.
#--------------------------------------------------------------------------------------------

# List of dataframes to concat
    dataframes = [
        df_c_arms_systems,
        df_ultrasound_systems,
        df_xray_systems,
        df_linear_accelerators,
        df_mammography_systems,
        df_radiotherapy_systems,
        df_mri_systems,
        df_ct_scanners
    ]

    df_devices = pd.concat(dataframes, ignore_index=True).sort_values("Country_Code").reset_index(drop=True)


#--------------------------------------------------------------------------------------------
# 4. Organize data
#--------------------------------------------------------------------------------------------

    selected_columns = [
        "Country",
        "Country_Code",
        "Product_Name",
        "Product_Code",
        "Year",
        "Trade Value 1000USD"
    ]

    df_devices = df_devices[selected_columns]


# ------------------------------------------------------------------------------
# 5. Create dynamic year coefficients and weighted product indices
# ------------------------------------------------------------------------------

# 5.1 Dynamic coefficient by year (based on the current year)
    current_year = pd.Timestamp.today().year

# Calculation of the coefficient based on the time lag relative to the last available year.
# Formula: coef = 1 - 0.02 * (current_year - Year)
    df_devices["Coefficient_Year"] = 1 - 0.02 * (current_year - df_devices["Year"])

# Avoid negative values if a user extends decades into the past.
    df_devices["Coefficient_Year"] = df_devices["Coefficient_Year"].clip(lower=0)


# 5.2 Normalize trade values within each Country-Product group
# Thus, each product is evaluated within its own country in a comparable manner
    df_devices["Standardized_Trade"] = (
    df_devices
    .groupby(["Country", "Product_Code"])["Trade Value 1000USD"]
    .transform(lambda x: x / x.max() if x.max() != 0 else 0)
    )

# 5.3 Calculate the annual product index
    df_devices["Annual_Product_Index"] = (
    df_devices["Standardized_Trade"] *
    df_devices["Coefficient_Year"]
    )

# 5.4 Calculate the Global Product Index by summing
# the Annual Product Index across all available years
# for each Country-Product combination.
    df_sum_product = (
    df_devices
    .groupby(["Country", "Country_Code", "Product_Name", "Product_Code"])
    .agg(Global_Product_Index=("Annual_Product_Index", "sum"))
    .reset_index()
    )

# 5.5 Merge the Global Product Index with the original dataset
# to keep both the annual and global indices
    df_product_index = df_devices.merge(
    df_sum_product,
    on=["Country", "Country_Code", "Product_Name", "Product_Code"],
    how="left"
    )


# -------------------------------------------------------------
# 6. Final result
# -------------------------------------------------------------
    #print("\n=== TOTAL INDEX DATA BY COUNTRY AND PRODUUCT  ===")
    #print(df_product_index.head(20))


    return df_product_index

