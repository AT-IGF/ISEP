## Overview
sample directory contains:
- PKL_Types - sample input that allows to quickly go through the application
- pklConverter - allows to save measurement files into ISEP input format (as presented in PKL_Types samples).

> [!NOTE]
> Rapid-E (like other instruments) has its own measurement file format. .pkl files works as interface between original measurement files and ISEP. To avoid copyright infringement conversion is not attached it must be provided by the user. 

### Pkl converter

To convert the files following steps must be done:
1. Go to sample.processing.Converter
2. Inside ```map_to_raw_data(self, filename)``` method implement measurement file mapping - output format and sample mapping is given in ```map(self, data: dict)``` method.
3. One input is provided run:
    ```bash
    python -m sample.pklConverter.PklConverter
    ```
4. Provide samples input and output path
    > Note: Samples input path should be measurements root path, e.g., having measurements in sub-folders "Measurements/Day1", "Measurements/Day2" the "Measurements" folder should be given
5. Mapped pkl files will be reflected in output path matching the original folder structure 

> [!TIP]
> Pkl conversion can also be skipped. It requires adopting the method common.rawData.Signal.RawDataAdapter.map_to_raw_data to read the original measurement files
