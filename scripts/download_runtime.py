"""Optional Windows setup helper: ranged download of the approved torch wheel.

Uses official PyPI release metadata and verifies its SHA256 before pip use.
No installation, code execution, or alternate package source occurs here.
"""
from concurrent.futures import ThreadPoolExecutor
import hashlib
from pathlib import Path
import requests

def main():
    release="2.14.1"
    filename=f"torch-{release}-cp314-cp314-win_amd64.whl"
    metadata=requests.get(f"https://pypi.org/pypi/torch/{release}/json",timeout=30)
    metadata.raise_for_status()
    item=next(x for x in metadata.json()["urls"] if x["filename"]==filename)
    if not item["url"].startswith("https://files.pythonhosted.org/"):
        raise ValueError("Unexpected package host")
    size=item["size"]; block=4*1024*1024
    ranges=[(start,min(size-1,start+block-1)) for start in range(0,size,block)]
    def fetch(pair):
        start,end=pair
        response=requests.get(item["url"],headers={"Range":f"bytes={start}-{end}"},timeout=180)
        response.raise_for_status()
        if response.status_code!=206 or len(response.content)!=end-start+1:
            raise ValueError("Range validation failed")
        return response.content
    with ThreadPoolExecutor(max_workers=8) as pool:
        parts=list(pool.map(fetch,ranges))
    body=b"".join(parts)
    if len(body)!=size or hashlib.sha256(body).hexdigest()!=item["digests"]["sha256"]:
        raise ValueError("Package digest mismatch")
    directory=Path(__file__).resolve().parents[1]/".downloads"
    directory.mkdir(exist_ok=True)
    target=directory/filename; target.write_bytes(body)
    print(f"Verified official PyPI wheel: {target}",flush=True)
    print("SHA256: "+item["digests"]["sha256"],flush=True)

if __name__=="__main__":main()
