import xarray as xr
import matplotlib.pyplot as plt
from tsdat import IngestPipeline, get_start_date_and_time_str, get_filename
from utils import format_time_xticks


class WindCubeNacelleSTA(IngestPipeline):
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

        # sta file
        # Wind speed and cnr plot
        with self.storage.uploadable_dir(datastream) as tmp_dir:
            fig, ax = plt.subplots(4, 1)

            dataset["HWS_low"].mean(dim="distance").plot(
                ax=ax[0], x="time", label="low"
            )
            dataset["HWS_hub"].mean(dim="distance").plot(
                ax=ax[0], x="time", label="hub"
            )
            dataset["HWS_high"].mean(dim="distance").plot(
                ax=ax[0], x="time", label="high"
            )
            ax[0].set_ylabel("HWS (m/s)")
            ax[0].set_xlabel("Time (UTC)")
            ax[0].legend()

            dataset["direction_low"].mean(dim="distance").plot(
                ax=ax[1], x="time", label="low"
            )
            dataset["direction_hub"].mean(dim="distance").plot(
                ax=ax[1], x="time", label="hub"
            )
            dataset["direction_high"].mean(dim="distance").plot(
                ax=ax[1], x="time", label="high"
            )
            ax[1].set_ylabel(r"WD ($^\circ$)")
            ax[1].set_xlabel("Time (UTC)")
            ax[1].legend()

            dataset["TI_low"].mean(dim="distance").plot(ax=ax[2], x="time", label="low")
            dataset["TI_hub"].mean(dim="distance").plot(ax=ax[2], x="time", label="hub")
            dataset["TI_high"].mean(dim="distance").plot(
                ax=ax[2], x="time", label="high"
            )
            ax[2].set_ylabel("TI (-)")
            ax[2].set_xlabel("Time (UTC)")
            ax[2].legend()

            dataset["CNR0"].mean(dim="distance").plot(ax=ax[3], x="time", label="CNR0")
            dataset["CNR1"].mean(dim="distance").plot(ax=ax[3], x="time", label="CNR1")
            dataset["CNR2"].mean(dim="distance").plot(ax=ax[3], x="time", label="CNR2")
            dataset["CNR3"].mean(dim="distance").plot(ax=ax[3], x="time", label="CNR3")
            ax[3].set_ylim((None, 0))
            ax[3].set_ylabel("CNR (dB)")
            ax[3].set_xlabel("Time (UTC)")
            ax[3].legend()

            fig.suptitle(f"Wind speed, direction and CNR at {location} on {date}")
            [a.set_title("") for a in ax]  # Remove bogus title created by xarray

            plot_file = get_filename(dataset, title="wind_cnr", extension="png")
            fig.savefig(tmp_dir / plot_file)
            plt.close(fig)
