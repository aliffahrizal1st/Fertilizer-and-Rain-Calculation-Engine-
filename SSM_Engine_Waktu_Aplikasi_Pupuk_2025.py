# %% [markdown]
#  # **ENGINE WAKTU APLIKASI PUPUK 2025**
# 
# 
# 
#  ## Refactored Code Structure

# %% [markdown]
#  ## 1. Imports and Setup

# %%
# Standard Libraries
import sys
import os
import datetime
from datetime import timedelta
import subprocess
import traceback # For detailed error printing
import random
import string

# Third-Party Libraries
import pandas as pd
import pytz # pip install pytz
from oauth2client.service_account import ServiceAccountCredentials # pip install oauth2client
# from google.oauth2.service_account import Credentials # Alternative auth
from supabase import create_client, Client

# GUI Libraries
import tkinter as tk # pip install tkinter
from tkinter import ttk, messagebox, StringVar
from tkcalendar import Calendar # pip install tkcalendar
from PIL import Image, ImageTk

# %% [markdown]
#  ## 2. Configuration and Constants

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
url: str = "https://wuleooydwhhgpyzkcuwb.supabase.co"
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind1bGVvb3lkd2hoZ3B5emtjdXdiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA4ODA0MzUsImV4cCI6MjA4NjQ1NjQzNX0.etXxyiGd_-cWpw8aE1-3kSK4WA9Y5mjiq1cr9OUunF4"

TARGET_ENVIRONMENT = "SSM"
SPLASH_IMAGE = resource_path('splash_image.png')

if getattr(sys, 'frozen', False):
    # Running as PyInstaller executable
    base_path = os.path.dirname(sys.executable)
elif '__file__' in globals():

    base_path = os.path.dirname(os.path.abspath(__file__))
else:

    base_path = os.getcwd()

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

