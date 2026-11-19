# isep/ui.py

import runpy


def handle():
    runpy.run_module(
        "src.ui.UI",
        run_name="__main__",
        alter_sys=True,
    )


if __name__ == "__main__":
    handle()