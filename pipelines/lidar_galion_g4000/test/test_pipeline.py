import xarray as xr
from pathlib import Path
from tsdat import PipelineConfig, assert_close


def test_lidar_galion_g4000_pipeline():
    config_path = Path("pipelines/lidar_galion_g4000/config/pipeline_nwtc.yaml")
    config = PipelineConfig.from_yaml(config_path)
    pipeline = config.instantiate_pipeline()

    test_file = "pipelines/lidar_galion_g4000/test/data/input/Galion - NREL - 1750194_23071906_56.scn"
    expected_file = "pipelines/lidar_galion_g4000/test/data/expected/nwtc.lidar_galion_g4000.a1.20190723.060354.nc"

    dataset = pipeline.run([test_file])
    expected: xr.Dataset = xr.open_dataset(expected_file)  # type: ignore
    assert_close(dataset, expected, check_attrs=False)
