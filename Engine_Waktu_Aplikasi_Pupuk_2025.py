# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # **ENGINE WAKTU APLIKASI PUPUK 2025**
# 
# ## Refactored Code Structure

# %% [markdown]
# ## 1. Imports and Setup

# %%
# Standard Libraries
import sys
import os
from datetime import datetime, timedelta
import datetime as dt
import subprocess
import traceback # For detailed error printing

# Third-Party Libraries
import pandas as pd
import pytz # pip install pytz
import gspread # pip install gspread
from oauth2client.service_account import ServiceAccountCredentials # pip install oauth2client
# from google.oauth2.service_account import Credentials # Alternative auth

# GUI Libraries
import tkinter as tk
from tkinter import ttk, messagebox, StringVar
from tkcalendar import Calendar # pip install tkcalendar


# %% [markdown]
# ## 2. Configuration and Constants

# %%
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- Authentication ---
JSON_PATH = resource_path('fourth-landing-316602-e06c4c4e3ba6.json') # Make sure file exists
SHEET_URL = "https://docs.google.com/spreadsheets/d/1f9taqCGKFtFVDmNIWFgqujf8yJLmshCFJ7j4_CgGl2Q/edit?usp=sharing"
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# --- Fertilizer Data ---
FERTILIZER_GROUPS = {
    "NPK": ["NPK 13", "NPK 15", "NPK 12"],
    "Dolomite": ["Dolomite"],
    "Urea": ["Urea"],
    "MOP": ["MOP"],
    "HGFB": ["HGFB"],
    "CuSO4": ["CuSO4"],
    "Zincop": ["Zincop Chelated"],
    "Kieserite": ["Kieserite"],
    "RP": ["RP"],
    "Kaptan": ["Kaptan"],
    "TSP": ["TSP"]
}

SYNERGIZE_GROUPS = { # Note: This dictionary seems less used in the provided core analysis logic
    "NPK": ["Urea", "Kieserite", "MOP"],
    "Urea": ["NPK", "Kieserite", "MOP"],
    "RP": ["Kieserite", "Dolomite"],
    "Kieserite": ["NPK", "Urea", "RP"],
    "Dolomite": ["Kaptan", "RP"],
    "MOP": ["NPK", "Urea"],
    "HGFB": ["Zincop Chelated", "CuSO4"],
    "Zincop": ["HGFB", "CuSO4"],
    "CuSO4": ["HGFB", "Zincop"],
    "Kaptan": ["Dolomite"],
}

SUPER_SLOW = {
    "Dolomite": ["Dolomite"]
}

HYGROSCOPIC = {
    "Urea": ["Urea"],
    "HGFB": ["HGFB"],
    "CuSO4": ["CuSO4"],
    "MOP": ["MOP"]
}

ESTATE_OPTIONS = ["Inti", "Plasma"] # Use constant for options

INTERVAL_TABLE = {
    "NPK": {"NPK": 60, "Urea": 14, "RP": 30, "TSP": 30, "Kieserite": 14, "Dolomite": 30, "MOP": 14, "HGFB": 30, "Zincop": 30},
    "Urea": {"NPK": 14, "Urea": 60, "RP": 30, "TSP": 30, "Kieserite": 14, "Dolomite": 30, "MOP": 14, "HGFB": 30, "Zincop": 30},
    "RP": {"NPK": 30, "Urea": 30, "RP": 60, "TSP": 60, "Kieserite": 14, "Dolomite": 14, "MOP": 30, "HGFB": 30, "Zincop": 30},
    "TSP": {"NPK": 30, "Urea": 30, "RP": None, "TSP": 30, "Kieserite": 30, "Dolomite": 30, "MOP": 30, "HGFB": 30, "Zincop": 30},
    "Kieserite": {"NPK": 14, "Urea": 14, "RP": 14, "TSP": 30, "Kieserite": 60, "Dolomite": 60, "MOP": 30, "HGFB": 14, "Zincop": 30},
    "Dolomite": {"NPK": 30, "Urea": 30, "RP": 14, "TSP": 30, "Kieserite": None, "Dolomite": 30, "MOP": 30, "HGFB": 30, "Zincop": 30},
    "MOP": {"NPK": 14, "Urea": 14, "RP": 30, "TSP": 30, "Kieserite": 30, "Dolomite": 30, "MOP": 60, "HGFB": 30, "Zincop": 30},
    "HGFB": {"NPK": 30, "Urea": 30, "RP": 30, "TSP": 30, "Kieserite": 14, "Dolomite": 30, "MOP": 30, "HGFB": 60, "Zincop": 14},
    "Zincop": {"NPK": 30, "Urea": 30, "RP": 30, "TSP": 30, "Kieserite": 30, "Dolomite": 30, "MOP": 30, "HGFB": 14, "Zincop": 60},
}

FERTILIZER_TYPE = ["NPK 13", "NPK 15", "NPK 12", "Dolomite", "Urea", "MOP", "HGFB", "CuSO4", "Zincop Chelated", "Kieserite", "RP", "Kaptan", "TSP"]

