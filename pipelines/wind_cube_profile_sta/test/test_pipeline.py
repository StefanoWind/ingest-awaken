import xarray as xr
from pathlib import Path
from tsdat import PipelineConfig, assert_close


def test_wind_cube_profile_sta_pipeline():
    config_path = Path("pipelines/wind_cube_profile_sta/config/pipeline_sb.yaml")
    config = PipelineConfig.from_yaml(config_path)
    pipeline = config.instantiate_pipeline()

    test_file = "pipelines/wind_cube_profile_sta/test/data/input/WLS71460_2022_02_02__00_01_00.sta.7z"
    expected_file = "pipelines/wind_cube_profile_sta/test/data/expected/sb.wind_cube_profile_sta.b0.20220202.000100.nc"

    dataset = pipeline.run([test_file])
    expected: xr.Dataset = xr.open_dataset(expected_file)  # type: ignore
    assert_close(dataset, expected, check_attrs=False)
