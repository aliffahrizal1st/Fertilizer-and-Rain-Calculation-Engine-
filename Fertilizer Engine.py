# %% [markdown]
# # **ENGINE WAKTU APLIKASI PUPUK 2025**

# %% [markdown]
# # Library and Utilities

# %%
import pytz
import sys
import os
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
from oauth2client.service_account import ServiceAccountCredentials
import tkinter as tk
from tkinter import ttk, messagebox, StringVar
import subprocess

# %%
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# %%
#Autentikasi
json_path = resource_path('fourth-landing-316602-e06c4c4e3ba6.json')
sheet_url = "https://docs.google.com/spreadsheets/d/1f9taqCGKFtFVDmNIWFgqujf8yJLmshCFJ7j4_CgGl2Q/edit?usp=sharing"
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# %%
# Grup Pupuk
fertilizer_groups = {
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

synergize_groups = {
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

super_slow = {
    "Dolomite": ["Dolomite"]
}

hygroscopic = {
    "Urea": ["Urea"],
    "HGFB": ["HGFB"],
    "CuSO4": ["CuSO4"],
    "MOP": ["MOP"]
}

estate = ["Inti", "Plasma"]

interval_table = {
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

fertilizer_type = ["NPK 13", "NPK 15", "NPK 12", "Dolomite", "Urea", "MOP", "HGFB", "CuSO4", "Zincop Chelated", "Kieserite", "RP", "Kaptan", "TSP"]

# %%
border_line = "=================================================================================="

# %%
current_timezone = pytz.timezone('Asia/Jakarta')
date_input = datetime.now(current_timezone)
current_time_date = datetime.now(current_timezone).date()

# %% [markdown]
# # Functions

# %%
def get_missing_dates(df, estate_name, current_time_date):
  # Filter the DataFrame to include only records for the specified estate
  estate_data = df[(df['Estate'] == estate_name)]

  # Get the last reported time
  if not estate_data.empty:
    last_reported_time = estate_data['Date'].iloc[-1].date()
  else:
    last_reported_time = None  # Return None if no data found for the estate

  # Check for missing dates between the last reported time and the current time
  if last_reported_time:
    missing_dates = pd.date_range(last_reported_time + pd.Timedelta(days=1), current_time_date - pd.Timedelta(days=1))
    total_missing_dates = len(missing_dates)
  else:
    missing_dates = pd.DatetimeIndex([])  # Empty DatetimeIndex if no last reported time
    total_missing_dates = 0

  return missing_dates, last_reported_time, total_missing_dates

# %%
def format_datetime(dt):
    dt_copy = dt
    return dt_copy.strftime('%d/%m/%Y')

def format_datetimehour(dt):
    dt_copy = dt
    return dt_copy.strftime('%d/%m/%Y %H:%M:%S')

# %%
def validate_date(last_reported_time, current_time_date):
  if  last_reported_time == current_time_date:
    return True
  else:
    return False

# %%
def calculate_rainfall(in_df, current_time_date, current_daily_rainfall, estate_name):
  global sheet_data

  # Create cache data
  df = in_df.copy()

  # Filter the DataFrame to include only records for the specified estate
  df = df[(df['Estate'] == estate_name)]

  # Hitung Accumulation Rainfall -29 days
  df.loc[df.index[-1], 'Accumulation Rainfall -29 days'] = df['Daily Rainfall (mm)'].iloc[-29:].sum()
  # print("df", df)

  # Hitung Evapotranspiration (dibagi 30 sesuai logic Excel)
  evapotranspiration = (120 if len(df.iloc[-29:]) > 10 else 150) / 30
  df.loc[df.index[-1], 'Evapotranspiration'] = evapotranspiration

  # Ambil Soil Water Reserve sehari sebelumnya
  previous_soil_water_reserve = df['Soil Water Reserve (mm)'].iloc[-1] if len(df) > 1 else 0

  # Hitung Water Balance
  water_balance = previous_soil_water_reserve + current_daily_rainfall - evapotranspiration
  # Simpan Water Balance ke dataframe
  df.loc[df.index[-1], 'Water Balance'] = water_balance

  # Hitung Soil Water Reserve
  df.loc[df.index[-1], 'Soil Water Reserve (mm)'] = min(water_balance, 200)

  # Hitung Water Surplus (WB - 200 >= 0 )
  df.loc[df.index[-1], 'Water Surplus'] = max(0, water_balance - 200)

  # Simpan hasil ke Google Sheets (DB)
  sheet_data.append_row([
      format_datetime(current_time_date),
      estate_name,
      current_daily_rainfall,
      df.loc[df.index[-1], 'Accumulation Rainfall -29 days'],
      df.loc[df.index[-1], 'Evapotranspiration'],
      df.loc[df.index[-1], 'Water Balance'],
      df.loc[df.index[-1], 'Soil Water Reserve (mm)'],
      df.loc[df.index[-1], 'Water Surplus']
  ])

  # Create a new row as a dictionary
  new_row = {
      'Date': pd.to_datetime(format_datetime(current_time_date), dayfirst=True),
      'Estate': estate_name,
      'Daily Rainfall (mm)': current_daily_rainfall,
      'Accumulation Rainfall -29 days': df.loc[df.index[-1], 'Accumulation Rainfall -29 days'],
      'Evapotranspiration': df.loc[df.index[-1], 'Evapotranspiration'],
      'Water Balance': df.loc[df.index[-1], 'Water Balance'],
      'Soil Water Reserve (mm)': df.loc[df.index[-1], 'Soil Water Reserve (mm)'],
      'Water Surplus': df.loc[df.index[-1], 'Water Surplus']
  }

  # Append the new row to the dataframe
  in_df = pd.concat([in_df, pd.DataFrame([new_row])], ignore_index=True)

  return in_df  # Return the modified dataframe

# %%
def remove_old_data(df, current_time_date, current_daily_rainfall, estate_name):

  # Remove the last data from dataframe
  filtered_df = df[(df['Estate'] == estate_name) & (df['Date'] == pd.to_datetime(format_datetime(current_time_date), dayfirst=True))]
  if not filtered_df.empty:
    row_index = filtered_df.index[0]
    df.drop(row_index, inplace=True)

  # Remove the last data from spreadsheet
  try:
    cell = sheet_data.find(format_datetime(current_time_date), in_column=1)
    if cell is not None:
      sheet_data.delete_rows(cell.row)
  except gspread.exceptions.CellNotFound:
      print("Data not found in spreadsheet for deletion.")
      sys.exit(1)

  return df

# %%
def check_groundwater(accumulation_rainfall, water_surplus):
  if (accumulation_rainfall >= 300) and (water_surplus == 0):
    return True
  elif (accumulation_rainfall >= 60) and (accumulation_rainfall <= 300) and (water_surplus >= 0):
    return True
  else:
    return False

def check_peilscale(peilscale):
  if peilscale <= -51:
    return True
  else:
    return False

def check_season(accumulation_rainfall):
  if accumulation_rainfall < 60 :
    return "Dry"
  elif accumulation_rainfall > 300:
    return "Wet"

def check_rain_in_dry_seasion(daily_rainfall_last_7):
  raining_once = (daily_rainfall_last_7 >= 60).sum() >= 1
  raining_twice = (daily_rainfall_last_7 >= 30).sum() >= 2

  if raining_once or raining_twice:
    return True
  else:
    return False

# %%
def validate_water_track(df, current_daily_rainfall, peilscale, next_fertilizer):

  last_row = df.iloc[-1]
  accumulation_rainfall = last_row['Accumulation Rainfall -29 days']
  water_surplus = last_row['Water Surplus']
  daily_rainfall_last_7 = df['Daily Rainfall (mm)'].iloc[-7:]

  # Syarat 1
  validation1 = check_groundwater(accumulation_rainfall, water_surplus)

  # Syarat 2
  print("peilscale", peilscale)
  validation2 = check_peilscale(peilscale)
  print("validation2", validation2)

  # Syarat 3
  season = check_season(accumulation_rainfall)
  validation3 = season not in ["Wet", "Dry"] # if validation3 has value that means it's either 'Wet' or 'Dry', None means it's Optimal

  # Check if season is 'Dry' with rains around 7 days back
  dry_with_rain = False
  if (season == "Dry"):
    dry_with_rain = check_rain_in_dry_seasion(daily_rainfall_last_7)

  return (validation1 and validation2 and validation3), validation1, validation2, season, dry_with_rain

# %%
def get_minimal_interval(last_group, next_group):
    return interval_table.get(last_group, {}).get(next_group, 30)  # Default to 30 if not found

# %%
def get_alternative_fertilizer(last_group, next_group, last_fertilizer_date, next_fertilizer_date, interval_table, fertilizer_groups):
    recommendation = []
    selisih_hari = (next_fertilizer_date - last_fertilizer_date).days

    for group, fertilizers in fertilizer_groups.items():
        if group != next_group:  # Exclude the desired fertilizer because it hits the interval
            interval = interval_table.get(last_group, {}).get(group, None)
            if interval is not None and selisih_hari >= interval:
                recommendation.extend(fertilizers)

    return recommendation

# %%
def get_all_recommendation(last_group, next_group, last_fertilizer_date, next_fertilizer_date, interval_table, fertilizer_groups):
  recommendation = []
  selisih_hari = (next_fertilizer_date - last_fertilizer_date).days

  # Always include the next_group
  if next_group in fertilizer_groups:
      recommendation.extend(fertilizer_groups[next_group])

  # Add other fertilizers that meet the interval
  for group, fertilizers in fertilizer_groups.items():
      if group != next_group:  # Exclude the desired fertilizer
          interval = interval_table.get(last_group, {}).get(group, None)
          if interval is not None and selisih_hari >= interval:
              recommendation.extend(fertilizers)

  return recommendation

# %%
def get_fertilizer(groups):
  recommendation = []

  for group, types in groups.items():
    recommendation.append(types)

  return recommendation

# %%
def validate_interval_fertilizer(last_group, next_group, last_fertilizer_date, next_fertilizer_date):
  min_interval = get_minimal_interval(last_group, next_group)
  if min_interval == None:  # Handle cases with no defined interval
      return False  # Or return True, depending on how you want to handle these cases
  
  selisih_hari = (next_fertilizer_date - last_fertilizer_date).days
  return selisih_hari >= min_interval

# %%
def get_fertilizer_group(fertilizer):
    for group, types in fertilizer_groups.items():
        if fertilizer in types:
            return group
    return None

# %%
def validate_dry_week(fertilizer, df):
  last_days = df['Daily Rainfall (mm)'].iloc[-7:]

  no_rain = 0
  for i in last_days:
    if i == 0:
      no_rain += 1

  return no_rain

# %%
def append_to_spreadsheet(date_input, username, estate_name, blok_name, current_daily_rainfall, peilscale, last_fertilizer, last_fertilizer_date, next_fertilizer, next_fertilizer_date, reason, recommendation):
  global sheet_output

  if len(reason) == 0:
    status = "Allowed"
  else:
    status = "Not Allowed"

  # ✅ Simpan Output ke Google Sheets
  output_data = [
      date_input.strftime('%Y-%m-%d %H:%M:%S'),
      username,
      estate_name,
      blok_name,
      current_daily_rainfall,
      peilscale,
      last_fertilizer,
      last_fertilizer_date.strftime("%Y-%m-%d"),
      next_fertilizer,
      next_fertilizer_date.strftime("%Y-%m-%d"),
      status,
      reason,
      recommendation
  ]
  sheet_output.append_row(output_data)

  # ✅Output
  print("\n=== Hasil Analisis Pemupukan ===")
  print(f"Nama User: {username}")
  print(f"Tanggal Input: {date_input.strftime('%Y-%m-%d')}")
  print(f"Curah Hujan: {current_daily_rainfall} mm")
  print(f"Peilscale: {peilscale}")
  print(f"Jenis Pupuk Terakhir: {last_fertilizer} (Tanggal: {last_fertilizer_date.strftime('%Y-%m-%d')})")
  print(f"Plan Jenis Pupuk: {next_fertilizer} (Tanggal: {next_fertilizer_date.strftime('%Y-%m-%d')})")
  print(f"Status: {status}")
  print(f"Reason: {reason}")
  print(f"Rekomendasi: {recommendation}")
  
  return status

# %%
def validate_dolomite(df, last_fertilizer, last_fertilizer_date, next_fertilizer_date, Alternatives):
  dolomite_fertilizer = "Dolomite"

  # Check if the alternatives already has Dolomite inside it
  if dolomite_fertilizer in Alternatives:
    return Alternatives  # Dolomite not allowed

  # 1. Check if the last Daily Rainfall (mm) is < 60
  last_daily_rainfall = df['Daily Rainfall (mm)'].iloc[-1]
  if last_daily_rainfall >= 60:
    return Alternatives  # Dolomite not allowed

  # 2. Check if Accumulation Rainfall is < 300
  accumulation_rainfall = df['Accumulation Rainfall -29 days'].iloc[-1]
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
def fill_rainfall_data(df, current_time_date, estate_name):
  # Get missing dates, last reported time, and total missing dates
  missing_dates, last_reported_time, total_missing_dates = get_missing_dates(df, estate_name, current_time_date)

  if total_missing_dates > 0:
    print(border_line)
    print(f"\nTerdapat {total_missing_dates} hari data hujan yang kosong pada estate {estate_name}, antara {format_datetime(current_time_date)} dan {format_datetime(last_reported_time)}")

    for date in missing_dates:
      current_daily_rainfall = float(input(f"Masukkan curah hujan {format_datetime(date.date())} (mm): "))
      df = calculate_rainfall(df, date.date(), current_daily_rainfall, estate_name)

  # Check if today's data is already filled
  is_calculate_rainfall = validate_date(last_reported_time, current_time_date)
  if not is_calculate_rainfall:
    print(border_line)
    current_daily_rainfall = float(input(f"\nMasukkan curah hujan hari ini (mm) untuk estate {estate_name}: "))
    df = calculate_rainfall(df, current_time_date, current_daily_rainfall, estate_name)

  return df

# %%
def analyze_fertilizer(date_input, username, estate_name, blok_name, df, peilscale, last_fertilizer, last_fertilizer_date, next_fertilizer, next_fertilizer_date):

  # Filter the DataFrame for the selected estate
  estate_df = df[df['Estate'] == estate_name]

  # Get the current daily rainfall (last entry for the estate)
  current_daily_rainfall = estate_df['Daily Rainfall (mm)'].iloc[-1]

  #check if today's rainfall is greater than or equal to 60
  reason = ""
  if current_daily_rainfall >= 60:
    reason = "Curah hujan lebih dari 60 mm, pemupukan dihentikan"
    print(reason)
    append_to_spreadsheet(date_input, username, estate_name, blok_name, current_daily_rainfall, 0, "", datetime(1970, 1, 1), "", datetime(1970, 1, 1), reason, "")

  #check the accumulated rainfall data
  validate_water, rain_factor, peilscale_factor, season_factor, dry_with_rain = validate_water_track(df, current_daily_rainfall, peilscale, next_fertilizer)
  if(not validate_water):
    if(not rain_factor):
      reason = "Tidak bisa melakukan pemupukan, karena curah hujan"
      append_to_spreadsheet(date_input, username, estate_name, blok_name, current_daily_rainfall, peilscale, "", datetime(1970, 1, 1), "", datetime(1970, 1, 1), reason, "")
    elif(not peilscale_factor):
      reason = "Tidak bisa melakukan pemupukan, karena peilscale di atas -51"
      append_to_spreadsheet(date_input, username, estate_name, blok_name, current_daily_rainfall, peilscale, "", datetime(1970, 1, 1), "", datetime(1970, 1, 1), reason, "")
    elif(not season_factor):
      reason = f"Tidak bisa melakukan pemupukan, karena musim {season_factor}"
      if season_factor == "Wet":
          append_to_spreadsheet(date_input, username, estate_name, blok_name, current_daily_rainfall, peilscale, "", datetime(1970, 1, 1), "", datetime(1970, 1, 1), reason, "")
      elif season_factor == "Dry":
          print(reason)

  #get the last fertilizer's group
  last_group = get_fertilizer_group(last_fertilizer)
  #get the next fertilizer's group
  next_group = get_fertilizer_group(next_fertilizer)

  #check the interval between the last & the next fertilizer
  validate_interval_result = validate_interval_fertilizer(last_group, next_group, last_fertilizer_date, next_fertilizer_date)

  #check the alternative
  Alternatives = []
  if (not validate_interval_result):
    if last_group == next_group:
      reason = "Karena jarak interval pemupukan di bawah 60 hari"
    elif last_group != next_group:
      reason = "Karena jarak interval pemupukan di bawah 30 hari"
    Alternatives = get_alternative_fertilizer(last_group, next_group, last_fertilizer_date, next_fertilizer_date, interval_table, fertilizer_groups)
  else:
    Alternatives = get_all_recommendation(last_group, next_group, last_fertilizer_date, next_fertilizer_date, interval_table, fertilizer_groups)

  #check the specific fertilizer trait
  #Dolomite
  Alternatives = validate_dolomite(df, last_fertilizer, last_fertilizer_date, next_fertilizer_date, Alternatives)
  #Discard because dry week
  is_dry_week = validate_dry_week(next_fertilizer, df)
  if next_fertilizer == "Urea" and is_dry_week >= 3:
      reason = "3 hari kebelakang tidak terdapat hujan sama sekali"
  elif next_fertilizer in ["Urea", "MOP", "HGFB"] and is_dry_week >= 7:
      reason = "7 hari kebelakang tidak terdapat hujan sama sekali"

  #Join the alternative option
  alternative = ', '.join(Alternatives)
  recommendation = ""
  plan_fertilizer_date = (last_fertilizer_date + timedelta(days=14)).date()
  if (len(Alternatives) != 0):
    recommendation = f"Pupuk alternatif yang disarankan: {alternative}"

  # Append to spreadsheet
  status = append_to_spreadsheet(date_input, username, estate_name, blok_name, current_daily_rainfall, peilscale, last_fertilizer, last_fertilizer_date, next_fertilizer, next_fertilizer_date, reason, recommendation)

  return current_daily_rainfall, status, reason, recommendation

# %%
def validate_and_update_last_data(df, estate_name):
  # Filter for the estate's data
  estate_data = df[(df['Estate'] == estate_name)]

  if not estate_data.empty:
    last_date = estate_data['Date'].iloc[-1].date()
    last_rainfall = estate_data['Daily Rainfall (mm)'].iloc[-1]

    print(f"Data terakhir untuk estate {estate_name} pada {format_datetime(last_date)}:")
    print(f"Curah hujan: {last_rainfall} mm")

    is_correct = input("Apakah data ini benar? (y/n): ").lower()

    if is_correct.lower() != "y":
      updated_rainfall = float(input(f"Masukkan curah hujan yang benar untuk {format_datetime(last_date)} (mm): "))

      # Remove the old data
      df = remove_old_data(df, last_date, updated_rainfall, estate_name)

      # Recalculate dependent columns using calculate_rainfall
      df = calculate_rainfall(df, last_date, updated_rainfall, estate_name)

      print(f"Data untuk {format_datetime(last_date)} telah diperbarui.")

  return df

# %% [markdown]
# # **User Input**

# %%
creds = ServiceAccountCredentials.from_json_keyfile_name(json_path, scope)
client = gspread.authorize(creds)
sheet_data = client.open_by_url(sheet_url).worksheet("DB")
sheet_output = client.open_by_url(sheet_url).worksheet("Output")

# %%
# Load data dari Google Sheets
data = sheet_data.get_all_records()
df = pd.DataFrame(data)

# Pastikan format kolom benar
df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y', errors='coerce')
df['Daily Rainfall (mm)'] = pd.to_numeric(df['Daily Rainfall (mm)'], errors='coerce')

# Cek apakah dataframe kosong
if df.empty:
    print("Dataset kosong! Pastikan ada data di Google Sheets.")

# Drop rows with NaT (Not a Time) values in the 'Date' column
df.dropna(subset=['Date'], inplace=True)

# %% [markdown]
# # GUI

# %%
def load_database(sheet_url, json_path):
    """Loads data from the Google Sheet into a Pandas DataFrame."""
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(json_path, scope)
        client = gspread.authorize(creds)
        sheet_data = client.open_by_url(sheet_url).worksheet("DB")
        data = sheet_data.get_all_records()
        df = pd.DataFrame(data)

        # Data type conversions and cleaning
        df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y', errors='coerce')
        df['Daily Rainfall (mm)'] = pd.to_numeric(df['Daily Rainfall (mm)'], errors='coerce')
        df.dropna(subset=['Date'], inplace=True)  # Drop rows with invalid dates

        return df

    except gspread.exceptions.SpreadsheetNotFound:
        print(f"Error: Spreadsheet not found at URL: {sheet_url}")
        return pd.DataFrame()  # Return an empty DataFrame on error
    except gspread.exceptions.APIError as e:
        print(f"Error: API Error accessing Google Sheets: {e}")
        return pd.DataFrame()
    except Exception as e:
        print(f"An unexpected error occurred loading data: {e}")
        return pd.DataFrame()

def format_datetime(dt):
    dt_copy = dt
    return dt_copy.strftime('%d/%m/%Y')

def format_datetimehour(dt):
    dt_copy = dt
    return dt_copy.strftime('%d/%m/%Y %H:%M:%S')

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def get_date(entry_widget):
    """Creates a calendar popup and inserts the selected date into the given entry widget."""
    from tkcalendar import Calendar  # Import INSIDE the function

    if not root_exists:  # Prevent interaction if window is closed
        return

    def set_date():
        """Sets the selected date from the calendar to the entry."""
        if not root_exists:  # Check again, inside the nested function
            return
        selected_date = cal.get_date()
        entry_widget.delete(0, tk.END)  # Clear the entry
        entry_widget.insert(0, selected_date)  # Insert the new date
        top.destroy()

    # Create a toplevel window for the calendar
    top = tk.Toplevel(root)

    # Get today's date
    today = datetime.now(current_timezone)

    # Create a Calendar widget
    cal = Calendar(top,
                   font="Arial 10",
                   selectmode='day',
                   year=today.year,
                   month=today.month,
                   day=today.day,
                   date_pattern="yyyy-mm-dd")  # Important: Set the date_pattern

    cal.pack(pady=20)

    # Add a button to confirm the selection
    confirm_button = tk.Button(top, text="OK", command=set_date)
    confirm_button.pack(pady=10)

    # Important: Make the toplevel window transient and grab focus
    top.transient(root)  # Keep the calendar on top of the main window
    top.grab_set()       # Prevent interaction with the main window until closed
    top.wait_window(top)  # Wait for the toplevel to be destroyed

def show_rainfall_options():
    global label_rainfall_option, back_button, current_menu, button_update_rainfall, button_add_rainfall, previous_menu

    if not root_exists:
        return

    hide_all_widgets()
    current_menu = "rainfall"
    previous_menu = "main"
    label_rainfall_option = tk.Label(root, text="Pilih Opsi Untuk Data Hujan:", font=("Arial", 12))
    label_rainfall_option.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

    button_update_rainfall = tk.Button(root, text="Update Data Hujan Terakhir", command=goto_update_rainfall, font=("Arial", 10))
    button_update_rainfall.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

    button_add_rainfall = tk.Button(root, text="Masukkan Data Hujan Baru", command=goto_add_rainfall, font=("Arial", 10))
    button_add_rainfall.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

    back_button = tk.Button(root, text="Back", command=go_back, font=("Arial", 10))
    back_button.grid(row=3, column=0, padx=10, pady=10)

    root.columnconfigure(0, weight=1)

def goto_update_rainfall():
    global previous_menu
    if not root_exists:
        return
    print(f"Selected Rainfall Option: Update Data Hujan Terakhir")
    previous_menu = "rainfall"
    show_estate_options()

def show_estate_options():
    global label_estate_option, combobox_estate, submit_estate_button, back_button, current_menu, main_menu_button, df
    if not root_exists:
        return

    hide_all_widgets()

    current_menu = "estate"
    label_estate_option = tk.Label(root, text="Pilih estate (Inti/Plasma):", font=("Arial", 12))
    label_estate_option.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
    estate_options = ["Inti", "Plasma"]
    combobox_estate = ttk.Combobox(root, values=estate_options, width=30, font=("Arial", 10))
    combobox_estate.grid(row=1, column=0, padx=10, pady=10)
    submit_estate_button = tk.Button(root, text="Submit Estate", command=lambda: submit_estate(combobox_estate.get()), font=("Arial", 10))
    submit_estate_button.grid(row=2, column=0, padx=10, pady=10)
    back_button = tk.Button(root, text="Back", command=go_back, font=("Arial", 10))
    back_button.grid(row=3, column=0, padx=10, pady=10)
    main_menu_button = tk.Button(root, text="Back to Main Menu", command=back_to_main, font=("Arial", 10))
    main_menu_button.grid(row=4, column=0, padx=10, pady=10)

    root.columnconfigure(0, weight=1)

def goto_add_rainfall():
    global previous_menu
    if not root_exists:
        return
    print(f"Selected Rainfall Option: Masukkan Data Hujan Baru")
    show_estate_options_for_add_rainfall()

def submit_estate_for_analysis(selected_estate, nama_blok, peilscale, jenis_terakhir, tanggal_terakhir, rencana_jenis, tanggal_rencana):
    global previous_menu, username_var, df
    if not root_exists:
        return
    
    estate_options = ["Inti", "Plasma"]
    if selected_estate not in estate_options:
        tk.messagebox.showerror("Error", f"Nama estate invalid: '{selected_estate}'. Tolong pilih antara: {', '.join(estate_options)}")
        return
    
    # Get current time
    date_input = datetime.now(current_timezone)

    # Get the username
    username = username_var.get()

    # Convert string to integer
    peilscale = int(peilscale)

    current_daily_rainfall, status, reason, recommendation = analyze_fertilizer(date_input, username, selected_estate, nama_blok, df, peilscale, jenis_terakhir, tanggal_terakhir, rencana_jenis, tanggal_rencana)

    # Display the results
    display_analysis_results(
        selected_estate, nama_blok, tanggal_rencana, peilscale, tanggal_terakhir,
        jenis_terakhir, rencana_jenis, username, current_daily_rainfall, status, reason, recommendation
    )
    # previous_menu = "main"  # No longer going back to main immediately
    # cancel_to_main()

def display_analysis_results(selected_estate, nama_blok, tanggal_rencana, peilscale, tanggal_terakhir,
                              jenis_terakhir, rencana_jenis, username, curah_hujan, status, reason, recommendation):
    
    global current_menu, label_tanggal_analisa, label_nama_user, label_curah_hujan, \
           label_status, label_reason, label_recommendation, label_selected_estate, \
           label_nama_blok, label_tanggal_rencana, label_peilscale_value, \
           label_tanggal_terakhir_value, label_jenis_terakhir_value, \
           label_rencana_jenis_value, back_to_main_button, reanalyze_button  # Add reanalyze_button

    if not root_exists: return
    hide_all_widgets()
    current_menu = "analysis_results"

    # --- Display Analysis Results ---
    current_time_input = datetime.now(current_timezone)
    label_tanggal_analisa = tk.Label(root, text=f"Tanggal Analisa: {current_time_input.strftime('%Y-%m-%d %H:%M:%S')}", font=("Arial", 12))
    label_tanggal_analisa.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

    label_nama_user = tk.Label(root, text=f"Nama User: {username}", font=("Arial", 12))
    label_nama_user.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

    label_selected_estate = tk.Label(root, text=f"Nama Estate: {selected_estate}", font=("Arial", 12))
    label_selected_estate.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

    label_nama_blok = tk.Label(root, text=f"Nama Blok: {nama_blok}", font=("Arial", 12))
    label_nama_blok.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

    label_curah_hujan = tk.Label(root, text=f"Curah Hujan: {curah_hujan}", font=("Arial", 12))
    label_curah_hujan.grid(row=4, column=0, padx=10, pady=5, sticky="ew")

    label_peilscale_value = tk.Label(root, text=f"Nilai Peilscale: {peilscale}", font=("Arial", 12))
    label_peilscale_value.grid(row=5, column=0, padx=10, pady=5, sticky="ew")

    label_jenis_terakhir_value = tk.Label(root, text=f"Jenis Pupuk Terakhir: {jenis_terakhir}", font=("Arial", 12, "bold"))
    label_jenis_terakhir_value.grid(row=6, column=0, padx=10, pady=5, sticky="ew")

    label_tanggal_terakhir_value = tk.Label(root, text=f"Tanggal Pupuk Terakhir: {tanggal_terakhir}", font=("Arial", 12, "bold"))
    label_tanggal_terakhir_value.grid(row=7, column=0, padx=10, pady=5, sticky="ew")

    label_rencana_jenis_value = tk.Label(root, text=f"Rencana Jenis Pupuk: {rencana_jenis}", font=("Arial", 12, "bold"))
    label_rencana_jenis_value.grid(row=8, column=0, padx=10, pady=5, sticky="ew")

    label_tanggal_rencana = tk.Label(root, text=f"Tanggal Rencana Pupuk: {tanggal_rencana}", font=("Arial", 12, "bold"))
    label_tanggal_rencana.grid(row=9, column=0, padx=10, pady=5, sticky="ew")

    label_status = tk.Label(root, text=f"Status: {status}", font=("Arial", 12, "bold"))
    label_status.grid(row=10, column=0, padx=10, pady=5, sticky="ew")

    label_reason = tk.Label(root, text=f"Alasan: {reason}", font=("Arial", 12))
    label_reason.grid(row=11, column=0, padx=10, pady=5, sticky="ew")

    label_recommendation = tk.Label(root, text=f"Rekomendasi: {recommendation}", font=("Arial", 12))
    label_recommendation.grid(row=12, column=0, padx=10, pady=5, sticky="ew")

    # --- Re-analyze Button --- (Row 13)
    reanalyze_button = tk.Button(root, text="Re-analyze", command=go_to_reanalyze, font=("Arial", 10))
    reanalyze_button.grid(row=13, column=0, padx=10, pady=10)

    # --- Back to Main Menu Button --- (Row 14)
    back_to_main_button = tk.Button(root, text="Back to Main Menu", command=back_to_main, font=("Arial", 10))
    back_to_main_button.grid(row=14, column=0, padx=10, pady=10)

    root.columnconfigure(0, weight=1)

def show_estate_options_for_analysis():
    global label_estate_option, combobox_estate, submit_estate_button, back_button, current_menu, \
           entry_blok, entry_tanggal_rencana_pupuk, entry_peilscale, entry_tanggal_pupuk_terakhir, \
           combobox_jenis_pupuk_terakhir, combobox_rencana_jenis_pupuk, label_blok, label_tanggal_rencana_pupuk, \
           label_peilscale, label_tanggal_pupuk_terakhir, label_jenis_pupuk_terakhir, label_rencana_jenis_pupuk, \
           button_tanggal_rencana_pupuk, button_tanggal_pupuk_terakhir

    if not root_exists:
        return

    hide_all_widgets()
    current_menu = "estate_analysis"

    # --- Use sticky="ew" on ALL widgets ---
    label_estate_option = tk.Label(root, text="Pilih estate (Inti/Plasma):", font=("Arial", 12))
    label_estate_option.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

    estate_options = ["Inti", "Plasma"]
    combobox_estate = ttk.Combobox(root, values=estate_options, width=30, font=("Arial", 10))
    combobox_estate.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

    label_blok = tk.Label(root, text="Masukkan Nama Blok:", font=("Arial", 12))
    label_blok.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

    entry_blok = tk.Entry(root, font=("Arial", 10))
    entry_blok.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

    label_tanggal_rencana_pupuk = tk.Label(root, text="Masukkan tanggal rencana pupuk:", font=("Arial", 12))
    label_tanggal_rencana_pupuk.grid(row=4, column=0, padx=10, pady=5, sticky="ew")

    entry_tanggal_rencana_pupuk = tk.Entry(root, font=("Arial", 10))
    entry_tanggal_rencana_pupuk.grid(row=5, column=0, padx=10, pady=5, sticky="ew")

    button_tanggal_rencana_pupuk = tk.Button(root, text="Pilih Tanggal", command=lambda: get_date(entry_tanggal_rencana_pupuk))
    button_tanggal_rencana_pupuk.grid(row=5, column=1, padx=5, pady=5) # Place button next to entry

    label_tanggal_pupuk_terakhir = tk.Label(root, text="Masukkan tanggal pupuk terakhir:", font=("Arial", 12))
    label_tanggal_pupuk_terakhir.grid(row=8, column=0, padx=10, pady=5, sticky="ew")

    entry_tanggal_pupuk_terakhir = tk.Entry(root, font=("Arial", 10))
    entry_tanggal_pupuk_terakhir.grid(row=9, column=0, padx=10, pady=5, sticky="ew")

    button_tanggal_pupuk_terakhir = tk.Button(root, text="Pilih Tanggal", command=lambda: get_date(entry_tanggal_pupuk_terakhir))
    button_tanggal_pupuk_terakhir.grid(row=9, column=1, padx=5, pady=5) # Place button next to entry

    label_peilscale = tk.Label(root, text="Masukkan nilai Peilscale:", font=("Arial", 12))
    label_peilscale.grid(row=6, column=0, padx=10, pady=5, sticky="ew")

    entry_peilscale = tk.Entry(root, font=("Arial", 10))
    entry_peilscale.grid(row=7, column=0, padx=10, pady=5, sticky="ew")

    label_jenis_pupuk_terakhir = tk.Label(root, text="Masukkan jenis pupuk terakhir:", font=("Arial", 12))
    label_jenis_pupuk_terakhir.grid(row=10, column=0, padx=10, pady=5, sticky="ew")

    combobox_jenis_pupuk_terakhir = ttk.Combobox(root, values=fertilizer_type, width=30, font=("Arial", 10))
    combobox_jenis_pupuk_terakhir.grid(row=11, column=0, padx=10, pady=5, sticky="ew")

    label_rencana_jenis_pupuk = tk.Label(root, text="Masukkan rencana jenis pupuk:", font=("Arial", 12))
    label_rencana_jenis_pupuk.grid(row=12, column=0, padx=10, pady=5, sticky="ew")

    combobox_rencana_jenis_pupuk = ttk.Combobox(root, values=fertilizer_type, width=30, font=("Arial", 10))
    combobox_rencana_jenis_pupuk.grid(row=13, column=0, padx=10, pady=5, sticky="ew")

    submit_estate_button = tk.Button(root, text="Submit", command=lambda: submit_analysis(
        combobox_estate.get(),
        entry_blok.get(),
        entry_peilscale.get(),
        combobox_jenis_pupuk_terakhir.get(),
        entry_tanggal_pupuk_terakhir.get(),
        combobox_rencana_jenis_pupuk.get(),
        entry_tanggal_rencana_pupuk.get()
    ), font=("Arial", 10))
    submit_estate_button.grid(row=14, column=0, padx=10, pady=10)

    back_button = tk.Button(root, text="Back", command=go_back, font=("Arial", 10))
    back_button.grid(row=15, column=0, padx=10, pady=10)

    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=0)

def submit_analysis(selected_estate, blok, peilscale,
                    jenis_pupuk_terakhir, tanggal_pupuk_terakhir, 
                    rencana_jenis_pupuk, tanggal_rencana_pupuk):
    global df
    if not root_exists:
        return

    if not selected_estate:
        messagebox.showerror("Error", "Tolong masukkan nama estate.")
        return
    valid_estates = ["Inti", "Plasma"]
    if selected_estate not in valid_estates:
        messagebox.showerror("Error", f"Nama estate invalid: '{selected_estate}'. Tolong pilih antara: {', '.join(valid_estates)}")
        return

    if not blok:
        messagebox.showerror("Error", "Tolong masukkan nama blok.")
        return

    if not tanggal_rencana_pupuk:
        messagebox.showerror("Error", "Tolong masukkan tanggal rencana pupuk.")
        return

    if not peilscale:
        messagebox.showerror("Error", "Masukkan nilai peilscale.")
        return
    try:
        peilscale = int(peilscale)
    except ValueError as e:
        messagebox.showerror("Error", f"Nilai peilscale invalid: {e}")
        return

    if not tanggal_pupuk_terakhir:
        messagebox.showerror("Error", "Tolong masukkan tanggal pupuk terakhir.")
        return

    if not jenis_pupuk_terakhir:
        messagebox.showerror("Error", "Tolong masukkan jenis pupuk terakhir.")
        return
    
    if not rencana_jenis_pupuk:
        messagebox.showerror("Error", "Tolong masukkan rencana jenis pupuk.")
        return

    try:
        tanggal_rencana_pupuk_dt = datetime.strptime(tanggal_rencana_pupuk, "%Y-%m-%d")
        tanggal_pupuk_terakhir_dt = datetime.strptime(tanggal_pupuk_terakhir, "%Y-%m-%d")
    except ValueError:
        messagebox.showerror("Error", "Format tanggal tidak valid, tolong masukkan tanggal dengan format DD/MM/YYYY.")
        return

    username = username_var.get()
    if not username.strip():
        messagebox.showerror("Error", "Tolong masukkan username di dalam main menu.")
        return

    current_daily_rainfall, status, reason, recommendation = analyze_fertilizer(
        datetime.now(current_timezone), username, selected_estate, blok, df,
        peilscale, jenis_pupuk_terakhir, tanggal_pupuk_terakhir_dt,
        rencana_jenis_pupuk, tanggal_rencana_pupuk_dt
    )

    display_analysis_results(
        selected_estate, blok, tanggal_rencana_pupuk, peilscale,
        tanggal_pupuk_terakhir, jenis_pupuk_terakhir, rencana_jenis_pupuk,
        username, current_daily_rainfall, status, reason, recommendation
    )

def go_to_reanalyze():
    global previous_menu
    if not root_exists:
        return
    hide_all_widgets()
    show_estate_options_for_analysis()
    previous_menu = "estate_analysis" 

def back_to_main():
    """Hides all widgets and recreates the main menu."""
    global previous_menu
    if not root_exists:
        return
    hide_all_widgets()
    create_main_widgets()
    previous_menu = "main"

def go_back():
    """Handles navigation back; uses after_idle and hide_all_widgets."""
    global previous_menu
    if not root_exists:
        return

    if previous_menu == "main":
        hide_all_widgets()
        root.after_idle(create_main_widgets)
    elif previous_menu == "rainfall":
        hide_all_widgets()
        root.after_idle(show_rainfall_options)
        previous_menu = "main"
    elif previous_menu == "estate":
        hide_all_widgets()
        root.after_idle(show_estate_options)
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

def submit_rainfall_option(selected_rainfall_option):
    global previous_menu
    if not root_exists:
        return
    print(f"Selected Rainfall Option: {selected_rainfall_option}")

    if selected_rainfall_option == "Update Data Hujan Terakhir":
        previous_menu = "rainfall"
        show_estate_options()
    elif selected_rainfall_option == "Masukkan Data Hujan Baru":
        previous_menu = "rainfall"
        show_estate_options_for_add_rainfall()

def show_estate_options_for_add_rainfall():
    global label_estate_option, combobox_estate, submit_estate_check_button, back_button, current_menu, previous_menu

    if not root_exists:
        return

    hide_all_widgets()
    current_menu = "estate_add_rainfall"
    previous_menu = "rainfall"

    label_estate_option = tk.Label(root, text="Pilih estate (Inti/Plasma):", font=("Arial", 12))
    label_estate_option.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

    estate_options = ["Inti", "Plasma"]
    combobox_estate = ttk.Combobox(root, values=estate_options, width=30, font=("Arial", 10))
    combobox_estate.grid(row=1, column=0, padx=10, pady=10)

    submit_estate_check_button = tk.Button(root, text="Check Estate", command=lambda: check_existing_rainfall(combobox_estate.get(), current_time_date), font=("Arial", 10))
    submit_estate_check_button.grid(row=2, column=0, padx=10, pady=10)

    back_button = tk.Button(root, text="Back", command=go_back, font=("Arial", 10))
    back_button.grid(row=3, column=0, padx=10, pady=10)

    main_menu_button = tk.Button(root, text="Back to Main Menu", command=back_to_main, font=("Arial", 10))
    main_menu_button.grid(row=4, column=0, padx=10, pady=10)

    root.columnconfigure(0, weight=1)

def check_existing_rainfall(selected_estate, current_time_date):
    global df, previous_menu

    if not root_exists:
        return
    
    estate_options = ["Inti", "Plasma"]
    if selected_estate not in estate_options:
        tk.messagebox.showerror("Error", f"Nama estate invalid: '{selected_estate}'. Tolong pilih antara: {', '.join(estate_options)}")
        return

    today_date = datetime.strptime(format_datetime(current_time_date), "%d/%m/%Y").date()
    estate_data_today = df[(df['Estate'] == selected_estate) & (df['Date'].dt.date == today_date)]
    
    if estate_data_today.empty:
        hide_estate_widgets()
        show_add_rainfall_entry(selected_estate, today_date)
        previous_menu = "estate_add_rainfall" 
    else:
        hide_estate_widgets()
        show_rainfall_data_entry(selected_estate)
        previous_menu = "estate_add_rainfall" 

def show_add_rainfall_entry(selected_estate, date):
    """Displays the screen to add new rainfall data."""
    global entry_daily_rainfall, label_daily_rainfall, submit_add_rainfall_button

    hide_all_widgets()

    label_daily_rainfall = tk.Label(root, text=f"Masukkan Data Hujan (mm) untuk {selected_estate} hari ini ({format_datetime(current_time_date)}):", font=("Arial", 12))
    label_daily_rainfall.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

    entry_daily_rainfall = tk.Entry(root, font=("Arial", 10))
    entry_daily_rainfall.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

    submit_add_rainfall_button = tk.Button(root, text="Submit Rainfall", command=lambda: submit_estate_for_add_rainfall(selected_estate, date, entry_daily_rainfall.get()), font=("Arial", 10))
    submit_add_rainfall_button.grid(row=2, column=0, padx=10, pady=10)

    back_button = tk.Button(root, text="Back", command=go_back, font=("Arial", 10))
    back_button.grid(row=3, column=0, padx=10, pady=10)

    main_menu_button = tk.Button(root, text="Back to Main Menu", command=back_to_main, font=("Arial", 10))
    main_menu_button.grid(row=4, column=0, padx=10, pady=10)
    root.columnconfigure(0, weight=1)

def submit_estate_for_add_rainfall(selected_estate, date, new_rainfall):
    global previous_menu, df

    if not root_exists:
        return
    
    estate_options = ["Inti", "Plasma"]
    if selected_estate not in estate_options:
        tk.messagebox.showerror("Error", f"Nama estate invalid: '{selected_estate}'. Tolong pilih antara: {', '.join(estate_options)}")
        return
    
    try:
        new_rainfall = float(new_rainfall)
        if new_rainfall < 0:
            raise ValueError("Rainfall cannot be negative.")
    except ValueError:
        tk.messagebox.showerror("Error", "Invalid rainfall value. Please enter a non-negative number.")
        return
    
    df = calculate_rainfall(df, date, new_rainfall, selected_estate)
    
    show_success_window()

def submit_estate(selected_estate):
    global previous_menu
    if not root_exists:
        return
    
    estate_options = ["Inti", "Plasma"]
    if selected_estate not in estate_options:
        tk.messagebox.showerror("Error", f"Nama estate invalid: '{selected_estate}'. Tolong pilih antara: {', '.join(estate_options)}")
        return

    print(f"Selected Estate: {selected_estate}")
    show_rainfall_data_entry(selected_estate)

def show_rainfall_data_entry(selected_estate):
    """Displays the rainfall data entry fields, pre-populated with the last entry."""
    global previous_menu, entry_update_rainfall, label_update_rainfall, back_button, main_menu_button, submit_update_rainfall_button, df

    if not root_exists:
        return

    hide_all_widgets()

    previous_menu = "estate"

    estate_data = df[df['Estate'] == selected_estate]

    if not estate_data.empty: 
        last_date = estate_data['Date'].iloc[-1] 
        last_rainfall = estate_data['Daily Rainfall (mm)'].iloc[-1]

        label_update_rainfall = tk.Label(root, text=f"Update Data Hujan Untuk {selected_estate} Pada Tanggal {format_datetime(last_date)} (mm):", font=("Arial", 12))
        label_update_rainfall.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        entry_update_rainfall = tk.Entry(root, font=("Arial", 10))
        entry_update_rainfall.insert(0, str(last_rainfall))  
        entry_update_rainfall.grid(row=3, column=0, padx=10, pady=10, sticky="ew")

        submit_update_rainfall_button = tk.Button(root, text="Submit Rainfall", command=lambda: submit_update_rainfall(selected_estate, last_date, entry_update_rainfall.get()), font=("Arial", 10))
        submit_update_rainfall_button.grid(row=4, column=0, padx=10, pady=10)

        back_button = tk.Button(root, text="Back", command=go_back, font=("Arial", 10))
        back_button.grid(row=5, column=0, padx=10, pady=10)

        main_menu_button = tk.Button(root, text="Back to Main Menu", command=back_to_main, font=("Arial", 10))
        main_menu_button.grid(row=6, column=0, padx=10, pady=10)

        root.columnconfigure(0, weight=1)

    else:
        # Handle the case where there's no data for the selected estate.
        label_no_data = tk.Label(root, text=f"No rainfall data found for {selected_estate}.", font=("Arial", 12))
        label_no_data.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        back_button = tk.Button(root, text="Back", command=go_back, font=("Arial", 10))
        back_button.grid(row=3, column=0, padx=10, pady=10)

        main_menu_button = tk.Button(root, text="Back to Main Menu", command=back_to_main, font=("Arial", 10))
        main_menu_button.grid(row=4, column=0, padx=10, pady=10)
        root.columnconfigure(0, weight=1)

def submit_update_rainfall(selected_estate, date, new_rainfall):
    """Submits the updated rainfall data to the spreadsheet."""
    global previous_menu, df, entry_update_rainfall
    if not root_exists:
        return
    
    try:
        new_rainfall = float(new_rainfall)
        if new_rainfall < 0:
            raise ValueError("Rainfall cannot be negative.")
    except ValueError:
        tk.messagebox.showerror("Error", "Invalid rainfall value. Please enter a non-negative number.")
        return
    
    # Remove the old data
    df = remove_old_data(df, date, new_rainfall, selected_estate)

    # Recalculate dependent columns using calculate_rainfall
    df = calculate_rainfall(df, date, new_rainfall, selected_estate)

    show_success_window()

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

    button_back_to_main = tk.Button(success_window, text="Back to Main Menu", command=close_success_and_go_back, font=("Arial", 10))
    button_back_to_main.pack(pady=5)
    
    success_window.columnconfigure(0, weight=1)

def close_success_and_go_back():
    """Closes the success window and returns to the main menu."""
    global success_window
    if not root_exists:
        return
    
    if success_window:
        success_window.destroy()  # Close the success window
        success_window = None  # Set to None after closing
    back_to_main()  # Go back to the main menu

def hide_all_widgets():
    """Hides ALL widgets in the application."""
    if not root_exists:
        return

    for widget in root.winfo_children():
        try:
            widget.grid_forget()
        except AttributeError:
            pass

def hide_estate_widgets():
    """Hides the widgets related to estate selection."""

    if not root_exists:
        return

    try:
        label_estate_option.grid_forget()
        combobox_estate.grid_forget()
        submit_estate_button.grid_forget()
        back_button.grid_forget()
        main_menu_button.grid_forget()
    except AttributeError:
        pass

def cancel_to_main():
    if not root_exists:
        return
    back_to_main()

def create_main_widgets():
    global label_username, entry_username, previous_menu, current_menu, back_button, exit_button, button_input_hujan, button_analisa_pemupukan, username_var, label_saved_username, username
    
    if not root_exists:
        return
    root.geometry("500x400")

    current_menu = "main"

    # Update the dataframe every time user access the main menu
    df = load_database(sheet_url, json_path)  #You already had this, keep it
    if df.empty:
        tk.messagebox.showerror("Error", "Failed to load data from the spreadsheet...")
        root.destroy()
        return

    if not username:
        label_username = tk.Label(root, text="Masukkan Username:", font=("Arial", 12))
        label_username.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        entry_username = tk.Entry(root, font=("Arial", 10), textvariable=username_var)
        entry_username.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        username_var.trace_add("write", lambda *args: set_username())

    else: 
        label_saved_username = tk.Label(root, text=f"Masuk ke sistem sebagai: {username}", font=("Arial", 12))
        label_saved_username.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

    button_input_hujan = tk.Button(root, text="Masukkan Data Hujan", command=goto_input_hujan, font=("Arial", 12))
    button_input_hujan.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

    button_analisa_pemupukan = tk.Button(root, text="Analisa Pemupukan", command=goto_analisa_pemupukan, font=("Arial", 12))
    button_analisa_pemupukan.grid(row=3, column=0, padx=10, pady=10, sticky="ew")

    exit_button = tk.Button(root, text="Exit", command=on_closing, font=("Arial", 10))
    exit_button.grid(row=5, column=0, padx=10, pady=10)

    root.columnconfigure(0, weight=1)

    previous_menu = None
    back_button = None

def set_username():
    global username
    username = username_var.get()

def goto_input_hujan():
    global previous_menu, entry_username
    if not root_exists: return

    # Check username for the first time
    username = entry_username.get()
    if not username.strip():
        messagebox.showerror("Error", "Tolong masukkan username.")
        return

    previous_menu = "main"
    hide_all_widgets()
    show_rainfall_options()

def goto_analisa_pemupukan():
    global previous_menu, entry_username
    if not root_exists: return

    # Check username for the first time
    username = entry_username.get()
    if not username.strip():
        messagebox.showerror("Error", "Please enter a username.")
        return
    
    previous_menu = "main"
    hide_all_widgets()
    show_estate_options_for_analysis()

def disable_buttons():
    """Disables all interactive buttons to prevent further events."""
    global back_button, submit_rainfall_button, submit_estate_button, exit_button, submit_estate_add_rainfall_button, button_input_hujan, button_analisa_pemupukan, button_update_rainfall, button_add_rainfall, reanalyze_button, main_menu_button, submit_update_rainfall_button, button_tanggal_rencana_pupuk, button_tanggal_pupuk_terakhir  # Add the new buttons

    # Crucial: Check if the root window exists before interacting with ANY widgets.
    if not root_exists:
        return

    # Use try-except blocks for extra safety.
    try:
        if back_button: back_button.config(state="disabled")
    except tk.TclError: pass
    try:
        if submit_rainfall_button: submit_rainfall_button.config(state="disabled")
    except tk.TclError: pass
    try:
        if submit_estate_button: submit_estate_button.config(state="disabled")
    except tk.TclError: pass
    try:
        if exit_button: exit_button.config(state="disabled")
    except tk.TclError: pass
    try:
        if submit_estate_add_rainfall_button: submit_estate_add_rainfall_button.config(state="disabled")
    except tk.TclError: pass
    try:
        if button_input_hujan: button_input_hujan.config(state="disabled")
    except tk.TclError: pass
    try:
        if button_analisa_pemupukan: button_analisa_pemupukan.config(state="disabled")
    except tk.TclError: pass
    try:
        if button_update_rainfall: button_update_rainfall.config(state="disabled")
    except tk.TclError: pass
    try:
        if button_add_rainfall: button_add_rainfall.config(state="disabled")
    except tk.TclError: pass
    try:
        if reanalyze_button: reanalyze_button.config(state="disabled")
    except tk.TclError: pass
    try:
        if main_menu_button: main_menu_button.config(state="disabled")
    except tk.TclError: pass
    try:
        if submit_update_rainfall_button: submit_update_rainfall_button.config(state="disabled")
    except tk.TclError: pass
    try:
        if button_tanggal_rencana_pupuk: button_tanggal_rencana_pupuk.config(state="disabled")
    except tk.TclError: pass
    try:
        if button_tanggal_pupuk_terakhir: button_tanggal_pupuk_terakhir.config(state="disabled")
    except tk.TclError: pass
 
def on_closing():
    global root_exists
    root_exists = False
    disable_buttons()
    root.destroy()

def main_process():
    global root, previous_menu, root_exists, current_menu, \
        back_button, submit_rainfall_button, \
        submit_estate_button, exit_button, \
        label_estate_option, combobox_estate, entry_blok, \
        label_tanggal_rencana_pupuk, entry_tanggal_rencana_pupuk, \
        label_peilscale, entry_peilscale, label_tanggal_pupuk_terakhir, \
        entry_tanggal_pupuk_terakhir, label_jenis_pupuk_terakhir, \
        combobox_jenis_pupuk_terakhir, label_rencana_jenis_pupuk, \
        combobox_rencana_jenis_pupuk, label_rainfall_option, \
        combobox_rainfall, submit_estate_add_rainfall_button, \
        entry_daily_rainfall, label_username, entry_username, \
        label_daily_rainfall, label_blok, button_input_hujan, \
        button_analisa_pemupukan, button_update_rainfall, \
        button_add_rainfall, label_tanggal_analisa, label_nama_user, \
        label_curah_hujan, label_status, label_reason, \
        label_recommendation, label_selected_estate, \
        label_nama_blok, label_tanggal_rencana, label_peilscale_value, \
        label_tanggal_terakhir_value, label_jenis_terakhir_value, \
        label_rencana_jenis_value, back_to_main_button, reanalyze_button, \
        main_menu_button, label_update_rainfall, entry_update_rainfall, \
        submit_update_rainfall_button, df, username_var, label_saved_username, username

    # Initialize utilities
    root = tk.Tk()
    root.title("Fertilizer Analysis")
    root.state('zoomed')
    previous_menu = None
    root_exists = True
    current_menu = None
    df = pd.DataFrame()
    username_var = StringVar() 
    username = ""

    # Initialize all widget variables to None
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

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.columnconfigure(0, weight=1)

    # Initial load data from google sheet
    df = load_database(sheet_url, json_path)
    if df.empty:
        tk.messagebox.showerror("Error", "Failed to load data from the spreadsheet.  Please check your connection and credentials.")
        root.destroy()
        return

    create_main_widgets()
    root.mainloop()

# %% [markdown]
# # Main Body Function

# %%
if __name__ == "__main__":
    main_process()


