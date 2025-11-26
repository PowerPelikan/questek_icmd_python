""" Importing Solidification-Model data from json in Pandas Dataframes"""
import pandas as pd
import numpy as np
from icmdoutput.redundant_data import PhasesAndTemps


class Solidification(PhasesAndTemps):
    """Solidification data of a JSON model."""

    # --- Internal getters --------------------------------------------------

    def _get_solid_regions(self):
        return self.data["coords"]["solidification_region"]["data"]

    def _get_temp_regions(self):
        return self.data["data_vars"]["temperature_by_phase_region"]["data"]

    def _get_percent_solid_molar(self):
        return self.data["data_vars"]["percent_solidified_molar_values"]["data"][0]

    # --- Public methods ----------------------------------------------------

    def get_solid_regions(self) -> pd.DataFrame:
        """Return calculated solidification regions."""
        return pd.DataFrame(self._get_solid_regions(), columns=["Phase Region"])

    def get_temperature_by_phase_region(self, unit="C") -> pd.DataFrame:
        """Return temperature by phase region."""
        idx = {"C": 0, "F": 1, "K": 2}.get(unit)
        if idx is None:
            raise ValueError(f"Unsupported temperature unit: '{unit}'")

        data = np.array(self._get_temp_regions())[0, :, :, idx]
        return pd.DataFrame(data, columns=self._get_solid_regions())

    def get_percent_solidified_molar(self) -> pd.DataFrame:
        """Return percentage of solidification."""
        return pd.DataFrame(self._get_percent_solid_molar(), columns=["Percent solidified molar"])

    def get_data_for_scheil_plot(self, temp_unit="C") -> pd.DataFrame:
        """Return DataFrame suitable for Scheil plot construction."""
        phase_region = self.get_temperature_by_phase_region(unit=temp_unit).drop(['LIQUID'], axis=1)
        melted = phase_region.replace("None", np.nan).apply(lambda row: row.first_valid_index(), axis=1)
        result = pd.DataFrame({"Phase Region": melted})
        temps = self.get_temperatures()
        df = self.get_percent_solidified_molar()
        return pd.concat([df, temps, result["Phase Region"]], axis=1, join="inner")
    