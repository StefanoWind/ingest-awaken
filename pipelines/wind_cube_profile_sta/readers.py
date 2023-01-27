from typing import Dict, Union
from pydantic import BaseModel, Extra
import xarray as xr
import pandas as pd
import numpy as np
import lzma
from tsdat import DataReader


class WindCubeProfileSTAReader(DataReader):
    """---------------------------------------------------------------------------------
    Custom DataReader that can be used to read data from a specific format.

    Built-in implementations of data readers can be found in the
    [tsdat.io.readers](https://tsdat.readthedocs.io/en/latest/autoapi/tsdat/io/readers)
    module.

    ---------------------------------------------------------------------------------"""

    def read(self, input_key: str) -> Union[xr.Dataset, Dict[str, xr.Dataset]]:
        att_dict = {}
        with lzma.open(input_key, "rt", encoding="cp1252") as f:
            header_len = int(f.readline().split("=")[1])

            for i_line in range(header_len - 1):
                header_line = f.readline()

                if "=" in header_line:
                    temp = header_line.split("=")

                att_string = temp[1].replace("\n", "")
                att_string = att_string.replace("°", "deg")

                att_key = temp[0].replace("°", "deg")
                att_key = att_key.replace("/", ",")
                att_dict[att_key] = att_string

            # start at 1 because we've already read the header
            df = pd.read_csv(f, sep="\t", header=1, index_col=False)

        # Get rid of '°'s
        rename_map = {}
        for col in df.columns:
            if "°" in col:
                rename_map[col] = col.replace("°", "deg")

        df.rename(columns=rename_map, inplace=True)

        # Change V to -1
        if "Position" in df:
            df["Position"][df["Position"] == "V"] = -1
            df["Position"] = df["Position"].astype(float)

        # # Drop rows with nan in Timestamp for rtd files
        # if "Timestamp" in df:
        #     df = df[~df["Timestamp"].isna()]

        ds = df.to_xarray()
        ds.attrs = att_dict

        # Add distance variable
        ds["distance"] = np.fromstring(
            ds.attrs["Altitudes AGL (m)"], sep="\t", dtype=int
        )

        # Compress row of variables in input into variables dimensioned by time and distance
        raw_categories = [
            "Wind Speed (m/s)",
            "Wind Direction (deg)",
            "CNR (dB)",
            "Wind Speed min (m/s)",
            "Wind Speed max (m/s)",
            "Wind Speed Dispersion (m/s)",
            "Z-wind (m/s)",
            "Z-wind Dispersion (m/s)",
            "Dopp Spect Broad (m/s)",
            "Data Availability (%)",
        ]
        output_var_names = [
            "wind_speed",
            "wind_direction",
            "CNR",
            "min_wind_speed",
            "max_wind_speed",
            "horizontal_dispersion",
            "vertical_wind_speed",
            "vertical_dispersion",
            "doppler_spectral_broadening",
            "data_availability",
        ]
        distances = ds.distance.data
        for category, output_name in zip(raw_categories, output_var_names):
            var_names = [f"{distance}m {category}" for distance in distances]
            var_data = [ds[name].data for name in var_names]
            ds = ds.drop_vars(var_names)
            var_data = np.array(var_data).transpose()  # type: ignore
            ds[output_name] = xr.DataArray(var_data, dims=["index", "distance"])

        return ds