SYNERGIZE_GROUPS = {
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

DRY_SEASON_ONLY = [
    "Dolomite",
    "TSP",
    "RP",
]

HYGROSCOPIC = {
    "Urea": ["Urea"],
    "HGFB": ["HGFB"],
    "CuSO4": ["CuSO4"],
    "MOP": ["MOP"]
}

NOT_ALLOWED_3_DAYS = ["Urea"]
NOT_ALLOWED_7_DAYS = ["Urea", "MOP", "HGFB"]

if TARGET_ENVIRONMENT == "TDK":
    ESTATE_OPTIONS = ["Inti", "Plasma"]
else:
    ESTATE_OPTIONS = ["Inti", "Plasma", "Pematang Danau"]
DIVISION_OPTIONS = ["1", "2", "3", "4", "5"]

INTERVAL_TABLE = {
    "NPK": {"NPK": 60, "Urea": 14, "RP": 30, "TSP": 30, "Kieserite": 14, "Dolomite": 30, "MOP": 14, "HGFB": 30, "Zincop": 30, "CuSO4": 30},
    "Urea": {"NPK": 14, "Urea": 60, "RP": 30, "TSP": 30, "Kieserite": 14, "Dolomite": 30, "MOP": 14, "HGFB": 30, "Zincop": 30, "CuSO4": 30},
    "RP": {"NPK": 30, "Urea": 30, "RP": 60, "TSP": 60, "Kieserite": 14, "Dolomite": 14, "MOP": 30, "HGFB": 30, "Zincop": 30, "CuSO4": 30},
    "TSP": {"NPK": 30, "Urea": 30, "RP": None, "TSP": 30, "Kieserite": 30, "Dolomite": 30, "MOP": 30, "HGFB": 30, "Zincop": 30, "CuSO4": 30},
    "Kieserite": {"NPK": 14, "Urea": 14, "RP": 14, "TSP": 30, "Kieserite": 60, "Dolomite": 60, "MOP": 30, "HGFB": 14, "Zincop": 30, "CuSO4": 30},
    "Dolomite": {"NPK": 30, "Urea": 30, "RP": 14, "TSP": 30, "Kieserite": None, "Dolomite": 30, "MOP": 30, "HGFB": 30, "Zincop": 30, "CuSO4": 30},
    "MOP": {"NPK": 14, "Urea": 14, "RP": 30, "TSP": 30, "Kieserite": 30, "Dolomite": 30, "MOP": 60, "HGFB": 30, "Zincop": 30, "CuSO4": 30},
    "HGFB": {"NPK": 30, "Urea": 30, "RP": 30, "TSP": 30, "Kieserite": 14, "Dolomite": 30, "MOP": 30, "HGFB": 60, "Zincop": 14, "CuSO4": 14},
    "Zincop": {"NPK": 30, "Urea": 30, "RP": 30, "TSP": 30, "Kieserite": 30, "Dolomite": 30, "MOP": 30, "HGFB": 14, "Zincop": 60, "CuSO4": 14},
    "CuSO4": {"NPK": 30, "Urea": 30, "RP": 30, "TSP": 30, "Kieserite": 30, "Dolomite": 30, "MOP": 30, "HGFB": 14, "Zincop": 14, "CuSO4": 60},
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
ANALISA_ID_TEXT_COLOR = "#0e7767"

# --- Timezone ---
CURRENT_TIMEZONE = pytz.timezone('Asia/Jakarta') # Or your preferred timezone

# %% [markdown]
#  ## 3. Utility Functions

# %%
def init_supabase():
    try:
        print(f"Initializing Supabase client...")
        return create_client(url, key)
    except Exception as e:
        print(f"[ERROR] Supabase initialization failed: {str(e)}")
        return None

# %%
def format_datetime(dt):
    # Use datetime.datetime and datetime.date
    if isinstance(dt, (datetime.datetime, datetime.date)):
         # ADD CHECK: Ensure dt is not None before calling strftime
         if dt:
             return dt.strftime('%Y%m/%d')
    return '' # Return empty string if not a valid date/datetime or if None

def format_datetimehour(dt):
    # Use datetime.datetime
    if isinstance(dt, datetime.datetime):
         # ADD CHECK: Ensure dt is not None
         if dt:
             return dt.strftime('%d/%m/%Y %H:%M:%S')
    return ''

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
    global username, username_var
    if username_var: # Check if StringVar exists
        username = username_var.get()

def get_fertilizer_group(fertilizer):
    """Finds the group a given fertilizer belongs to."""
    for group, types in FERTILIZER_GROUPS.items():
        if fertilizer in types:
            return group
    return None # Return None if not found


# %%
def get_missing_dates(df, current_time_date):
    
    if df.empty:
        return pd.DatetimeIndex([]), None, 0

    print(f"df['Date'].max(): {df['Date'].max()}, type: {type(df['Date'].max())}")
    start_date = df['Date'].max() + pd.Timedelta(days=1)

    print(f"current_time_date: {current_time_date}, type: {type(current_time_date)}")
    end_date = current_time_date - pd.Timedelta(days=1)

    if start_date > end_date:
        return pd.DatetimeIndex([]), start_date, 0

    missing_dates = pd.date_range(start=start_date, end=end_date, freq='D')

    return missing_dates, start_date, len(missing_dates)

# %% [markdown]
#  ## 4. Global Variables (Application State)

# %%
# --- Core App State ---
root = None
previous_menu = None
root_exists = False
current_menu = None
df = pd.DataFrame() # In-memory data store
current_time_date = datetime.datetime.now(CURRENT_TIMEZONE).date() # Ensure it uses datetime.datetime
formatted_today = format_datetime(current_time_date)
yesterday_time_date = current_time_date - datetime.timedelta(days=1)

# --- User State ---
username_var = None # Will be StringVar, created in main_process
username = ""     # Will store the string username

# --- Database Objects ---
supadatabase = None
rain_data = None   # DB data object
output_data = None # Output data object

# --- GUI State ---
success_window = None
missing_dates_widgets = {}

# %% [markdown]
#  ## 5. Google Sheets Interaction

# %%
def load_initial_database():
    global rain_data, output_data, supadatabase

    print(f"[DEBUG] load_initial_database")

    if (supadatabase == None):
        supadatabase = init_supabase()
        
    try:
        if (TARGET_ENVIRONMENT == "TDK") :
            res_data = supadatabase.table("rainfall_station_tdk").select("*").order("date", desc=True).execute()
            res_output = supadatabase.table("hasil_analisa_pupuk_tdk").select("*").execute()

            print(f"Connection to TDK DB Success!")
        elif (TARGET_ENVIRONMENT == "SSM"):
            res_data = supadatabase.table("rainfall_station_ssm").select("*").order("date", desc=True).execute()
            res_output = supadatabase.table("hasil_analisa_pupuk_ssm").select("*").execute()

            print(f"Connection to SSM DB Success!")
    
        rain_data = pd.DataFrame(res_data.data)
        output_data = pd.DataFrame(res_output.data)

        # print(f"[DEBUG] res_output.data:\n{res_output.data}")
        # print(f"[DEBUG] output_data head:\n{output_data.head(1)}")
        # print(f"[DEBUG] rain_data head:\n{rain_data.head(1)}")
        # print(f"[DEBUG] rain_data info:\n{rain_data.info()}")

        # Data type conversions and cleaning
        print(f"[DEBUG] Starting datetime conversions and cleaning")
        if 'date' in rain_data.columns:
            rain_data['date'] = pd.to_datetime(rain_data['date'], format='%Y-%m-%d', errors='coerce')
            rain_data.dropna(subset=['date'], inplace=True)
        else:
             print("Data Error Kolom 'date' tidak ditemukan di database.")
             messagebox.showerror("Data Error", "Kolom 'date' tidak ditemukan di database.")
             return pd.DataFrame()
        
        print(f"[DEBUG] Starting estate conversions and cleaning")
        if 'estate' in rain_data.columns:
            rain_data['estate'] = rain_data['estate'].fillna('').astype(str)
        else:
            print("Data Error Kolom 'estate' tidak ditemukan di database.")
            messagebox.showerror("Data Error", "Kolom 'estate' tidak ditemukan di database.")
            return pd.DataFrame()

        print(f"[DEBUG] Starting division conversions and cleaning")
        if 'division' in rain_data.columns:
            rain_data['division'] = rain_data['division'].fillna('').astype(str)
        else:
            print("Data Error Kolom 'division' tidak ditemukan di database.")
            messagebox.showerror("Data Error", "Kolom 'division' tidak ditemukan di database.")
            return pd.DataFrame()

        rain_data = rain_data.rename(columns={
            'date': 'Date',
            'estate': 'Estate',
            'division': 'Division',
            'daily_rainfall_mm': 'Daily Rainfall (mm)',
            'accumulation_rainfall_29_days': 'Accumulation Rainfall -29 days',
            'evapotranspiration': 'Evapotranspiration',
            'water_balance': 'Water Balance',
            'soil_water_reserve_mm': 'Soil Water Reserve (mm)',
            'water_surplus': 'Water Surplus',
            'id': 'id'
        })
        
        print(f"[DEBUG] Column names after standardization:\n{rain_data.columns.tolist()}")

        print(f"[DEBUG] rain_data.head(): {rain_data.head()}")

        return rain_data

    except Exception as e:
        print(f"[ERROR] Failed to load database: {str(e)}")
        messagebox.showerror("Database Error", f"Gagal memuat database:\n{str(e)}")
        return pd.DataFrame()

# %%
def load_estate_database(selected_estate, selected_division):
    global rain_data, output_data, supadatabase

    print(f"[DEBUG] load_estate_database")

    if (supadatabase == None):
        supadatabase = init_supabase()
        
    try:
        # Convert division to integer for proper database filtering
        division_int = int(selected_division)
        
        if (TARGET_ENVIRONMENT == "TDK") :
            res_data = supadatabase.table("rainfall_station_tdk").select("*").eq("estate", selected_estate).eq("division", division_int).order("date", desc=True).execute()
            res_output = supadatabase.table("hasil_analisa_pupuk_tdk").select("*").execute()

            # messagebox.showinfo("DEBUG", "Connection to TDK DB Success!")
            print(f"Connection to TDK DB Success!")
        elif (TARGET_ENVIRONMENT == "SSM"):
            res_data = supadatabase.table("rainfall_station_ssm").select("*").eq("estate", selected_estate).eq("division", division_int).order("date", desc=True).execute()
            res_output = supadatabase.table("hasil_analisa_pupuk_ssm").select("*").execute()

            print(f"Connection to SSM DB Success!")
    
        rain_data = pd.DataFrame(res_data.data)
        output_data = pd.DataFrame(res_output.data)

        # print(f"[DEBUG] res_output.data:\n{res_output.data}")
        # print(f"[DEBUG] output_data head:\n{output_data.head(1)}")
        # print(f"[DEBUG] rain_data head:\n{rain_data.head(1)}")    
        # print(f"[DEBUG] rain_data info:\n{rain_data.info()}")

        # Data type conversions and cleaning
        if 'date' in rain_data.columns:
            rain_data['date'] = pd.to_datetime(rain_data['date'], format='%Y-%m-%d', errors='coerce').dt.date
            rain_data.dropna(subset=['date'], inplace=True)
        else:
             print("Data Error Kolom 'date' tidak ditemukan di database.")
             messagebox.showerror("Data Error", "Kolom 'date' tidak ditemukan di database.")
             return pd.DataFrame()
        
        if 'estate' in rain_data.columns:
            rain_data['estate'] = rain_data['estate'].fillna('').astype(str)
        else:
            print("Data Error Kolom 'estate' tidak ditemukan di database.")
            messagebox.showerror("Data Error", "Kolom 'estate' tidak ditemukan di database.")
            return pd.DataFrame()

        if 'division' in rain_data.columns:
            rain_data['division'] = rain_data['division'].fillna('').astype(str)
        else:
            print("Data Error Kolom 'division' tidak ditemukan di database.")
            messagebox.showerror("Data Error", "Kolom 'division' tidak ditemukan di database.")
            return pd.DataFrame()

        rain_data = rain_data.rename(columns={
            'date': 'Date',
            'estate': 'Estate',
            'division': 'Division',
            'daily_rainfall_mm': 'Daily Rainfall (mm)',
            'accumulation_rainfall_29_days': 'Accumulation Rainfall -29 days',
            'evapotranspiration': 'Evapotranspiration',
            'water_balance': 'Water Balance',
            'soil_water_reserve_mm': 'Soil Water Reserve (mm)',
            'water_surplus': 'Water Surplus',
            'id': 'id'
        })

        # print(f"[DEBUG] Column names after standardization:\n{rain_data.columns.tolist()}")

        # print(f"[DEBUG] rain_data.head(): {rain_data.head()}")

        # messagebox.showinfo("DEBUG", f"Data untuk Estate: {selected_estate}, Divisi: {selected_division} berhasil dimuat!")
        # messagebox.showinfo("DEBUG", f"rain_data: {rain_data}")

        return rain_data

    except Exception as e:
        print(f"Connection to {TARGET_ENVIRONMENT} DB failed! Reason:", e)
        messagebox.showerror("Startup Error", f"Connection to {TARGET_ENVIRONMENT} DB failed!\nReason: {e}")
        return pd.DataFrame()

# %%
def insert_rain_data(new_row_values):
    global rain_data, output_data, supadatabase

    print(f"[DEBUG] insert_rain_data")

    if (supadatabase is None):
        supadatabase = init_supabase()

    if supadatabase is None:
        print("[ERROR] Supabase database connection failed. Cannot insert data.")
        messagebox.showerror("Error", "Koneksi database gagal. Data tidak dapat dikirim.")
        return
        
    try:
        if (TARGET_ENVIRONMENT == "TDK") :
            input_tabel = "rainfall_station_tdk"
            
        elif (TARGET_ENVIRONMENT == "SSM"):
            input_tabel = "rainfall_station_ssm"

        supadatabase.table(input_tabel).insert(
            {"date": new_row_values[0], 
                "estate": new_row_values[1],
                "division": new_row_values[2],
                "daily_rainfall_mm": new_row_values[3],
                "accumulation_rainfall_29_days": new_row_values[4],
                "evapotranspiration": new_row_values[5],
                "water_balance": new_row_values[6],
                "soil_water_reserve_mm": new_row_values[7],
                "water_surplus": new_row_values[8],
                }).execute()

        print(f"Insert rain data to {TARGET_ENVIRONMENT} DB Success!")
    
    except Exception as e:
        print(f"Insert rain data to {TARGET_ENVIRONMENT} DB failed! Reason:", e)

# %%
def update_rain_data(new_row_values):
    global rain_data, output_data, supadatabase

    print(f"[DEBUG] update_rain_data")

    if (supadatabase is None):
        supadatabase = init_supabase()

    if supadatabase is None:
        print("[ERROR] Supabase database connection failed. Cannot update data.")
        messagebox.showerror("Error", "Koneksi database gagal. Data tidak dapat diupdate.")
        return
        
    try:
        if (TARGET_ENVIRONMENT == "TDK") :
            input_tabel = "rainfall_station_tdk"
            
        elif (TARGET_ENVIRONMENT == "SSM"):
            input_tabel = "rainfall_station_ssm"

        supadatabase.table(input_tabel).update(
            {"date": new_row_values[0], 
                "estate": new_row_values[1],
                "division": new_row_values[2],
                "daily_rainfall_mm": new_row_values[3],
                "accumulation_rainfall_29_days": new_row_values[4],
                "evapotranspiration": new_row_values[5],
                "water_balance": new_row_values[6],
                "soil_water_reserve_mm": new_row_values[7],
                "water_surplus": new_row_values[8],
                }).eq("date", new_row_values[0]).eq("estate", new_row_values[1]).eq("division", new_row_values[2]).execute()

        print(f"Update rain data to {TARGET_ENVIRONMENT} DB Success!")
    
    except Exception as e:
        print(f"Update rain data to {TARGET_ENVIRONMENT} DB failed! Reason:", e)

# %%
def insert_output_data(output_data):
    global supadatabase

    print(f"[DEBUG] insert_output_data")

    if (supadatabase is None):
        supadatabase = init_supabase()
        
    try:
        if (TARGET_ENVIRONMENT == "TDK") :
            hasil_analisa_tabel = "hasil_analisa_pupuk_tdk"

        elif (TARGET_ENVIRONMENT == "SSM"):
            hasil_analisa_tabel = "hasil_analisa_pupuk_ssm"

        supadatabase.table(hasil_analisa_tabel).insert(
            {"tanggal_analisa": output_data[0], 
                "nama_user": output_data[1],
                "estate": output_data[2],
                "division": output_data[3],
                "blok": output_data[4],
                "id_analisa": output_data[5],
                "curah_hujan": output_data[6],
                "peilscale": output_data[7],
                "pupuk_terakhir": output_data[8],
                "tanggal_aplikasi_terakhir": output_data[9],
                "plan_pupuk": output_data[10],
                "plan_aplikasi": output_data[11],
                "status": output_data[12],
                "reason": output_data[13],
                "recommendation": output_data[14],
                }).execute()

        print(f"Insert output data to {TARGET_ENVIRONMENT} DB Success!")
    
    except Exception as e:
        print(f"Insert output data to {TARGET_ENVIRONMENT} DB failed! Reason:", e)

# %%
def delete_rain_data(input_date, estate, division):
    global supadatabase

    print(f"[DEBUG] delete_rain_data")
    print(f"[DEBUG] input_date: {input_date}, estate: {estate}, division: {division}")

    if (supadatabase == None):
        supadatabase = init_supabase()
        
    try:
        if (TARGET_ENVIRONMENT == "TDK") :
            delete_tabel = "rainfall_station_ssm"
            
        elif (TARGET_ENVIRONMENT == "SSM"):
            delete_tabel = "rainfall_station_ssm"

        supadatabase.table(delete_tabel).delete()\
            .eq("date", input_date)\
            .eq("estate", estate)\
            .eq("division", division)\
            .execute()

        print(f"Delete rain data for {input_date}, {estate}-{division} DB Success!")
    
    except Exception as e:
        print(f"Delete rain data for {input_date}, {estate}-{division} DB Failed! Reason:", e)

# %%
def calculate_and_append_db(date_input, username, estate_name, division_number, blok_name, id_analisa, current_daily_rainfall, peilscale, last_fertilizer, last_fertilizer_date, next_fertilizer, next_fertilizer_date, reason, recommendation):
    status = "Allowed" if not reason else "Not Allowed"

    try:
        # --- Format dates safely ---
        last_fert_date_str = ""
        if isinstance(last_fertilizer_date, (datetime.datetime, datetime.date)): # Use full class names
            last_fert_date_str = last_fertilizer_date.strftime("%Y-%m-%d")

        next_fert_date_str = ""
        if isinstance(next_fertilizer_date, (datetime.datetime, datetime.date)): # Use full class names
            next_fert_date_str = next_fertilizer_date.strftime("%Y-%m-%d")
        # --- End date formatting ---

        output_result = [
            date_input.strftime('%Y-%m-%d %H:%M:%S'), username, estate_name, division_number,
            blok_name, id_analisa, current_daily_rainfall, peilscale, last_fertilizer,
            last_fert_date_str,
            next_fertilizer,
            next_fert_date_str,
            status, reason, recommendation
        ]
        insert_output_data(output_result)
        
        print("Analysis results appended to database.")
        return status
    except Exception as e:
         messagebox.showerror("Error", f"Gagal menyimpan hasil ke database: {e}")
         back_to_main()

# %%
def remove_old_data(df, date_to_remove, estate_name, division_number):

    # --- Load Initial Data ---
    if (df is None) or (df.empty):
        print("Loading data...") # Feedback
        df = load_estate_database(estate_name, division_number)
        if df.empty:
            messagebox.showerror("Startup Error", "Gagal memuat data.\nAplikasi akan ditutup.")
            if root: root.destroy()
            return
        print("Data loaded successfully.") # Feedback

    try:
        delete_rain_data(date_to_remove, estate_name, division_number)

        return df.reset_index(drop=True) # Reset index after dropping rows

    except Exception as e:
        messagebox.showerror("Error", f"Gagal menghapus data lama: {e}")
        print(f"Error in remove_old_data: {e}")
        return df # Return original df on error

# %% [markdown]
#  ## 6. Core Logic - Rainfall & Water Balance

# %%
def calculate_rainfall(df_original, calc_date, daily_rainfall, estate_name, division_number, update=False):

    # --- Load Initial Data ---
    if (df_original is None) or df_original.empty:
        print("Loading data...") # Feedback
        df_original = load_estate_database(estate_name, division_number)
        if df_original.empty:
            messagebox.showerror("Startup Error", "Gagal memuat data.\nAplikasi akan ditutup.")
            if root: root.destroy()
            return
        print("Data loaded successfully.") # Feedback

    try:
        # --- Input Validation & Date Conversion ---
        if isinstance(calc_date, (datetime.datetime, pd.Timestamp)):
            calc_date = calc_date.date()
        elif not isinstance(calc_date, datetime.date):
             try: calc_date = pd.to_datetime(calc_date).date()
             except Exception: raise ValueError(f"calc_date received an invalid type: {type(calc_date)}")

        daily_rainfall = float(daily_rainfall)
        if daily_rainfall < 0: raise ValueError("Curah hujan tidak boleh negatif.")
        # --- End Validation ---

        # --- Get Previous Day's Data ---
        prev_day_date = calc_date - timedelta(days=1)
        # Ensure consistent datetime format before filtering
        df_original['Date'] = pd.to_datetime(df_original['Date']).dt.normalize()
        prev_day_row = df_original[
            (df_original['Estate'] == estate_name) &
            (df_original['Division'] == division_number) &
            (df_original['Date'].dt.date == prev_day_date)
        ]

        previous_soil_water_reserve = 0.0
        if not prev_day_row.empty:
            swr_val = prev_day_row['Soil Water Reserve (mm)'].iloc[0]
            previous_soil_water_reserve = pd.to_numeric(swr_val, errors='coerce')
            if pd.isna(previous_soil_water_reserve): previous_soil_water_reserve = 0.0
        else:
             print(f"Note: No data found for previous day {prev_day_date} for {estate_name} - {division_number}. Assuming SWR=0.")

        # --- Calculate Accumulation (29 days ENDING YESTERDAY) ---
        start_window_date = calc_date - timedelta(days=29)
        end_window_date = calc_date - timedelta(days=1)

        # Filter original df_original for the date window *up to the previous day* AND estate
        window_df = df_original[
             (df_original['Estate'] == estate_name) &
             (df_original['Division'] == division_number) &
             (df_original['Date'].dt.date >= start_window_date) &
             (df_original['Date'].dt.date <= end_window_date)
        ].copy()

        # Ensure rainfall column is numeric and fill NaNs
        window_df['Daily Rainfall (mm)'] = pd.to_numeric(window_df['Daily Rainfall (mm)'], errors='coerce').fillna(0)

        # --- FIX: Sum rainfall ONLY within the window (excluding current day's rainfall) ---
        accumulation_rainfall = round(window_df['Daily Rainfall (mm)'].sum(), 1)
        # --- END FIX ---

        # --- Calculate Evapotranspiration ---
        # Logic depends on definition - using length of accumulation window here
        days_in_acc_window = len(window_df)
        # Adjust evapotranspiration logic if needed based on how 'days in window' should be counted
        evapotranspiration = (120 if days_in_acc_window >= 10 else 150) / 30

        # --- Calculate Water Balance & Reserves ---
        # Correctly uses current day's rainfall here
        water_balance = round((previous_soil_water_reserve + daily_rainfall - evapotranspiration), 1)
        soil_water_reserve = round(min(water_balance, 200), 1)
        water_surplus = max(0, water_balance - 200)

        # --- Prepare Data for Sheet and DataFrame ---
        date_str_sheet = calc_date.strftime('%Y-%m-%d')
        new_row_values = [
            date_str_sheet, estate_name, division_number, daily_rainfall, accumulation_rainfall,
            evapotranspiration, water_balance, soil_water_reserve, water_surplus
        ]
        new_row_dict = {
            'Date': pd.Timestamp(calc_date),
            'Estate': estate_name,
            'Division': division_number,
            'Daily Rainfall (mm)': daily_rainfall,
            'Accumulation Rainfall -29 days': accumulation_rainfall,
            'Evapotranspiration': evapotranspiration,
            'Water Balance': water_balance,
            'Soil Water Reserve (mm)': soil_water_reserve,
            'Water Surplus': water_surplus
        }

        # --- Update Sheet and DataFrame ---
        try:
            if update:
                update_rain_data(new_row_values)
            else:
                insert_rain_data(new_row_values)
            
            print(f"Appended to Database: {new_row_values}")
        except Exception as e:
             messagebox.showerror("Sheet Error", f"Gagal menyimpan data ke Database: {e}")
             print(f"Error appending to database: {e}")
             return df_original

        df_updated = pd.concat([df_original, pd.DataFrame([new_row_dict])], ignore_index=True)
        df_updated = df_updated.sort_values(by='Date').reset_index(drop=True)
        print(f"Successfully calculated and added data for {estate_name} - {division_number} on {date_str_sheet}")
        return df_updated

    except ValueError as ve: 
        messagebox.showerror("Input Error", f"Gagal memproses data untuk {format_datetime(calc_date)}: {ve}")
        print(f"Validation Error in calculate_rainfall for {format_datetime(calc_date)}: {ve}")
        return df_original
    except Exception as e:
        messagebox.showerror("Error", f"Gagal menghitung data hujan untuk {format_datetime(calc_date)}: {e}")
        print(f"Error in calculate_rainfall for {format_datetime(calc_date)}: {e}")
        traceback.print_exc()
        return df_original

# %% [markdown]
#  ## 7. Core Logic - Fertilizer Rules & Validation

# %%
def analyze_fertilizer(date_input, username, estate_name, division_number, blok_name, id_analisa, df, peilscale, last_fertilizer, last_fertilizer_date, next_fertilizer, next_fertilizer_date):

  reason = ""
  recommendation = ""
  
  # Filter the DataFrame and make a copy to avoid SettingWithCopyWarning
  estate_df = df[(df['Estate'] == estate_name) & (df['Division'] == division_number)].copy()

  # Convert 'Date' column to datetime.date safely
  estate_df['Date'] = pd.to_datetime(estate_df['Date'], errors='coerce').dt.date
  
  # Get all available dates
  available_dates = estate_df['Date'].dropna().sort_values().unique()

  # Get Today's and Yesterday's dates
  today_date = current_time_date
  yesterday_date = yesterday_time_date
  
  # Decide which date to use for rainfall
  if next_fertilizer_date.date() == today_date: # If next fertilizer date is today
      use_date = yesterday_date
      estate_df = estate_df[estate_df['Date'] != today_date]
  elif today_date == (next_fertilizer_date.date() - datetime.timedelta(days=1)): # If today is one day before next fertilizer date
      use_date = today_date
  elif next_fertilizer_date.date() < today_date: # If next fertilizer date is in the past
     use_date = next_fertilizer_date.date() - datetime.timedelta(days=1)
     estate_df = estate_df[estate_df['Date'] <= use_date]
  else: # If next fertilizer date is in the future
      use_date = max(available_dates)

  # Fetch rainfall for that date
  rainfall_row = estate_df[estate_df['Date'] == use_date]
  if not rainfall_row.empty:
      current_daily_rainfall = rainfall_row['Daily Rainfall (mm)'].values[0]
  else:
      current_daily_rainfall = 0  # or consider throwing a warning
      
  # Check data gap
  last_available_date = max(available_dates)
  gap_days = (next_fertilizer_date.date() - last_available_date).days
  if gap_days >= 2:
      reason += f"Waktu curah hujan terakhir terlalu jauh dengan tanggal pemupukan selanjutnya. Terdapat {gap_days} hari kosong."
      status = calculate_and_append_db(date_input, username, estate_name, division_number, blok_name, id_analisa, current_daily_rainfall, 0, last_fertilizer, last_fertilizer_date, next_fertilizer, next_fertilizer_date, reason, "")
      return current_daily_rainfall, status, reason, recommendation

  #check if today's rainfall is greater than or equal to 60
  if current_daily_rainfall >= 60:
    reason = "Curah hujan lebih dari 60 mm, pemupukan dihentikan"
    print(reason)
    status = calculate_and_append_db(date_input, username, estate_name, division_number, blok_name, id_analisa, current_daily_rainfall, 0, last_fertilizer, last_fertilizer_date, next_fertilizer, next_fertilizer_date, reason, "")
    return current_daily_rainfall, status, reason, recommendation

  #check the accumulated rainfall data
  validate_water, rain_factor, peilscale_factor, season_factor, current_season, dry_with_rain, accumulation_rainfall, water_surplus, daily_rainfall_last_7 = validate_water_track(estate_df, current_daily_rainfall, peilscale, next_fertilizer)
  if(not validate_water):
    # Validasi 1
    if(not rain_factor):
      if(not season_factor):
        if current_season == "Basah":
            print(f"water surplus2: {water_surplus}")
            if water_surplus == 0.0:
               print("Bulan basah & water surplus 0")
            else:
              reason = f"Tidak bisa melakukan pemupukan, karena musim {current_season}"
              status = calculate_and_append_db(date_input, username, estate_name, division_number, blok_name, id_analisa, current_daily_rainfall, peilscale, last_fertilizer, last_fertilizer_date, next_fertilizer, next_fertilizer_date, reason, "")
              recommendation = ""
              return current_daily_rainfall, status, reason, recommendation
        elif current_season == "Kering" and next_fertilizer in DRY_SEASON_ONLY:
            print(reason)
        elif current_season == "Kering":
            reason = f"Tidak bisa melakukan pemupukan, karena musim {current_season}"
            recommendation = "Dolomite, RP, TSP"
            status = calculate_and_append_db(date_input, username, estate_name, division_number, blok_name, id_analisa, current_daily_rainfall, peilscale, last_fertilizer, last_fertilizer_date, next_fertilizer, next_fertilizer_date, reason, f"Pupuk alternatif yang disarankan: {recommendation}")
            return current_daily_rainfall, status, reason, recommendation      

    #Valdasi 2
    elif(not peilscale_factor):
      reason = "Tidak bisa melakukan pemupukan, karena peilscale di atas -51"
      status = calculate_and_append_db(date_input, username, estate_name, division_number, blok_name, id_analisa, current_daily_rainfall, peilscale, last_fertilizer, last_fertilizer_date, next_fertilizer, next_fertilizer_date, reason, "")
      recommendation = ""
      return current_daily_rainfall, status, reason, recommendation
    
    #Validasi 3
    elif(not season_factor):
      reason = f"Tidak bisa melakukan pemupukan, karena musim {current_season}"
      if current_season == "Basah":
          print(f"water surplus3: {water_surplus}")
          if water_surplus == 0.0:
             print("Bulan basah & water surplus 0")
             reason = ""
          else:
            status = calculate_and_append_db(date_input, username, estate_name, division_number, blok_name, id_analisa, current_daily_rainfall, peilscale, last_fertilizer, last_fertilizer_date, next_fertilizer, next_fertilizer_date, reason, "")
            recommendation = ""
            return current_daily_rainfall, status, reason, recommendation
      elif current_season == "Kering":
          print(reason)

  #get the last fertilizer's group
  last_group = get_fertilizer_group(last_fertilizer)
  #get the next fertilizer's group
  next_group = get_fertilizer_group(next_fertilizer)

  #check the interval between the last & the next fertilizer
  validate_interval_result = validate_interval_fertilizer(last_group, next_group, last_fertilizer_date, next_fertilizer_date)

  #Check the alternative
  #If the interval is not valid, get the alternatives
  Alternatives = []
  if (not validate_interval_result):
    if last_group == next_group:
      reason = "Karena jarak interval pemupukan di bawah 60 hari"
    elif last_group != next_group:
      reason = "Karena jarak interval pemupukan di bawah 30 hari"
    Alternatives = get_alternative_fertilizer(last_group, next_group, last_fertilizer_date, next_fertilizer_date, INTERVAL_TABLE, FERTILIZER_GROUPS)
  else:
    Alternatives = get_all_recommendation(last_group, next_group, last_fertilizer_date, next_fertilizer_date, INTERVAL_TABLE, FERTILIZER_GROUPS)

  #Check the specific fertilizer trait
  #Dolomite
  Alternatives = validate_dolomite(estate_df, last_fertilizer, last_fertilizer_date, next_fertilizer_date, Alternatives)
  #Discard because dry week
  is_dry_week = validate_dry_week(estate_df)
  
  #if current fertilizer is not allowed
  #3 days dry
  if next_fertilizer in NOT_ALLOWED_3_DAYS and is_dry_week >= 3:
      reason = "3 hari kebelakang tidak terdapat hujan sama sekali"
      Alternatives = [item for item in Alternatives if item not in NOT_ALLOWED_3_DAYS]
  #7 days dry
  elif next_fertilizer in NOT_ALLOWED_7_DAYS and is_dry_week >= 7:
      reason = "7 hari kebelakang tidak terdapat hujan sama sekali"
      Alternatives = [item for item in Alternatives if item not in NOT_ALLOWED_7_DAYS]

  #if current fertilizer is allowed
  #3 days dry
  if is_dry_week >= 3:
      Alternatives = [item for item in Alternatives if item not in NOT_ALLOWED_3_DAYS]
  #7 days dry
  elif is_dry_week >= 7:
      Alternatives = [item for item in Alternatives if item not in NOT_ALLOWED_7_DAYS]

  #Check if current season is dry 
  if current_season == "Kering" and next_fertilizer in DRY_SEASON_ONLY:
     Alternatives = [item for item in Alternatives if item in DRY_SEASON_ONLY]

  #Join the alternative option
  alternative = ', '.join(Alternatives)
  recommendation = ""
  plan_fertilizer_date = (last_fertilizer_date + datetime.timedelta(days=14)).date()
  if (len(Alternatives) != 0):
    recommendation = f"Pupuk alternatif yang disarankan: {alternative}"

  # Append to database
  status = calculate_and_append_db(date_input, username, estate_name, division_number, blok_name, id_analisa, current_daily_rainfall, peilscale, last_fertilizer, last_fertilizer_date, next_fertilizer, next_fertilizer_date, reason, recommendation)

  return current_daily_rainfall, status, reason, recommendation

# %%
def validate_dolomite(df, last_fertilizer, last_fertilizer_date, next_fertilizer_date, Alternatives):
  dolomite_fertilizer = "Dolomite"

  # Check if the alternatives already has Dolomite inside it
  if dolomite_fertilizer in Alternatives:
    return Alternatives  # Dolomite not allowed

  # 1. Check if the last Daily Rainfall (mm) is >= 60
  last_daily_rainfall = df['Daily Rainfall (mm)'].iloc[0]
  if last_daily_rainfall >= 60:
    return Alternatives  # Dolomite not allowed

  # 2. Check if Accumulation Rainfall is >= 300
  accumulation_rainfall = df['Accumulation Rainfall -29 days'].iloc[0]
  if accumulation_rainfall >= 300:
    return Alternatives  # Dolomite not allowed

  # 3. Check if the interval is met (same as other fertilizers)
  last_group = get_fertilizer_group(last_fertilizer)
  next_group = get_fertilizer_group(dolomite_fertilizer)  # Assuming Dolomite is the next_fertilizer
  min_interval = get_minimal_interval(last_group, next_group)
  
  selisih_hari = (next_fertilizer_date - last_fertilizer_date).days
  if selisih_hari < min_interval:
    return Alternatives  # Dolomite not allowed

  # If all checks pass, add Dolomite to Alternatives
  Alternatives.append(dolomite_fertilizer)
  return Alternatives

# %%
def validate_dry_week(df):
  print(f"[DEBUG] validate dry week, df: {df.head(7)}")
  last_days = df['Daily Rainfall (mm)'].iloc[:7]
  print(f"[DEBUG] last_days: {last_days}")

  no_rain = 0
  for i in last_days:
    if i == 0:
      no_rain += 1

  return no_rain

# %%
def get_fertilizer_group(fertilizer):
    for group, types in FERTILIZER_GROUPS.items():
        if fertilizer in types:
            return group
    return None

# %%
def check_groundwater(accumulation_rainfall, water_surplus):
  if (accumulation_rainfall >= 300) and (water_surplus == 0):
    return True
  elif (accumulation_rainfall >= 60) and (accumulation_rainfall <= 300) and (water_surplus >= 0):
    return True
  else:
    return False

# %%
def check_peilscale(peilscale):
  if peilscale <= -51:
    return True
  else:
    return False

# %%
def check_season(accumulation_rainfall):
  if accumulation_rainfall < 60 :
    return "Kering"
  elif accumulation_rainfall > 300:
    return "Basah"

# %%
def check_rain_in_dry_seasion(daily_rainfall_last_7):
  raining_once = (daily_rainfall_last_7 >= 60).sum() >= 1
  raining_twice = (daily_rainfall_last_7 >= 30).sum() >= 2

  if raining_once or raining_twice:
    return True
  else:
    return False

# %%
def validate_water_track(df, current_daily_rainfall, peilscale, next_fertilizer):
  last_row = df.iloc[0]
  print(f"last_row: {last_row}")
  accumulation_rainfall = last_row['Accumulation Rainfall -29 days']
  print(f"accumulation_rainfall: {accumulation_rainfall}")
  water_surplus = last_row['Water Surplus']
  print(f"water_surplus: {water_surplus}")
  daily_rainfall_last_7 = df['Daily Rainfall (mm)'].iloc[:7]
  print(f"daily_rainfall_last_7: {daily_rainfall_last_7.tolist()}")

  # Syarat 1
  validation1 = check_groundwater(accumulation_rainfall, water_surplus)
  print("validation1", validation1)

  # Syarat 2
  print("peilscale", peilscale)
  validation2 = check_peilscale(peilscale)
  print("validation2", validation2)

  # Syarat 3
  season = check_season(accumulation_rainfall)
  validation3 = season not in ["Basah", "Kering"] # if validation3 has value that means it's either 'Wet' or 'Dry', None means it's Optimal
  print("season", season)
  print("validation3", validation3)

  # Check if season is 'Dry' with rains around 7 days back
  dry_with_rain = False
  if (season == "Kering"):
    dry_with_rain = check_rain_in_dry_seasion(daily_rainfall_last_7)

  return (validation1 and validation2 and validation3), validation1, validation2, validation3, season, dry_with_rain, accumulation_rainfall, water_surplus, daily_rainfall_last_7

# %%
def get_minimal_interval(last_group, next_group):
    return INTERVAL_TABLE.get(last_group, {}).get(next_group, 30)  # Default to 30 if not found

# %%
def validate_interval_fertilizer(last_group, next_group, last_fertilizer_date, next_fertilizer_date):
  min_interval = get_minimal_interval(last_group, next_group)
  if min_interval == None:  # Handle cases with no defined interval
      return False  # Or return True, depending on how you want to handle these cases
  
  selisih_hari = (next_fertilizer_date - last_fertilizer_date).days
  return selisih_hari >= min_interval

# %%
def get_alternative_fertilizer(last_group, next_group, last_fertilizer_date, next_fertilizer_date, INTERVAL_TABLE, FERTILIZER_GROUPS):
    recommendation = []
    selisih_hari = (next_fertilizer_date - last_fertilizer_date).days

    for group, fertilizers in FERTILIZER_GROUPS.items():
        if group != next_group:  # Exclude the desired fertilizer because it hits the interval
            interval = INTERVAL_TABLE.get(last_group, {}).get(group, None)
            if interval is not None and selisih_hari >= interval:
                recommendation.extend(fertilizers)

    return recommendation

# %%
def get_all_recommendation(last_group, next_group, last_fertilizer_date, next_fertilizer_date, INTERVAL_TABLE, FERTILIZER_GROUPS):
  recommendation = []
  selisih_hari = (next_fertilizer_date - last_fertilizer_date).days

  # Always include the next_group
  if next_group in FERTILIZER_GROUPS:
      recommendation.extend(FERTILIZER_GROUPS[next_group])

  # Add other fertilizers that meet the interval
  for group, fertilizers in FERTILIZER_GROUPS.items():
      if group != next_group:  # Exclude the desired fertilizer
          interval = INTERVAL_TABLE.get(last_group, {}).get(group, None)
          if interval is not None and selisih_hari >= interval:
              recommendation.extend(fertilizers)

  return recommendation

# %% [markdown]
#  ## 8. GUI - Utility Functions

# %%
# (Place this function definition somewhere appropriate, e.g., Section 11)
def exit_fullscreen(event=None):
    """Exits fullscreen mode when the Escape key is pressed."""
    global root
    if root:
        print("Escape key pressed, exiting fullscreen.") # Feedback
        root.attributes('-fullscreen', False)
        # Optional: You might want to set a default size after exiting fullscreen
        # root.geometry("1200x800") # Example size
        # Or, just let it revert to its natural size based on content/previous state.

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
    today = datetime.datetime.now(CURRENT_TIMEZONE)
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
    if not root_exists: return
    for widget in root.grid_slaves():
         widget.grid_forget()

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

# %%
def validate_rainfall_data_exists(df, selected_estate, selected_division, current_time_date):

    if not selected_estate:
        messagebox.showerror("Error", "Estate belum dipilih.")
        return False
    if selected_estate not in ESTATE_OPTIONS:
         messagebox.showerror("Error", f"Nama estate invalid: '{selected_estate}'.")
         return False
    if not selected_division:
        messagebox.showerror("Error", "Estate belum dipilih.")
        return False
    if selected_division not in DIVISION_OPTIONS:
         messagebox.showerror("Error", f"Nomor divisi invalid: '{selected_division}'.")
         return False
    
    missing_dates, last_reported_time, total_missing_dates = get_missing_dates(df, current_time_date)

    if total_missing_dates > 0:
        last_reported_str = format_datetime(last_reported_time.date()) if last_reported_time else "awal data"
        messagebox.showerror("Data Tidak Lengkap",
                             f"Terdapat {total_missing_dates} hari data hujan yang belum diinput untuk estate {selected_estate} - {selected_division} "
                             f"sejak {last_reported_str}.\n\n"
                             "Harap lengkapi data melalui menu 'Masukkan Data Hujan' → 'Masukkan Data Hujan Baru'")
        return False
    
    estate_data_today = df[(df['Estate'] == selected_estate) & (df['Division'] == selected_division) & (df['Date'] == current_time_date)]

    if estate_data_today.empty:
        messagebox.showerror("Data Tidak Lengkap",
                             f"Data curah hujan untuk hari ini ({current_time_date}) "
                             f"bagi estate {selected_estate} - {selected_division} belum dimasukkan.\n\n"
                             "Harap masukkan data hari ini melalui menu 'Masukkan Data Hujan'.")
        return False
    
    # If all checks pass
    print(f"Rainfall data validation passed for {selected_estate} - {selected_division}") # Debug print
    return True

# %% [markdown]
#  ## 9. GUI - Screen Creation Functions

# %%
def create_splash_screen():
    """Creates and displays the splash screen."""
    global splash_label, splash_button, root

    if not root_exists: return

    # Ensure root window is clean (optional, good practice)
    for widget in root.winfo_children():
        widget.destroy()

    try:
        # --- Load and Resize Image ---
        image_path = SPLASH_IMAGE # <-- REPLACE with your image filename
        if not os.path.exists(image_path):
             messagebox.showerror("Error", f"Splash image not found at:\n{image_path}")
             # Fallback or exit? Let's proceed without image for now
             img = None
             photo_image = None
        else:
            # Get screen size
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()

            # Open image with Pillow
            img_original = Image.open(image_path)

            # Resize to fit screen (using LANCZOS for good quality)
            # Pillow versions >= 9.1.0 use Image.Resampling.LANCZOS
            # Older versions use Image.LANCZOS
            try:
                resample_filter = Image.Resampling.LANCZOS
            except AttributeError:
                resample_filter = Image.LANCZOS # Fallback for older Pillow

            img_resized = img_original.resize((screen_width, screen_height), resample_filter)

            # Convert to Tkinter PhotoImage
            photo_image = ImageTk.PhotoImage(img_resized)

        # --- Create Label for Image ---
        splash_label = tk.Label(root, image=photo_image)
        # IMPORTANT: Keep a reference to the image to prevent garbage collection
        if photo_image:
            splash_label.image = photo_image
        splash_label.place(x=0, y=0, relwidth=1, relheight=1) # Cover entire window

        # --- Create Start Button ---
        # Place it slightly offset from the bottom-right corner
        splash_button = tk.Button(root, text="Start", command=start_main_app,
                                  font=("Arial", 14, "bold"), # Make it stand out
                                  bg="#4CAF50", # Green background
                                  fg="white",   # White text
                                  relief=tk.RAISED, bd=3)
        splash_button.place(relx=1.0, rely=1.0, anchor='se', x=-20, y=-20) # anchor='se' means South-East corner

    except FileNotFoundError:
         messagebox.showerror("Error", f"Splash image file not found: {image_path}")
         root.after(100, start_main_app) # Start app after short delay
    except Exception as e:
        messagebox.showerror("Splash Screen Error", f"Could not load splash screen: {e}")
        traceback.print_exc()
        root.after(100, start_main_app) # Start app after short delay


# %%
def start_main_app():
    """Destroys splash screen elements, loads data, and starts the main app."""
    global splash_label, splash_button, root, df, supadatabase

    if not root_exists: return # Exit if window closed prematurely

    # Destroy splash screen widgets
    if splash_label:
        splash_label.destroy()
    if splash_button:
        splash_button.destroy()

    # --- Now create the main application widgets ---
    create_main_widgets()

# %%
def create_main_widgets():
    global label_username, entry_username, previous_menu, current_menu, back_button, exit_button, button_input_hujan, button_analisa_pemupukan, username_var, label_saved_username, username, df, supadatabase # Add df

    if not root_exists: return
    root.geometry("500x400")
    current_menu = "main"
    configure_bg("#f0f0f0") # Default background

    # --- ROW & COLUMN CONFIGURATION RESET ---
    for i in range(20): root.rowconfigure(i, weight=0)
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=0)
    # --- END CONFIGURATION ---

    if (supadatabase == None):
        supadatabase = init_supabase()

    # Update the dataframe every time user access the main menu
    df = load_initial_database()
    if df.empty:
        messagebox.showerror("Error", "Gagal memuat data di awal\nAplikasi akan ditutup.")
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

# Apply reset to show_ESTATE_OPTIONS, show_ESTATE_OPTIONS_for_add_rainfall,
# show_add_rainfall_entry, show_rainfall_data_entry, show_estate_options_for_analysis,
# display_analysis_results, show_missing_dates_input (it already does it)

def display_analysis_results(selected_estate, selected_division, nama_blok, tanggal_rencana, peilscale, tanggal_terakhir,
                              jenis_terakhir, rencana_jenis, username, curah_hujan, status, id_analisa, reason, recommendation):
    
    global current_menu, label_tanggal_analisa, label_nama_user, label_curah_hujan, \
           label_status, label_id_analisa, label_reason, label_recommendation, label_selected_estate, \
           label_nama_blok, label_tanggal_rencana, label_peilscale_value, \
           label_tanggal_terakhir_value, label_jenis_terakhir_value, \
           label_rencana_jenis_value, back_to_main_button, reanalyze_button  # Add reanalyze_button

    if not root_exists: return

    # --- ROW & COLUMN CONFIGURATION RESET ---
    for i in range(20): root.rowconfigure(i, weight=0)
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=0)
    # --- END CONFIGURATION ---

    hide_all_widgets()
    current_menu = "analysis_results"

    # --- Display Analysis Results ---
    row_offset = 0
    current_time_input = datetime.datetime.now(CURRENT_TIMEZONE)
    label_tanggal_analisa = tk.Label(root, text=f"Tanggal Analisa: {current_time_input.strftime('%Y-%m-%d %H:%M:%S')}", font=("Arial", 12))
    label_tanggal_analisa.grid(row=row_offset, column=0, padx=10, pady=5, sticky="ew")
    row_offset += 1

    label_nama_user = tk.Label(root, text=f"Nama User: {username}", font=("Arial", 12))
    label_nama_user.grid(row=row_offset, column=0, padx=10, pady=5, sticky="ew")
    row_offset += 1

    label_selected_estate = tk.Label(root, text=f"Nama Estate: {selected_estate}", font=("Arial", 12))
    label_selected_estate.grid(row=row_offset, column=0, padx=10, pady=5, sticky="ew")
    row_offset += 1

    label_selected_division = tk.Label(root, text=f"Nomor Divisi: {selected_division}", font=("Arial", 12))
    label_selected_division.grid(row=row_offset, column=0, padx=10, pady=5, sticky="ew")
    row_offset += 1

    label_nama_blok = tk.Label(root, text=f"Nama Blok: {nama_blok}", font=("Arial", 12))
    label_nama_blok.grid(row=row_offset, column=0, padx=10, pady=5, sticky="ew")
    row_offset += 1

    label_curah_hujan = tk.Label(root, text=f"Curah Hujan: {curah_hujan}", font=("Arial", 12))
    label_curah_hujan.grid(row=row_offset, column=0, padx=10, pady=5, sticky="ew")
    row_offset += 1

    label_peilscale_value = tk.Label(root, text=f"Nilai Peilscale: {peilscale}", font=("Arial", 12))
    label_peilscale_value.grid(row=row_offset, column=0, padx=10, pady=5, sticky="ew")
    row_offset += 1

    label_jenis_terakhir_value = tk.Label(root, text=f"Jenis Pupuk Terakhir: {jenis_terakhir}", font=("Arial", 12, "bold"))
    label_jenis_terakhir_value.grid(row=row_offset, column=0, padx=10, pady=5, sticky="ew")
    row_offset += 1

    label_tanggal_terakhir_value = tk.Label(root, text=f"Tanggal Pupuk Terakhir: {tanggal_terakhir}", font=("Arial", 12, "bold"))
    label_tanggal_terakhir_value.grid(row=row_offset, column=0, padx=10, pady=5, sticky="ew")
    row_offset += 1

    label_rencana_jenis_value = tk.Label(root, text=f"Rencana Jenis Pupuk: {rencana_jenis}", font=("Arial", 12, "bold"))
    label_rencana_jenis_value.grid(row=row_offset, column=0, padx=10, pady=5, sticky="ew")
    row_offset += 1

    label_tanggal_rencana = tk.Label(root, text=f"Tanggal Rencana Pupuk: {tanggal_rencana}", font=("Arial", 12, "bold"))
    label_tanggal_rencana.grid(row=row_offset, column=0, padx=10, pady=5, sticky="ew")
    row_offset += 1

    label_status = tk.Label(root, text=f"Status: {status}", font=("Arial", 12, "bold"))
    label_status.grid(row=row_offset, column=0, padx=10, pady=5, sticky="ew")
    row_offset += 1

    label_id_analisa = tk.Label(root, text=f"ID Analisa: {id_analisa}", font=("Arial", 12, "bold"), fg=ANALISA_ID_TEXT_COLOR)
    label_id_analisa.grid(row=row_offset, column=0, padx=10, pady=5, sticky="ew")
    row_offset += 1

    label_reason = tk.Label(root, text=f"Alasan: {reason}", font=("Arial", 12))
    label_reason.grid(row=row_offset, column=0, padx=10, pady=5, sticky="ew")
    row_offset += 1

    label_recommendation = tk.Label(root, text=f"Rekomendasi: {recommendation}", font=("Arial", 12))
    label_recommendation.grid(row=row_offset, column=0, padx=10, pady=5, sticky="ew")
    row_offset += 1

    # --- Re-analyze Button --- (Row 13)
    reanalyze_button = tk.Button(root, text="Reanalyze", command=show_estate_options_for_analysis, font=("Arial", 10), bg=SECONDARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR) # set color
    reanalyze_button.grid(row=row_offset, column=0, padx=10, pady=10)
    row_offset += 1

    # --- Back to Main Menu Button --- (Row 14)
    back_to_main_button = tk.Button(root, text="Back to Main Menu", command=back_to_main, font=("Arial", 10), bg=MAIN_MENU_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR) # set color
    back_to_main_button.grid(row=row_offset, column=0, padx=10, pady=10)
    row_offset += 1

    root.columnconfigure(0, weight=1)


