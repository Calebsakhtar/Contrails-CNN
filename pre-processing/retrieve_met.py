import cdsapi
import calendar

def retrieve_era5_data(year, month, download_dir="inputs"):
    dataset = "reanalysis-era5-pressure-levels"
    
    # Determine the number of days in the month
    num_days = calendar.monthrange(int(year), int(month))[1] #https://docs.python.org/3/library/calendar.html#calendar.monthrange
    days = [f"{day:02d}" for day in range(1, num_days + 1)]
    
    request = {
        "product_type": ["reanalysis"],
        "variable": [
            "fraction_of_cloud_cover",
            "geopotential",
            "relative_humidity",
            "temperature"
        ],
        "year": [year],
        "month": [f"{month:02d}"],
        "day": days,
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
            "50", "70", "100",
            "125", "150", "175",
            "200", "225", "250",
            "300", "350", "400"
        ],
        "data_format": "netcdf",
        "download_format": "unarchived",
        "area": [71, -83, 35, 3]
    }

    target = f"{download_dir}/{year}{month:02d}.nc"
    client = cdsapi.Client()
    client.retrieve(dataset, request, target)

if __name__ == "__main__":
    year = 2018

    for month in range(1, 13):
        retrieve_era5_data(year, month)
