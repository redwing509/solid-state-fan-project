# Profiling (py-spy + scalene)

`profile.sh` profiles any Python command with two free, pip-installable profilers:

| Tool | What it gives | Files |
| --- | --- | --- |
| [py-spy](https://github.com/benfred/py-spy) | sampling flamegraph, including native (NumPy/SciPy) frames when available | `pyspy.svg`, `pyspy.speedscope.json` (open at https://www.speedscope.app) |
| [scalene](https://github.com/plasma-umass/scalene) | line-level CPU (Python vs native) and memory | `scalene.json`, `scalene.txt`, `scalene-profile.html` |

```bash
pip install py-spy scalene
cd engines/thermal1d && pip install -e .
../../tools/profiling/profile.sh -o /tmp/prof -- python -m thermal1d verify --out /tmp/verify.json
../../tools/profiling/profile.sh -t pyspy -o /tmp/prof -- python my_script.py --arg 1
```

Notes
- The command must start with `python`/`python3`; `-m module` is supported.
- For SciPy-heavy solvers most time is native; read the py-spy flamegraph first, scalene for memory and Python-vs-native split.
- Profiling repeats the run (py-spy twice, scalene once). Keep large cases off shared research machines unless the owner approved the compute.
- `.github/workflows/profiling.yml` runs the thermal1d verification profile on a free GitHub-hosted runner on manual dispatch only and uploads the files as an artifact.
