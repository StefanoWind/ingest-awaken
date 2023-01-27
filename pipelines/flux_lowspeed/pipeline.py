import xarray as xr
import matplotlib.pyplot as plt
from tsdat import IngestPipeline, get_start_date_and_time_str, get_filename
from utils import format_time_xticks


class FluxLowspeed(IngestPipeline):
    """---------------------------------------------------------------------------------
    FLUX_LOWSPEED_NWTC INGESTION PIPELINE

    Low speed data from surface flux station from NWTC
    ---------------------------------------------------------------------------------"""

    def hook_customize_dataset(self, dataset: xr.Dataset) -> xr.Dataset:
        # (Optional) Use this hook to modify the dataset before qc is applied
        return dataset

    def hook_finalize_dataset(self, dataset: xr.Dataset) -> xr.Dataset:
        # (Optional) Use this hook to modify the dataset after qc is applied
        # but before it gets saved to the storage area
        return dataset

    def hook_plot_dataset(self, dataset: xr.Dataset):
        # (Optional, recommended) Create plots.
        location = self.dataset_config.attrs.location_id
        datastream: str = self.dataset_config.attrs.datastream

        date, time = get_start_date_and_time_str(dataset)

        plt.style.use("default")  # clear any styles that were set before
        plt.style.use("shared/styling.mplstyle")

        with self.storage.uploadable_dir(datastream) as tmp_dir:
            # Create the figure and axes objects
            fig, ax = plt.subplots(
                nrows=4, ncols=1, figsize=(14, 8), constrained_layout=True
            )
            fig.suptitle(
                f"Wind Speed and Direction Time Series at {location} on {date}"
            )

            dataset.wind_speed.plot(ax=ax[0], linewidth=2)
            dataset.surface_air_pressure.plot(ax=ax[1], linewidth=2)
            dataset.air_temperature.plot(ax=ax[2], linewidth=2)
            dataset.relative_humidity.plot(ax=ax[3], linewidth=2)

            # Set the labels and ticks

            [a.set_xticklabels("") for a in ax]
            [a.set_ylabel(a.get_ylabel(), rotation=45, labelpad=50) for a in ax]

            format_time_xticks(ax[-1])

            ax[-1].set_xlabel("Time (UTC)")

            plot_file = get_filename(
                dataset, title="wind_speed_and_dir", extension="png"
            )
            fig.savefig(tmp_dir / plot_file)
            plt.close(fig)
