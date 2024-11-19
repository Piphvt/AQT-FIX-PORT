#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import threading
from tqdm import tqdm
import time
from tvDatafeed import TvDatafeed, Interval
import os
import mysql.connector
from dotenv import load_dotenv
from datetime import datetime

# โหลดค่าจากไฟล์ .env
load_dotenv()

# ดึงค่าจาก environment variables
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_NAME = os.getenv('DB_NAME')

tv = TvDatafeed()
fetched_data = {}
data_lock = threading.Lock()
error_symbols = []

# เชื่อมต่อกับฐานข้อมูล
def get_stock_symbols():
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME
        )
        
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM stocks")
        symbols = cursor.fetchall()
        
        # ดึงชื่อหุ้นออกมาเป็นลิสต์
        stock_symbols = [symbol[0] for symbol in symbols]
        return stock_symbols
        
    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def fetch_hist_data(symbol, data_storage, max_retries=3):
    retries = 0
    original_symbol = symbol  # เก็บชื่อสัญลักษณ์เดิมสำหรับใช้ในภายหลัง
    while retries < max_retries:
        try:
            hist_data_mins = tv.get_hist(symbol=symbol, exchange='SET', interval=Interval.in_1_minute, n_bars=5000)
            with data_lock:
                data_storage[original_symbol] = hist_data_mins if hist_data_mins is not None else None
            if hist_data_mins is not None:
                break
            else:
                raise ValueError("The retrieved data was not found")
        except Exception as e:
            print(f"There was an error retrieving data for {symbol}: {e}")
            retries += 1
            time.sleep(1)
    
    if retries == max_retries:
        # พยายามดึงข้อมูลด้วยสัญลักษณ์ที่แก้ไข
        modified_symbol = symbol.replace('-', '.')
        retries = 0  # รีเซ็ตการลองใหม่สำหรับสัญลักษณ์ใหม่
        while retries < max_retries:
            try:
                hist_data_mins = tv.get_hist(symbol=modified_symbol, exchange='SET', interval=Interval.in_1_minute, n_bars=5000)
                with data_lock:
                    data_storage[original_symbol] = hist_data_mins if hist_data_mins is not None else None
                if hist_data_mins is not None:
                    break
                else:
                    raise ValueError("The retrieved data was not found")
            except Exception as e:
                print(f"There was an error retrieving data for {modified_symbol}: {e}")
                retries += 1
                time.sleep(1)
        
        # เก็บชื่อสัญลักษณ์ที่มีข้อผิดพลาด
        with data_lock:
            if symbol not in error_symbols:
                error_symbols.append(symbol)

# ดึงชื่อหุ้นจากฐานข้อมูล
symbols_to_fetch = get_stock_symbols()

threads = []
fetch_counter = 0
for symbol in tqdm(symbols_to_fetch, desc="Fetching data"):
    thread = threading.Thread(target=fetch_hist_data, args=(symbol, fetched_data))
    threads.append(thread)
    thread.start()
    fetch_counter += 1
    if fetch_counter % 4 == 0:
        time.sleep(4)

for thread in tqdm(threads, desc="Waiting for data fetching"):
    thread.join()

if error_symbols:
    for symbol in error_symbols:
        fetch_hist_data(symbol, fetched_data, max_retries=3)

# ฟังก์ชันส่งออกข้อมูล
def export_symbol_data(symbol, data, save_path):
    data_df = pd.DataFrame(data)
    if isinstance(data_df.index, pd.DatetimeIndex):
        data_df.reset_index(inplace=True)
    if 'datetime' in data_df.columns:
        data_df['datetime'] = pd.to_datetime(data_df['datetime']).dt.strftime('%Y-%m-%d %H:%M:%S')
    # ใช้ชื่อสัญลักษณ์เดิมสำหรับชื่อไฟล์
    csv_file_name = f"{symbol}_data.csv"
    full_path = os.path.join(save_path, csv_file_name)
    data_df.to_csv(full_path, index=False)

def export_data_to_csv_multithreaded(data_storage, save_path):
    threads = []
    for symbol, data in tqdm(data_storage.items(), desc="Exporting data"):
        thread = threading.Thread(target=export_symbol_data, args=(symbol, data, save_path))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()

# กำหนด path สำหรับการบันทึกไฟล์
base_dir = os.path.dirname(os.path.abspath(__file__))  
save_path = os.path.join(base_dir, 'close_price', 'symbol')  # ปรับให้เป็นโฟลเดอร์ Symbol

# สร้าง directory ถ้ายังไม่มี
os.makedirs(save_path, exist_ok=True)

# ส่งออกข้อมูล
export_data_to_csv_multithreaded(fetched_data, save_path)

# สร้าง DataFrame สำหรับเก็บราคาปิดของวันศุกร์
last_day_df = pd.DataFrame()

for symbol in symbols_to_fetch:
    try:
        file_path = os.path.join(save_path, f"{str(symbol)}_data.csv")
        print(f"Checking file: {file_path}")  # แสดงชื่อไฟล์ที่กำลังเช็ค
        if not os.path.isfile(file_path):
            print(f"File not found for {symbol}: {file_path}")
            continue
        
        data_set_df = pd.read_csv(file_path)

        if data_set_df.empty:
            print(f"File is empty for {symbol}: {file_path}")
            continue
        
        print(f"Columns for {symbol}: {data_set_df.columns.tolist()}")  # แสดงชื่อคอลัมน์
        
        data_set_df['datetime'] = pd.to_datetime(data_set_df['datetime'])
        data_set_df = data_set_df.sort_values(by='datetime', ascending=True)
        last_day_row = data_set_df.iloc[-1:]
        last_day_row.loc[:, 'symbol'] = symbol.replace('SET:', '')
        last_day_df = pd.concat([last_day_df, last_day_row], ignore_index=True)
        
    except Exception as e:
        print(f"Failed to process {symbol}: {e}")

# ใช้ os.path.join สำหรับการบันทึกไฟล์สุดท้าย
if not last_day_df.empty:
    last_day_df = last_day_df[['datetime', 'symbol', 'close']]
    last_day_save_path = os.path.join(base_dir, 'last_day_close_price.csv')  # บันทึกใน base_dir
    last_day_df.to_csv(last_day_save_path, index=False)
else:
    print("No last day data to save.")

print("All data fetching and exporting complete.")

result_dir = os.path.join(base_dir, 'result', 'close_price')
os.makedirs(result_dir, exist_ok=True)

if not last_day_df.empty:
    last_day_df = last_day_df[['datetime', 'symbol', 'close']]
    
    # Format the file name as 'date+YYYY-MM-DD+time+HH-MM.csv'
    current_time = datetime.now().strftime('%Y_%m_%d_%H_%M_close_price')
    last_day_save_path = os.path.join(result_dir, f'{current_time}.csv')

    # Save the DataFrame to the new path
    last_day_df.to_csv(last_day_save_path, index=False)
    print(f"File saved as {last_day_save_path}")
else:
    print("No last day data to save.")
