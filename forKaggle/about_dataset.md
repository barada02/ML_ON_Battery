# NASA Li-ion Battery Aging Dataset (Consolidated)

## Overview
This dataset contains the results of experiments on Li-ion batteries conducted at the NASA Prognostics Center of Excellence (PCoE). The batteries were run through various operational profiles (charge, discharge, and impedance) at different temperatures to study their degradation over time. 

### Why use this version?
The original NASA dataset is often distributed with a deeply nested directory structure and redundant files, making it difficult to process programmatically. This dataset version has been **refactored into a clean, canonical form**:
* **Flattened Directory Structure:** All battery `.mat` files are easily accessible at a single directory level.
* **Consolidated Metadata:** Disparate `README_*.txt` files have been merged into a comprehensive `DATA_STRUCTURE_AND_GROUP_DESCRIPTIONS.md` for quick reference on experimental conditions and visual diagrams of the `.mat` file structure.
* **ML-Ready Pathway:** The attached notebook `EDA_+DE` provides a complete pipeline to transform these raw `.mat` files into a feature-engineered CSV that is ready for Machine Learning tasks like Remaining Useful Life (RUL) prediction.

---

## Directory & File Structure

The dataset consists of the raw `.mat` files, a metadata CSV, original README texts, and consolidated markdown descriptions.

```text
├── B0005.mat ... B0056.mat                   # Flattened raw MATLAB data files (34 batteries)
├── metadata.csv                              # Tabular summary of test conditions per battery
├── DATA_STRUCTURE_AND_GROUP_DESCRIPTIONS.md  # Consolidated metadata & structure diagram
├── README.md                                 # Quick summary of the dataset
├── README_*.txt                              # Original NASA README files
└── source.md                                 # Origin information
```

> **Note on Feature Engineering:** For a detailed walkthrough of how the raw `.mat` files were processed, filtered, and transformed into the ML-Engineered CSV, please check out the attached notebook **`EDA_+DE`** from the **Code** tab of this dataset!

---

## Dataset Structure (Raw `.mat` Files)
The raw dataset is organized by **Cycles**. Each cycle contains specific measurements based on its operation type. Here is the internal ASCII structure of a typical `.mat` file (e.g., `B0005.mat`):

```text
B0005.mat
└── B0005 (1x1 struct)
    └── cycle (1xN struct array)
        ├── [1] (struct)
        │   ├── type: 'charge'
        │   ├── ambient_temperature: 24
        │   ├── time: [array]
        │   └── data (struct)
        │       ├── Voltage_measured: [array]
        │       ├── Current_measured: [array]
        │       ├── Temperature_measured: [array]
        │       ├── Current_charge: [array]
        │       ├── Voltage_charge: [array]
        │       └── Time: [array]
        ├── [2] (struct)
        │   ├── type: 'discharge'
        │   ├── ambient_temperature: 24
        │   ├── time: [array]
        │   └── data (struct)
        │       ├── Voltage_measured: [array]
        │       ├── Current_measured: [array]
        │       ├── Temperature_measured: [array]
        │       ├── Current_load: [array]
        │       ├── Voltage_load: [array]
        │       ├── Time: [array]
        │       └── Capacity: [scalar]
        ├── [3] (struct)
        │   ├── type: 'impedance'
        │   ├── ambient_temperature: 24
        │   ├── time: [array]
        │   └── data (struct)
        │       ├── Sense_current: [array]
        │       ├── Battery_current: [array]
        │       ├── Current_ratio: [array]
        │       ├── Battery_impedance: [array]
        │       ├── Rectified_impedance: [array]
        │       ├── Re: [scalar]
        │       └── Rct: [scalar]
        └── ...
```

### Common Data Fields
| Field | Description |
| :--- | :--- |
| `type` | Operation type: `charge`, `discharge`, or `impedance` |
| `ambient_temperature` | The temperature of the testing environment (°C) |
| `time` | Start time of the cycle (MATLAB date vector) |
| `data` | Sub-structure containing sensors (Voltage, Current, Temp, etc.) |

### Measurement Details
* **Charge/Discharge:** Includes terminal voltage, output current, battery temperature, and time vectors. Discharge cycles also include the calculated **Capacity (Ahr)**.
* **Impedance:** Includes Electrochemical Impedance Spectroscopy (EIS) results, specifically electrolyte resistance ($Re$) and charge transfer resistance ($Rct$).

---

### Full Experimental Group Breakdown
The batteries are categorized by ambient temperature and discharge protocols. 

| Group | Batteries | Ambient Temp | Discharge Protocol |
| :--- | :--- | :--- | :--- |
| **G1** | B0005, 06, 07, 18 | Room Temp | 2A Constant Current (CC) |
| **G2** | B0025, 26, 27, 28 | 24°C | 4A Square Wave (0.05Hz, 50% Duty) |
| **G3** | B0029, 30, 31, 32 | 43°C (High) | 4A Constant Current (CC) |
| **G4** | B0033, 34, 36 | 24°C | 2A or 4A Constant Current (CC) |
| **G5** | B0038, 39, 40 | 24°C & 44°C | Mixed Loads (1A, 2A, 4A) |
| **G6** | B0041, 42, 43, 44 | 4°C (Cold) | 1A and 4A Fixed Loads |
| **G7** | B0045, 46, 47, 48 | 4°C (Cold) | 1A Constant Current (CC) |
| **G8** | B0049, 50, 51, 52 | 4°C (Cold) | 2A Constant Current (CC) |
| **G9** | B0053, 54, 55, 56 | 4°C (Cold) | 2A Constant Current (CC) |

---

### Important Data Notes for Users
* **Cold Weather Performance:** Groups 6 through 9 (4°C) are specifically designed to study battery behavior in cold environments. Note that some runs in these groups show significantly lower capacity due to the temperature constraints.
* **End of Life (EOL):** Most experiments were stopped when the battery reached a 20% to 30% fade from its nominal capacity (e.g., dropping from 2.0Ahr to 1.4Ahr). Absolute capacity differs by group.
* **Normalized Target:** When predicting degradation, normalizing the raw Capacity to **State of Health (SoH)** allows for universal models across all battery groups.

## Suggested Use Cases
1.  **Remaining Useful Life (RUL) Prediction:** Predicting when a battery will hit its End-of-Life (EOL), typically defined here as a 20-30% fade in capacity.
2.  **State of Health (SoH) Estimation:** Using physics-informed features (like Voltage Drop Rate or Max Temperature Reached) to estimate battery health.
3.  **Impedance Analysis:** Correlating internal resistance growth ($Re$, $Rct$) with capacity loss.
4.  **Thermal Modeling:** Analyzing temperature fluctuations during high-current discharge cycles and varying environmental conditions.

## Acknowledgements
The raw data was provided by the NASA Ames Prognostics Center of Excellence.
