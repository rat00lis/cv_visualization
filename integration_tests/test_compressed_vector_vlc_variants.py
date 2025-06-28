from utils import run_compression_method, save_result
import sdsl4py

def test_vlc_vector_elias_delta():
    result = run_compression_method("VLC Elias Delta", sdsl4py.vlc_vector_elias_delta)
    save_result(result)
    assert result["success"], result["error"]

def test_vlc_vector_elias_gamma():
    result = run_compression_method("VLC Elias Gamma", sdsl4py.vlc_vector_elias_gamma)
    save_result(result)
    assert result["success"], result["error"]

def test_vlc_vector_fibonacci():
    result = run_compression_method("VLC Fibonacci", sdsl4py.vlc_vector_fibonacci)
    save_result(result)
    assert result["success"], result["error"]

def test_vlc_vector_comma_2():
    result = run_compression_method("VLC Comma-2", sdsl4py.vlc_vector_comma_2)
    save_result(result)
    assert result["success"], result["error"]
