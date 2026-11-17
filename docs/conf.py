import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(Path(__file__).parent / "_ext"))

project = "ISEP"
author = "Artur Tomczak"
copyright = "2023-2026, Artur Tomczak, University of Warsaw"
release = "1.0.1"
root_doc = "index"
language = "en"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
    "isep_autodoc",
]

autodoc_mock_imports = [
    "numpy",
    "scipy",
    "pandas",
    "sklearn",
    "matplotlib",
    "seaborn",
    "tensorflow",
    "keras",
    "h5py",
    "hdbscan",
    "joblib",
    "netCDF4",
    "PyQt5",
    "qtawesome",
    "QtAwesome",
    "umap",
    "varname",
    "dacite",
]
autodoc_member_order = "bysource"
autodoc_typehints = "none"
numpydoc_show_class_members = False

html_theme = "sphinx_rtd_theme"
html_title = "ISEP documentation"
html_theme_options = {
    "collapse_navigation": True,
    "navigation_depth": 4,
    "titles_only": True,
}
html_static_path = ["_static"]
html_css_files = ["styling.css"]

exclude_patterns = ["_build"]
