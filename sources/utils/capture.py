from io import TextIOWrapper
from pathlib import Path
from typing import Self

from sources import settings


class OutputCapture:
    def __init__(
        self,
        filename: str = 'capture.log'
    ) -> None:
        self._filename = filename
        self._lines = []
        self._file: TextIOWrapper | None = None

    def __enter__(self) -> Self:
        if self._file:
            raise RuntimeError('Capture is already active and cannot be re-entered')

        self._temp_path.parent.mkdir(parents=True, exist_ok=True)
        self._file = open(self._temp_path, 'w+')

        #HACK: doesn't fully understand how this work, but think it doesn't need fd, 
        # so comment for now, maybe need to rewrite Capture later

        # self._stdout = sys.stdout
        # self._stderr = sys.stderr

        # self._stdout_descriptor = self._stdout.fileno()
        # self._stderr_descriptor = self._stderr.fileno()

        # self._stdout_duplicate = os.dup(self._stdout_descriptor)
        # self._stderr_duplicate = os.dup(self._stderr_descriptor)

        # sys.stdout = self._file
        # sys.stderr = self._file

        # os.dup2(self._file.fileno(), self._stdout_descriptor)
        # os.dup2(self._file.fileno(), self._stderr_descriptor)

        return self

    def __exit__(
        self,
        exc_type: object,
        exc_val: object,
        exc_tb: object,
    ) -> None:
        # os.dup2(self._stdout_duplicate, self._stdout_descriptor)
        # os.dup2(self._stderr_duplicate, self._stderr_descriptor)

        # os.close(self._stdout_duplicate)
        # os.close(self._stderr_duplicate)

        # sys.stdout = self._stdout
        # sys.stderr = self._stderr

        self._file.seek(0)
        self._lines = self._file.read().splitlines()

        self._file.close()
        self._file = None

        self._temp_path.unlink(missing_ok=True)

    def write(self, message) -> None:
        if self._file:
            self._file.write(f'{message}\n')
        else:
            print(message)

    def flush(self) -> None:
        if self._file:
            self._file.flush()

    @property
    def lines(self) -> list[str]:
        return self._lines

    @property
    def _temp_path(self) -> Path:
        return Path(settings.TEMPORARY_LOCATION) / self._filename