# --- Styling and Misc ---
BORDER_LINE = "=" * 80
PRIMARY_BUTTON_COLOR = "#4CAF50"  # Green
SECONDARY_BUTTON_COLOR = "#2196F3"  # Blue
MAIN_MENU_BUTTON_COLOR = "#f44336"  # Red
EXIT_BUTTON_COLOR = "#f44336" # Red
TEXT_COLOR = "#000000" # Black
BUTTON_TEXT_COLOR = "#ffffff"  # White

# --- Timezone ---
CURRENT_TIMEZONE = pytz.timezone('Asia/Jakarta') # Or your preferred timezone

# %% [markdown]
# ## 3. Global Variables (Application State)

# %%
# --- Core App State ---
root = None
previous_menu = None
root_exists = False
current_menu = None
df = pd.DataFrame() # In-memory data store
current_time_date = datetime.now(CURRENT_TIMEZONE) # Store initial time
formatted_today = format_datetime(current_time_date)

# --- User State ---
username_var = None # Will be StringVar, created in main_process
username = ""     # Will store the string username

# --- Google Sheets Objects ---
sheet_data = None   # DB sheet object
sheet_output = None # Output sheet object

# --- GUI State ---
success_window = None
missing_dates_widgets = {}

# --- Widget References (Initialized to None in main_process) ---
# These are numerous, keeping them listed in main_process might be okay for now,
# but consider a class structure for larger apps.
# (List of widget variables like label_username, entry_username, etc.)

# %% [markdown]
# ## 4. Utility Functions

# %%
def format_datetime(dt):
    """Formats a datetime or date object to 'dd/mm/yyyy'."""
    if isinstance(dt, (datetime, dt.date)):
        return dt.strftime('%d/%m/%Y')
    return '' # Return empty if not a date/datetime

def format_datetimehour(dt):
    """Formats a datetime object to 'dd/mm/yyyy HH:MM:SS'."""
    if isinstance(dt, datetime):
        return dt.strftime('%d/%m/%Y %H:%M:%S')
    return '' # Return empty if not a datetime

def _on_mousewheel(event, canvas):
    """Handles mouse wheel scrolling on the canvas."""
    # Determine scroll direction and amount based on platform
    if event.num == 4:  # Linux scroll up
        canvas.yview_scroll(-1, "units")
    elif event.num == 5:  # Linux scroll down
        canvas.yview_scroll(1, "units")
    else:  # Windows/macOS scroll
        # Adjust scrolling speed if necessary
        scroll_factor = 1 if sys.platform == 'darwin' else 120 # macOS needs smaller delta factor
        canvas.yview_scroll(int(-1*(event.delta/scroll_factor)), "units")

def set_username():
    """Updates the global username string from the StringVar."""
    global username
    if username_var: # Check if StringVar exists
        username = username_var.get()

def get_fertilizer_group(fertilizer):
    """Finds the group a given fertilizer belongs to."""
    for group, types in FERTILIZER_GROUPS.items():
        if fertilizer in types:
            return group
    return None # Return None if not found

# %% [markdown]
# ## 5. Google Sheets Interaction

# %%
def load_database(sheet_url, json_path):
    """Loads data from the Google Sheet 'DB' worksheet into a Pandas DataFrame."""
    global sheet_data, sheet_output # Keep sheet objects global for calculation/output functions
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(json_path, SCOPE)
        client = gspread.authorize(creds)
        sheet_data = client.open_by_url(sheet_url).worksheet("DB")
        sheet_output = client.open_by_url(sheet_url).worksheet("Output") # Get output sheet handle too
        data = sheet_data.get_all_records()
        df_loaded = pd.DataFrame(data)

        # Data type conversions and cleaning
        if 'Date' in df_loaded.columns:
            df_loaded['Date'] = pd.to_datetime(df_loaded['Date'], format='%d/%m/%Y', errors='coerce')
            df_loaded.dropna(subset=['Date'], inplace=True)
        else:
             messagebox.showerror("Data Error", "Kolom 'Date' tidak ditemukan di spreadsheet.")
             return pd.DataFrame()

        if 'Daily Rainfall (mm)' in df_loaded.columns:
            df_loaded['Daily Rainfall (mm)'] = pd.to_numeric(df_loaded['Daily Rainfall (mm)'], errors='coerce')
            # Optionally handle NaNs in rainfall here (e.g., fillna(0) or dropna())
            # df_loaded['Daily Rainfall (mm)'].fillna(0, inplace=True)
        else:
            messagebox.showerror("Data Error", "Kolom 'Daily Rainfall (mm)' tidak ditemukan di spreadsheet.")
            return pd.DataFrame()

        # Ensure all calculation columns exist, add them with default NaN or 0 if not
        calc_columns = ['Accumulation Rainfall -29 days', 'Evapotranspiration',
                        'Water Balance', 'Soil Water Reserve (mm)', 'Water Surplus']
        for col in calc_columns:
            if col not in df_loaded.columns:
                df_loaded[col] = pd.NA # Or 0 if preferred

        # Convert calculation columns to numeric, coercing errors
        for col in calc_columns:
             df_loaded[col] = pd.to_numeric(df_loaded[col], errors='coerce')


        return df_loaded.sort_values(by='Date').reset_index(drop=True) # Ensure data is sorted

    except gspread.exceptions.SpreadsheetNotFound:
        messagebox.showerror("Connection Error", f"Spreadsheet tidak ditemukan: {sheet_url}")
        return pd.DataFrame()
    except gspread.exceptions.APIError as e:
        messagebox.showerror("Connection Error", f"Kesalahan API Google Sheets: {e}")
        return pd.DataFrame()
    except Exception as e:
        messagebox.showerror("Error", f"Kesalahan saat memuat data: {e}")
        print(f"An unexpected error occurred loading data: {e}")
        traceback.print_exc() # Print full traceback for debugging
        return pd.DataFrame()

