import xarray as xr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from tsdat import IngestPipeline, get_start_date_and_time_str, get_filename

# from utils import format_time_xticks


def subplots(vert_size, hor_size, margin=0.05, spacing=0.02):

    w = hor_size / np.sum(hor_size) * (1 - 2 * margin - len(hor_size) * spacing)
    x = margin + np.append(0, np.cumsum(w[:-1] + spacing))

    h = vert_size / np.sum(vert_size) * (1 - 2 * margin - len(vert_size) * spacing)
    y = np.flip(margin + np.append(0, np.cumsum(np.flip(h[1:]) + spacing)))

    ax = []
    fig = plt.gcf()
    for j in range(len(hor_size)):
        for i in range(len(vert_size)):
            ax.append(fig.add_axes((x[j], y[i], w[j], h[i])))
    return ax


class Assist(IngestPipeline):
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

        extract = {
            r"Tb at 675 cm$^{-1}$": "mean_tb_675_680",
            r"Tb at 985 cm$^{-1}$": "mean_tb_985_990",
            "ABB (apex)": "abb_apex_temperature",
            "ABB (bottom)": "abb_bottom_temperature",
            "ABB (top)": "abb_top_temperature",
            "HBB (apex)": "hbb_apex_temperature",
            "HBB (bottom)": "hbb_bottom_temperature",
            "HBB (top)": "hbb_top_temperature",
            "Front End": "front_end_temperature",
            "Interferometer": "interferometer_temperature",
            "Cooling Temp": "cooler_block_temperature",
            "LW Responsivity": "lw_responsivity",
            "IM Radiance": "mean_imaginary_rad_985_990",
            "Humidity [%]": "interferometer_humidity",
            "Hatch status": "hatch_status",
        }

        offset = {
            r"Tb at 675 cm$^{-1}$": -273.15,
            r"Tb at 985 cm$^{-1}$": -273.15,
            "ABB (apex)": 0,
            "ABB (bottom)": 0,
            "ABB (top)": 0,
            "HBB (apex)": 0,
            "HBB (bottom)": 0,
            "HBB (top)": 0,
            "Front End": 0,
            "Interferometer": 0,
            "Cooling Temp": 0,
            "LW Responsivity": 0,
            "IM Radiance": 0,
            "Humidity [%]": 0,
            "Hatch status": 0,
        }

        # graphics
        plot_split = [
            [
                r"Tb at 675 cm$^{-1}$",
                r"Tb at 985 cm$^{-1}$",
                "ABB (apex)",
                "Front End",
                "Interferometer",
                "Cooling Temp",
            ],
            [
                "ABB (apex)",
                "ABB (top)",
                "ABB (bottom)",
                "HBB (apex)",
                "HBB (top)",
                "HBB (bottom)",
            ],
            ["LW Responsivity"],
            ["IM Radiance"],
            ["Humidity [%]"],
        ]

        colors = [
            [0, 0, 0, 1],
            [1, 0, 0, 1],
            [0, 1, 0, 1],
            [0, 0, 1, 1],
            [1, 0, 1, 1],
            [0, 1, 1, 1],
        ]
        ylim = [[-150, 50], [0, 70], [0, 5 * 10**5], [-1, 1], [0, 15]]
        yscale = ["linear", "linear", "linear", "linear", "linear"]

        N_days = 2

        t0 = []  # type: ignore

        plt.style.use("default")  # clear any styles that were set before
        plt.style.use("shared/styling.mplstyle")

        with self.storage.uploadable_dir(datastream) as tmp_dir:
            D = pd.DataFrame()
            C = dataset
            for c in extract.keys():
                D[c] = C[extract[c]].to_dataframe() + offset[c]

            # # indexing, already doing this
            # time = D.index + C["base_time"].values + dtm.datetime(1970, 1, 1)
            # D.index = time

            if t0 == []:
                t0 = C["time"].data[0]
                Data = pd.DataFrame()

            Data = pd.concat([Data, D])
            time = C["time"]  # type: ignore

            # plots
            if (
                True
            ):  # time.data[-1] - t0 >= np.timedelta64(int(N_days * 24 * 3600 * 0.9), "s"):
                t0 = []

                fig = plt.figure(figsize=(18, 10))
                ax = subplots([0.1, 3, 1.5, 1, 1, 1], [1])

                # hatch
                hopen = Data["Hatch status"].values == 1
                hclosed = Data["Hatch status"].values == 0
                hmove = Data["Hatch status"].values == -1

                plt.sca(ax[0])
                for i in range(10):
                    plt.plot(
                        Data.index[hopen],
                        np.zeros(np.sum(hopen)) + i,
                        ".g",
                        markersize=0.5,
                    )
                    plt.plot(
                        Data.index[hclosed],
                        np.zeros(np.sum(hclosed)) + i,
                        ".r",
                        markersize=0.5,
                    )
                    plt.plot(
                        Data.index[hmove],
                        np.zeros(np.sum(hmove)) + i,
                        ".b",
                        markersize=0.5,
                    )
                plt.xticks([])
                plt.yticks([])
                plt.title(f"ASSIST summary at {location} on {date}")

                i = 2
                for a, ps, yl, ys in zip(ax[1:], plot_split, ylim, yscale):
                    plt.sca(a)
                    ii = 0
                    for c in ps:
                        y = Data[c]
                        y_in = y.copy()
                        y_out = y.copy()
                        y_out[(y_in < yl[1]) & (y_in > yl[0])] = np.nan  # type: ignore
                        y_in[(y > yl[1]) + (y < yl[0])] = np.nan  # type: ignore
                        y_out[y_out > yl[1]] = yl[1] - (yl[1] - yl[0]) * 0.01  # type: ignore
                        y_out[y_out < yl[0]] = yl[0] + (yl[1] - yl[0]) * 0.01  # type: ignore
                        plt.plot(y_in, "-", linewidth=1, color=colors[ii], label=c)
                        plt.plot(y_out, "-", linewidth=1, color=colors[ii], alpha=0.5)
                        ii += 1
                    if len(ps) > 1:
                        leg = plt.legend()
                        leg.set_draggable(state=True)
                    else:
                        a.set_ylabel(ps[0], rotation=80)
                    plt.yscale(ys)

                    plt.ylim(yl)
                    if i < len(ax):
                        a.xaxis.set_ticklabels([])
                    i += 1
                    a.grid(visible=True)
                plt.xlabel("UTC time")

            plot_file = get_filename(dataset, title="summary", extension="png")
            fig.savefig(tmp_dir / plot_file, bbox_inches="tight")
            plt.close(fig)
