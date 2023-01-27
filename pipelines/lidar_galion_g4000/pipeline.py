import xarray as xr
import matplotlib.pyplot as plt
import cmocean
from tsdat import IngestPipeline, get_start_date_and_time_str, get_filename

from utils import format_time_xticks


class GalionG4000Lidar(IngestPipeline):
    """---------------------------------------------------------------------------------
    GALION G4000 LIDAR INGESTION PIPELINE
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
        ds = dataset

        # Create the first plot - Az, El, Pitch and Roll
        with self.storage.uploadable_dir(datastream) as tmp_dir:
            # Create the figure and axes objects
            fig, ax = plt.subplots(
                nrows=4, ncols=1, figsize=(14, 8), constrained_layout=True
            )
            fig.suptitle(f"Position of lidar at {location} on {date}")

            # Select heights to plot
            range_gates = [2, 22, 42, 62, 82]

            # Plot the data
            ds.azimuth.plot(ax=ax[0], linewidth=2)
            ds.elevation.plot(ax=ax[1], linewidth=2)
            ds.pitch.plot(ax=ax[2], linewidth=2)
            ds["roll"].plot(ax=ax[3], linewidth=2)

            # Set the labels and ticks
            [format_time_xticks(a) for a in ax]
            # ax.legend(facecolor="white", ncol=len(heights), bbox_to_anchor=(1, -0.05))
            ax[0].set_title("")  # Remove bogus title created by xarray
            [a.set_xlabel("") for a in ax[:-1]]
            ax[-1].set_xlabel("Time (UTC)")

            plot_file = get_filename(dataset, title="position", extension="png")
            fig.savefig(tmp_dir / plot_file)
            plt.close(fig)

        # Create the second plot - Doppler, Intensity at several range gates
        with self.storage.uploadable_dir(datastream) as tmp_dir:
            # Create the figure and axes objects
            fig, ax = plt.subplots(
                nrows=2, ncols=1, figsize=(14, 8), constrained_layout=True
            )
            fig.suptitle(f"Lidar Time Series at {location} on {date}")
            wind_cmap = cmocean.cm.deep_r

            # Select range_gates to plot
            range_gates = [2, 22, 42, 62, 82]

            # Plot the data
            for i, range_gate in enumerate(range_gates):
                wind_speed = ds.wind_speed.sel(range_gate=range_gate)
                wind_speed.plot(
                    ax=ax[0],
                    linewidth=2,
                    c=wind_cmap(i / len(range_gates)),
                    label=f"RG_{range_gate}",
                )

                intensity = ds.intensity.sel(range_gate=range_gate)
                intensity.plot(ax=ax[1], linewidth=2, c=wind_cmap(i / len(range_gates)))

            # # Set the labels and ticks
            # format_time_xticks(ax)
            ax[0].legend(facecolor="white", ncol=len(range_gates))
            [a.set_title("") for a in ax]  # Remove bogus title created by xarray
            # ax[-1].set_xlabel("Time (UTC)")
            # ax[0].set_ylabel(r"Wind Speed (ms$^{-1}$)")

            plot_file = get_filename(
                dataset, title="wind_speed_intensity", extension="png"
            )
            fig.savefig(tmp_dir / plot_file)
            plt.close(fig)