def append_to_spreadsheet(date_input, username, estate_name, blok_name, current_daily_rainfall, peilscale, last_fertilizer, last_fertilizer_date, next_fertilizer, next_fertilizer_date, reason, recommendation):
    """Appends analysis results to the 'Output' Google Sheet."""
    global sheet_output

    if sheet_output is None:
        messagebox.showerror("Error", "Koneksi ke sheet Output belum siap.")
        return "Error"

    status = "Allowed" if not reason else "Not Allowed"

    try:
        output_data = [
            date_input.strftime('%Y-%m-%d %H:%M:%S'), username, estate_name,
            blok_name, current_daily_rainfall, peilscale, last_fertilizer,
            last_fertilizer_date.strftime("%Y-%m-%d") if isinstance(last_fertilizer_date, (datetime, dt.date)) else "", # Handle potential invalid date
            next_fertilizer,
            next_fertilizer_date.strftime("%Y-%m-%d") if isinstance(next_fertilizer_date, (datetime, dt.date)) else "", # Handle potential invalid date
            status, reason, recommendation
        ]
        sheet_output.append_row(output_data)
        print("Analysis results appended to spreadsheet.")
        return status
    except Exception as e:
         messagebox.showerror("Error", f"Gagal menyimpan hasil ke spreadsheet: {e}")
         print(f"Error appending to spreadsheet: {e}")
         return "Error"

# NOTE: The remove_old_data function interacts directly with the sheet by row number.
# This can be brittle if the sheet structure changes or rows are manually deleted/inserted.
# Consider using gspread's batch_update or finding rows by criteria before deleting if needed.
def remove_old_data(df, date_to_remove, estate_name):
    """Removes data for a specific date and estate from DataFrame and Spreadsheet."""
    global sheet_data
    if sheet_data is None: return df # Cannot modify sheet if not connected

    try:
        date_to_remove_dt = pd.to_datetime(date_to_remove).normalize() # Ensure consistent datetime for comparison
        date_str_format = date_to_remove_dt.strftime('%d/%m/%Y') # Format for finding in sheet

        # Remove from DataFrame
        original_len = len(df)
        indices_to_drop = df[(df['Estate'] == estate_name) & (df['Date'] == date_to_remove_dt)].index
        if not indices_to_drop.empty:
            df.drop(indices_to_drop, inplace=True)
            print(f"Removed {len(indices_to_drop)} row(s) from DataFrame for {estate_name} on {date_str_format}")
        else:
             print(f"No matching row found in DataFrame for {estate_name} on {date_str_format}")


        # Remove from spreadsheet (find all matching rows and delete)
        # Use findall to get all matching cells for the date in the first column
        cells = sheet_data.findall(date_str_format, in_column=1)
        rows_to_delete_sheet = []
        if cells:
            for cell in cells:
                row_data = sheet_data.row_values(cell.row)
                # Check if the estate in that row also matches
                if len(row_data) > 1 and row_data[1] == estate_name: # Assuming Estate is in column 2 (index 1)
                    rows_to_delete_sheet.append(cell.row)

        if rows_to_delete_sheet:
            # Sort rows in descending order to avoid index shifting issues during deletion
            rows_to_delete_sheet.sort(reverse=True)
            for row_num in rows_to_delete_sheet:
                 try:
                     sheet_data.delete_rows(row_num)
                     print(f"Deleted row {row_num} from spreadsheet for {estate_name} on {date_str_format}")
                 except Exception as delete_err:
                     print(f"Error deleting row {row_num} from spreadsheet: {delete_err}")
                     # Decide if you want to stop or continue if a deletion fails
                     # return df # Example: Stop if deletion fails

        else:
            print(f"Data for {date_str_format} and estate {estate_name} not found in spreadsheet for deletion.")

        return df.reset_index(drop=True) # Reset index after dropping rows

    except Exception as e:
        messagebox.showerror("Error", f"Gagal menghapus data lama: {e}")
        print(f"Error in remove_old_data: {e}")
        return df # Return original df on error


