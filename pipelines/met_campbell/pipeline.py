import xarray as xr
import matplotlib.pyplot as plt
from tsdat import IngestPipeline, get_start_date_and_time_str, get_filename
from utils import format_time_xticks


class MET(IngestPipeline):
    """---------------------------------------------------------------------------------
    This is an example ingestion pipeline meant to demonstrate how one might set up a
    pipeline using this template repository.

    ---------------------------------------------------------------------------------"""

    def hook_customize_dataset(self, dataset: xr.Dataset) -> xr.Dataset:
        # (Optional) Use this hook to modify the dataset before qc is applied
        return dataset

    def hook_finalize_dataset(self, dataset: xr.Dataset) -> xr.Dataset:
        # (Optional) Use this hook to modify the dataset after qc is applied
        # but before it gets saved to the storage area
        return dataset

    def hook_plot_dataset(self, dataset: xr.Dataset):
        location = self.dataset_config.attrs.location_id
        datastream: str = self.dataset_config.attrs.datastream

        date, time = get_start_date_and_time_str(dataset)
        ds = dataset

        plt.style.use("default")  # clear any styles that were set before
        plt.style.use("shared/styling.mplstyle")

        with self.storage.uploadable_dir(datastream) as tmp_dir:
            fig, ax = plt.subplots(
                nrows=2, ncols=1, figsize=(14, 8), constrained_layout=True
            )

            ax[0].plot(ds["time"], ds["wind_speed"], label="resultant")
            ax[0].plot(ds["time"], ds["average_wind_speed"], label="mean")
            ax[0].legend(ncol=2, bbox_to_anchor=(1, -0.05))
            ax[0].set_ylabel("Wind Speed [m/s]")
            ax[0].set_xlabel("Time (UTC)")

            ax[1].plot(ds["time"], ds["wind_direction"])
            ax[1].set_ylabel("Wind Direction [deg]")
            ax[1].set_xlabel("Time (UTC)")

            plot_file = get_filename(dataset, title="wind", extension="png")
            fig.savefig(tmp_dir / plot_file)
            plt.close(fig)

        with self.storage.uploadable_dir(datastream) as tmp_dir:
            fig, ax = plt.subplots(
                nrows=4, ncols=1, figsize=(14, 8), constrained_layout=True
            )

            ax[0].plot(ds["time"], ds["temperature"])
            ax[0].set_ylabel("Temperature [deg C]")
            ax[0].set_xlabel("Time (UTC)")

            ax[1].plot(ds["time"], ds["pressure"])
            ax[1].set_ylabel("Pressure [kPa]")
            ax[1].set_xlabel("Time (UTC)")

            ax[2].plot(ds["time"], ds["relative_humidity"])
            ax[2].set_ylabel("Relative Humidity [%]")
            ax[2].set_xlabel("Time (UTC)")

            ax[3].plot(ds["time"], ds["shortwave_radiation"])
            ax[3].set_ylabel("Shortwave Radiation [W/m^2]")
            ax[3].set_xlabel("Time (UTC)")

            plot_file = get_filename(dataset, title="met", extension="png")
            fig.savefig(tmp_dir / plot_file)
            plt.close(fig)
