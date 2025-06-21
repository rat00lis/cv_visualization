from common import run_compression_method, save_result

def test_no_compression():
    result = run_compression_method("No Compression", None)
    save_result(result)
    assert result["success"], result["error"]