# %% [markdown]
# ## 6. Core Logic - Rainfall & Water Balance

# %%
# Note: Reworked calculate_rainfall for robustness
def calculate_rainfall(df_original, calc_date, daily_rainfall, estate_name):
    """
    Calculates rainfall metrics for a specific date and estate,
    appends to the sheet, and returns the UPDATED ORIGINAL DataFrame.
    """
    global sheet_data
    if sheet_data is None: return df_original # Cannot modify sheet if not connected

    try:
        # Ensure calc_date is a date object
        if isinstance(calc_date, (datetime, pd.Timestamp)):
            calc_date = calc_date.date()
        elif not isinstance(calc_date, dt.date):
            raise ValueError("calc_date must be a date or datetime object")

        # Ensure rainfall is a valid number
        daily_rainfall = float(daily_rainfall)
        if daily_rainfall < 0: raise ValueError("Rainfall cannot be negative")

        # Create a working copy to avoid modifying the original df directly during checks
        df_temp = df_original.copy()
        # Ensure Date column is datetime
        if not pd.api.types.is_datetime64_any_dtype(df_temp['Date']):
            df_temp['Date'] = pd.to_datetime(df_temp['Date'], errors='coerce')

        # Filter for the estate and sort by date
        estate_df_temp = df_temp[df_temp['Estate'] == estate_name].sort_values(by='Date').reset_index()

        # Find the row for the day *before* calc_date
        prev_day_date = calc_date - timedelta(days=1)
        prev_day_row = estate_df_temp[estate_df_temp['Date'].dt.date == prev_day_date]

        previous_soil_water_reserve = 0
        if not prev_day_row.empty:
            # Ensure the column exists and value is numeric, handle NaN
            if 'Soil Water Reserve (mm)' in prev_day_row.columns:
                 prev_swr_val = pd.to_numeric(prev_day_row['Soil Water Reserve (mm)'].iloc[0], errors='coerce')
                 previous_soil_water_reserve = prev_swr_val if pd.notna(prev_swr_val) else 0
            else:
                 print(f"Warning: Column 'Soil Water Reserve (mm)' not found for {prev_day_date}")

        # Get rainfall data for accumulation calculation (up to *and including* the current calc_date)
        # Create temporary entry for current day to include its rainfall
        temp_current_row = pd.DataFrame([{'Date': pd.Timestamp(calc_date), 'Daily Rainfall (mm)': daily_rainfall}])
        relevant_rainfall_df = pd.concat([estate_df_temp[['Date', 'Daily Rainfall (mm)']], temp_current_row], ignore_index=True)
        relevant_rainfall_df['Date'] = pd.to_datetime(relevant_rainfall_df['Date']) # Ensure datetime
        relevant_rainfall_df = relevant_rainfall_df.sort_values(by='Date')

        # Calculate accumulation over the window ending on calc_date
        start_window = pd.Timestamp(calc_date) - timedelta(days=29)
        accumulation_rainfall = relevant_rainfall_df[
            (relevant_rainfall_df['Date'] >= start_window) &
            (relevant_rainfall_df['Date'] <= pd.Timestamp(calc_date))
        ]['Daily Rainfall (mm)'].sum()

        # Evapotranspiration
        # Count days within the last 29 days *before* today from the historical data
        days_in_window = len(estate_df_temp[estate_df_temp['Date'] >= start_window])
        evapotranspiration = (120 if days_in_window > 10 else 150) / 30

        # Water Balance
        water_balance = previous_soil_water_reserve + daily_rainfall - evapotranspiration

        # Soil Water Reserve
        soil_water_reserve = min(water_balance, 200)

        # Water Surplus
        water_surplus = max(0, water_balance - 200)

        # --- Data to Append/Insert ---
        date_str = calc_date.strftime('%d/%m/%Y') # Format for sheet
        new_row_values = [
            date_str, estate_name, daily_rainfall, accumulation_rainfall,
            evapotranspiration, water_balance, soil_water_reserve, water_surplus
        ]
        new_row_dict = {
            'Date': pd.Timestamp(calc_date), # Use Timestamp for DataFrame consistency
            'Estate': estate_name,
            'Daily Rainfall (mm)': daily_rainfall,
            'Accumulation Rainfall -29 days': accumulation_rainfall,
            'Evapotranspiration': evapotranspiration,
            'Water Balance': water_balance,
            'Soil Water Reserve (mm)': soil_water_reserve,
            'Water Surplus': water_surplus
        }

        # Append to Google Sheet
        sheet_data.append_row(new_row_values)

        # Append to the original DataFrame and return it
        df_updated = pd.concat([df_original, pd.DataFrame([new_row_dict])], ignore_index=True)
        # Keep df sorted by date after adding
        df_updated = df_updated.sort_values(by='Date').reset_index(drop=True)
        return df_updated

    except Exception as e:
        messagebox.showerror("Error", f"Gagal menghitung data hujan untuk {format_datetime(calc_date)}: {e}")
        print(f"Error in calculate_rainfall for {format_datetime(calc_date)}: {e}")
        traceback.print_exc()
        return df_original # Return original df on error

