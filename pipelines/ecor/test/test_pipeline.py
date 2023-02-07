import xarray as xr
from pathlib import Path
from tsdat import PipelineConfig, assert_close


def test_ecor_pipeline():
    config_path = Path("pipelines/ecor/config/pipeline_sgp.yaml")
    config = PipelineConfig.from_yaml(config_path)
    pipeline = config.instantiate_pipeline()

    test_file = "pipelines/ecor/test/data/input/sgpecorE14.00.20190910.010201.raw.2019_0910_0000_14.flx"
    expected_file = (
        "pipelines/ecor/test/data/expected/sgp.ecor_e14.b0.20190910.000000.nc"
    )

    dataset = pipeline.run([test_file])
    expected: xr.Dataset = xr.open_dataset(expected_file)  # type: ignore
    assert_close(dataset, expected, check_attrs=False)
