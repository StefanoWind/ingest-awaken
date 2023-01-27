import xarray as xr
from pathlib import Path
from tsdat import PipelineConfig, assert_close


def test_lidar_halo_xrp_pipeline():
    config_path = Path("pipelines/lidar_halo_xrp/config/pipeline_sa5.yaml")
    config = PipelineConfig.from_yaml(config_path)
    pipeline = config.instantiate_pipeline()

    test_file = "pipelines/lidar_halo_xrp/test/data/input/sa5.lidar.z01.00.20230119.210000.stare_236.hpl"
    expected_file = "pipelines/lidar_halo_xrp/test/data/expected/sa5.lidar-halo_xrp_stare_236_z01.a1.20230119.210133.nc"

    dataset = pipeline.run([test_file])
    expected: xr.Dataset = xr.open_dataset(expected_file)  # type: ignore
    assert_close(dataset, expected, check_attrs=False)
