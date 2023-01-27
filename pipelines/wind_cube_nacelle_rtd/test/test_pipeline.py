import xarray as xr
from pathlib import Path
from tsdat import PipelineConfig, assert_close


def test_wind_cube_nacelle_rtd_pipeline():
    config_path = Path("pipelines/wind_cube_nacelle_rtd/config/pipeline_nwtc.yaml")
    config = PipelineConfig.from_yaml(config_path)
    pipeline = config.instantiate_pipeline()

    test_file = "pipelines/wind_cube_nacelle_rtd/test/data/input/WIPO0200010-(wi020200010)_real_time_data_2022-01-12_19-00-00.csv"
    expected_file = "pipelines/wind_cube_nacelle_rtd/test/data/expected/nwtc.wind_cube_nacelle_rtd.a1.20220112.181801.nc"

    dataset = pipeline.run([test_file])
    expected: xr.Dataset = xr.open_dataset(expected_file)  # type: ignore
    assert_close(dataset, expected, check_attrs=False)
