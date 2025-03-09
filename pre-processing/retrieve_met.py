import cdsapi
import calendar
import os

reques_template = {
    "product_type": ["reanalysis"],
    "variable": [
        "fraction_of_cloud_cover",
        "geopotential",
        "relative_humidity",
        "temperature"
    ],
    "year": [],
    "month": [],
    "day": [],
    "time": [
        "00:00", "01:00", "02:00",
        "03:00", "04:00", "05:00",
        "06:00", "07:00", "08:00",
        "09:00", "10:00", "11:00",
        "12:00", "13:00", "14:00",
        "15:00", "16:00", "17:00",
        "18:00", "19:00", "20:00",
        "21:00", "22:00", "23:00"
    ],
    "pressure_level": [
        "1", "2", "3",
        "5", "7", "10",
        "20", "30", "50",
        "70", "100", "125",
        "150", "175", "200",
        "225", "250", "300",
        "350", "400", "450",
        "500", "550", "600",
        "650", "700", "750",
        "775", "800", "825",
        "850", "875", "900",
        "925", "950", "975",
        "1000"
    ],
    "data_format": "netcdf",
    "download_format": "unarchived",
    "area": [71, -83, 35, 3]
}

def retrieve_era5_data_month(year, month, download_dir="inputs"):
    global request_template
    dataset = "reanalysis-era5-pressure-levels"
    
    # Make the download directory if it doesn't exist
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    # Determine the number of days in the month
    num_days = calendar.monthrange(int(year), int(month))[1] #https://docs.python.org/3/library/calendar.html#calendar.monthrange
    
    for i in range(2):
        if i == 0:
            lower = 1
            upper = 16
        else:
            lower = 16
            upper = num_days + 1

        days = [f"{day:02d}" for day in range(lower, upper)]
        target = f"{download_dir}/{year}{month:02d}-{lower:02d}to{upper:02d}.nc"
        
        request = reques_template.copy()
        request["day"] = days
        request["month"] = [f"{month:02d}"]
        request["year"] = [year]
        
        client = cdsapi.Client()
        client.retrieve(dataset, request, target)

if __name__ == "__main__":
    year = 2018
    split_month = 6
    
    start_months = [1, split_month + 1]
    end_months = [split_month, 12]

    for i in range(len(start_months)):
        start_month = start_months[i]
        end_month = end_months[i]

        for month in range(start_month, end_month + 1):
            retrieve_era5_data_month(year, month, download_dir=f"inputs-{year}-{start_month:02d}to{end_month:02d}")
            print(f"Data for {year}-{month:02d} retrieved.")

        break
