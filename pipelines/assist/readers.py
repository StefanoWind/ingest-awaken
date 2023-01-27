from typing import Dict, Union, Any
from pydantic import BaseModel, Extra
import xarray as xr
import numpy as np
from tsdat import DataReader


class AssistReader(DataReader):
    """---------------------------------------------------------------------------------
    Custom DataReader that can be used to read data from a specific format.

    Built-in implementations of data readers can be found in the
    [tsdat.io.readers](https://tsdat.readthedocs.io/en/latest/autoapi/tsdat/io/readers)
    module.

    ---------------------------------------------------------------------------------"""

    def read(self, input_key: str) -> Union[xr.Dataset, Dict[str, xr.Dataset]]:
        ds = xr.load_dataset(input_key)
        # Offset time based on base-time
        ds["time"] = np.datetime64(0, "ns") + ds["time"] + ds["base_time"]

        return ds