# Modify show_missing_dates_input slightly for clarity
def show_missing_dates_input(selected_estate, selected_division, missing_dates_list):
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
    label_missing_dates_title = tk.Label(root, text=f"Masukkan data hujan untuk tanggal yang belum diinput ({selected_estate} - {selected_division}):", font=("Arial", 12, "bold"))
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
    submit_missing_dates_button = tk.Button(root, text="Submit Data", command=lambda: submit_missing_dates(selected_estate, selected_division, missing_dates_list), font=("Arial", 10), bg=PRIMARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)
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

# --- (Ensure the reset block is added to show_ESTATE_OPTIONS, show_add_rainfall_entry, etc.) ---


# %%
def show_ESTATE_OPTIONS():
    global label_estate_option, combobox_estate, submit_estate_button, back_button, current_menu, main_menu_button, df
    if not root_exists:
        return

    # --- ROW & COLUMN CONFIGURATION RESET ---
    for i in range(20): # Reset rows
        root.rowconfigure(i, weight=0)
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=0)
    # --- END CONFIGURATION ---

    hide_all_widgets()

    current_menu = "estate"

    label_estate_option = tk.Label(root, text=f"Pilih estate ({'/'.join(ESTATE_OPTIONS)}):", font=("Arial", 12))
    label_estate_option.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

    combobox_estate = ttk.Combobox(root, values=ESTATE_OPTIONS, width=30, font=("Arial", 10))
    combobox_estate.grid(row=1, column=0, padx=10, pady=10)

    label_estate_option = tk.Label(root, text="Pilih Divisi:", font=("Arial", 12))
    label_estate_option.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

    DIVISION_OPTIONS = ["1", "2", "3", "4", "5"]
    combobox_division = ttk.Combobox(root, values=DIVISION_OPTIONS, width=30, font=("Arial", 10))
    combobox_division.grid(row=3, column=0, padx=10, pady=10)

    submit_estate_button = tk.Button(root, text="Submit Estate", command=lambda: submit_estate(combobox_estate.get(), combobox_division.get()), font=("Arial", 10), bg=PRIMARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR) # Set color
    submit_estate_button.grid(row=4, column=0, padx=10, pady=10)

    back_button = tk.Button(root, text="Back", command=go_back, font=("Arial", 10), bg=SECONDARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR) # Set color
    back_button.grid(row=5, column=0, padx=10, pady=10)

    main_menu_button = tk.Button(root, text="Back to Main Menu", command=back_to_main, font=("Arial", 10), bg=MAIN_MENU_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR) # Set color
    main_menu_button.grid(row=6, column=0, padx=10, pady=10)

    root.columnconfigure(0, weight=1)


