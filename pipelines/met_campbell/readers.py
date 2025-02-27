from typing import Dict, Union
from pydantic import BaseModel, Extra
import xarray as xr
import pandas as pd
from datetime import datetime
from tsdat import DataReader


class METReader(DataReader):
    """---------------------------------------------------------------------------------
    Custom file handler for reading meteorological files from Campbell dataloggers
    for the A2E AWAKEN effort.

    Built-in implementations of data readers can be found in the
    [tsdat.io.readers](https://tsdat.readthedocs.io/en/latest/autoapi/tsdat/io/readers)
    module.

    ---------------------------------------------------------------------------------"""

    def read(self, input_key: str) -> Union[xr.Dataset, Dict[str, xr.Dataset]]:
        columns = [
            "id",
            "year",
            "day",
            "time",
            "S",
            "U",
            "U_dir",
            "U_dir_std",
            "T",
            "RH",
            "P",
            "E",
            "T_10X",
            "p_10X",
        ]
        df = pd.read_csv(
            input_key, delimiter=",", header=None, index_col=False, names=columns
        )

        dt = [0] * len(df)
        for year, jd, t, i in zip(df["year"], df["day"], df["time"], df.index):
            t = f"{'0'*(4 - len(str(t)))}{t}"  # pad t so it is always HHMM (not HMM or MM)
            dt[i] = datetime.strptime(f"{year}-{jd}-{t}", "%Y-%j-%H%M")  # type: ignore

        df["datetime"] = dt
        df.drop(columns=["year", "day", "time"], inplace=True)
        df.set_index("datetime", drop=True, inplace=True)

        return df.to_xarray()
