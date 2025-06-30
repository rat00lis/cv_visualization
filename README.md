

# 📦 `cv_visualization` Documentation

`cv_visualization` is a Python library for efficient and flexible manipulation, compression, and visualization of numerical vectors, especially designed for time series and data-intensive workflows. It provides compact memory representations and visualization tools, including support for common downsampling techniques.

---

## ✨ Features

* ✅ Efficient floating-point compression via integer-vector representation
* ✅ Built-in support for multiple compression codecs (`sdsl4py`)
* ✅ Arithmetic operations over compressed vectors (`+=`, `+`, `*`, etc.)
* ✅ Downsampling methods for large datasets (LTTB, M4, MinMax, etc.)

---

## 📦 Modules Overview

### 1. `CompressedVector`

Core class to store float arrays in compressed form.

### 2. `CompressedVectorDownsampler`

Utility for downsampling vectors before compression.

### 3. `common.available_methods`

Provides available codecs and downsamplers as mappings.

---

## 🚀 Getting Started

### 📦 Installation

I highly recommend creating a python environment for this.

Clone this repository and its submodules:
```bash
git clone https://github.com/rat00lis/cv_visualization.git
git submodule update --init --recursive
```

Install via pip:
```bash
pip install .
```
OR Install (editable mode):
```bash
pip install -e .
```

### Installing Dependencies

#### SDSL4py Installation

You'll also need to install `sdsl4py` (Succinct Data Structure Library for Python):

```bash
cd ./externals/sdsl4py/
pip install .
```

This library provides the compression codecs used by `cv_visualization`.

---
Here’s your content converted into a clean, organized **Markdown list format**:

---

## 📦 Available Compression Methods

* `enc_vector_elias_gamma`
* `enc_vector_fibonacci`
* `enc_vector_comma_2`
* `enc_vector_elias_delta`
* `vlc_vector_elias_delta`
* `vlc_vector_elias_gamma`
* `vlc_vector_fibonacci`
* `vlc_vector_comma_2`
* `dac_vector`
* `No Compression`

---

## 📉 Available Downsamplers

* `MinMaxLTTBDownsampler`
* `M4Downsampler`
* `LTTBDownsampler`
* `MinMaxDownsampler`
* `EveryNthDownsampler`
* `NaNM4Downsampler`
* `NaNMinMaxDownsampler`
* `NaNMinMaxLTTBDownsampler`

---
# Examples

I highly recommend to checkout the [examples](/examples/examples.md) provided to understand the usage of `cv_visualization`.

## 📘 CompressedVector

### 🔧 Creating a Compressed Vector

```python
from cv_visualization import CompressedVector

cv = CompressedVector(decimal_places=2, int_width=16)
cv.create_vector(5)
cv.fill_from_vector([1.23, -2.34, 3.14, 0.0, 5.67])
```

### 🔁 Iteration & Access

```python
for val in cv:
    print(val)

print(cv[0])        # Get single item
print(cv[1:4])      # Get a slice
```

You can set values as well:

```python
cv[2] = 42.0
```

---

## 🔧 Arithmetic Operations

You can perform operations on the vector directly:

```python
cv += 2.0               # Add scalar
cv *= 0.5               # Scale
cv -= [1.0, 0, 1, 0, 0] # Element-wise subtraction
```

These work via operator overloading using `__iadd__`, `__imul__`, etc.

---

### 🧬 Copying a Compressed Vector

```python
cv2 = cv.__copy__()
cv2 += 10
```
This creates a deep copy with independent memory.

### Compress the vector:

```python
cv.compress("enc_vector_elias_gamma")
```

⚠️You will NOT be able to modify a vector once is compressed.⚠️


---

## 📚 Downsampling with `CompressedVectorDownsampler`

Useful when visualizing or compressing large arrays.

```python
from cv_visualization import CompressedVectorDownsampler as cvd
x, y = cvd().downsample(
    x = x,
    y = y,
    n_out=1000
    # method = Downsampler Method
    # compress_method = Compress Method for vector
)
```

## 📈 Visualization Integration

You can plot compressed vectors with supported libraries such as `PyGal` or `Altair`

![Compressed Vector Visualization](/examples/images/cv_visualization.png)

You can also use `CompressedVectorDownsampler` to downsample before plotting for performance.
```python
import altair as alt
# create sin wave data
x = pd.Series(range(100000))
y = pd.Series(np.sin(x / 1000.0))

cvd_downsampler_x, cvd_downsampler_y = cvd().downsample(
    x=x,
    y=y,
    n_out=1000,
    compress_method='vlc_vector_elias_gamma',
    method='EveryNthDownsampler'
)
start = time.time()
# create a new dataframe with the downsampled data
df_cvd_downsampled = pd.DataFrame({
    'x': cvd_downsampler_x,
    'y': cvd_downsampler_y
})

# plot the downsampled data
chart_cvd_downsampled = alt.Chart(df_cvd_downsampled).mark_line().encode(
    x='x',
    y='y'
).properties(
    title='Compressed Vector Downsampled Data with VLC Vector Elias Gamma'
).interactive()
end = time.time()
print(f"Time taken to plot Compressed Vector Downsampled data: {end - start:.2f} seconds")
# display the chart
chart_cvd_downsampled   
```
![cvd visualization](/examples/images/cvd_visualization.png)
---

## 🗂️ File Input

```python
cv.build_from_file("data.csv", column=2, delimiter=",")
```

This builds the vector from a CSV file column.

---

## 📏 Memory Usage

You can use the function `.size_in_bytes()` in any `CompressedVector`to check the size of it.

## 🧪 Jupyter Notebooks

Check out the following examples provided in the `examples/` folder:

1. [Creating a Compressed Vector](/examples/example_compressed_vector.ipynb)
1. [Downsampling large vectors with Compressed Vector Downsampler](/examples/example_compressed_vector_downsampler.ipynb)
1. [Restrictions on Libraries](/examples/example_plotly_matplotlib.ipynb)
1. [Recommended visualization tools](/examples/example_allowed_plot.ipynb)

They demonstrate:

* Full usage flow
* Downsampling techniques
* Recommended visualization tools
* Why you cant use it in Plotly and Matplotlib
* Arithmetic operations in practice

---

## 📌 Internals

The vector is stored as three `sdsl4py` int\_vectors:

* `integer_part`
* `decimal_part`
* `sign_part` (1 for +, 0 for -, 2 for NaN)

The float value is reconstructed as:

```python
value = int_part + dec_part / (10^decimal_places)
```

Compression methods operate on these base integer vectors using SDSL codecs.

---

# Areas of Improvement

1. It would be great to be able to use common plotting libraries such as plotly or matplotlib (while mantaining the compressed vectors), but this would require a lot of effort.
2. Add some kind of logic to use the best amount of decimal places, int width and compress method.
3. For sure there are better ways to handle negative numbers that use less space.