# %%
def show_estate_options_for_analysis():
    global label_estate_option, combobox_estate, submit_estate_button, back_button, current_menu, \
           entry_blok, entry_tanggal_rencana_pupuk, entry_peilscale, entry_tanggal_pupuk_terakhir, \
           combobox_jenis_pupuk_terakhir, combobox_rencana_jenis_pupuk, label_blok, label_tanggal_rencana_pupuk, \
           label_peilscale, label_tanggal_pupuk_terakhir, label_jenis_pupuk_terakhir, label_rencana_jenis_pupuk, \
           button_tanggal_rencana_pupuk, button_tanggal_pupuk_terakhir

    if not root_exists:
        return

    # --- ROW & COLUMN CONFIGURATION RESET ---
    for i in range(20): # Reset rows
        root.rowconfigure(i, weight=0)
    root.columnconfigure(0, weight=1) # Configure columns needed by THIS screen
    root.columnconfigure(1, weight=0) # Reset unused columns
    # --- END CONFIGURATION ---

    hide_all_widgets()
    current_menu = "estate_analysis"

    # --- Use sticky="ew" on ALL widgets ---
    label_estate_option = tk.Label(root, text=f"Pilih estate ({'/'.join(ESTATE_OPTIONS)}):", font=("Arial", 12))
    label_estate_option.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

    combobox_estate = ttk.Combobox(root, values=ESTATE_OPTIONS, width=30, font=("Arial", 10))
    combobox_estate.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
    
    label_estate_option = tk.Label(root, text="Pilih Divisi:", font=("Arial", 12))
    label_estate_option.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

    DIVISION_OPTIONS = ["1", "2", "3", "4", "5"]
    combobox_division = ttk.Combobox(root, values=DIVISION_OPTIONS, width=30, font=("Arial", 10))
    combobox_division.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

    label_blok = tk.Label(root, text="Masukkan Nama Blok:", font=("Arial", 12))
    label_blok.grid(row=4, column=0, padx=10, pady=5, sticky="ew")

    entry_blok = tk.Entry(root, font=("Arial", 10))
    entry_blok.grid(row=5, column=0, padx=10, pady=5, sticky="ew")

    label_tanggal_rencana_pupuk = tk.Label(root, text="Masukkan tanggal rencana pupuk:", font=("Arial", 12))
    label_tanggal_rencana_pupuk.grid(row=6, column=0, padx=10, pady=5, sticky="ew")

    entry_tanggal_rencana_pupuk = tk.Entry(root, font=("Arial", 10))
    entry_tanggal_rencana_pupuk.grid(row=7, column=0, padx=10, pady=5, sticky="ew")

    button_tanggal_rencana_pupuk = tk.Button(root, text="Select Date", command=lambda: get_date(entry_tanggal_rencana_pupuk), font=("Arial", 10), bg=SECONDARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR) #Added button and color
    button_tanggal_rencana_pupuk.grid(row=7, column=1, padx=5, pady=5)

    label_tanggal_pupuk_terakhir = tk.Label(root, text="Masukkan tanggal pupuk terakhir:", font=("Arial", 12))
    label_tanggal_pupuk_terakhir.grid(row=8, column=0, padx=10, pady=5, sticky="ew")

    entry_tanggal_pupuk_terakhir = tk.Entry(root, font=("Arial", 10))
    entry_tanggal_pupuk_terakhir.grid(row=9, column=0, padx=10, pady=5, sticky="ew")

    button_tanggal_pupuk_terakhir = tk.Button(root, text="Select Date", command=lambda: get_date(entry_tanggal_pupuk_terakhir), font=("Arial", 10), bg=SECONDARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR) #Added button and color
    button_tanggal_pupuk_terakhir.grid(row=9, column=1, padx=5, pady=5)

    label_peilscale = tk.Label(root, text="Masukkan nilai Peilscale:", font=("Arial", 12))
    label_peilscale.grid(row=10, column=0, padx=10, pady=5, sticky="ew")

    entry_peilscale = tk.Entry(root, font=("Arial", 10))
    entry_peilscale.grid(row=11, column=0, padx=10, pady=5, sticky="ew")

    label_jenis_pupuk_terakhir = tk.Label(root, text="Masukkan jenis pupuk terakhir:", font=("Arial", 12))
    label_jenis_pupuk_terakhir.grid(row=12, column=0, padx=10, pady=5, sticky="ew")

    combobox_jenis_pupuk_terakhir = ttk.Combobox(root, values=FERTILIZER_TYPE, width=30, font=("Arial", 10))
    combobox_jenis_pupuk_terakhir.grid(row=13, column=0, padx=10, pady=5, sticky="ew")

    label_rencana_jenis_pupuk = tk.Label(root, text="Masukkan rencana jenis pupuk:", font=("Arial", 12))
    label_rencana_jenis_pupuk.grid(row=14, column=0, padx=10, pady=5, sticky="ew")

    combobox_rencana_jenis_pupuk = ttk.Combobox(root, values=FERTILIZER_TYPE, width=30, font=("Arial", 10))
    combobox_rencana_jenis_pupuk.grid(row=15, column=0, padx=10, pady=5, sticky="ew")

    submit_estate_button = tk.Button(root, text="Submit", command=lambda: submit_analysis(
        combobox_estate.get(),
        combobox_division.get(),
        entry_blok.get(),
        entry_peilscale.get(),
        combobox_jenis_pupuk_terakhir.get(),
        entry_tanggal_pupuk_terakhir.get(),
        combobox_rencana_jenis_pupuk.get(),
        entry_tanggal_rencana_pupuk.get()
    ), font=("Arial", 10), bg=PRIMARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR) # Set color
    submit_estate_button.grid(row=16, column=0, padx=10, pady=10)

    back_button = tk.Button(root, text="Back", command=go_back, font=("Arial", 10), bg=SECONDARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR) # Set color
    back_button.grid(row=17, column=0, padx=10, pady=10)

    root.columnconfigure(0, weight=1)


