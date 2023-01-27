import xarray as xr
import numpy as np
from matplotlib import cm, pyplot as plt

from tsdat import IngestPipeline, get_start_date_and_time_str, get_filename
from utils import format_time_xticks


class WindCubeProfile(IngestPipeline):
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

        plt.style.use("default")  # clear any styles that were set before
        plt.style.use("shared/styling.mplstyle")

        with self.storage.uploadable_dir(datastream) as tmp_dir:

            fig, ax = plt.subplots(2, 1)

            cols = cm.coolwarm(np.linspace(0, 1, len(dataset.distance)))
            for h, c in zip(dataset.distance, cols):
                ws_distance = dataset.wind_speed.sel(distance=h)
                wd_distance = dataset.wind_direction.sel(distance=h)

                ws_distance.plot.line(
                    ax=ax[0],
                    x="time",
                    label=f"z = {float(h)}m",
                    color=c,
                    ylim=[0, 25],
                    linewidth=0.5,
                )
                wd_distance.plot.line(
                    ax=ax[1],
                    x="time",
                    color=c,
                    add_legend=False,
                    ylim=[0, 360],
                    linewidth=0.5,
                )

            [a.grid() for a in ax]
            fig.suptitle(f"Wind speed and direction at {location} on {date}")
            [a.set_title("") for a in ax]  # Remove bogus title created by xarray
            ax[0].legend(ncol=2)
            # ax.set_ylabel("Example (m)")
            ax[-1].set_xlabel("Time (UTC)")
            # [format_time_xticks(a) for a in ax]

            plot_file = get_filename(
                dataset, title="wind_speed_and_dir", extension="png"
            )
            fig.savefig(tmp_dir / plot_file)
            plt.close(fig)
