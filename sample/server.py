import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import lifegame_py
import logging


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description="lifegame server",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "host",
        help="hostname or ip address to bind",
    )
    parser.add_argument(
        "port", type=int,
        help="port number to listen, e.g., 2000",
    )
    parser.add_argument(
        "--verbose", action='store_true',
        help="show messages received from or sent to clients",
    )
    args = parser.parse_args()
    
    FORMAT = '%(asctime)s %(levelname)s %(message)s'
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(format=FORMAT, level=log_level, force=True)
    
    lifegame_py.server_main(args.host, args.port)