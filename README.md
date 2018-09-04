#metal_etl#
Metal Sartigan packages for Extract-transform-load

###Build and release###
Make sure the `setup.py` file is up to date with at least the current version.

Then, in the `src` folder:

```
python2 setup.py bdist_wheel
twine upload dist/*
```

the package `df1` can then be installed using `pip install df1`