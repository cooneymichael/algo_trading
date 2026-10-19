from pathlib import Path
from shiny import run_app
from shiny.express import wrap_express_app


def main() -> None:

    app = wrap_express_app(Path(__file__).parent / 'Dashboard' / 'app.py')
    run_app(app)


if __name__ == '__main__':
    main()