# %%
def show_ESTATE_OPTIONS_for_add_rainfall():
    global label_estate_option, combobox_estate, submit_estate_check_button, back_button, current_menu, previous_menu

    if not root_exists:
        return

    hide_all_widgets()
    current_menu = "estate_add_rainfall"
    previous_menu = "rainfall"

    # --- ROW & COLUMN RESET for ROOT ---
    for i in range(20): root.rowconfigure(i, weight=0)
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=0)
    # --- END ROOT RESET ---

    label_estate_option = tk.Label(root, text=f"Pilih estate ({'/'.join(ESTATE_OPTIONS)}):", font=("Arial", 12))
    label_estate_option.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

    combobox_estate = ttk.Combobox(root, values=ESTATE_OPTIONS, width=30, font=("Arial", 10))
    combobox_estate.grid(row=1, column=0, padx=10, pady=10)

    label_estate_option = tk.Label(root, text="Pilih Divisi:", font=("Arial", 12))
    label_estate_option.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

    DIVISION_OPTIONS = ["1", "2", "3", "4", "5"]
    combobox_division = ttk.Combobox(root, values=DIVISION_OPTIONS, width=30, font=("Arial", 10))
    combobox_division.grid(row=3, column=0, padx=10, pady=10)

    submit_estate_check_button = tk.Button(root, text="Check Estate", command=lambda: check_existing_rainfall(combobox_estate.get(), combobox_division.get(), current_time_date), font=("Arial", 10), bg=PRIMARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR) # Set color
    submit_estate_check_button.grid(row=4, column=0, padx=10, pady=10)

    back_button = tk.Button(root, text="Back", command=go_back, font=("Arial", 10), bg=SECONDARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR) # Set color
    back_button.grid(row=5, column=0, padx=10, pady=10)

    main_menu_button = tk.Button(root, text="Back to Main Menu", command=back_to_main, font=("Arial", 10), bg=MAIN_MENU_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR) # Set color
    main_menu_button.grid(row=6, column=0, padx=10, pady=10)

    root.columnconfigure(0, weight=1)