# %% [markdown]
# ## 7. Core Logic - Fertilizer Rules & Validation

# %%
# (Keep functions: check_groundwater, check_peilscale, check_season,
#  check_rain_in_dry_seasion, validate_water_track, get_minimal_interval,
#  get_alternative_fertilizer, get_all_recommendation, validate_interval_fertilizer,
#  get_fertilizer_group, validate_dry_week, validate_dolomite, analyze_fertilizer)
# Ensure analyze_fertilizer uses the updated arguments if necessary and that
# date objects (not strings) are passed where expected.

# Example: Minor correction in analyze_fertilizer if needed
# Make sure last_fertilizer_date and next_fertilizer_date are datetime objects
# when calling validate_interval_fertilizer, get_alternative_fertilizer, etc.

# %% [markdown]
# ## 8. GUI - Utility Functions

# %%
def configure_bg(color):
    """Sets the background color of the root window."""
    # Simplified: Only set root background. Widgets keep default or specific colors.
    if not root_exists:
        return
    root.configure(bg=color)

def get_date(entry_widget):
    """Creates a calendar popup and inserts the selected date (yyyy-mm-dd) into the entry widget."""
    if not root_exists: return

    def set_date():
        if not root_exists: return
        selected_date = cal.get_date() # This is "yyyy-mm-dd" from tkcalendar
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, selected_date)
        top.destroy()

    top = tk.Toplevel(root)
    today = datetime.now(CURRENT_TIMEZONE) # Use global timezone
    cal = Calendar(top, font="Arial 10", selectmode='day',
                   year=today.year, month=today.month, day=today.day,
                   date_pattern="yyyy-mm-dd") # Keep this pattern for consistency
    cal.pack(pady=20)
    confirm_button = tk.Button(top, text="OK", command=set_date)
    confirm_button.pack(pady=10)
    top.transient(root)
    top.grab_set()
    top.wait_window(top)

def hide_all_widgets():
    """Hides ALL widgets gridded directly onto the root window."""
    if not root_exists: return
    # Be more specific: Hide only widgets placed with grid on root
    for widget in root.grid_slaves():
         widget.grid_forget()
    # Also forget frames that might contain other widgets if needed
    # Example: if outer_frame exists and is a direct child
    # try:
    #     if 'outer_frame' in globals() and outer_frame:
    #         outer_frame.grid_forget()
    # except NameError: pass # If outer_frame was never created

def hide_rainfall_data_entry_widgets(): # Make sure this is defined
    """Hides the widgets specifically for the rainfall data entry/update screen."""
    global label_update_rainfall, entry_update_rainfall, submit_update_rainfall_button, back_button, main_menu_button, label_no_data

    if not root_exists: return

    widgets_to_hide = [
        label_update_rainfall, entry_update_rainfall, submit_update_rainfall_button,
        back_button, main_menu_button, label_no_data # Include label_no_data
    ]
    for widget in widgets_to_hide:
        try:
            if widget: widget.grid_forget()
        except (AttributeError, NameError, tk.TclError): # Catch potential errors if widget doesn't exist or is destroyed
            pass

# Removed hide_estate_widgets as it seems redundant with hide_all_widgets strategy

# %% [markdown]
# ## 9. GUI - Screen Creation Functions

# %%
def create_main_widgets():
    global label_username, entry_username, previous_menu, current_menu, back_button, exit_button, button_input_hujan, button_analisa_pemupukan, username_var, label_saved_username, username, df # Add df

    if not root_exists: return
    root.geometry("500x400")
    current_menu = "main"
    configure_bg("#f0f0f0") # Default background

    # --- ROW & COLUMN CONFIGURATION RESET ---
    for i in range(20): root.rowconfigure(i, weight=0)
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=0)
    # --- END CONFIGURATION ---

    # Update the dataframe every time user access the main menu
    df = load_database(SHEET_URL, JSON_PATH) # Use constants
    if df.empty:
        messagebox.showerror("Error", "Gagal memuat data dari spreadsheet...")
        root.destroy()
        return

    # --- Username Section ---
    row_offset = 0 # Start widgets at row 0
    if not username:
        label_username = tk.Label(root, text="Masukkan Username:", font=("Arial", 12))
        label_username.grid(row=row_offset, column=0, padx=10, pady=10, sticky="ew")
        row_offset += 1
        entry_username = tk.Entry(root, font=("Arial", 10), textvariable=username_var)
        entry_username.grid(row=row_offset, column=0, padx=10, pady=10, sticky="ew")
        row_offset += 1
        # Setup trace *only if* entry is created
        if not username_var.trace_info(): # Check if trace exists
             username_var.trace_add("write", lambda *args: set_username())
    else:
        label_saved_username = tk.Label(root, text=f"Masuk ke sistem sebagai: {username}", font=("Arial", 12))
        label_saved_username.grid(row=row_offset, column=0, padx=10, pady=10, sticky="ew")
        row_offset += 2 # Skip the row where entry would have been

    # --- Buttons ---
    button_input_hujan = tk.Button(root, text="Masukkan Data Hujan", command=goto_input_hujan, font=("Arial", 12), bg=PRIMARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)
    button_input_hujan.grid(row=row_offset, column=0, padx=10, pady=10, sticky="ew")
    row_offset += 1

    button_analisa_pemupukan = tk.Button(root, text="Analisa Pemupukan", command=goto_analisa_pemupukan, font=("Arial", 12), bg=PRIMARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)
    button_analisa_pemupukan.grid(row=row_offset, column=0, padx=10, pady=10, sticky="ew")
    row_offset += 1

    # Add some space before exit button
    root.rowconfigure(row_offset, weight=1) # Add flexible space before exit
    row_offset += 1

    exit_button = tk.Button(root, text="Exit", command=on_closing, font=("Arial", 10), bg=EXIT_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)
    exit_button.grid(row=row_offset, column=0, padx=10, pady=10)

    previous_menu = None
    back_button = None

