import numpy as np
import xarray as xr
import os
import shutil

def calculate_cutoff_indexes(ds, alt_min_ft_AMSL, alt_max_ft_AMSL):
    height_ft = height = ds["z"].isel(latitude=0, longitude=0).values / 9.81 * 3.28084

    min_idx = -1
    max_idx = -1
    for i, h in enumerate(height_ft):
        if min_idx < 0:
            if h >= alt_min_ft_AMSL:
                min_idx = i
        elif max_idx < 0:
            if h > alt_max_ft_AMSL:
                max_idx = i - 1
            elif h == alt_max_ft_AMSL:
                max_idx = i
        else:
            break

    return min_idx, max_idx


def fix_RH(ds_temp, ds_RH):
    # See https://www.ecmwf.int/sites/default/files/elibrary/2016/17117-part-iv-physical-processes.pdf#subsection.7.4.2

    if np.max(ds_temp) - 273.15 >= -23:
        raise ValueError("Don't be lazy and fix the RHi")

    return ds_RH / 100


def filter_cc(ds):
    # https://docs.xarray.dev/en/stable/generated/xarray.Dataset.max.html
    return ds["cc"].max(dim="pressure_level").values


def filter_RHi(ds, alt_min_ft_AMSL, alt_max_ft_AMSL):
    # Slice the relavant altitudes
    min_idx, max_idx = calculate_cutoff_indexes(
        ds, alt_min_ft_AMSL=alt_min_ft_AMSL, alt_max_ft_AMSL=alt_max_ft_AMSL
    )
    ds_temp = ds["t"].isel(pressure_level=slice(min_idx, max_idx + 1))
    ds_RH = ds["r"].isel(pressure_level=slice(min_idx, max_idx + 1))

    # Ensure that the RH is in ratio and is with respect to ice
    ds_RH = fix_RH(ds_temp, ds_RH)

    ds_RH_collapsed = ds_RH.max(dim="pressure_level").values

    # https://docs.xarray.dev/en/stable/generated/xarray.where.html
    mask = xr.where(ds_RH_collapsed >= 0.98, 1, 0)

    return mask


if __name__ == "__main__":
    ipdir = "inputs/"
    opdir = "processed_data/"
    delete = True

    # Clear the output directory if requested and it exists
    if delete and os.path.exists(opdir):
        shutil.rmtree(opdir)

    # Create the output directory
    if not os.path.exists(opdir):
        os.makedirs(opdir)

    for filename in os.listdir(ipdir):
        file_path = os.path.join(ipdir, filename)

        if filename.endswith(".nc"):  # Ensures it's a file
            ds = xr.open_dataset(f"inputs/{filename}", engine="netcdf4")
            filename = filename.split(".")[0]
            
            times = ds["valid_time"].values
            for i in range(len(times)):
                ds_current = ds.isel(valid_time=i)
                
                hour = times[i].astype('datetime64[h]').item().hour
                day = times[i].astype('datetime64[D]').item().day
                month = times[i].astype('datetime64[M]').item().month
                year = times[i].astype('datetime64[Y]').item().year
                op_filename = f"{opdir}{year}{month:02d}{day:02d}{hour:02d}"
                
                # Filter and save the cloud coverage and RHi
                np.save(f"{op_filename}-cc", filter_cc(ds_current))
                np.save(
                    f"{op_filename}-rhi",
                    filter_RHi(ds_current, alt_min_ft_AMSL=25000, alt_max_ft_AMSL=45000),
                )
