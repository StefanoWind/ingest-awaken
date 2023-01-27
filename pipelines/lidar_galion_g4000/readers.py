from typing import Dict, Union
from pydantic import BaseModel, Extra
import xarray as xr
import pandas as pd
import numpy as np
from tsdat import DataReader


class ScnReader(DataReader):
    """---------------------------------------------------------------------------------
    Custom DataReader that can be used to read data from a specific format.

    Built-in implementations of data readers can be found in the
    [tsdat.io.readers](https://tsdat.readthedocs.io/en/latest/autoapi/tsdat/io/readers)
    module.

    ---------------------------------------------------------------------------------"""

    def read(self, input_key: str) -> Union[xr.Dataset, Dict[str, xr.Dataset]]:
        df = pd.read_csv(input_key, sep="\t", header=5, index_col=False)

        time = df["Ray time"].unique()
        azimuth = df[df["Range gate"] == 0]["Az"].to_numpy()
        elevation = df[df["Range gate"] == 0]["El"].to_numpy()
        pitch = df[df["Range gate"] == 0]["Pitch"].to_numpy()
        roll = df[df["Range gate"] == 0]["Roll"].to_numpy()
        range_gate = np.unique(df["Range gate"].to_numpy())

        wind_speed = np.full(
            (len(time), len(range_gate)), fill_value=-9999, dtype=np.float64
        )
        intensity = np.full(
            (len(time), len(range_gate)), fill_value=-9999, dtype=np.float64
        )

        for index, row in df.iterrows():
            i_range = row["Range gate"]
            i_time = np.where(row["Ray time"] == time)

            wind_speed[i_time, i_range] = row["Doppler"]
            intensity[i_time, i_range] = row["Intensity"]

        dataset = xr.Dataset(
            {
                "azimuth": (("time"), azimuth),
                "elevation": (("time"), elevation),
                "pitch": (("time"), pitch),
                "roll": (("time"), roll),
                "wind_speed": (("time", "range_gate"), wind_speed),
                "intensity": (("time", "range_gate"), intensity),
            },
            coords={"time": time, "range_gate": range_gate},
        )

        return dataset
