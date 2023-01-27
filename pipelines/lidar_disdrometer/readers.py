from typing import Dict, Union, Any
from pydantic import BaseModel, Extra
import xarray as xr
import pandas as pd
from tsdat import DataReader


class DisdrometerReader(DataReader):
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

        # Pull non-time data
        df1: pd.DataFrame = pd.read_csv(
            input_key, nrows=18, **self.parameters.read_csv_kwargs
        )
        df2: pd.DataFrame = pd.read_csv(
            input_key, skiprows=21, **self.parameters.read_csv_kwargs
        )
        # Merge results and create dataset
        df = pd.concat([df1, df2])
        df.index = df.index.map(str)
        df = df.T

        # Get time data
        t: pd.DataFrame = pd.read_csv(
            input_key,
            skiprows=18,
            nrows=3,
            **self.parameters.read_csv_kwargs,
        )
        dt = t.values[0][-1].replace(" ", "_")
        deployment_time = ":".join((t.values[0, 0], t.values[0, 1], dt))
        sensor_time = ":".join(
            (t.values[1, 0], t.values[1, 1], t.values[1, 2] + "_" + t.values[2, 0])
        )

        # Add time to dataset
        df["19"] = sensor_time
        df["20"] = deployment_time

        ds = xr.Dataset.from_dataframe(df, **self.parameters.from_dataframe_kwargs)
        return ds
