"""Define Phase, Volume Fraction, and Temperature values for multiple models."""

import pandas as pd
from .json_import import SingleModel


class PhasesAndTemps(SingleModel):
    """Extract phase fraction, volume fraction, and temperature data from models."""

    # --- Core field accessors -----------------------------------------------

    def get_phase_names(self):
        return self.data["coords"]["phase"]["data"]

    def _get_temperatures(self, unit: str, parameter: bool):
        try:
            temps = self.data["data_vars"]["temperature_values"]["data"]
        except KeyError:
            temps = self.data["data_vars"]["temperature"]["data"]
        
        if parameter:
            match unit:
                case "C":
                    return [[row[0] for row in block] for block in temps]
                case "K":
                    return [[row[1] for row in block] for block in temps]
                case "F":
                    return [[row[2] for row in block] for block in temps]
                case _:
                    raise ValueError(f"Unknown temperature unit '{unit}'")

        match unit:
            case "C":
                return [t[0][0] for t in temps]
            case "K":
                return [t[0][1] for t in temps]
            case "F":
                return [t[0][2] for t in temps]
            case _:
                raise ValueError(f"Unknown temperature unit '{unit}'")

    def _get_elements(self):
        return self.data["coords"]["component"]["data"]

    # --- Composition and phase fractions ------------------------------------

    def _get_composition(self, phase: str, unit: str, phaselist: pd.DataFrame):
        try:
            phase_index = phaselist.isin([phase]).any(axis=1).idxmax()
        except KeyError as exc:
            raise KeyError(f"Phase '{phase}' not found in data") from exc

        try:
            data = self.data["data_vars"]["composition"]["data"][0]
        except KeyError:
            data = self.data["data_vars"]["phase_composition"]["data"][0]

        selector = 1 if unit == "mass" else 0
        comp = [[[elem[selector] for elem in row] for row in block] for block in data]
        return [block[phase_index] for block in comp]

    def _get_volume_fraction(self):
        return self.data["data_vars"]["volume_fraction"]["data"][0]

    def _get_phase_fraction(self, unit: str, parameter: bool):
        """Return raw phase-fraction data."""
        data = self.data["data_vars"]["phase_fraction"]["data"]
        selector = 1 if unit == "mass" else 0

        if parameter:
            return [[[elem[selector] for elem in row] for row in block] for block in data]
        return [[elem[selector] for elem in plane] for plane in data[0]]

    # --- Public interface ---------------------------------------------------

    def get_elements(self) -> pd.DataFrame:
        return pd.DataFrame(self._get_elements(), columns=["Element"])

    def get_phase_names_df(self) -> pd.DataFrame:
        return pd.DataFrame(self.get_phase_names(), columns=["Phase"])

    def get_components_df_complete(self):
        return pd.DataFrame(self.data["attrs"]["input_dict"]["composition"]["components"])

    def get_components(self, exclude=None):
        df = self.get_components_df_complete()
        if exclude:
            df = df[df["name"] != exclude]
        return pd.DataFrame({row["name"]: row["samples"] for _, row in df.iterrows()})

    def get_composition(self, phases=None, unit="mole"):
        """Return composition of given phases over temperature."""
        phaselist = self.get_phase_names_df()
        if phases is None:
            phases = self.get_phase_names()

        elements = self._get_elements()
        df_all = []

        for phase in phases:
            comp = self._get_composition(phase, unit, phaselist)
            part = pd.DataFrame(comp, columns=elements)
            part["Phase"] = phase
            df_all.append(part)

        return pd.concat(df_all, ignore_index=True)

    def get_phase_fraction(self, phase_unit="mole", temp_unit="C", parameter=False):
        """Return DataFrame with phase fractions."""
        phase_values = self._get_phase_fraction(phase_unit, parameter)
        #temps = pd.DataFrame(self._get_temperatures(temp_unit), columns=[f"Temperature in {temp_unit}"])
        temps = self._get_temperatures(temp_unit, parameter)
        phases = self.get_phase_names()

        if parameter:
            components = self.get_components()
            df_all = []
            for params, temp_values, values in zip(components.values, temps, phase_values):
                pa_df = pd.DataFrame([params] * len(temp_values), columns=components.columns)
                tm_df = pd.DataFrame(temp_values, columns=[f"Temperature in {temp_unit}"])
                pf_df = pd.DataFrame(values, columns=phases)
                df = pd.concat([pa_df, tm_df, pf_df], axis=1)
                df_all.append(df)
            return pd.concat(df_all, ignore_index=True)

        phase_df = pd.DataFrame(phase_values, columns=phases)
        return pd.concat([temps, phase_df], axis=1)

    def get_volume_fraction(self, temp_unit="C", parameter=False):
        """Return DataFrame with volume fractions."""
        volume_values = self._get_volume_fraction()
        temps = pd.DataFrame(self._get_temperatures(temp_unit, parameter), columns=[f"Temperature in {temp_unit}"])
        phase_df = pd.DataFrame(volume_values, columns=self.get_phase_names())
        return pd.concat([temps, phase_df], axis=1)

    def get_temperatures(self, unit="C", parameter=False):
        """Return temperature values."""
        temps = self._get_temperatures(unit, parameter)
        return pd.DataFrame(temps, columns=[f"Temperature in {unit}"])
