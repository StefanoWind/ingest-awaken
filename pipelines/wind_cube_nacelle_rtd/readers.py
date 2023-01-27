from typing import Dict, Union
from pydantic import BaseModel, Extra
import xarray as xr
import pandas as pd
import numpy as np
from tsdat import DataReader


class WindCubeReaderRTD(DataReader):
    """---------------------------------------------------------------------------------
    Custom DataReader that can be used to read data from a specific format.

    Built-in implementations of data readers can be found in the
    [tsdat.io.readers](https://tsdat.readthedocs.io/en/latest/autoapi/tsdat/io/readers)
    module.

    ---------------------------------------------------------------------------------"""

    def read(self, input_key: str) -> Union[xr.Dataset, Dict[str, xr.Dataset]]:
        df = pd.read_csv(input_key, sep=";")

        # replace column names ' ' with '_'
        rename_map = {}
        for col in df.columns:
            rename_map[col] = col.replace(" ", "_")
        df.rename(columns=rename_map, inplace=True)

        # Drop UTC info from Timestamp
        if "Date_and_Time" in df:  # 10-min avg file
            time_chan = "Date_and_Time"
        else:
            time_chan = "Timestamp"
        tt = pd.DatetimeIndex(df[time_chan])
        df[time_chan] = tt.tz_convert(None)
        dataset = df.to_xarray()

        # Add distance variable
        dataset["distance"] = xr.DataArray(df.Distance.unique(), dims="distance")
        distances = dataset.distance.data

        # 1D variables
        raw_categories = [
            time_chan,
            "Tilt",
            "Roll",
        ]
        output_var_names = [
            "time",
            "tilt",
            "roll",
        ]
        for category, output_name in zip(raw_categories, output_var_names):
            var_data = np.reshape(
                dataset[category].values,
                (len(dataset[category]) // len(distances), len(distances)),
            )
            dataset[output_name] = xr.DataArray(var_data[:, 0], dims=["time"])

        # 2D variables
        raw_categories = [
            "RWS",
            "DRWS",
            "CNR",
        ]
        output_var_names = [
            "radial_wind_speed",
            "radial_dispersion",
            "CNR",
        ]

        for category, output_name in zip(raw_categories, output_var_names):
            var_data = np.reshape(
                dataset[category].values,
                (len(dataset[category]) // len(distances), len(distances)),
            )
            dataset[output_name] = xr.DataArray(var_data, dims=["time", "distance"])

        return dataset
