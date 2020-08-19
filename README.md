# ethr_summarizer

Summarize [ethr](https://github.com/microsoft/ethr) result log file to CSV.

## Usage

```
$ python3 main.py -t [log dir]
```

## Log dir structure

```
$ ls [log dir]
0 1 2 3 ...
$ ls [log dir]/0
0 1 2 3 ....
$ ls [log dir]/0/0
bandwidth.jl connections.jl latency.jl # ethr client logs
```
