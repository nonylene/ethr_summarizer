import argparse
import csv
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import List, Optional

# https://github.com/microsoft/ethr/blob/master/utils.go#L107
UNITS = {
    "K": 1000 ** 1,
    "M": 1000 ** 2,
    "G": 1000 ** 3,
    "T": 1000 ** 4,
}

# https://github.com/microsoft/ethr/blob/master/utils.go#L198
TIME_UNITS = {
    "s": 1000 ** 2,
    "ms": 1000 ** 1,
    "us": 1000 ** 0,
    "ns": 1000 ** -1,
}


def to_number(with_unit: str) -> Optional[float]:
    if not with_unit:
        return None

    try:
        return float(with_unit)
    except ValueError:
        return float(with_unit[:-1]) * UNITS[with_unit[-1]]


def to_usec(with_unit: str) -> Optional[float]:
    if not with_unit:
        return None

    if with_unit[-2].isdigit():
        return float(with_unit[:-1]) * TIME_UNITS[with_unit[-1]]

    return float(with_unit[:-2]) * TIME_UNITS[with_unit[-2:]]


@dataclass
class LatencyResult:
    remote_addr: List[str]
    protocool: str
    # usec
    avg: float
    min_: float
    p50: float
    p90: float
    p95: float
    p99: float
    p999: float
    p9999: float
    max_: float

    @staticmethod
    def from_json(json: dict):
        return LatencyResult(
            json['RemoteAddr'][1:-1].split(","),
            json["Protocol"],
            to_usec(json["Avg"]),
            to_usec(json["Min"]),
            to_usec(json["P50"]),
            to_usec(json["P90"]),
            to_usec(json["P95"]),
            to_usec(json["P99"]),
            to_usec(json["P999"]),
            to_usec(json["P9999"]),
            to_usec(json["Max"]),
        )


@dataclass
class TestResult:
    remote_addr: List[str]
    protocol: str
    bits_per_second: Optional[float]  # bps
    connections_per_second: Optional[float]  # cps
    packets_per_second: Optional[float]  # pps
    average_latency: Optional[float]  # us

    @staticmethod
    def from_json(json: dict):
        return TestResult(
            json['RemoteAddr'][1:-1].split(","),
            json["Protocol"],
            to_number(json["BitsPerSecond"]),
            to_number(json["ConnectionsPerSecond"]),
            to_number(json["PacketsPerSecond"]),
            to_usec(json["AverageLatency"]),
        )


def avg_pps(path: os.PathLike):

    def _get_pps(line: str) -> Optional[float]:
        json_ = json.loads(line)
        if json_['Type'] != "TestResult":
            return None
        test_result = TestResult.from_json(json_)
        return test_result.packets_per_second

    return mean(b for b in map(_get_pps, open(path)) if b is not None)


def avg_latency(path: os.PathLike):

    def _get_latency(line: str) -> Optional[float]:
        json_ = json.loads(line)
        if json_['Type'] != "LatencyResult":
            return None
        latency_result = LatencyResult.from_json(json_)
        return latency_result.avg

    return mean(b for b in map(_get_latency, open(path)) if b is not None)


def main(target: os.PathLike):
    writer = csv.writer(sys.stdout)
    writer.writerow(['Alpha', 'Packets (pps)', 'Latency (us)'])

    for alphadir in Path(target).iterdir():
        alpha = 0 if alphadir.name == 'baseline' else alphadir.name
        avg_pps_ = avg_pps(alphadir / 'pps.jl')
        avg_latency_ = avg_latency(alphadir / 'latency.jl')
        writer.writerow([alpha, avg_pps_, avg_latency_])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ethr result summarizer")
    parser.add_argument("-t", "--target", dest="target", type=str, required=True, help="log dir")
    args = parser.parse_args()
    main(args.target)
