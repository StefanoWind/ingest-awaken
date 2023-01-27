import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from tsdat import IngestPipeline, get_start_date_and_time_str, get_filename

from utils import format_time_xticks


class FluxSonics(IngestPipeline):
    """---------------------------------------------------------------------------------
    This is an example ingestion pipeline meant to demonstrate how one might set up a
    pipeline using this template repository.

    ---------------------------------------------------------------------------------"""

    def hook_customize_dataset(self, dataset: xr.Dataset) -> xr.Dataset:
        # Standard UV directions: assume U is west (270 deg.), V is south (180 deg.)
        met_direction = (
            dataset.orientation.data
        )  # - 270        # TODO: check this offset with conventions
        met_direction = np.where(met_direction < 0, met_direction + 360, met_direction)

        # Rotate velocity (270 - 90) degrees counter-clockwise so that the first dimension (U)
        # points East and V points North
        sine = np.sin(np.pi / 180 * (met_direction - 90))
        cos = np.cos(np.pi / 180 * (met_direction - 90))

        R = np.array([[cos, sine, 0], [-sine, cos, 0], [0, 0, 1]])
        vel = np.einsum("ij,k...j->k...i", R, dataset["wind_velocity"])

        dataset["wind_velocity_ENU"].values = vel

        # wind speed and direction, relative to North
        dataset["wind_speed"] = np.sqrt(
            dataset.wind_velocity_ENU[..., 0] ** 2
            + dataset.wind_velocity_ENU[..., 1] ** 2
        )
        direction_raw = np.degrees(
            np.arctan2(
                dataset.wind_velocity_ENU[..., 0], dataset.wind_velocity_ENU[..., 1]
            )
        )
        dataset["wind_direction"].values = np.where(
            direction_raw < 0, direction_raw + 360, direction_raw
        ).squeeze()

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
                nrows=2, ncols=1, figsize=(14, 8), constrained_layout=True
            )
            fig.suptitle(
                f"Wind Speed and Direction Time Series at {location} on {date}"
            )

            # Select heights to plot
            heights = [3, 7]

            # Plot the wind speed
            for i, height in enumerate(heights):
                velocity = dataset.wind_speed.sel(height=height)
                velocity.plot(
                    ax=ax[0],
                    linewidth=2,
                    # c=wind_cmap(i / len(heights)),
                    label=f"{height} m",
                )

            # Set the labels and ticks
            format_time_xticks(ax[0])
            ax[0].legend(
                facecolor="white", ncol=len(heights), bbox_to_anchor=(1, -0.05)
            )
            ax[0].set_title("")  # Remove bogus title created by xarray
            ax[0].set_xlabel("Time (UTC)")
            ax[0].set_ylabel(r"Wind Speed (ms$^{-1}$)")

            # Plot the wind direction
            for i, height in enumerate(heights):
                direction = dataset.wind_direction.sel(height=height)
                direction.plot(
                    ax=ax[1],
                    linewidth=2,
                    # c=wind_cmap(i / len(heights)),
                    label=f"{height} m",
                )

            # Set the labels and ticks
            format_time_xticks(ax[1])
            ax[1].legend(
                facecolor="white", ncol=len(heights), bbox_to_anchor=(1, -0.05)
            )
            ax[1].set_title("")  # Remove bogus title created by xarray
            ax[1].set_xlabel("Time (UTC)")
            ax[1].set_ylabel(r"Wind Direction (deg. relative to U)")

            plot_file = get_filename(dataset, title="sonic_anemometer", extension="png")
            fig.savefig(tmp_dir / plot_file)
            plt.close(fig)
