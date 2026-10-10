"""Tiny YAML writer for the demo content (keeps multi-line text readable)."""
import json

def dump(data):
    out = []
    for k, v in data.items():
        if v is None:
            continue
        if isinstance(v, list):
            out.append(f"{k}:")
            for item in v:
                first = True
                for ik, iv in item.items():
                    out.append(("  - " if first else "    ") + f"{ik}: {json.dumps(iv, ensure_ascii=False)}")
                    first = False
        elif isinstance(v, str) and "\n" in v:
            out.append(f"{k}: |-")
            out += ["  " + line if line else "" for line in v.split("\n")]
        elif isinstance(v, (int, float)) or (isinstance(v, str) and len(v) == 10 and v[4] == "-" and v[7] == "-"):
            out.append(f"{k}: {v}")           # numbers and bare dates
        else:
            out.append(f"{k}: {json.dumps(v, ensure_ascii=False)}")
    return "\n".join(out) + "\n"