# %%
def show_rainfall_data_entry(selected_estate, selected_division):
    global previous_menu, entry_update_rainfall, label_update_rainfall, back_button, main_menu_button, submit_update_rainfall_button, df

    if not root_exists:
        return
    
    # --- Load Initial Data ---
    try:
        print("Loading data...")
        df = load_estate_database(selected_estate, selected_division)
        # messagebox.showinfo("DEBUG", f"df: {df}")

        if df.empty:
            messagebox.showerror("Startup Error", "Gagal memuat data.\nAplikasi akan ditutup.")
            if root: root.destroy()
            return
        print("Data loaded successfully.")
        # messagebox.showinfo("DEBUG", f"Data loaded successfully")
    except Exception as e:
        messagebox.showerror("Startup Error", f"Connection to {TARGET_ENVIRONMENT} DB failed!\nReason: {e}")

    hide_all_widgets()

    previous_menu = "estate"

    print(f"show_rainfall_data_entry df.head():\n{df.head(1)}")
    estate_data = df
    # messagebox.showinfo("DEBUG", f"estate_data: {estate_data}")

    if not estate_data.empty: 
        last_date = estate_data['Date'].iloc[0] 
        last_rainfall = estate_data['Daily Rainfall (mm)'].iloc[0]

        label_update_rainfall = tk.Label(root, text=f"Update Data Hujan (mm)", font=("Arial", 12, "bold"))
        label_update_rainfall.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        label_update_rainfall = tk.Label(root, text=f"Untuk {selected_estate} - {selected_division} Pada Tanggal {last_date}:", font=("Arial", 12))
        label_update_rainfall.grid(row=3, column=0, padx=10, pady=10, sticky="ew")

        entry_update_rainfall = tk.Entry(root, font=("Arial", 10))
        entry_update_rainfall.insert(0, str(last_rainfall))  
        entry_update_rainfall.grid(row=4, column=0, padx=10, pady=10, sticky="ew")

        submit_update_rainfall_button = tk.Button(root, text="Submit Rainfall", command=lambda: submit_update_rainfall(selected_estate, selected_division, last_date, entry_update_rainfall.get()), font=("Arial", 10), bg=PRIMARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR) # set color
        submit_update_rainfall_button.grid(row=5, column=0, padx=10, pady=10)

        back_button = tk.Button(root, text="Back", command=go_back, font=("Arial", 10), bg=SECONDARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR) # set color
        back_button.grid(row=6, column=0, padx=10, pady=10)

        main_menu_button = tk.Button(root, text="Back to Main Menu", command=back_to_main, font=("Arial", 10), bg=MAIN_MENU_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR) # set color
        main_menu_button.grid(row=7, column=0, padx=10, pady=10)

        root.columnconfigure(0, weight=1)
    else:
        label_no_data = tk.Label(root, text=f"No rainfall data found for {selected_estate}.", font=("Arial", 12))
        label_no_data.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        back_button = tk.Button(root, text="Back", command=go_back, font=("Arial", 10), bg=SECONDARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR) # set color
        back_button.grid(row=3, column=0, padx=10, pady=10)

        main_menu_button = tk.Button(root, text="Back to Main Menu", command=back_to_main, font=("Arial", 10), bg=MAIN_MENU_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR) # set color
        main_menu_button.grid(row=4, column=0, padx=10, pady=10)

        root.columnconfigure(0, weight=1)

# %%
def show_add_rainfall_entry(selected_estate, selected_division, date):
    global entry_daily_rainfall, label_daily_rainfall, submit_add_rainfall_button, previous_menu

    if not root_exists: return

    # --- ROW & COLUMN RESET for ROOT ---
    for i in range(20): root.rowconfigure(i, weight=0)
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=0)
    # --- END ROOT RESET ---

    hide_all_widgets()
    previous_menu = "missing_dates_input"

    # --- COLUMN CONFIGURATION (Add Reset for Column 1) ---
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=0)
    # --- END COLUMN CONFIGURATION ---

    # --- FIX THE LABEL TEXT ---
    label_input_rainfall = tk.Label(root, text=f"Data Hujan (mm) Baru", font=("Arial", 12, "bold"))
    label_input_rainfall.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

    label_daily_rainfall = tk.Label(root, text=f"{selected_estate} - {selected_division} pada tanggal {date}", font=("Arial", 12))
    label_daily_rainfall.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

    entry_daily_rainfall = tk.Entry(root, font=("Arial", 10))
    entry_daily_rainfall.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

    submit_add_rainfall_button = tk.Button(root, text="Submit Rainfall", command=lambda: submit_estate_for_add_rainfall(selected_estate, selected_division, date, entry_daily_rainfall.get()), font=("Arial", 10), bg=PRIMARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)
    submit_add_rainfall_button.grid(row=3, column=0, padx=10, pady=10)

    back_button = tk.Button(root, text="Back", command=go_back, font=("Arial", 10), bg=SECONDARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)
    back_button.grid(row=4, column=0, padx=10, pady=10)

    main_menu_button = tk.Button(root, text="Back to Main Menu", command=back_to_main, font=("Arial", 10), bg=MAIN_MENU_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)
    main_menu_button.grid(row=5, column=0, padx=10, pady=10)
    root.columnconfigure(0, weight=1)


# %% [markdown]
#  ## 10. GUI - Navigation & Action Functions

