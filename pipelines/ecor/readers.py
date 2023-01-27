from typing import Dict, Union
from pydantic import BaseModel, Extra
import xarray as xr
import numpy as np
from datetime import datetime
from tsdat import DataReader


class EcorReader(DataReader):
    """---------------------------------------------------------------------------------
    Custom file handler for reading txt files from an eddy flux tower
    for the A2E AWAKEN effort.

    ---------------------------------------------------------------------------------"""

    def read(self, input_key: str) -> Union[xr.Dataset, Dict[str, xr.Dataset]]:
        """----------------------------------------------------------------------------
        Method to read data in a custom format and convert it into an xarray Dataset.

        Args:
            input_key (str): The path to the file to read in.

        Returns:
            xr.Dataset: An xr.Dataset object
        ----------------------------------------------------------------------------"""

        with open(input_key) as f:
            content = f.readlines()

        dump1 = content[58].split()
        idt = list(map(int, dump1[1:4] + dump1[5:7]))
        time = datetime(idt[0], idt[1], idt[2], idt[3], idt[4])
        props = {
            "siteID": dump1[7],
            "sonic_SN": dump1[8],
            "IRGA_SN": dump1[9],
            "analog_min": float(dump1[10]),
            "analog_max": float(dump1[11]),
            "H2O_min": float(dump1[12]),
            "H2O_max": float(dump1[13]),
            "CO2_min": float(dump1[14]),
            "CO2_max": float(dump1[15]),
            "sonic_temperature_offset": float(dump1[16]),
            "sonic_temperature_slope": float(dump1[17]),
            "boom_direction": float(dump1[18]),
            "irga_lag": float(dump1[19]),
        }

        flux = list(map(float, content[9].split()))
        vars_flux = {
            "sensible_heat_flux": flux[0],
            "latent_heat_flux": flux[1],
            "CO2_flux": flux[2],
            "momentum_flux": flux[3],
            "friction_velocity": flux[4],
        }

        wind = list(map(float, content[12].split()))
        vars_wind = {
            "wind_speed": wind[0],
            "wind_direction": wind[1],
            "wind_rotation_vertical": wind[2],
            "wind_rotation_horizontal": wind[3],
            "boom_angle": wind[4],
            "wind_direction_std": wind[5],
            "wind_vertical_std": wind[6],
        }

        irga = list(map(float, content[15].split()[2:]))
        vars_irga = {
            "N_datapoints": int(content[15].split()[0][1:]),
            "irga_H2O": irga[0],
            "irga_CO2": irga[1],
            "irga_pressure": irga[2],
            "irga_temperature": irga[3],
            "irga_cooler": irga[4],
            "irga_status": irga[5],
        }

        air = list(map(float, content[18].replace("(", "").replace(")", "").split()))
        air50 = list(
            map(float, content[19].replace("(", "").replace(")", "").split()[1:])
        )
        vars_air = {
            "specific_heat": air[0],
            "specific_heat_50%RH": air50[0],
            "heat_of_vaporization": air[1],
            "heat_of_vaporization_50%RH": air50[1],
            "moist_air_density": air[2],
            "moist_air_density_50%RH": air50[2],
            "mixing_ratio": air[3],
            "mixing_ratio_50%RH": air50[3],
        }

        variables = content[29].split()
        main = {}
        for i in range(6):
            data = content[30 + i].split()
            name = data[0].replace('"', "").lower()
            # main[name] = list(map(float, data[-7:]))
            for (var, val) in zip(variables, data[-7:]):
                main[var + "_" + name] = float(val)

        data_vars = {**main, **vars_flux, **vars_wind, **vars_irga, **vars_air}

        cov = np.empty((7, 7))
        cov[:] = np.nan
        for i in range(len(variables)):
            data = np.array(list(map(float, content[40 + i].split()[1:-1])))  # type: ignore
            cov[i, : len(data)] = data

        cov_rot = np.empty((7, 7))
        cov_rot[:] = np.nan
        for i in range(len(variables)):
            data = np.array(list(map(float, content[50 + i].split()[1:-1])))  # type: ignore
            cov_rot[i, : len(data)] = data

        ds = xr.Dataset(data_vars, coords={"time": time}, attrs=props)
        # for name in main:
        #     ds[name] = xr.DataArray(main[name],
        #                             coords={'var':variables})
        ds["covariance"] = xr.DataArray(
            cov, coords={"var0": variables, "var1": variables}
        )
        ds["covariance_rotated"] = xr.DataArray(
            cov_rot, coords={"var0": variables, "var1": variables}
        )

        return ds.expand_dims(dim="time")
