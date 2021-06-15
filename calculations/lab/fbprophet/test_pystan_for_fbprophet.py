"""
ImportError: DLL load failed: The specified module could not be found.

It says in the Pystan documentation that configuring a C++ compiler can be challenging on Windows. Following approach worked for me to install Pystan 2.17.1 and FBProphet 0.6:

1. Install C++ compiler, mingw-w64 (http://mingw-w64.org/doku.php/download) -> I selected this one https://sourceforge.net/projects/mingw-w64/files/
2. Add C:<MinGW_w64 installation directory>\bin to the PATH environment variable
3. Create a distutils.cfg file with the following contents in the folder \Lib\distutils in Python install directory (in venv):
    [build] compiler=mingw32
    [build_ext] compiler=mingw32
4. pip install numpy cython
5. pip install pystan==2.17.1
6. Verify the Pystan installation (https://pystan.readthedocs.io/en/latest/windows.html)
7. pip install fbprophet==0.6
"""

import pystan

model_code = 'parameters {real y;} model {y ~ normal(0,1);}'
model = pystan.StanModel(model_code=model_code)  # this will take a minute
y = model.sampling(n_jobs=1).extract()['y']
print(f"should be close to 0: {y.mean()}")  # should be close to 0
