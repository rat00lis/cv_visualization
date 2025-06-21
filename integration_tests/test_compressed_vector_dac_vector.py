from common import run_compression_method, save_result
import sdsl4py

def test_dac_vector():
    result = run_compression_method("DAC Vector", sdsl4py.dac_vector)
    save_result(result)
    assert result["success"], result["error"]
