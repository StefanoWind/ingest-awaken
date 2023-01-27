import xarray as xr
from pathlib import Path
from tsdat import PipelineConfig, assert_close


def test_wind_cube_profile_rtd_pipeline():
    config_path = Path("pipelines/wind_cube_profile_rtd/config/pipeline_sb.yaml")
    config = PipelineConfig.from_yaml(config_path)
    pipeline = config.instantiate_pipeline()

    test_file = "pipelines/wind_cube_profile_rtd/test/data/input/WLS71460_2022_02_01__00_00_00.rtd.7z"
    expected_file = "pipelines/wind_cube_profile_rtd/test/data/expected/sb.wind_cube_profile_rtd.a1.20220201.000000.nc"

    dataset = pipeline.run([test_file])
    expected: xr.Dataset = xr.open_dataset(expected_file)  # type: ignore
    assert_close(dataset, expected, check_attrs=False)
