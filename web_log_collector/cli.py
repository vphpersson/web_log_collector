from argparse import Action, ArgumentParser, Namespace, ArgumentDefaultsHelpFormatter
from pathlib import Path

from typed_argument_parser import TypedArgumentParser


class WebLogCollectorArgumentParser(TypedArgumentParser):

    class Namespace:
        log_directory: Path
        host: str
        port: int

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            **(
                dict(
                    description='Run an HTTP server that collects reports from web sites and logs them.',
                    formatter_class=ArgumentDefaultsHelpFormatter
                ) | kwargs
            )
        )

        self.add_argument(
            '--host',
            help='The host address on which to listen.',
            default='localhost'
        )

        self.add_argument(
            '--port',
            help='The port on which to listen.',
            default=80
        )

        self.add_argument(
            '--log-directory',
            help='The path of the directory where to write log files.',
            action=self._CheckLogDirectoryAction
        )

    class _CheckLogDirectoryAction(Action):
        def __call__(
                self,
                parser: ArgumentParser,
                namespace: Namespace,
                log_directory: str,
                option_string: str | None = None
        ):
            if (log_directory_path := Path(log_directory)).exists():
                setattr(namespace, self.dest, log_directory_path)
            else:
                parser.error(message='The specified log directory does not exist.')


