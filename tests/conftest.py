import inspect
import os
from pathlib import Path
import shutil
import time
import pytest

os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ["MPLBACKEND"] = "Agg"

from pathlib import Path
import shutil
import pytest
import logging

@pytest.fixture
def test_resources(tmp_path):
    base_path = Path(__file__).resolve().parent / "end_to_end"

    source_resources = base_path / "resources"
    generated_resources = tmp_path / "generated"

    shutil.copytree(source_resources, generated_resources)

    yield generated_resources
        
@pytest.fixture(autouse=True)
def save_matplotlib_plots(monkeypatch, test_resources):
    import matplotlib.pyplot as plt

    plots_path = test_resources / "plots"
    plots_path.mkdir(exist_ok=True)

    def save_show(*args, **kwargs):
        caller = inspect.stack()[2].function

        existing = list(plots_path.glob(f"{caller}_*.png"))
        index = len(existing) + 1

        plt.savefig(
            plots_path / f"{caller}_{index}.png"
        )

        plt.close()

    monkeypatch.setattr(plt, "show", save_show)