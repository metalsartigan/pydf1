This is the original project and is no longer maintained.

There is an active fork with python3 support, serial connection support and other improvements. Check it out:

https://github.com/reyanvaldes/pydf1


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

### Known limitations
Although the current code is working and quite stable too, the implementation is incomplete:
- Only ethernet connection is supported but the code is modular and ready to accept a new PLC class that supports any connection type, like serial.
- Some commands are not implemented, but the architecture is ready for more.
- Only for Python 2.7. Will not work on anything more recent.
