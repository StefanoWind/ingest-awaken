import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cmocean
from tsdat import IngestPipeline, get_start_date_and_time_str, get_filename

from utils import format_time_xticks


class LidarHaloXrp(IngestPipeline):
    """---------------------------------------------------------------------------------
    This is an example ingestion pipeline meant to demonstrate how one might set up a
    pipeline using this template repository.

    ---------------------------------------------------------------------------------"""

    def hook_customize_dataset(self, dataset: xr.Dataset) -> xr.Dataset:
        dataset["distance"] = (
            "range_gate",
            dataset.coords["range_gate"].data * dataset.attrs["Range gate length (m)"]
            + dataset.attrs["Range gate length (m)"] / 2,
        )
        dataset["distance_overlapped"] = (
            "range_gate",
            dataset.coords["range_gate"].data * 1.5
            + dataset.attrs["Range gate length (m)"] / 2,
        )
        intensity = dataset.intensity.data.copy()
        intensity[intensity <= 1] = np.nan
        dataset["SNR"].data = 10 * np.log10(intensity - 1)

        # Dynamically add scan type and z-id (z02, z03, etc) to dataset metadata
        qualifier = dataset.qualifier
        new_qualifier = "_".join(
            [qualifier, dataset.attrs.pop("scan_type"), dataset.attrs.pop("z_id")]
        )
        dataset.attrs["datastream"] = dataset.attrs["datastream"].replace(
            qualifier, new_qualifier
        )

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
            fig, ax = plt.subplots()

            ds.wind_speed.plot(
                ax=ax, x="time", cmap=cmocean.cm.deep_r, vmin=-15, vmax=15,
            )

            fig.suptitle(
                f"Wind Speed at {location} on {date} \n File: "
                + dataset.attrs["Filename"]
            )
            # add_colorbar(axs, csf, r"Wind Speed (ms$^{-1}$)")
            format_time_xticks(ax)
            ax.set_xlabel("Time (UTC)")
            ax.set_ylabel("Range Gate")

            plot_file = get_filename(
                dataset, title="wind_speed_v_dist_time", extension="png"
            )
            fig.savefig(tmp_dir / plot_file)
            plt.close(fig)

        with self.storage.uploadable_dir(datastream) as tmp_dir:
            fig, ax = plt.subplots()

            csf = ds.SNR.plot(
                ax=ax, x="time", cmap=cmocean.cm.deep_r, vmin=-30, vmax=0,
            )

            fig.suptitle(
                f"Signal to Noise Ratio at {location} on {date} \n File: "
                + dataset.attrs["Filename"]
            )

            format_time_xticks(ax)
            ax.set_xlabel("Time (UTC)")
            ax.set_ylabel("Range Gate")

            plot_file = get_filename(dataset, title="SNR_v_dist_time", extension="png")
            fig.savefig(tmp_dir / plot_file)
            plt.close(fig)
