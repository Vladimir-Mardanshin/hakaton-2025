import pandas as pd
import pymysql
from datetime import datetime

# Путь к файлу
file_path = 'ДЕКАБРЬ.xlsx'

# Подключение к БД
connection = pymysql.connect(
    host='localhost',
    user='root',
    database='hahaton-db',
)
print(1)
# Чтение файла
df = pd.read_excel(file_path)
print(2)
# Парсим дату и время
df['signal_time'] = pd.to_datetime(df['signal_time'], format='%d.%m.%Y %H:%M:%S')
df['date'] = df['signal_time'].dt.date
df['time'] = df['signal_time'].dt.time
print(3)
# Переименовываем для удобства
df.rename(columns={
    'clid': 'city',
    'uuid': 'transport',
    'vehicle_type': 'vehicle_type',
    'route': 'route',
    'lat': 'lat',
    'lon': 'lon',
    'speed': 'speed',
    'direction': 'direction'
}, inplace=True)

# Получаем уникальные значения
cities = df['city'].dropna().unique()
routes = df['route'].dropna().unique()
vehicle_types = df['vehicle_type'].dropna().unique()
transports = df[['transport', 'vehicle_type', 'route', 'city']].drop_duplicates()


# Вставка уникальных данных
def insert_unique(table, column, values):
    with connection.cursor() as cursor:
        for value in values:
            sql = f"INSERT IGNORE INTO {table} ({column}) VALUES (%s)"
            cursor.execute(sql, (value,))
    connection.commit()


# Вставляем города
insert_unique('cities', 'name', cities)

# Вставляем маршруты
insert_unique('routes', 'number', routes)

# Вставляем типы транспорта
insert_unique('vehicle_types', 'name', vehicle_types)

# Вставляем транспорты
with connection.cursor() as cursor:
    for _, row in transports.iterrows():
        sql = """
            INSERT IGNORE INTO transports (id, vehicle_type, route, city)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(sql, (row['transport'], row['vehicle_type'], row['route'], row['city']))
connection.commit()

# Теперь вставляем данные в таблицу data
with connection.cursor() as cursor:
    for _, row in df.iterrows():
        sql = """
            INSERT INTO data (date, time, transport, city, lat, lon, speed, direction)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            row['date'],
            row['time'],
            row['transport'],
            row['city'],
            row['lat'],
            row['lon'],
            row['speed'],
            row['direction']
        ))
connection.commit()

print("Импорт данных во все 5 таблиц завершён!")

# Закрываем соединение
connection.close()
