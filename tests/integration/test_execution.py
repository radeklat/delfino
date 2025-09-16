import subprocess as sp
from pathlib import Path

import pytest

from src.delfino.execution import OnError, run

# Test constants
MAX_EXECUTION_TIME_SECONDS = 30


def _big_dual_stream_cmd(total_bytes: int = 64 * 1024 * 1024, chunk: int = 64 * 1024):
    """Creates a shell command that outputs large amounts of data to both stdout and stderr.

    This tests for deadlock conditions when parent processes don't properly handle
    concurrent reading from both output streams.
    """
    shell_script = f"""
# Configuration
TOTAL_BYTES={total_bytes}
CHUNK_SIZE={chunk}

# Create buffers - strings of A's and B's for stdout/stderr
STDOUT_CHUNK=$(printf 'A%.0s' $(seq 1 $CHUNK_SIZE))
STDERR_CHUNK=$(printf 'B%.0s' $(seq 1 $CHUNK_SIZE))

# Write data alternately to both streams
written=0
while [ $written -lt $TOTAL_BYTES ]; do
    # Write to stdout (file descriptor 1)
    printf '%s' "$STDOUT_CHUNK" >&1

    # Write to stderr (file descriptor 2)
    printf '%s' "$STDERR_CHUNK" >&2

    # Update bytes written counter
    written=$((written + 2 * CHUNK_SIZE))
done

exit 0
"""
    return ["/bin/sh", "-c", shell_script.strip()]


class TestExecution:
    @pytest.mark.timeout(10)
    @staticmethod
    def should_run_without_deadlock_on_large_both_streams(tmp_path: Path):
        cmd = _big_dual_stream_cmd(total_bytes=64 * 1024 * 1024, chunk=64 * 1024)

        cp = run(
            cmd,
            stdout=sp.PIPE,
            stderr=sp.PIPE,
            on_error=OnError.PASS,
            running_hook=lambda: None,
            text=False,
        )

        # 正常終了し、双方の出力が十分にあることを確認
        assert cp.returncode == 0
        assert isinstance(cp.stdout, (bytes, bytearray)) and len(cp.stdout) > 0
        assert isinstance(cp.stderr, (bytes, bytearray)) and len(cp.stderr) > 0
