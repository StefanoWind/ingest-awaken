import xarray as xr
from pathlib import Path
from tsdat import PipelineConfig, assert_close


def test_flux_lowspeed_pipeline():
    config_path = Path("pipelines/flux_lowspeed/config/pipeline_nwtc.yaml")
    config = PipelineConfig.from_yaml(config_path)
    pipeline = config.instantiate_pipeline()

    test_file = "pipelines/flux_lowspeed/test/data/input/CR1000X_21544_Cellular_LowSpeedData_2021_08_24_1600.dat"
    expected_file = "pipelines/flux_lowspeed/test/data/expected/nwtc.flux_lowspeed_21544.a1.20210824.160003.nc"

    dataset = pipeline.run([test_file])
    expected: xr.Dataset = xr.open_dataset(expected_file)  # type: ignore
    assert_close(dataset, expected, check_attrs=False)
