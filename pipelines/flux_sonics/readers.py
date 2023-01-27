from typing import Dict, Union, Any
from pydantic import BaseModel, Extra
import xarray as xr
import pandas as pd
import numpy as np
from tsdat import DataReader


class FluxSonicsReader(DataReader):
    """---------------------------------------------------------------------------------
    Custom DataReader that can be used to read data from a specific format.

    Built-in implementations of data readers can be found in the
    [tsdat.io.readers](https://tsdat.readthedocs.io/en/latest/autoapi/tsdat/io/readers)
    module.

    ---------------------------------------------------------------------------------"""

    class Parameters(BaseModel, extra=Extra.forbid):
        read_csv_kwargs: Dict[str, Any] = {}
        from_dataframe_kwargs: Dict[str, Any] = {}

    parameters: Parameters = Parameters()
    """Extra parameters that can be set via the retrieval configuration file. If you opt
    to not use any configuration parameters then please remove the code above."""

    def read(self, input_key: str) -> Union[xr.Dataset, Dict[str, xr.Dataset]]:
        df: pd.DataFrame = pd.read_csv(input_key, **self.parameters.read_csv_kwargs)  # type: ignore
        ds = df.to_xarray()

        # combine into inputs defined by config file
        ds["height"] = xr.DataArray([3, 7], dims="height")
        inputs = ["U_ax", "V_ax", "W_ax", "Ts"]

        input_data = {}
        for inp in inputs:
            input_data[inp] = np.r_[
                [np.array(ds[f"{inp}_{h}m"]) for h in ds.height.data]
            ]

        ds["wind_velocity"] = xr.DataArray(
            np.array([input_data["U_ax"], input_data["V_ax"], input_data["W_ax"]]).T,
            dims=["index", "height", "dir"],
            coords={"index": ds.index, "height": ds.height, "dir": ["U", "V", "W"]},
        )
        ds["air_temperature"] = xr.DataArray(
            input_data["Ts"].T, dims=["index", "height"]
        )

        return ds
