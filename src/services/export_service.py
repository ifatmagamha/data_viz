from __future__ import annotations

def figure_to_png_bytes(fig) -> bytes:
    """
    Plotly -> PNG bytes (requires kaleido installed)
    """
    return fig.to_image(format="png")
