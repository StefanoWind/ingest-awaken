import xarray as xr
from pathlib import Path
from tsdat import PipelineConfig, assert_close


def test_aml_lidar_pipeline():
    config_path = Path("pipelines/aml_lidar/config/pipeline_aml.yaml")
    config = PipelineConfig.from_yaml(config_path)
    pipeline = config.instantiate_pipeline()

    test_file = "pipelines/aml_lidar/test/data/input/aml.ld.z01.00.20211222.204000.dat"
    expected_file = (
        "pipelines/aml_lidar/test/data/expected/aml.lidar_z01.b0.20211222.203010.nc"
    )

    dataset = pipeline.run([test_file])
    expected: xr.Dataset = xr.open_dataset(expected_file)  # type: ignore
    assert_close(dataset, expected, check_attrs=False)
