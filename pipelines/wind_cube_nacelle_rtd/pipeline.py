import xarray as xr
import matplotlib.pyplot as plt
from tsdat import IngestPipeline, get_start_date_and_time_str, get_filename
from utils import format_time_xticks


class WindCubeNacelleRTD(IngestPipeline):
    """---------------------------------------------------------------------------------
    WIND_CUBE_NACELLE INGESTION PIPELINE

    Ingest for nacelle-based wind cube
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

        plt.style.use("default")  # clear any styles that were set before
        plt.style.use("shared/styling.mplstyle")

        # Real-time plots
        # Scan pattern plot
        with self.storage.uploadable_dir(datastream) as tmp_dir:
            fig, ax = plt.subplots(2, 1)

            # dataset["distance"].plot(
            #     ax=ax[0], x="time",
            # )
            # ax[0].set_ylabel("Distance (m)")
            # ax[0].set_xlabel("Time (UTC)")

            dataset["tilt"].plot(
                ax=ax[0],
                x="time",
            )
            ax[0].set_ylabel("Tilt (deg)")
            ax[0].set_xlabel("Time (UTC)")

            dataset["roll"].plot(
                ax=ax[1],
                x="time",
            )
            ax[1].set_ylabel("Roll (deg)")
            ax[1].set_xlabel("Time (UTC)")

            fig.suptitle(f"Scan pattern at {location} on {date}")
            [a.set_title("") for a in ax]  # Remove bogus title created by xarray
            [format_time_xticks(a) for a in ax]

            plot_file = get_filename(dataset, title="scan_pattern", extension="png")
            fig.savefig(tmp_dir / plot_file)
            plt.close(fig)

        # Wind speed and cnr plot
        with self.storage.uploadable_dir(datastream) as tmp_dir:
            fig, ax = plt.subplots(3, 1)

            dataset["radial_wind_speed"].plot(
                ax=ax[0],
                x="time",
            )
            ax[0].set_ylabel("Distance (m)")
            ax[0].set_xlabel("Time (UTC)")

            dataset["radial_dispersion"].plot(
                ax=ax[1],
                x="time",
            )
            ax[1].set_ylabel("Distance (m)")
            ax[1].set_xlabel("Time (UTC)")

            dataset["CNR"].plot(
                ax=ax[2],
                x="time",
                vmax=0,
            )
            ax[2].set_ylabel("Distance (m)")
            ax[2].set_xlabel("Time (UTC)")

            fig.suptitle(f"Scan pattern at {location} on {date}")
            [a.set_title("") for a in ax]  # Remove bogus title created by xarray
            [format_time_xticks(a) for a in ax]

            plot_file = get_filename(dataset, title="wind_cnr", extension="png")
            fig.savefig(tmp_dir / plot_file)
            plt.close(fig)
