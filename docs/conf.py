from pathlib import Path
import sys

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"

sys.path.insert(0, str(SRC_DIR))
sys.path.insert(0, str(REPO_ROOT))

project = "ISEP"
author = "ISEP contributors"
release = "1.0.1"
root_doc = "index"
language = "en"

extensions = [
    "sphinx.ext.apidoc",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

apidoc_modules = [
    {
        "path": "../src",
        "destination": "api",
        "separate_modules": True,
        "automodule_options": {
            "members", "undoc-members", "show-inheritance"
        },
    },
]

autodoc_mock_imports = [
    "numpy", "scipy", "pandas", "sklearn", "matplotlib", "seaborn",
    "tensorflow", "keras", "h5py", "hdbscan", "joblib", "netCDF4",
    "PyQt5", "qtawesome", "QtAwesome", "umap", "varname", "dacite",
]

autodoc_member_order = "bysource"
autodoc_typehints = "none"
napoleon_google_docstring = True
napoleon_numpy_docstring = True

html_theme = "sphinx_rtd_theme"
html_title = "ISEP documentation"
exclude_patterns = [
    "_build",
    "api/modules.rst",
    "api/src.rst",
]

html_theme = "sphinx_rtd_theme"

html_theme_options = {
    "collapse_navigation": True,
    "navigation_depth": 4,
    "titles_only": True,
}