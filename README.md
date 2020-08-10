# pydf1

See src folder for usage instructions and license.

### Build and release
Make sure the `setup.py` file is up to date with at least the current version.

Then, in the `src` folder:

```
rm dist/*
python2 setup.py bdist_wheel
twine upload dist/*
```

the package `df1` can then be installed using `pip install df1`
