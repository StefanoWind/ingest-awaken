import xarray as xr

# import matplotlib.pyplot as plt
from tsdat import IngestPipeline  # , get_start_date_and_time_str, get_filename

# from utils import format_time_xticks


class LidarDisdrometer(IngestPipeline):
    """---------------------------------------------------------------------------------
    sh_lidar INGESTION PIPELINE

    Awaken lidar disdrometer ingest
    ---------------------------------------------------------------------------------"""

    def hook_customize_dataset(self, dataset: xr.Dataset) -> xr.Dataset:
        # (Optional) Use this hook to modify the dataset before qc is applied
        dvars = [
            "serial_number",
            "firmware_iop_version",
            "firmware_dsp_version",
            "deployment_time",
            "station_name",
            "station_number",
        ]
        for v in dvars:
            dataset.attrs[v] = dataset[v].data[0]

        return dataset.drop_vars(dvars)

    def hook_finalize_dataset(self, dataset: xr.Dataset) -> xr.Dataset:
        # (Optional) Use this hook to modify the dataset after qc is applied
        # but before it gets saved to the storage area
        return dataset

    def hook_plot_dataset(self, dataset: xr.Dataset):
        # (Optional) Create plots.
        # location = self.dataset_config.attrs.location_id
        # datastream: str = self.dataset_config.attrs.datastream

        # date, time = get_start_date_and_time_str(dataset)

        # plt.style.use("default")  # clear any styles that were set before
        # plt.style.use("shared/styling.mplstyle")

        # with self.storage.uploadable_dir(datastream) as tmp_dir:

        #     fig, ax = plt.subplots()
        #     dataset["example_var"].plot(ax=ax, x="time")  # type: ignore
        #     fig.suptitle(f"Example Variable at {location} on {date} {time}")
        #     format_time_xticks(ax)
        #     plot_file = get_filename(dataset, title="example_plot", extension="png")
        #     fig.savefig(tmp_dir / plot_file)
        #     plt.close(fig)
        pass
