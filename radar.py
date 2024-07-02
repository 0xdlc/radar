#!/usr/bin/env python
import argparse
from utils.marine import marine
from utils.flight import flight
from alive_progress import alive_bar
from utils.bounds.marine_bounds import bounds 
import time
from multiprocessing.pool import ThreadPool
from typing import List




def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-flight',required=False,nargs='?', const='true', metavar='flight-radar', type=bool)
    parser.add_argument('-marine',required=False,nargs='?', const='true', metavar='marine-radar', type=bool)
    parser.add_argument('-o', required=False, default=False, metavar='output file', type=str)
    parser.add_argument('-v',required=False,nargs='?', const='true', metavar='more-detailed data', type=bool)
    parser.add_argument('-airport',required=False,nargs='?', const='true', metavar='more-detailed data', type=bool)
    parser.add_argument('-track',required=False,nargs='?', const='true', metavar='more-detailed data', type=bool)
    parser.add_argument('-t', required=False, default=False, metavar='Number of Threads', type=int)
    parser.add_argument('-qgis', required=False, default=False, metavar='write flightradar24 file as qgis file', type=str)
    parser.add_argument('-debug',required=False,nargs='?', const=True, metavar='debug Mode', type=bool)
    args = parser.parse_args()
    if args.flight:
        flight(
            v=args.v,
            airport=args.airport,
            track=args.track,
            output=args.o,
            threads=args.t,
            qgis=args.qgis,
            debug=args.debug
            )
    if args.marine:
        with alive_bar(1,length=3,stats=False,monitor=False) as bar:
            with ThreadPool(processes=args.t) as pool:
                while True:
                    self = marine(debug=args.debug)
                    results = [pool.apply_async(marine.fetcher, (self,bound,bar)) for bound in bounds]
                    for r in results:
                        r.get()

if __name__ == "__main__":
    main()
# end main
