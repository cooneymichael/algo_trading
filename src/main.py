import logging.config
from pathlib import Path
from shiny import run_app
from shiny.express import wrap_express_app


def main() -> None:


    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '{asctime} {levelname}: <{name}> {message}',
                'datefmt': '[%Y-%m-%d %H:%M:%S]',
                'style': '{',
            },
        },

        'loggers': {
            'src.Domain': {'level': 'DEBUG'},
            'src.Database': {'level': 'DEBUG'},
            'src.Dashboard': {'level': 'DEBUG'},
        },

        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'INFO',
                'formatter': 'standard',
                'stream': 'ext://sys.stdout',
            },
        },

        'root': {
            'level': 'DEBUG',
            'handlers': ['console']
        },
    })

    app = wrap_express_app(Path(__file__).parent / 'Dashboard' / 'app.py')
    run_app(app)


if __name__ == '__main__':
    main()
