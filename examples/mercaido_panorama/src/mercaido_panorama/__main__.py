# SPDX-FileCopyrightText: 2023, 2024 Horus View and Explore B.V.
#
# SPDX-License-Identifier: MIT

import sys
import traceback

from . import main

if __name__ == "__main__":
    rc = 1
    try:
        main()
        rc = 0
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        traceback.print_exc()

    sys.exit(rc)
