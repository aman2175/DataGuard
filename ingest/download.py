import gzip
import json
import requests
from pathlib import Path

RAW_DIR=Path("data/raw")

def download_hour(date: str, hour: int) -> Path:
    filename=f"{date}-{hour}.json.gz"
    target=RAW_DIR/filename
    if target.exists():
        print(f"file is already there with the name {filename}")
        return target
    url=f"https://data.gharchive.org/{filename}"
    print(f"downloading from {url}")
    RAW_DIR.mkdir(parents= True, exist_ok=True)

    with requests.get(url, stream=True, timeout=120) as response:
        response.raise_for_status()
        with target.open ("wb") as f:
            for i in response.iter_content(chunk_size=1024*1024):
                f.write(i)
    print(f"saved to {target}")
    return target


def inspect (path: Path) -> None:
    c=0
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for i in f:
            if c==0:
                print(json.dumps(json.loads(i), indent=2) [:800])# dump the first line in a pretty format a=== json load the line to a dictionary and then dump the dictionary in a pretty format and then print the first 800 characters of the line
            c+=1
    print(f"total lines: {c}")

if __name__ == "__main__":
    path=download_hour("2026-08-01", 15)
    inspect(path)

