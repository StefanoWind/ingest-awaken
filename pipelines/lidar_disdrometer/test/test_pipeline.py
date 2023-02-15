import xarray as xr
from pathlib import Path
from tsdat import PipelineConfig, assert_close


def test_lidar_disdrometer_pipeline():
    config_path = Path("pipelines/lidar_disdrometer/config/pipeline_sh.yaml")
    config = PipelineConfig.from_yaml(config_path)
    pipeline = config.instantiate_pipeline()

    test_file = (
        "pipelines/lidar_disdrometer/test/data/input/sh.ld.z01.00.20221114.200300.txt"
    )
    expected_file = "pipelines/lidar_disdrometer/test/data/expected/sh_.ldis_z01.b0.20221114.200300.nc"

    dataset = pipeline.run([test_file])
    expected: xr.Dataset = xr.open_dataset(expected_file)  # type: ignore
    assert_close(dataset, expected, check_attrs=False)
