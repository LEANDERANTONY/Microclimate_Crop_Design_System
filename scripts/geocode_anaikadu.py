import json, urllib.parse, urllib.request

def geocode(q):
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(
        {"q": q, "format": "jsonv2", "limit": 5})
    req = urllib.request.Request(url, headers={"User-Agent": "microclimate-crop-design/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

for q in ["GD Homestay, Anaikadu, Pattukkottai, Tamil Nadu",
          "GD Homestay Anaikadu",
          "GD Homestay, Anaikkadu",
          "GD Home Stay, Pattukkottai, Thanjavur"]:
    print("Q:", q)
    try:
        for h in geocode(q):
            print(f"   {h.get('lat')}, {h.get('lon')}  | {h.get('display_name')}")
    except Exception as e:
        print("   ERR", e)
    print()
