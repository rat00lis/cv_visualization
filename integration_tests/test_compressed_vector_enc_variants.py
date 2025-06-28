from utils import run_compression_method, save_result
import sdsl4py

INT_WIDTH_ENC = 64

"""
    enc vectors work weird with different integer widths, so we use a fixed width for these tests.
"""

def test_enc_vector_elias_gamma():
    result = run_compression_method("Elias Gamma", sdsl4py.enc_vector_elias_gamma, width=INT_WIDTH_ENC)
    save_result(result)
    assert result["success"], result["error"]

def test_enc_vector_fibonacci():
    result = run_compression_method("Fibonacci", sdsl4py.enc_vector_fibonacci, width=INT_WIDTH_ENC)
    save_result(result)
    assert result["success"], result["error"]

def test_enc_vector_comma_2():
    result = run_compression_method("Comma-2", sdsl4py.enc_vector_comma_2, width=INT_WIDTH_ENC)
    save_result(result)
    assert result["success"], result["error"]

def test_enc_vector_elias_delta():
    result = run_compression_method("Elias Delta", sdsl4py.enc_vector_elias_delta, width=INT_WIDTH_ENC)
    save_result(result)
    assert result["success"], result["error"]
