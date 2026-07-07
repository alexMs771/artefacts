#!/usr/bin/env python3
"""Download and mirror the real CAL FIRE Unit Strategic Fire Plan PDFs.

WHY THIS EXISTS
---------------
The redesigned wildfire task fans out over the *real* CAL FIRE Unit Strategic
Fire Plans (one dense public PDF per operational unit). The official hosts
(osfm.fire.ca.gov / the OSFM Azure CDN / bof.fire.ca.gov) sit behind an Akamai
bot filter that refuses most automated fetches, so - exactly like the approved
CA-NORTHCOAST-WATER enforcement task - the documents must be mirrored to a
pinned public raw location (e.g. a GitHub repo pinned to a commit SHA) that the
task's agent fetches from reproducibly.

WORKFLOW
--------
1. Run this on a normal machine/browser network (NOT the task sandbox):
       python fetch_unit_plans.py
   It downloads each unit plan into ./plans/<CODE>.pdf, validates it is a real
   PDF, and writes plans/manifest.json + plans/sha256sums.txt.
2. Push the ./plans/ folder to a public repo, e.g.
       github.com/alexMs771/ca-unit-fire-plans   (folder: plans/)
   and note the exact commit SHA.
3. Give me the pinned raw base, e.g.
       https://raw.githubusercontent.com/alexMs771/ca-unit-fire-plans/<SHA>/plans/
   I bake the per-unit fetch URLs into instruction.md and sources.json, keeping
   each unit's official source page as the citation.

NOTHING here is fabricated: every URL below is a real, publicly indexed CAL FIRE
Unit Strategic Fire Plan. Any URL that fails to download is reported so it can be
replaced with the copy from the OSFM Pre-Fire Planning map.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import urllib.request
import urllib.error

OFFICIAL_INDEX = (
    "https://www.fire.ca.gov/osfm/what-we-do/"
    "community-wildfire-preparedness-and-mitigation/pre-fire-planning"
)

# code, name, counties, plan_year, download url(s) (first that works wins), official citation page
UNITS = [
    ("AEU", "Amador-El Dorado Unit", ["Amador", "El Dorado", "Sacramento", "Alpine"], "2024",
     ["https://www.eldoradocounty.ca.gov/files/assets/county/v/1/documents/public-safety-amp-justice/wildfire-amp-disaster/wildfire-preparedness/2024-amador-el-dorado-alpine-sacramento-unit-fire-plan-final-and-published.pdf"],
     "https://www.eldoradocounty.ca.gov/"),
    ("BTU", "Butte Unit", ["Butte"], "2025",
     ["https://34c031f8-c9fd-4018-8c5a-4159cdff6b0d-cdn-endpoint.azureedge.net/-/media/osfm-website/what-we-do/community-wildfire-preparedness-and-mitigation/2025-butte-unit-fire-plan-and-cwpp.pdf"],
     OFFICIAL_INDEX),
    ("HUU", "Humboldt-Del Norte Unit", ["Humboldt", "Del Norte"], "2025",
     ["https://34c031f8-c9fd-4018-8c5a-4159cdff6b0d-cdn-endpoint.azureedge.net/-/media/osfm-website/what-we-do/community-wildfire-preparedness-and-mitigation/huu_2025_fireplan.pdf",
      "https://34c031f8-c9fd-4018-8c5a-4159cdff6b0d-cdn-endpoint.azureedge.net/-/media/osfm-website/what-we-do/community-wildfire-preparedness-and-mitigation/2025-humboldt-del-norte-unit-fire-plan.pdf"],
     OFFICIAL_INDEX),
    ("LMU", "Lassen-Modoc Unit", ["Lassen", "Modoc", "Plumas"], "2025",
     ["https://34c031f8-c9fd-4018-8c5a-4159cdff6b0d-cdn-endpoint.azureedge.net/-/media/osfm-website/what-we-do/community-wildfire-preparedness-and-mitigation/2025-lmu-strategic-fire-plan.pdf"],
     OFFICIAL_INDEX),
    ("MEU", "Mendocino Unit", ["Mendocino"], "2025",
     ["https://34c031f8-c9fd-4018-8c5a-4159cdff6b0d-cdn-endpoint.azureedge.net/-/media/osfm-website/what-we-do/community-wildfire-preparedness-and-mitigation/2025-mendocino-unit-fire-plan.pdf"],
     OFFICIAL_INDEX),
    ("NEU", "Nevada-Yuba-Placer Unit", ["Nevada", "Yuba", "Placer", "Sutter", "Sierra"], "2025",
     ["https://34c031f8-c9fd-4018-8c5a-4159cdff6b0d-cdn-endpoint.azureedge.net/-/media/osfm-website/what-we-do/community-wildfire-preparedness-and-mitigation/pre-fire-planning/2025-neu-strategic-fire-plan.pdf"],
     OFFICIAL_INDEX),
    ("CZU", "San Mateo-Santa Cruz Unit", ["San Mateo", "Santa Cruz"], "2021",
     ["https://osfm.fire.ca.gov/media/ye0hefak/2021_czu_fireplan.pdf"],
     "https://osfm.fire.ca.gov/"),
    ("SCU", "Santa Clara Unit", ["Santa Clara", "Contra Costa", "Alameda", "San Joaquin", "Stanislaus"], "2025",
     ["https://34c031f8-c9fd-4018-8c5a-4159cdff6b0d-cdn-endpoint.azureedge.net/-/media/osfm-website/what-we-do/community-wildfire-preparedness-and-mitigation/2025-santa-clara-contra-costa-alameda-west-stanislaus-west-san-joaquin-unit-fire-plan.pdf"],
     OFFICIAL_INDEX),
    ("SHU", "Shasta-Trinity Unit", ["Shasta", "Trinity"], "2025",
     ["https://34c031f8-c9fd-4018-8c5a-4159cdff6b0d-cdn-endpoint.azureedge.net/-/media/osfm-website/what-we-do/community-wildfire-preparedness-and-mitigation/2025-shasta-trinity-unit-fire-plan.pdf"],
     OFFICIAL_INDEX),
    ("SKU", "Siskiyou Unit", ["Siskiyou"], "2025",
     ["https://34c031f8-c9fd-4018-8c5a-4159cdff6b0d-cdn-endpoint.azureedge.net/-/media/osfm-website/what-we-do/community-wildfire-preparedness-and-mitigation/2025-siskiyou-unit-fire-plan.pdf"],
     OFFICIAL_INDEX),
    ("LNU", "Sonoma-Lake-Napa Unit", ["Sonoma", "Lake", "Napa", "Solano", "Yolo", "Colusa"], "2021",
     ["https://osfm.fire.ca.gov/media/lpafffiu/2021_lnu_fireplan.pdf"],
     "https://osfm.fire.ca.gov/"),
    ("TGU", "Tehama-Glenn Unit", ["Tehama", "Glenn"], "2024",
     ["https://bof.fire.ca.gov/media/5bobq0yn/rpc-2-b-i-_-do-not-print__4-tehama-glenn-unit-fire-plan-2024_re_adamfk.pdf"],
     "https://bof.fire.ca.gov/"),
    ("FKU", "Fresno-Kings Unit", ["Fresno", "Kings"], "2025",
     ["https://34c031f8-c9fd-4018-8c5a-4159cdff6b0d-cdn-endpoint.azureedge.net/-/media/osfm-website/what-we-do/community-wildfire-preparedness-and-mitigation/fku_2025_fireplan.pdf"],
     OFFICIAL_INDEX),
    ("MMU", "Madera-Mariposa-Merced Unit", ["Madera", "Mariposa", "Merced"], "2025",
     ["https://34c031f8-c9fd-4018-8c5a-4159cdff6b0d-cdn-endpoint.azureedge.net/-/media/osfm-website/what-we-do/community-wildfire-preparedness-and-mitigation/mmu_2025_fireplan.pdf"],
     OFFICIAL_INDEX),
    ("RRU", "Riverside Unit", ["Riverside"], "2025",
     ["https://34c031f8-c9fd-4018-8c5a-4159cdff6b0d-cdn-endpoint.azureedge.net/-/media/osfm-website/what-we-do/community-wildfire-preparedness-and-mitigation/pre-fire-planning/riverside_unit_fire_plan_2025_1.pdf"],
     OFFICIAL_INDEX),
    ("BEU", "San Benito-Monterey Unit", ["San Benito", "Monterey"], "2025",
     ["https://34c031f8-c9fd-4018-8c5a-4159cdff6b0d-cdn-endpoint.azureedge.net/-/media/osfm-website/what-we-do/community-wildfire-preparedness-and-mitigation/beu_2025_fire_plan.pdf"],
     OFFICIAL_INDEX),
    ("BDU", "San Bernardino Unit", ["San Bernardino", "Inyo", "Mono"], "2025",
     ["https://34c031f8-c9fd-4018-8c5a-4159cdff6b0d-cdn-endpoint.azureedge.net/-/media/osfm-website/what-we-do/community-wildfire-preparedness-and-mitigation/pre-fire-planning/bdu_fireplan_final_052025_1502.pdf"],
     OFFICIAL_INDEX),
    ("SDU", "San Diego Unit", ["San Diego", "Imperial"], "2022",
     ["https://osfm.fire.ca.gov/media/nvmduq3i/2022-san-diego-imperial-unit-fire-plan.pdf"],
     "https://osfm.fire.ca.gov/"),
    ("SLU", "San Luis Obispo Unit", ["San Luis Obispo"], "2025",
     ["https://34c031f8-c9fd-4018-8c5a-4159cdff6b0d-cdn-endpoint.azureedge.net/-/media/osfm-website/what-we-do/community-wildfire-preparedness-and-mitigation/2025-slu-fire-plan.pdf"],
     OFFICIAL_INDEX),
    ("TUU", "Tulare Unit", ["Tulare"], "2025",
     ["https://34c031f8-c9fd-4018-8c5a-4159cdff6b0d-cdn-endpoint.azureedge.net/-/media/osfm-website/what-we-do/community-wildfire-preparedness-and-mitigation/2025_tulare_unit_fire_plan.pdf"],
     OFFICIAL_INDEX),
    ("TCU", "Tuolumne-Calaveras Unit", ["Tuolumne", "Calaveras", "San Joaquin", "Stanislaus", "Alpine"], "2025",
     ["https://34c031f8-c9fd-4018-8c5a-4159cdff6b0d-cdn-endpoint.azureedge.net/-/media/osfm-website/what-we-do/community-wildfire-preparedness-and-mitigation/tcu-unit-fire-plan-2025.pdf"],
     OFFICIAL_INDEX),
]

_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
       "(KHTML, like Gecko) Chrome/125.0 Safari/537.36")
MIN_BYTES = 200 * 1024  # a real unit plan is hundreds of KB+; reject tiny error pages


def _download(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": _UA, "Accept": "application/pdf,*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def main() -> int:
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plans")
    os.makedirs(out_dir, exist_ok=True)
    manifest = []
    sums = []
    ok = 0
    for code, name, counties, year, urls, official in UNITS:
        got = None
        used = None
        err = ""
        for url in urls:
            try:
                data = _download(url)
                if not data.startswith(b"%PDF"):
                    err = f"not a PDF (starts {data[:8]!r})"
                    continue
                if len(data) < MIN_BYTES:
                    err = f"too small ({len(data)} bytes)"
                    continue
                got, used = data, url
                break
            except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as e:
                err = f"{type(e).__name__}: {e}"
        if got is None:
            print(f"FAIL {code:4s} {name:34s} -> {err}  (grab from OSFM map: {OFFICIAL_INDEX})")
            manifest.append({"code": code, "name": name, "counties": counties, "year": year,
                             "status": "FAILED", "tried": urls, "official_page": official})
            continue
        path = os.path.join(out_dir, f"{code}.pdf")
        with open(path, "wb") as f:
            f.write(got)
        digest = hashlib.sha256(got).hexdigest()
        sums.append(f"{digest}  {code}.pdf")
        manifest.append({"code": code, "name": name, "counties": counties, "year": year,
                         "status": "OK", "bytes": len(got), "sha256": digest,
                         "fetch_origin": used, "official_page": official,
                         "mirror_file": f"{code}.pdf"})
        ok += 1
        print(f"OK   {code:4s} {name:34s} {len(got)//1024:6d} KB  {used}")

    with open(os.path.join(out_dir, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    with open(os.path.join(out_dir, "sha256sums.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(sums) + "\n")

    print(f"\n{ok}/{len(UNITS)} unit plans downloaded into {out_dir}")
    print("manifest.json + sha256sums.txt written.")
    if ok < len(UNITS):
        print("\nReplace any FAILED unit by opening the OSFM Pre-Fire Planning map,")
        print("clicking that unit, and saving its Unit Fire Plan PDF into plans/<CODE>.pdf,")
        print("then re-run to refresh the manifest.")
    print("\nNext: push plans/ to a public repo, note the commit SHA, and send me")
    print("  https://raw.githubusercontent.com/<you>/<repo>/<SHA>/plans/")
    return 0 if ok >= len(UNITS) else 1


if __name__ == "__main__":
    sys.exit(main())