# (Add the ROW/COLUMN reset block to the start of ALL other show_ functions)
# Example for show_rainfall_options:
def show_rainfall_options():
    global label_rainfall_option, back_button, current_menu, button_update_rainfall, button_add_rainfall, previous_menu

    if not root_exists: return

    # --- ROW & COLUMN CONFIGURATION RESET ---
    for i in range(20): root.rowconfigure(i, weight=0)
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=0)
    # --- END CONFIGURATION ---

    hide_all_widgets()
    current_menu = "rainfall"
    previous_menu = "main"
    configure_bg("#f0f0f0") # Use default bg

    label_rainfall_option = tk.Label(root, text="Pilih Opsi Untuk Data Hujan:", font=("Arial", 12))
    label_rainfall_option.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
    # ... rest of widgets with colors ...
    button_update_rainfall = tk.Button(root, text="Update Data Hujan Terakhir", command=goto_update_rainfall, font=("Arial", 10), bg=PRIMARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)
    button_update_rainfall.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
    button_add_rainfall = tk.Button(root, text="Masukkan Data Hujan Baru", command=goto_add_rainfall, font=("Arial", 10), bg=PRIMARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)
    button_add_rainfall.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
    back_button = tk.Button(root, text="Back", command=go_back, font=("Arial", 10), bg=SECONDARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)
    back_button.grid(row=3, column=0, padx=10, pady=10)

# Apply reset to show_estate_options, show_estate_options_for_add_rainfall,
# show_add_rainfall_entry, show_rainfall_data_entry, show_estate_options_for_analysis,
# display_analysis_results, show_missing_dates_input (it already does it)

# Modify show_missing_dates_input slightly for clarity
def show_missing_dates_input(selected_estate, missing_dates_list):
    global missing_dates_widgets, label_missing_dates_title, submit_missing_dates_button, \
           back_button, main_menu_button, previous_menu, current_menu, \
           canvas, scrollbar, inner_frame

    if not root_exists: return

    hide_all_widgets()
    current_menu = "missing_dates_input"
    previous_menu = "estate_add_rainfall"
    configure_bg("#f0f0f0") # Use default bg

    # --- ROW & COLUMN RESET for ROOT ---
    for i in range(20): root.rowconfigure(i, weight=0)
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=0)
    # --- END ROOT RESET ---

    # --- Title (On Root) ---
    label_missing_dates_title = tk.Label(root, text=f"Masukkan data hujan untuk tanggal yang hilang ({selected_estate}):", font=("Arial", 12, "bold"))
    label_missing_dates_title.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")

    # --- Create Scrollable Area (On Root) ---
    outer_frame = tk.Frame(root)
    outer_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
    outer_frame.grid_rowconfigure(0, weight=1)
    outer_frame.grid_columnconfigure(0, weight=1)

    canvas = tk.Canvas(outer_frame)
    canvas.grid(row=0, column=0, sticky="nsew")
    scrollbar = ttk.Scrollbar(outer_frame, orient="vertical", command=canvas.yview)
    scrollbar.grid(row=0, column=1, sticky="ns")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    inner_frame = tk.Frame(canvas) # Frame INSIDE canvas
    canvas.create_window((0, 0), window=inner_frame, anchor="nw")

    # --- Bind Mouse Wheel ---
    # ... (keep mouse wheel bindings) ...

    # --- Populate Inner Frame ---
    missing_dates_widgets = {}
    row_num = 0
    for date in missing_dates_list:
        # ... (create label and entry INSIDE inner_frame) ...
        label = tk.Label(inner_frame, text=f"Tanggal {format_datetime(date.date())} (mm):", font=("Arial", 10))
        label.grid(row=row_num, column=0, padx=5, pady=2, sticky="w")
        entry = tk.Entry(inner_frame, font=("Arial", 10))
        entry.grid(row=row_num, column=1, padx=5, pady=2, sticky="ew")
        missing_dates_widgets[date.date()] = {"label": label, "entry": entry}
        row_num += 1
    inner_frame.columnconfigure(1, weight=1)

    # --- Buttons (On Root) ---
    button_row = 2
    submit_missing_dates_button = tk.Button(root, text="Submit Data Hilang", command=lambda: submit_missing_dates(selected_estate, missing_dates_list), font=("Arial", 10), bg=PRIMARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)
    submit_missing_dates_button.grid(row=button_row, column=0, padx=10, pady=10)
    button_row += 1
    back_button = tk.Button(root, text="Back", command=go_back, font=("Arial", 10), bg=SECONDARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)
    back_button.grid(row=button_row, column=0, padx=10, pady=5)
    button_row += 1
    main_menu_button = tk.Button(root, text="Back to Main Menu", command=back_to_main, font=("Arial", 10), bg=MAIN_MENU_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)
    main_menu_button.grid(row=button_row, column=0, padx=10, pady=5)

    # --- Configure Root Window Rows for Resizing ---
    root.grid_rowconfigure(0, weight=0)  # Title row
    root.grid_rowconfigure(1, weight=1)  # Scrollable area row
    root.grid_rowconfigure(button_row, weight=0) # Last button row

