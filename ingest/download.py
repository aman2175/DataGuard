import gzip
import json
import requests
from pathlib import Path
from datetime import datetime, timezone, timedelta

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

def latest_hour() -> Path:
    now= datetime.now(timezone.utc)-timedelta(hours=1)
    hour=now.hour
    date=now.strftime("%Y-%m-%d")#format the date as YYYY-MM-DD
    name=f"{date}-{hour}.json.gz"#create the filename
    return RAW_DIR/name#return the filenamewhy 

if __name__ == "__main__":
    now=datetime.now(timezone.utc)-timedelta(hours=1)
    hour=now.hour
    date=now.strftime("%Y-%m-%d")
    for i in RAW_DIR.glob("*.json.gz"):
        i.unlink()
    
    path=download_hour(date, hour)
    inspect(path)