# %%
def submit_analysis(selected_estate, selected_division, blok, peilscale,
                    jenis_pupuk_terakhir, tanggal_pupuk_terakhir_str,
                    rencana_jenis_pupuk, tanggal_rencana_pupuk_str):
    global df, username_var

    if not root_exists: return

    # --- Load Initial Data ---
    try:
        print("Loading data...") # Feedback
        df = load_estate_database(selected_estate, selected_division)
        if df.empty:
            messagebox.showerror("Startup Error", "Gagal memuat data.\nAplikasi akan ditutup.")
            if root: root.destroy()
            return
        print("Data loaded successfully.") # Feedback
    except Exception as e:
        messagebox.showerror("Startup Error", f"Connection to {TARGET_ENVIRONMENT} DB failed!\nReason: {e}")

    # --- Basic Input Validation ---
    if not selected_estate: messagebox.showerror("Error", "Tolong masukkan nama estate."); return
    if selected_estate not in ESTATE_OPTIONS: messagebox.showerror("Error", f"Nama estate invalid: '{selected_estate}'."); return
    if not selected_division: messagebox.showerror("Error", "Tolong masukkan nomor divisi."); return
    if selected_division not in DIVISION_OPTIONS: messagebox.showerror("Error", f"Nomor divisi invalid: '{selected_division}'."); return
    if not blok: messagebox.showerror("Error", "Tolong masukkan nama blok."); return
    if not tanggal_rencana_pupuk_str: messagebox.showerror("Error", "Tolong masukkan tanggal rencana pupuk."); return
    if not peilscale: messagebox.showerror("Error", "Masukkan nilai peilscale."); return
    if not tanggal_pupuk_terakhir_str: messagebox.showerror("Error", "Tolong masukkan tanggal pupuk terakhir."); return
    if not jenis_pupuk_terakhir: messagebox.showerror("Error", "Tolong masukkan jenis pupuk terakhir."); return
    if not rencana_jenis_pupuk: messagebox.showerror("Error", "Tolong masukkan rencana jenis pupuk."); return

    # --- Type/Format Validation ---
    try:
        # Use %Y-%m-%d as returned by tkcalendar's get_date()
        tanggal_rencana_pupuk_dt = datetime.datetime.strptime(tanggal_rencana_pupuk_str, "%Y-%m-%d")
        tanggal_pupuk_terakhir_dt = datetime.datetime.strptime(tanggal_pupuk_terakhir_str, "%Y-%m-%d")
    except ValueError:
        # Try the other format just in case user typed it manually
        try:
             tanggal_rencana_pupuk_dt = datetime.datetime.strptime(tanggal_rencana_pupuk_str, "%d/%m/%Y")
             tanggal_pupuk_terakhir_dt = datetime.datetime.strptime(tanggal_pupuk_terakhir_str, "%d/%m/%Y")
        except ValueError:
             messagebox.showerror("Error", "Format tanggal tidak valid. Gunakan kalender atau format YYYY-MM-DD.")
             return

    try:
        peilscale_int = int(peilscale)
    except ValueError:
        messagebox.showerror("Error", "Nilai peilscale harus berupa angka integer.")
        return
    
    # --- Duplicate Data Check ---
    duplicate_rows = df[df.duplicated(subset=['Date'], keep=False)]

    if not duplicate_rows.empty:
        # Find the dates that occur multiple times
        duplicate_dates = duplicate_rows['Date'].value_counts()
        duplicate_dates_multiple = duplicate_dates[duplicate_dates > 1]
        
        # Show the message box with the duplicate dates
        duplicate_dates_str = "\n".join([f"{date}: {count} kemunculan" for date, count in duplicate_dates_multiple.items()])
        messagebox.showerror("Error", f"Terdapat data duplikat untuk tanggal:\n{duplicate_dates_str}\nSilahkan hubungi agronomy team")
        return
    else:
        print("No duplicate rows found.")

    # --- Missing Data Check (Full Range) ---
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.date
    available_dates = set(df['Date'].dropna())

    # Define full date range from first date in data up to one day before the planned date
    start_date = min(available_dates)
    end_date = tanggal_rencana_pupuk_dt.date() - datetime.timedelta(days=1)
    expected_dates = set(pd.date_range(start=start_date, end=end_date).date)

    # Find missing dates
    missing_dates = sorted(expected_dates - available_dates)

    if missing_dates:
        missing_str = "\n".join([d.strftime("%Y-%m-%d") for d in missing_dates])
        messagebox.showwarning(
            "Data Curah Hujan Tidak Lengkap",
            f"Ditemukan data curah hujan yang hilang dari {start_date} sampai {end_date}:\n\n{missing_str}\n\nSilakan lengkapi data sebelum melanjutkan analisis."
        )
        return

    # --- Rainfall Data Validation ---
    if not validate_rainfall_data_exists(df, selected_estate, selected_division, current_time_date):
        return # Exit if rainfall validation fails
    
    # Create ID Analisa
    random_characters = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    id_analisa = f"PA-{current_time_date.strftime('%Y%m%d')}-{random_characters}"

    # --- Proceed with analysis ---
    current_daily_rainfall, status, reason, recommendation = analyze_fertilizer(
        datetime.datetime.now(CURRENT_TIMEZONE), username, selected_estate, selected_division, blok, id_analisa, df,
        peilscale_int, jenis_pupuk_terakhir, tanggal_pupuk_terakhir_dt, # Pass datetime object
        rencana_jenis_pupuk, tanggal_rencana_pupuk_dt # Pass datetime object
    )

    if recommendation is None:
        recommendation = "Tidak ada rekomendasi yang tersedia."

    # Display the results - Pass strings for display as they were entered/selected
    display_analysis_results(
        selected_estate, selected_division, blok, tanggal_rencana_pupuk_str, peilscale, # Pass original peilscale string
        tanggal_pupuk_terakhir_str, jenis_pupuk_terakhir, rencana_jenis_pupuk,
        username, current_daily_rainfall, status, id_analisa, reason, recommendation
    )

# %%
def submit_missing_dates(selected_estate, selected_division, missing_dates_list):
    """Processes the input for missing rainfall dates."""
    global df, missing_dates_widgets # Remove current_time_date from global if not needed elsewhere in this func

    if not root_exists:
        return

    rainfall_inputs = {}
    try:
        # --- Validation Phase ---
        for date_item in missing_dates_list: # Use different variable name to avoid confusion
            print(f"Validating date: {date_item}, Type: {type(date_item)}") # Debug print

            # --- Gracefully handle date object ---
            if isinstance(date_item, datetime.datetime) or hasattr(date_item, 'date'): # Check if it's datetime or has .date() (like Timestamp)
                 date_obj = date_item.date()
            elif isinstance(date_item, datetime.date):
                 date_obj = date_item # It's already a date object
            else:
                 # Handle unexpected type if necessary
                 messagebox.showerror("Error", f"Tipe data tanggal tidak dikenal: {type(date_item)}")
                 return
            # --- End of handling ---

            # Now use date_obj (which is guaranteed to be a datetime.date) as the key
            if date_obj not in missing_dates_widgets:
                 messagebox.showerror("Error", f"Widget input tidak ditemukan untuk tanggal {format_datetime(date_obj)}")
                 print(f"Key error: {date_obj} not in {missing_dates_widgets.keys()}") # Debug print
                 return

            entry_widget = missing_dates_widgets[date_obj]["entry"]
            rainfall_str = entry_widget.get()
            if not rainfall_str:
                messagebox.showerror("Error", f"Nilai curah hujan untuk tanggal {format_datetime(date_obj)} tidak boleh kosong.")
                return

            rainfall_val = float(rainfall_str)
            if rainfall_val < 0:
                messagebox.showerror("Error", f"Nilai curah hujan untuk tanggal {format_datetime(date_obj)} tidak boleh negatif.")
                return
            rainfall_inputs[date_obj] = rainfall_val # Store validated value, keyed by date_obj

        # --- Processing Phase ---
        # Sort dates to ensure correct calculation order
        sorted_dates = sorted(rainfall_inputs.keys())

        for date_obj in sorted_dates:
            rainfall_val = rainfall_inputs[date_obj]
            print(f"Processing missing date: {format_datetime(date_obj)}, Rainfall: {rainfall_val}") # Debug print
            df = calculate_rainfall(df, date_obj, rainfall_val, selected_estate, selected_division)
            root.update_idletasks() # Update UI briefly


        messagebox.showinfo("Sukses", f"Data hujan untuk tanggal yang belum diinput ({len(sorted_dates)} hari) telah berhasil ditambahkan.")

        # --- Proceed to Today's Input ---
        today_now = datetime.datetime.now(CURRENT_TIMEZONE) # Get FRESH datetime HERE
        today_date_obj = today_now.date()          # Extract date part correctly

        # Ensure 'Date' column is datetime before comparison
        if not pd.api.types.is_datetime64_any_dtype(df['Date']):
             df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df.dropna(subset=['Date'], inplace=True) # Drop rows where conversion failed

        estate_data_today = df[(df['Estate'] == selected_estate) & (df['Division'] == selected_division) & (df['Date'].dt.date == today_date_obj)]

        if estate_data_today.empty:
            print("Proceeding to input today's rainfall...")
            # Pass today_date_obj (which is datetime.date)
            show_add_rainfall_entry(selected_estate, selected_division, today_date_obj)
        else:
            print("Today's rainfall already exists after filling gaps.")
            messagebox.showinfo("Info", f"Data hujan untuk hari ini ({format_datetime(today_date_obj)}) sudah ada.")
            back_to_main()

    except ValueError:
        messagebox.showerror("Error", "Input curah hujan tidak valid. Harap masukkan angka.")
        return
    except Exception as e:
        # Print detailed traceback
        import traceback
        print("--- Traceback ---")
        traceback.print_exc()
        print("--- End Traceback ---")
        messagebox.showerror("Error", f"Terjadi kesalahan saat memproses data: {e}")
        print(f"Error during submit_missing_dates: {e}") # Log the error
        return


# %%
def close_success_and_go_back():
    """Closes the success window and returns to the main menu."""
    global success_window
    if not root_exists:
        return
    
    if success_window:
        success_window.destroy()  # Close the success window
        success_window = None  # Set to None after closing
    back_to_main()  # Go back to the main menu


# %%
def show_success_window():
    """Displays a success window with a button to return to the main menu."""
    global success_window, root  # Declare success_window as global
    if not root_exists:
        return
    
    # Create a new top-level window
    success_window = tk.Toplevel(root)
    success_window.title("Success")
    success_window.geometry("300x100")  # Adjust size as needed

    # Make the new window modal (prevent interaction with the main window)
    success_window.transient(root) 
    success_window.grab_set()   

    label_success = tk.Label(success_window, text="Update data hujan sukses!", font=("Arial", 12))
    label_success.pack(pady=10)
    
    button_back_to_main = tk.Button(success_window, text="Back to Main Menu", command=close_success_and_go_back, font=("Arial", 10), bg=MAIN_MENU_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR) # set color
    button_back_to_main.pack(pady=5)
    
    success_window.columnconfigure(0, weight=1)


# %%
def submit_update_rainfall(selected_estate, selected_division, date, new_rainfall):
    """Submits the updated rainfall data to the database."""
    global previous_menu, df, entry_update_rainfall
    if not root_exists:
        return
    
    try:
        new_rainfall = float(new_rainfall)
        if new_rainfall < 0:
            raise ValueError("Rainfall cannot be negative.")
    except ValueError:
        tk.messagebox.showerror("Error", "Nilai curah hujan invalid. Tolong masukkan bilangan positif.")
        return
    
    # Recalculate dependent columns using calculate_rainfall
    df = calculate_rainfall(df, date, new_rainfall, selected_estate, selected_division, update=True)

    show_success_window()

# %%
def submit_estate_for_add_rainfall(selected_estate, selected_division, date, new_rainfall):
    global previous_menu, df

    if not root_exists:
        return
    
    if selected_estate not in ESTATE_OPTIONS:
        tk.messagebox.showerror("Error", f"Nama estate invalid: '{selected_estate}'. Tolong pilih antara: {', '.join(ESTATE_OPTIONS)}")
        return
    
    DIVISION_OPTIONS = ["1", "2", "3", "4", "5"]
    if selected_division not in DIVISION_OPTIONS:
        tk.messagebox.showerror("Error", f"Nomor divisi invalid: '{selected_division}'. Tolong pilih antara: {', '.join(ESTATE_OPTIONS)}")
        return
    
    try:
        new_rainfall = float(new_rainfall)
        if new_rainfall < 0:
            raise ValueError("Nilai curah hujan tidak boleh negatif.")
    except ValueError:
        tk.messagebox.showerror("Error", "Nilai curah hujan invalid. Tolong masukkan bilangan positif.")
        return
    
    df = calculate_rainfall(df, date, new_rainfall, selected_estate, selected_division)
    
    show_success_window()


