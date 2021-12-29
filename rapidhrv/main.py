import argparse
import pathlib

import rapidhrv as rhv


def main():
    parser = argparse.ArgumentParser(description="Rapid HRV")
    parser.add_argument("input_file", metavar="input-file", type=pathlib.Path)
    parser.add_argument("output_file", metavar="output-file", type=pathlib.Path)
    parser.add_argument("--sample-rate", type=int)
    parser.add_argument("--signal-output", type=pathlib.Path)
    args = parser.parse_args()

    print(f"Loading input from: {args.input_file}")
    signal = read_file(args, parser)
    print("Analyzing...")
    analyzed = rhv.analyze(rhv.preprocess(signal))
    print(f"Writing output to: {args.output_file}")
    analyzed.to_csv(args.output_file, index=False)
    if args.signal_output:
        print(f"Writing signal to: {args.signal_output}")
        signal.save(args.signal_output)
    print("Done")


def read_file(args, parser) -> rhv.Signal:
    if args.input_file.suffix == ".hdf5":
        return rhv.Signal.load(args.input_file)

    if args.sample_rate is None:
        parser.error("Non hdf5 files require a sample rate")

    if args.input_file.suffix == ".csv":
        return rhv.Signal.from_csv(args.input_file, args.sample_rate)
    else:
        parser.error("Unsupported file type")
