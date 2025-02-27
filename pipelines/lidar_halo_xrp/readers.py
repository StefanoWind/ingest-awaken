from typing import Dict, Union
from pydantic import BaseModel, Extra
import xarray as xr
import numpy as np
from tsdat import DataReader


class HplReader(DataReader):
    """---------------------------------------------------------------------------------
    Custom DataReader that can be used to read data from a specific format.

    Built-in implementations of data readers can be found in the
    [tsdat.io.readers](https://tsdat.readthedocs.io/en/latest/autoapi/tsdat/io/readers)
    module.

    ---------------------------------------------------------------------------------"""

    def read(self, input_key: str) -> Union[xr.Dataset, Dict[str, xr.Dataset]]:
        with open(input_key, "r") as f:
            lines = []
            for line_num in range(11):
                lines.append(f.readline())

            # read metadata into strings
            metadata = {}
            for line in lines:
                metaline = line.split(":")
                if "Start time" in metaline:
                    metadata["Start time"] = metaline[1:]
                else:
                    metadata[metaline[0]] = metaline[1]  # type: ignore

            # convert some metadata
            num_gates = int(metadata["Number of gates"])  # type: ignore

            # Read some of the label lines
            for line_num in range(6):
                f.readline()

            # initialize arrays
            time = []
            azimuth = []
            elevation = []
            pitch = []
            roll = []
            doppler = []
            intensity = []
            beta = []

            while True:
                a = f.readline().split()
                if not len(a):  # is empty
                    break

                time.append(float(a[0]))
                azimuth.append(float(a[1]))
                elevation.append(float(a[2]))
                pitch.append(float(a[3]))
                roll.append(float(a[4]))

                doppler.append([0] * num_gates)
                intensity.append([0] * num_gates)
                beta.append([0] * num_gates)

                for _ in range(num_gates):
                    b = f.readline().split()
                    range_gate = int(b[0])
                    doppler[-1:][0][range_gate] = float(b[1])
                    intensity[-1:][0][range_gate] = float(b[2])
                    beta[-1:][0][range_gate] = float(b[3])

        # convert date to np.datetime64
        start_time_string = "{}-{}-{}T{}:{}:{}".format(
            metadata["Start time"][0][1:5],  # year
            metadata["Start time"][0][5:7],  # month
            metadata["Start time"][0][7:9],  # day
            "00",  # hour
            "00",  # minute
            "00.00",  # second
        )

        # find times where it wraps from 24 -> 0, add 24 to all indices after
        new_day_indices = np.where(np.diff(time) < -23)
        for new_day_index in new_day_indices[0]:
            time[new_day_index + 1 :] += 24.0

        start_time = np.datetime64(start_time_string)
        datetimes = [
            start_time + np.timedelta64(int(3600 * 1e6 * dtime), "us") for dtime in time
        ]

        dataset = xr.Dataset(
            {
                "Decimal time (hours)": (("time"), time),
                "Azimuth (degrees)": (("time"), azimuth),
                "Elevation (degrees)": (("time"), elevation),
                "Pitch (degrees)": (("time"), pitch),
                "Roll (degrees)": (("time"), roll),
                "Doppler": (("time", "range_gate"), doppler),
                "Intensity": (("time", "range_gate"), intensity),
                "Beta": (("time", "range_gate"), beta),
            },
            coords={"time": np.array(datetimes), "range_gate": np.arange(num_gates)},
            attrs={"Range gate length (m)": float(metadata["Range gate length (m)"])},  # type: ignore
        )

        # Save some attributes
        dataset.attrs["Range gate length (m)"] = float(
            metadata["Range gate length (m)"]  # type: ignore
        )
        dataset.attrs["Number of gates"] = float(metadata["Number of gates"])  # type: ignore
        dataset.attrs["Scan type"] = str(metadata["Scan type"]).strip()
        dataset.attrs["Pulses or ray"] = float(metadata["Pulses/ray"])  # type: ignore
        dataset.attrs["System ID"] = int(metadata["System ID"])  # type: ignore
        dataset.attrs["Filename"] = str(metadata["Filename"])[1:-5]

        # Dynamically add scan type and z-id (z02, z03, etc) to dataset metadata
        # loc_id, instrument, z02/z03, data level, date, time, scan type, extension
        raw_basename = input_key.replace("\\", "/").rsplit("/")[-1]
        if ".z" in raw_basename:
            _, _, z_id, _, _, _, scan_type, _ = raw_basename.lower().split(".")
        else:  # local NREL tsdat-ing
            z_id = str(dataset.attrs["System ID"])
            scan_type = ""
            if "user" in raw_basename.lower():
                scan_type = raw_basename.split("_")[0].lower()
            elif "stare" in raw_basename.lower():
                scan_type = "stare"
            elif "vad" in raw_basename.lower():
                scan_type = "vad"
            elif "wind_profile" in raw_basename.lower():
                scan_type = "wind_profile"

        valid_types = ["user", "stare", "vad", "wind_profile"]
        if not any(valid_type in scan_type for valid_type in valid_types):
            raise NameError(f"Scan type '{scan_type}' not supported.")

        dataset.attrs["scan_type"] = scan_type
        dataset.attrs["z_id"] = z_id

        return dataset