# --- (Ensure the reset block is added to show_estate_options, show_add_rainfall_entry, etc.) ---

# %% [markdown]
# ## 10. GUI - Navigation & Action Functions

# %%
# (Keep functions: goto_update_rainfall, goto_add_rainfall, submit_estate,
#  submit_estate_for_analysis, submit_analysis, go_to_reanalyze, back_to_main,
#  go_back, check_existing_rainfall, submit_estate_for_add_rainfall,
#  submit_update_rainfall, show_success_window, close_success_and_go_back,
#  submit_missing_dates)

# Make corrections to submit_analysis date handling:
def submit_analysis(selected_estate, blok, peilscale,
                    jenis_pupuk_terakhir, tanggal_pupuk_terakhir_str, # Renamed for clarity
                    rencana_jenis_pupuk, tanggal_rencana_pupuk_str): # Renamed for clarity
    global df, current_time_date, username_var # Added username_var

    if not root_exists: return

    # --- Basic Input Validation ---
    # (Keep all the initial checks for empty strings, valid estate etc.)
    if not selected_estate: messagebox.showerror("Error", "Tolong masukkan nama estate."); return
    if selected_estate not in ESTATE_OPTIONS: messagebox.showerror("Error", f"Nama estate invalid: '{selected_estate}'."); return
    if not blok: messagebox.showerror("Error", "Tolong masukkan nama blok."); return
    if not tanggal_rencana_pupuk_str: messagebox.showerror("Error", "Tolong masukkan tanggal rencana pupuk."); return
    if not peilscale: messagebox.showerror("Error", "Masukkan nilai peilscale."); return
    if not tanggal_pupuk_terakhir_str: messagebox.showerror("Error", "Tolong masukkan tanggal pupuk terakhir."); return
    if not jenis_pupuk_terakhir: messagebox.showerror("Error", "Tolong masukkan jenis pupuk terakhir."); return
    if not rencana_jenis_pupuk: messagebox.showerror("Error", "Tolong masukkan rencana jenis pupuk."); return

    # --- Type/Format Validation ---
    try:
        # Use %Y-%m-%d as returned by tkcalendar's get_date()
        tanggal_rencana_pupuk_dt = datetime.strptime(tanggal_rencana_pupuk_str, "%Y-%m-%d")
        tanggal_pupuk_terakhir_dt = datetime.strptime(tanggal_pupuk_terakhir_str, "%Y-%m-%d")
    except ValueError:
        # Try the other format just in case user typed it manually
        try:
             tanggal_rencana_pupuk_dt = datetime.strptime(tanggal_rencana_pupuk_str, "%d/%m/%Y")
             tanggal_pupuk_terakhir_dt = datetime.strptime(tanggal_pupuk_terakhir_str, "%d/%m/%Y")
             # If manual format is okay, maybe warn user about preferred format?
        except ValueError:
             messagebox.showerror("Error", "Format tanggal tidak valid. Gunakan kalender atau format YYYY-MM-DD.")
             return

    try:
        peilscale_int = int(peilscale) # Keep original peilscale string for display if needed
    except ValueError:
        messagebox.showerror("Error", "Nilai peilscale harus berupa angka integer.")
        return

    # --- Username Check ---
    username = username_var.get()
    if not username.strip():
        messagebox.showerror("Error", "Tolong masukkan username di dalam main menu.")
        return

    # --- Rainfall Data Validation ---
    if not validate_rainfall_data_exists(selected_estate):
        return # Exit if rainfall validation fails

    # --- Proceed with analysis ---
    current_daily_rainfall, status, reason, recommendation = analyze_fertilizer(
        datetime.now(CURRENT_TIMEZONE), username, selected_estate, blok, df,
        peilscale_int, jenis_pupuk_terakhir, tanggal_pupuk_terakhir_dt, # Pass datetime object
        rencana_jenis_pupuk, tanggal_rencana_pupuk_dt # Pass datetime object
    )

    # Display the results - Pass strings for display as they were entered/selected
    display_analysis_results(
        selected_estate, blok, tanggal_rencana_pupuk_str, peilscale, # Pass original peilscale string
        tanggal_pupuk_terakhir_str, jenis_pupuk_terakhir, rencana_jenis_pupuk,
        username, current_daily_rainfall, status, reason, recommendation
    )


