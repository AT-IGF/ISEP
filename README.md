# ISEP - Integrated Solution for Environmental Pollen detection
Library created for handling Rapid-E input files, designed for:
- Data viewer - visualize the data as single sample or aggregated samples
  - Single sample - characteristics for one sample at a time
  - Aggregated samples - characteristics for all samples across modality
- Model builder - train and evaluate machine-learning models 
  - Scaler - fitting scaler to the available dataset
  - Supervised - train supervised convolutional neural network (CNN)
  - Unsupervised - train unsupervised convolutional autoencoder
- Model runner - run trained model on real-word data
- Predictions mapper - visualize model predictions

## Repository construction
- <i>resources</i> - place for configuration files and data to process
- <i>src</i> - codebase
- <i>sample</i> - sample input fot the app, file converter to PKL file format

## Requirements
### Hardware
> No strict hardware setup is required, however to be able to fully use utilities of program GPU with CUDA support is recommended. Depending on the volume of data processed 16+ GB of RAM is also advised.

### Software
> [!NOTE]
> Note: For parallel GPU computing in tensorflow CUDA* is required. On windows tensorflow do not support CUDA, WSL2 is required - [install WSL2 guide](https://learn.microsoft.com/en-us/windows/wsl/install?utm_source=chatgpt.com). 

*For CUDA installation see - <i>[www.tensorflow.org](https://www.tensorflow.org/install/pip#step-by-step_instructions)</i> (before: [check](https://www.tensorflow.org/install/source#gpu)</i> tensorflow version compatibility)


#### <span style="color: lightblue">*Running from source*</span>
- Ubuntu 22.04.2 LTS - install on WSL2, if used
- Python 3.11.4 - [download](https://www.python.org/downloads/)
- pip (python package installer) - installed with python


Rest of required packages is given in <i>requirements.txt</i> and will be installed automativally via pip install (next step).

#### <span style="color: lightblue">*Running compiled executable (.exe)*</span>
runs standalone, no additional installation required

## How to run (from source)
1. Install [Requirements](#requirements)
2. Check if pip is installed (should return version):
    ``` pwsh
    pip --version
    ```
3. Install required packages:
    ``` pwsh
    pip install .
    ```
4. Run the application
- [Visual Studio Code](https://code.visualstudio.com/docs/setup/windows):
  - Select RUN AND DEBUG icon
  - Select UI
  - Run
- Shell:
    ```bash
    python -m src.ui.UI
    ```

> [!NOTE]
> Running other sub-apps directly from VSC or shell without UI is supported, however UI is a good point to start with. All modules are listed in .vscode -> settings.json

## Funding
> The doctoral scholarship and research of Artur Tomczak were funded by the National Science Centre, Poland, under the PRELUDIUM BIS 2 “Impact of allergenic pollen on the optical and microphysical properties of the urban aerosol” (PrePOLLEN) grant no. UMO-2020/39/O/ST10/03586, grant PI: Iwona Stachlewska.

> The work within machine learning pollen typing was financed by the Polish National Agency for Academic Exchange (NAWA) within the framework of the PRELUDIUM BIS 2 project, managed by me, entitled "Synergic use of Lidar and Pollen sensor for Aerosol Typing (SLaP4AT)", (grant no. PN/PRE/2022/1/00024).

## Acknowledgements
> The ISEP software was developed on the basis of data samples collected by Mikhail Boldeanu, Andrei Dandocsi, and Jeni Vasilescu at the Măgurele centre for Atmosphere and Radiation Studies (MARS) of the National Institute of Research and Development for Optoelectronics (INOE) in Romania.