import xarray as xr
from pathlib import Path
from tsdat import PipelineConfig, assert_close


def test_met_campbell_pipeline():
    config_path = Path("pipelines/met_campbell/config/pipeline_sa1.yaml")
    config = PipelineConfig.from_yaml(config_path)
    pipeline = config.instantiate_pipeline()

    test_file = (
        "pipelines/met_campbell/test/data/input/sa1.met.z01.00.20211207.130000.txt"
    )
    expected_file = (
        "pipelines/met_campbell/test/data/expected/sa1.met_z01.a1.20211207.130000.nc"
    )

    dataset = pipeline.run([test_file])
    expected: xr.Dataset = xr.open_dataset(expected_file)  # type: ignore
    assert_close(dataset, expected, check_attrs=False)
