This repository is under construction

# ICMD Output Data Tools

Utilities for reading, cleaning, and visualizing **ICMD JSON model output** as structured `pandas` DataFrames.  
The toolkit streamlines access to thermodynamic, equilibrium, and solidification data for analysis and plotting.

---

## 📁 Project Structure
icmdoutput/ <br>
├── json_import.py                  # Load JSON models into structured objects <br>
├── redundant_data.py               # Phase composition and temperature handling <br>
├── models/ <br>
│   ├── solidification.py           # Solidification & Scheil analysis tools <br>
│   └── equilibrium.py              # Equilibrium properties (density, enthalpy, etc.) <br>
│   ├── user_scripts <br>
│   │   ├── interactive_plots.py        # Work in progress making interactive plots for parameter studies <br>
│   │   └── scheil_plotting.py          # Funktions to direct pltting Scheil data, fixing bugs icmd data has <br>

---

## ⚙️ Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/PowerPelikan/questek_icmd_python.git
   cd icmdoutput
   ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

    Typical dependencies

    pandas>=2.0
    numpy>=1.24
    plotly>=5.0
    pytest>=7.0

## Usage examples

### Reading model data
```python
from icmdoutput.json_import import JsonData

data = JsonData("simulation.json")
print(data.get_models())
elements = data.get_elements()
``` 

### Single model access
```python
from icmdoutput.json_import import SingleModel

model = SingleModel("simulation.json", "model1")
params = model.get_parameter_values()
```    

### Phase fractions and temperature data
```python
from icmdoutput.redundant_data import PhasesAndTemps

pt = PhasesAndTemps("simulation.json", "model1")
phase_fractions = pt.get_phase_fraction()
temperatures = pt.get_temperatures()
```
    
 ### Solidification and Scheil plotting
```python
from icmdoutput.models.solidification import Solidification

solid = Solidification("simulation.json", "model1")
scheil_data = solid.get_data_for_scheil_plot(temp_unit="C")
fig = solid.scheil_plot(plotname="Scheil Solidification")
fig.show()
``` 

### Equilibrium properties
```python
from icmdoutput.models.equilibrium import Equilibrium

eq = Equilibrium("simulation.json", "model1")
density_df = eq.get_system_density()
pressure_df = eq.get_pressure("Pa")
```

### Scheil plots
```python
from icmdoutput.models.plotting.scheil_plot import Scheil

scheil = Scheil("simulation.json", "model1")
fig = scheil.scheil_plot(plotname="Scheil Solidification")
fig.show()
```

**License**
GPL-3.0 License

**Maintainer**
Jonathan Hartmann <br>
Contributions, bug reports, and improvements are welcome.

