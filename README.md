# Synapse Selector

## Table of Contents

- [Overview](#Overview)
- [Installation](#Installation)
- [Adapt the Settings](#Adapt-the-Settings)
  - [General](#General)
  - [Detection](#Detection)
  - [Threshold Settings](#Threshold-Settings)
  - [Stimulation](#Stimulation)
- [Usage](#Usage)
  - [Shortcuts and brief overview](#Shortcuts-and-brief-overview)
  - [Detailed Explanation](#Detailed-Explanation)
- [Train a custom Model](#Train-a-custom-Model)

## Overview

Lorem ipsum

## Installation
You will need [Anaconda](https://www.anaconda.com/download) to be installed. If Anaconda is installed, open the "Anaconda Prompt" (Windows) or a terminal (Linux + Mac).
1. **Create a conda enviorment**:
   ```bash
      conda create -n synapse_selector python=3.10 pip
      conda activate synapse_selector
   ```
2. **Install synapse selector**:

   ```bash
      pip install synapse_selector
   ```
Alternatively, you can also clone this repository and install it from there
```bash
   git clone https://github.com/s-weissbach/synapse_selector.git
   cd synapse_selector
   pip install -e .
```

## Getting Started
The mean traces should be stored in a `.csv` or an excel file `.xls`, `.xlsx`. Ensure that the mean traces are organized with one trace per column. You can have columns with meta information (e.g. Time) that will be carried over to the output files.

**Example input file**
| Time (ms) | Trace 1 | Trace 2 | (...) |
| --------- | ------- | ------- | ----- |
| 0         | 23.5    | 18.7    | (...) |
| 1         | 25.1    | 20.3    | (...) |
| 2         | 22.8    | 17.6    | (...) |
| 3         | 21.4    | 19.2    | (...) |
| 4         | (...)   | (...)   | (...) |

> [!Tip]
> Meta columns won't be included for analysis, but will be carried over to the output files.

### Run Synapse Selector
To run Synapse Selector, follow these steps:
1. ```bash
   conda activate synapse_selector
   ```
2. Launch the Synapse Selector using the following command:
   ```bash
   python -m synapse_selector.main
   ```

### Adapt the Settings
To access the settings, press the settings symbol <img src="./synapse_selector/assets/settings.svg" width="20"> in the top icon bar. The settings are organized in the Tabs `General`, `Detection`, `Threshold Settings`, and `Stimulation`.

#### General
In the general settings section, you can configure the following options:
- **Set Output Path:**
  Specify the directory where you want the output files to be saved.
- **Export as XLSX:**
  Choose whether to export the results in XLSX format, otherwise .csv files will be created.
- **Add/Remove Meta Columns:**
  Customize the meta columns based on your requirements.

#### Detection
> [!NOTE]
> Rolling window z-normalization will be applied for detection.

Configure the detection settings according to your analysis preferences:
- **Selection Methods:**
  Choose between ML-based and Thresholding.
- **Deep Learning Model:**
  If ML-based selection is chosen, specify the deep learning model specific for the sensor you used.
- **Time Window for Tau Computation:**
  Set the time window for tau computation, which determines the decay estimate.
- **Show Normalized Trace (Toggle):**
  Toggle this option to display z-normalized traces in the output.
- **Compute PPR (Toggle):**
  If stimulation was used, enable this option to compute the paired pulse ratio (PPR).

#### Threshold Settings
- **Baseline Start:** Specify the start point of the baseline for threshold calculation.
- **Baseline Stop:** Define the stop point of the baseline for threshold calculation.
- **Threshold Multiplier:** Set the multiplier used in the

> [!NOTE]
> Threshold is calculated witht the formula:
> $$\text{threshold} = (\text{multiplier} * std_{baseline}) + mean_{baseline}$$

#### Stimulation
- **Enable Stimulation (Toggle):**
  Toggle this option when you used stimulation in this recording.
- **Start Frame for Stimulation:**
  Specify the starting frame for stimulation. Stimulation frames will be infered automatically.
- **Step Size for Stimulation:**
  Set the step size for stimulation. Stimulation frames will be infered automatically.
- **Patience:**
  Define the duration for which a response should be counted as a valid response to the stimulation.
- **Use Manual Stimulation Frames:**
  Input stimulation frames manually

> [!IMPORTANT]
> When entering stimulation frames manually, separate the frames by commas **without spaces**.

## Usage
### Shortcuts and brief overview
| Command          | Button                                                            | Shortcut | Description                                           |
| ---------------- | ----------------------------------------------------------------- | -------- | ----------------------------------------------------- |
| Open File        | <img src="synapse_selector/assets/open.svg" width="20">     | Ctrl + O | Open a file                                           |
| Save File        | <img src="synapse_selector/assets/save.svg"  width="20">     | Ctrl + S | Save all traces up to this point and discard the rest |
| Settings         | <img src="synapse_selector/assets/settings.svg"  width="20"> | S        | Open the settings                                     |
| Back             | <img src="synapse_selector/assets/back.svg" width="20">     | B        | Go one trace back                                     |
| Discard          | <img src="synapse_selector/assets/trash.svg" width="20">    | Q        | Discard trace from analysis                           |
| Accept           | <img src="synapse_selector/assets/keep.svg" width="20">     | E        | Accept trace and keep for analysis                    |
| Modify Responses | <img src="synapse_selector/assets/peak.svg" width="20">     | W        | Add or remove responses                               |

### Detailed explanation

1. **Open a File** pressing the open button <img src="synapse_selector/assets/open.svg" width="20"> in the top bar.
   - Synapse Selector will visualize the first column of the file that is not a meta column.
   - All detected responses will be annotated.
   - If specified in the settings, a horizontal, red dashed line will be shown

2. **Modify responses** pressing the modify response button <img src="synapse_selector/assets/peak.svg" width="20"> in the top bar
   - A window with all detected responses will be opened
   - Deselect false-positive responses
   - Add false-negative responses

3. **Accept or Discard a trace**
   - To **accept** a trace and subsequently include it in the analysis: <img src="synapse_selector/assets/keep.svg" width="20">
   - To **discard** a trace from analysis: <img src="synapse_selector/assets/trash.svg" width="20">

4. **Change certantiy threshold** (only when using ML-based detection):
   - Use the slider at the bottom to adjust the certantiy threshold used in the model. A lower threshold will lead to more detections, possibly, to more false-positives.

5. **Save and skip rest**: press the save button  <img src="synapse_selector/assets/save.svg" width="20"> in the top bar. All remaining traces of the file will be discarded.

## Train a custom Model
See the[ Synapse Selector Detect](https://github.com/s-weissbach/synapse_selector_detect/tree/main) for detailed tutorial on how to train a custom model.
> [!Tip]
> You can share your model with the community - submit it to [Synapse Selector Modelzoo](https://github.com/s-weissbach/synapse_selector_modelzoo/tree/main).[GitHub - s-weissbach/synapse_selector_modelzoo](https://github.com/s-weissbach/synapse_selector_modelzoo/tree/main).