# %% [markdown]
# ## 11. GUI - Window Management

# %%
def on_closing():
    global root_exists
    root_exists = False
    disable_buttons()
    if root: # Check if root exists before destroying
       root.destroy()

def disable_buttons():
    """Disables all interactive buttons to prevent further events."""
    # Keep this function as is, it's robust.
    # ... (Your existing disable_buttons code) ...

# %% [markdown]
# ## 12. Main Application (`main_process`)

# %%
def main_process():
    # Define all globals used within this function and others it calls
    global root, previous_menu, root_exists, current_menu, df, \
           username_var, username, \
           sheet_data, sheet_output, \
           label_username, entry_username, exit_button, label_rainfall_option, \
           button_update_rainfall, button_add_rainfall, back_button, \
           label_estate_option, combobox_estate, submit_estate_button, \
           main_menu_button, submit_estate_check_button, \
           label_missing_dates_title, missing_dates_widgets, submit_missing_dates_button, \
           canvas, scrollbar, inner_frame, \
           label_daily_rainfall, entry_daily_rainfall, submit_add_rainfall_button, \
           label_update_rainfall, entry_update_rainfall, submit_update_rainfall_button, \
           entry_blok, entry_tanggal_rencana_pupuk, entry_peilscale, entry_tanggal_pupuk_terakhir, \
           combobox_jenis_pupuk_terakhir, combobox_rencana_jenis_pupuk, \
           label_blok, label_tanggal_rencana_pupuk, label_peilscale, label_tanggal_pupuk_terakhir, \
           label_jenis_pupuk_terakhir, label_rencana_jenis_pupuk, \
           button_tanggal_rencana_pupuk, button_tanggal_pupuk_terakhir, \
           label_tanggal_analisa, label_nama_user, label_curah_hujan, \
           label_status, label_reason, label_recommendation, label_selected_estate, \
           label_nama_blok, label_tanggal_rencana, label_peilscale_value, \
           label_tanggal_terakhir_value, label_jenis_terakhir_value, \
           label_rencana_jenis_value, back_to_main_button, reanalyze_button, \
           label_saved_username, label_no_data # Added label_no_data


    # --- Initialize App ---
    root = tk.Tk()
    root.title("Fertilizer Analysis")
    root.state('zoomed')

    # --- Initialize State Variables ---
    username_var = StringVar()
    username = ""
    previous_menu = None
    root_exists = True
    current_menu = None
    df = pd.DataFrame()
    missing_dates_widgets = {} # Ensure this is initialized

    # --- Initialize Widget References (Good Practice) ---
    # (Keep the list of widget=None assignments here)
    label_username = None; entry_username = None; exit_button = None; # etc...
    label_saved_username = None; label_missing_dates_title = None; submit_missing_dates_button = None;
    canvas = None; scrollbar = None; inner_frame = None; label_no_data = None;

    # --- Connect to Google Sheets ---
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(JSON_PATH, SCOPE)
        client = gspread.authorize(creds)
        sheet_data = client.open_by_url(SHEET_URL).worksheet("DB")
        sheet_output = client.open_by_url(SHEET_URL).worksheet("Output")
        print("Successfully connected to Google Sheets.")
    except Exception as e:
        messagebox.showerror("Startup Error", f"Gagal terhubung ke Google Sheets: {e}")
        root.destroy()
        return

    # --- Load Initial Data ---
    df = load_database(SHEET_URL, JSON_PATH) # load_database now gets sheet handles
    if df.empty:
        # load_database shows its own error, just ensure window closes
        messagebox.showerror("Startup Error", "Gagal memuat data awal. Aplikasi akan ditutup.")
        root.destroy()
        return

    # --- Setup Window Closing Protocol ---
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.columnconfigure(0, weight=1) # Configure root column initially

    # --- Start GUI ---
    create_main_widgets()
    root.mainloop()

# %% [markdown]
# ## 13. Execution Block

# %%
if __name__ == "__main__":
    # Any setup required before starting the process
    # (like checking for credential file existence maybe)
    if not os.path.exists(JSON_PATH):
         print(f"ERROR: Credential file not found at {JSON_PATH}")
         # Optionally show a Tkinter error box even before root is created
         # temp_root = tk.Tk(); temp_root.withdraw() # Hide temp root
         # messagebox.showerror("Startup Error", f"Credential file missing:\n{JSON_PATH}")
         # temp_root.destroy()
         sys.exit("Credential file missing.") # Exit if critical file missing

    main_process()