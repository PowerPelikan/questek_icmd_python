"""Module for plotting Solidification data."""

import pandas as pd
import plotly.express as px
import numpy as np
from icmdoutput.models.solidification import Solidification


class Scheil(Solidification):
    """Methods for plotting solidification (Scheil) data."""

    def __init__(self, path: str, modelname: str):
        super().__init__(path, modelname)
        self.temp_by_phase = self._compute_temp_by_phase()

    # ------------------------------------------------------------------

    def _get_present_phases(self, row: pd.Series, threshold: float) -> list[str]:
        """Return list of phases with fraction above given threshold."""
        df = self.get_phase_fraction()
        phase_columns = [
            c for c in df.columns if c not in ("Temperature in C", "SOLID")
        ]
        return [ph for ph in phase_columns if row[ph] > threshold]

    def _compute_temp_by_phase(self, threshold: float = 1e-6) -> pd.DataFrame:
        """Generate a DataFrame mapping temperature to phase regions."""
        phase_df = self.get_phase_fraction(parameter=False)
        temp_df = self.get_temperatures()

        present = phase_df.apply(
            lambda r: self._get_present_phases(r, threshold), axis=1
        )

        # Typo corrected: 'Temperature' not 'Temperatere'
        mapped = pd.DataFrame({
            "Temperature in C": temp_df["Temperature in C"].values,
            "Phase Region": present.apply(lambda ph: "+".join(sorted(ph))),
        })
        return mapped

    def get_temp_by_phase(self) -> pd.DataFrame:
        """Return the cached temperature-by-phase DataFrame."""
        return self.temp_by_phase

    # ------------------------------------------------------------------

    def get_scheil_df(self, threshold: float = 1e-6) -> pd.DataFrame:
        """Return combined Scheil DataFrame (phase + temperature)."""
        base = self.get_percent_solidified_molar()
        phase_info = self._compute_temp_by_phase(threshold)
        return pd.concat([base, phase_info], axis=1).iloc[:-1]

    # ------------------------------------------------------------------

    def scheil_plot(
        self,
        temp_unit: str = "C",
        plotname: str = "",
        user_script: bool = False,
        threshold: float = 1e-6,
    ):
        """Generate a Plotly line plot showing phase regions during solidification."""
        df = (
            self.get_scheil_df(threshold)
            if user_script
            else self.get_data_for_scheil_plot(temp_unit)
        )

        fig = px.line(
            df,
            x="Percent solidified molar",
            y=f"Temperature in {temp_unit}",
            color="Phase Region",
            title=plotname,
        )
        fig.update_traces(line={"width": 3})
        fig.update_layout(font={"size": 16}, title_font={"size": 22})
        return fig

    # ------------------------------------------------------------------

    def _scheil_plot_fig(
        self,
        df: pd.DataFrame,
        temp_col: str,
        plotname: str,
        log: bool,
        y_range: tuple | None,
    ):
        """Helper: build phase-fraction-over-temperature plot."""
        fig = px.line(
            df,
            x=temp_col,
            y="Phase Fraction",
            color="Phase",
            log_y=log,
            title=plotname,
        )
        fig.update_traces(line={"width": 2})

        if y_range:
            fig.update_yaxes(range=y_range)
        elif log:
            fig.update_yaxes(range=[-4, 0])

        fig.update_layout(
            font={"size": 16},
            title_font={"size": 22},
            xaxis_title=temp_col,
            yaxis_title="Phase fraction (mol)",
        )
        return fig

    # ------------------------------------------------------------------

    def scheil_step_plot(
        self,
        parameter: bool = False,
        temp_unit: str = "C",
        plotname: str = "",
        log: bool = True,
        y_range: tuple | None = None,
    ):
        """Plot phase fractions over temperature for a Scheil simulation."""
        df = self.get_phase_fraction(parameter=parameter, temp_unit=temp_unit)
        temp_col = f"Temperature in {temp_unit}"

        # Drop 'SOLID' if present
        phase_cols = [p for p in self.get_phase_names() if p != "SOLID" and p in df]
        df_long = (
            df.melt(
                id_vars=[temp_col],
                value_vars=phase_cols,
                var_name="Phase",
                value_name="Phase Fraction",
            )
            .sort_values(temp_col)
            .reset_index(drop=True)
        )

        return self._scheil_plot_fig(df_long, temp_col, plotname, log, y_range)
    