# %%
def check_existing_rainfall(selected_estate, selected_division, current_time_date):
    global df, previous_menu

    if not root_exists:
        return
    
    # --- Load Initial Data ---
    try:
        # messagebox.showinfo("DEBUG", f"Loading data based on {selected_estate} - {selected_division}.")
        print(f"Loading data based on {selected_estate} - {selected_division}.") # Feedback
        df = load_estate_database(selected_estate, selected_division)
        if df.empty:
            messagebox.showerror("Startup Error", "Gagal memuat data.\nAplikasi akan ditutup.")
            if root: root.destroy()
            return
        print("Data loaded successfully.") # Feedback
        # messagebox.showinfo("DEBUG", f"Loading data based on {selected_estate} - {selected_division} success.")
    except Exception as e:
        messagebox.showerror("Startup Error", f"Connection to {TARGET_ENVIRONMENT} DB failed!\nReason: {e}")


    # --- Input Validation ---
    if not selected_estate:
        messagebox.showerror("Error", "Silakan pilih estate terlebih dahulu.")
        return
    if selected_estate not in ESTATE_OPTIONS:
        messagebox.showerror("Error", f"Nama estate invalid: '{selected_estate}'. Tolong pilih antara: {', '.join(ESTATE_OPTIONS)}")
        return
    
    DIVISION_OPTIONS = ["1", "2", "3", "4", "5"]
    if not selected_division:
        messagebox.showerror("Error", "Silakan pilih divisi terlebih dahulu.")
        return
    if selected_division not in DIVISION_OPTIONS:
        messagebox.showerror("Error", f"Nomor divisi invalid: '{selected_division}'. Tolong pilih antara: {', '.join(DIVISION_OPTIONS)}")
        return

    # --- Check for Missing Dates FIRST ---
    # messagebox.showinfo("DEBUG", f"Getting missing dates for {selected_estate} - {selected_division}.")
    missing_dates, last_reported_time, total_missing_dates = get_missing_dates(df, current_time_date)
    # messagebox.showinfo("DEBUG", f"Getting missing dates for {selected_estate} - {selected_division}. Done.")

    print(f"Checking estate: {selected_estate}, divisi: {selected_division}") # Debug
    print(f"Last reported: {last_reported_time}, Missing: {total_missing_dates}") # Debug
    print(f"Missing dates list: {missing_dates}") # Debug

    if total_missing_dates > 0:
        # --- Show Missing Dates Input Screen ---
        print(f"Found {total_missing_dates} missing dates. Showing input screen.") # Debug
        # It's generally better *not* to show a blocking error here, but proceed to the input screen
        # messagebox.showinfo("Info", f"Terdapat {total_missing_dates} hari data hujan yang hilang untuk estate {selected_estate} sejak {format_datetime(last_reported_time + timedelta(days=1))}.\n\nAnda akan diminta untuk mengisi data tersebut terlebih dahulu.")
        show_missing_dates_input(selected_estate, selected_division, missing_dates)
        # previous_menu is set inside show_missing_dates_input

    else:
        # --- No Missing Dates, Check Today's Data ---
        print("No missing dates found. Checking today's data.") # Debug
        estate_data_today = df[(df['Estate'] == selected_estate) & (df['Division'] == selected_division) & (df['Date'] == current_time_date)]

        if estate_data_today.empty:
            # --- Today's Data Missing: Show Input Screen for Today ---
            print("Today's data not found. Showing add rainfall entry.") # Debug
            show_add_rainfall_entry(selected_estate, selected_division, current_time_date)
            previous_menu = "estate_add_rainfall"
        else:
            # --- Today's Data Exists ---
            print("Today's data already exists.") # Debug
            estate_rainfall_today = df['Daily Rainfall (mm)'].iloc[0]
            messagebox.showinfo("Info", f"Data hujan untuk estate {selected_estate}, divisi {selected_division} pada hari ini ({format_datetime(current_time_date)}) sudah dimasukkan sebesar {estate_rainfall_today}."
                                "\nSilahkan update data melalui menu 'Masukkan Data Hujan' → 'Update Data Hujan Terakhir' ")
            back_to_main()

# %%
def go_back():
    """Handles navigation back; uses after_idle and hide_all_widgets."""
    global previous_menu
    if not root_exists:
        return
    
    if previous_menu == "missing_dates_input":
        hide_all_widgets()
        root.after_idle(show_ESTATE_OPTIONS_for_add_rainfall)
        previous_menu = "rainfall"
    elif previous_menu == "main":
        hide_all_widgets()
        root.after_idle(create_main_widgets)
    elif previous_menu == "rainfall":
        hide_all_widgets()
        root.after_idle(show_rainfall_options)
        previous_menu = "main"
    elif previous_menu == "estate":
        hide_all_widgets()
        root.after_idle(show_ESTATE_OPTIONS)
        previous_menu = "rainfall"
    elif previous_menu == "estate_analysis":
        hide_all_widgets()
        root.after_idle(create_main_widgets)
        previous_menu = "main"
    elif previous_menu == "estate_add_rainfall":
        hide_all_widgets()
        root.after_idle(show_rainfall_options)
        previous_menu = "rainfall"
    elif previous_menu == "analysis_results":
        hide_all_widgets()
        root.after_idle(show_estate_options_for_analysis)
        previous_menu = "estate_analysis"


# %%
def back_to_main():
    """Hides all widgets and recreates the main menu."""
    global previous_menu
    if not root_exists:
        return
    hide_all_widgets()
    create_main_widgets()
    previous_menu = "main"


# %%
def go_to_reanalyze():
    global previous_menu
    if not root_exists:
        return
    hide_all_widgets()
    show_estate_options_for_analysis()
    previous_menu = "estate_analysis" 


# %%
def submit_estate_for_analysis(selected_estate, nama_blok, peilscale, jenis_terakhir, tanggal_terakhir, rencana_jenis, tanggal_rencana):
    global previous_menu, username_var, df
    if not root_exists:
        return
    
    if selected_estate not in ESTATE_OPTIONS:
        tk.messagebox.showerror("Error", f"Nama estate invalid: '{selected_estate}'. Tolong pilih antara: {', '.join(ESTATE_OPTIONS)}")
        return
    
    # Get current time
    date_input = datetime.now(CURRENT_TIMEZONE)

    # Get the username
    username = username_var.get()

    # Convert string to integer
    peilscale = int(peilscale)

    # Create ID Analisa
    random_characters = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    id_analisa = f"PA-{current_time_date.strftime('%Y%m%d')}-{random_characters}"

    current_daily_rainfall, status, reason, recommendation = analyze_fertilizer(date_input, username, selected_estate, nama_blok, id_analisa, df, peilscale, jenis_terakhir, tanggal_terakhir, rencana_jenis, tanggal_rencana)

    if recommendation is None:
        recommendation = "Tidak ada rekomendasi yang tersedia."

    # Display the results
    display_analysis_results(
        selected_estate, nama_blok, tanggal_rencana, peilscale, tanggal_terakhir,
        jenis_terakhir, rencana_jenis, username, current_daily_rainfall, status, id_analisa, id_analisa, reason, recommendation
    )
    # previous_menu = "main"  # No longer going back to main immediately
    # cancel_to_main()


# %%
def submit_estate(selected_estate, selected_division):
    global previous_menu, df
    if not root_exists:
        return
    
    if selected_estate not in ESTATE_OPTIONS:
        tk.messagebox.showerror("Error", f"Nama estate invalid: '{selected_estate}'. Tolong pilih antara: {', '.join(ESTATE_OPTIONS)}")
        return
    
    DIVISION_OPTIONS = ["1", "2", "3", "4", "5"]
    if selected_division not in DIVISION_OPTIONS:
        tk.messagebox.showerror("Error", f"Nomor divisi invalid: '{selected_division}'. Tolong pilih antara: {', '.join(DIVISION_OPTIONS)}")
        return

    print(f"Selected Estate: {selected_estate}")
    print(f"Selected Division: {selected_division}")
    
    show_rainfall_data_entry(selected_estate, selected_division)


# %%
def goto_input_hujan():
    global previous_menu, entry_username
    if not root_exists: return

    # --- ROW & COLUMN CONFIGURATION RESET ---
    for i in range(20): # Reset rows
        root.rowconfigure(i, weight=0)
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=0)
    # --- END CONFIGURATION ---

    # Check username for the first time
    username = entry_username.get()
    if not username.strip():
        messagebox.showerror("Error", "Tolong masukkan username.")
        return

    previous_menu = "main"
    hide_all_widgets()
    show_rainfall_options()


# %%
def goto_analisa_pemupukan():
    global previous_menu, entry_username
    if not root_exists: return

    # --- ROW & COLUMN CONFIGURATION RESET ---
    for i in range(20): # Reset rows
        root.rowconfigure(i, weight=0)
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=0)
    # --- END CONFIGURATION ---

    # Check username for the first time
    username = entry_username.get()
    if not username.strip():
        messagebox.showerror("Error", "Tolong masukkan username.")
        return
    
    previous_menu = "main"
    hide_all_widgets()
    show_estate_options_for_analysis()

# %%
def goto_update_rainfall():
    global previous_menu
    if not root_exists:
        return
    
    # --- ROW & COLUMN CONFIGURATION RESET ---
    for i in range(20): # Reset rows
        root.rowconfigure(i, weight=0)
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=0)
    # --- END CONFIGURATION ---
    
    print(f"Selected Rainfall Option: Update Data Hujan Terakhir")
    previous_menu = "rainfall"

    show_ESTATE_OPTIONS()


# %%
def goto_add_rainfall():
    global previous_menu
    if not root_exists:
        return
    
    # --- ROW & COLUMN CONFIGURATION RESET ---
    for i in range(20): # Reset rows
        root.rowconfigure(i, weight=0)
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=0)
    # --- END CONFIGURATION ---
    
    print(f"Selected Rainfall Option: Masukkan Data Hujan Baru")

    show_ESTATE_OPTIONS_for_add_rainfall()


# %% [markdown]
#  ## 11. GUI - Window Management

# %%
def on_closing():
    global root_exists
    root_exists = False
    if root:
       root.destroy()

# %% [markdown]
#  ## 12. Main Application (`main_process`)

# %%
def main_process():
    # Define all globals used within this function and others it calls
    global root, previous_menu, root_exists, current_menu, df, \
           username_var, username, \
           rain_data, output_data, \
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
           label_status, label_id_analisa, label_reason, label_recommendation, label_selected_estate, \
           label_nama_blok, label_tanggal_rencana, label_peilscale_value, \
           label_tanggal_terakhir_value, label_jenis_terakhir_value, \
           label_rencana_jenis_value, back_to_main_button, reanalyze_button, \
           label_saved_username, label_no_data, splash_label, splash_button


    # --- Initialize App ---
    root = tk.Tk()
    root.title("Engine Waktu Aplikasi Pemupukan ({TARGET_ENVIRONMENT})")
    root.attributes('-fullscreen', True)

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
    label_username = None
    entry_username = None
    exit_button = None
    label_rainfall_option = None
    combobox_rainfall = None
    submit_rainfall_button = None
    back_button = None
    label_estate_option = None
    combobox_estate = None
    submit_estate_button = None
    entry_blok = None
    label_tanggal_rencana_pupuk = None
    entry_tanggal_rencana_pupuk = None
    label_peilscale = None
    entry_peilscale = None
    label_tanggal_pupuk_terakhir = None
    entry_tanggal_pupuk_terakhir = None
    label_jenis_pupuk_terakhir = None
    combobox_jenis_pupuk_terakhir = None
    label_rencana_jenis_pupuk = None
    combobox_rencana_jenis_pupuk = None
    submit_estate_add_rainfall_button = None
    entry_daily_rainfall = None
    label_daily_rainfall = None
    label_blok = None
    button_input_hujan = None
    button_analisa_pemupukan = None
    button_update_rainfall = None
    button_add_rainfall = None
    label_tanggal_analisa = None
    label_nama_user = None
    label_curah_hujan = None
    label_status = None
    label_id_analisa = None
    label_reason = None
    label_recommendation = None
    label_selected_estate = None
    label_nama_blok = None
    label_tanggal_rencana = None
    label_peilscale_value = None
    label_tanggal_terakhir_value = None
    label_jenis_terakhir_value = None
    label_rencana_jenis_value = None
    back_to_main_button = None
    reanalyze_button = None
    main_menu_button = None
    label_update_rainfall = None
    entry_update_rainfall = None
    submit_update_rainfall_button = None
    label_saved_username = None
    missing_dates_widgets = {}
    label_missing_dates_title = None
    submit_missing_dates_button = None
    splash_label = None
    splash_button = None
    
    # --- Setup Window Closing Protocol ---
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.columnconfigure(0, weight=1) # Configure root column initially

    root.bind('<Escape>', lambda event: on_closing())

    # --- Start GUI ---
    create_splash_screen()
    root.iconbitmap(resource_path("Logo_Pancaran_Agro-removebg-preview.ico"))  # Make sure the path is correct
    root.mainloop()

# %% [markdown]
#  ## 13. Execution Block

# %%
if __name__ == "__main__":
    main_process()


