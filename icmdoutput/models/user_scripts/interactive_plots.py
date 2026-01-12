import ipywidgets as widgets
from IPython.display import display
import numpy as np
import plotly.graph_objects as go

def make_elem_sliders(comp_cols, comp_array):
    '''Create selection sliders for all components except Al'''

    #Add fallback for big datasets

    sliders = {}
    for i, c in enumerate(comp_cols):
        if c == "Al":
            continue
        values = sorted(set(comp_array[:, i]))
        sliders[c] = widgets.SelectionSlider(
            options = values,
            value = values[len(values) // 2],
            description = c,
            continous_update = True
        )
    return sliders

def get_data_slice(data_dict, target):
    '''FInd matching data entry for given composition, handling rounding errors'''
    # Add Al as the remainder to make total = 100
    target = {"Al": max(0.0, 100 - sum(target.values())), **target}
    key = tuple(round(float(i), 3) for i in target.values())

    # Try exactz match
    if key in data_dict:
        return data_dict[key], target

    # Otherwise find closest key numerically
    keys = np.array(list(data_dict.keys()))
    diffs = np.linalg.norm(keys - np.array(list(key)), axis=1)
    nearest_key = tuple(keys[np.argmin(diffs)])
    return data_dict[nearest_key], target

def plot_composition_step(g, comp_cols, target, t_col="Temperature in C", liquid_col="LIQUID"):
    '''Plot temperature vs phase fracstions'''
    fig = go.Figure()
    t = g[t_col]
    f_liq = np.nan_to_num(g[liquid_col], nan=0.0)
    fig.add_trace(go.Scatter(x=t, y=f_liq, mode='lines', name='LIQUID', 
                             line={'color': 'black', 'width': 2}))

    phases = [c for c in g.keys() if c not in {t_col, liquid_col, *comp_cols}]
    for p in phases:
        f = np.nan_to_num(g[p], nan=0.0)
        if f.max() > 0.0001:
            fig.add_trace(go.Scatter(x=t, y=f, mode='lines', name=p))

    fig.update_layout(
        xaxis=dict(title='Temperature in °C'),
        yaxis=dict(title='Phase Fraction in mole', type='log', range=[-4, 0]),
        template='plotly_white',
        height=600,
        width=900,
        title= "Composition:\n" +
            ",".join(f"{k}={target[k]:.2f}" for k in comp_cols)
    )

    config = {
        "toImageButtonOptions": {
            "format": "svg",
            "filename": ", ".join(f"{k}={target[k]:.2f}" for k in comp_cols),
            "height": 600,
            "width": 900,
            "scale": 1
        }
    }

    fig.show(config=config)

def plot_composition_scheil(g, comp_cols, target, t_col="Temperature in C", solid_col="SOLID", liquid_col="LIQUID"):
    '''Plot solid fraction over Temperature'''
    fig = go.Figure()
    # Temperature and solid fraction arrays
    t = g[t_col]
    f_solid = np.nan_to_num(g[solid_col], nan=0.0)
    fig.add_trace(go.Scatter(
        x=f_solid, y=t, mode="lines", name="Solid", line={'color':"black", 'width':2}, showlegend=False
    ))

    # Nur Marker für das erste Auftreten jeder Phase
    phases = [c for c in g.keys() if c not in {t_col, solid_col, liquid_col, *comp_cols}]
    for p in phases:
        f = np.nan_to_num(g[p], nan=0.0)
        #print(f)
        # Skip empty or near-zero phases
        if np.all(f <= 0):
            continue

        # Get first valid occurrence
        threshold = 1e-4
        onset_candidates = np.where(f[1:] > threshold)[0]
        if len(onset_candidates) == 0:
            continue
        onset_idx = onset_candidates[-1]

        fig.add_trace(go.Scatter(
            x=[f_solid[onset_idx]],  # Punkt auf Liquidus-Linie
            y=[t[onset_idx]], 
            mode="markers+text",
            marker=dict(size=10, symbol="circle"),
            text=[p],
            textposition="top right",
            name=p,
            showlegend=False
        ))
    fig.update_layout(
        #xaxis=dict(title="Fraktion", range=[0, 1]),
        xaxis=dict(title="Fraction of solid"),
        yaxis=dict(title="Temperatur in °C"),
        template="plotly_white",
        height=600,
        width=900,
        title= "Composition:\n" +
            ",".join(f"{k}={target[k]:.2f}" for k in comp_cols),

        legend=dict(y=1, x=0.99)
    )

    fig.show()

def make_interactive_step(comp_cols, data_dict, t_col="Temperature in C", liquid_col="LIQUID"):
    """Main function combining sliders, plot, and interactivity."""
    comp_array = np.array(list(data_dict.keys()))
    sliders = make_elem_sliders(comp_cols, comp_array)
    out = widgets.Output()

    def update_plot(**kwargs):
        out.clear_output(wait=True)
        g, target = get_data_slice(data_dict, kwargs)
        with out:
            plot_composition_step(g, comp_cols, target, t_col, liquid_col)

    interactive = widgets.interactive_output(update_plot, sliders)
    ui = widgets.VBox([*sliders.values(), out])
    display(ui, interactive)

def make_interactive_scheil(comp_cols, data_dict, t_col="Temperature in C", solid_col="SOLID", liquid_col="LIQUID"):
    """Main function combining sliders, plot, and interactivity."""
    comp_array = np.array(list(data_dict.keys()))
    sliders = make_elem_sliders(comp_cols, comp_array)
    out = widgets.Output()

    def update_plot(**kwargs):
        out.clear_output(wait=True)
        g, target = get_data_slice(data_dict, kwargs)
        with out:
            plot_composition_scheil(g, comp_cols, target, t_col, solid_col, liquid_col)

    interactive = widgets.interactive_output(update_plot, sliders)
    ui = widgets.VBox([*sliders.values(), out])
    display(ui, interactive)
