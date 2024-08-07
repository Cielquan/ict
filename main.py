#!/usr/bin/env python3
"""ICT, a simple script for tracking the internet connection downtime."""

from __future__ import annotations

import asyncio
import datetime
import pathlib

LOG_FILE = pathlib.Path(__file__).parent / "ict.log"
PING_TARGET = "1.1.1.1"
SLEEP_DURATION = 10


async def _main() -> int:
    """Run the actual script."""
    if not LOG_FILE.exists():
        LOG_FILE.touch()

    if not LOG_FILE.is_file():
        err_msg = f"Expected {LOG_FILE} to be a file."
        raise AssertionError(err_msg)

    log_file_has_content = LOG_FILE.read_text() != ""

    with LOG_FILE.open("a") as file:
        if log_file_has_content:
            file.write("\n")
        file.write(f"Starting script - {PING_TARGET=} - {SLEEP_DURATION=}\n")

    downtime_start: datetime.datetime | None = None

    try:
        while True:
            current_time = datetime.datetime.now(datetime.UTC)
            proc = await asyncio.create_subprocess_exec(
                "ping",
                "-c",
                "1",
                PING_TARGET,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            status_code = await proc.wait()

            if status_code != 0 and downtime_start is None:
                downtime_start = current_time
                with LOG_FILE.open("a") as file:
                    file.write(f"Downtime start:    {downtime_start}\n")

            if status_code == 0 and downtime_start is not None:
                downtime_total = current_time - downtime_start
                with LOG_FILE.open("a") as file:
                    file.write(f"Downtime end:      {current_time}\n")
                    file.write(f"Downtime duration: {downtime_total}\n")
                downtime_start = None

            await asyncio.sleep(SLEEP_DURATION)

    except Exception as exc:
        with LOG_FILE.open("a") as file:
            file.write(f"Exception occured: {exc}\n")
        raise

    finally:
        with LOG_FILE.open("a") as file:
            file.write("Stopping script\n")


def main() -> int:
    """Run the script."""
    try:
        return asyncio.run(_main())
    except KeyboardInterrupt:
        print("Stopping the script")  # noqa: T201
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
