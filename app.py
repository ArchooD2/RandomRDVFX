import io
import json
import random
import re
from flask import Flask, render_template, request, send_file

PRESETS = [
    "SilhouettesOnHBeat", "Vignette", "VignetteFlicker",
    "ColourfulShockwaves", "BassDropOnHit", "ShakeOnHeartBeat",
    "ShakeOnHit", "WavyRows", "LightStripVert", "VHS",
    "CutsceneMode", "HueShift", "Brightness", "Contrast",
    "Saturation", "GlitchObstruction", "Noise", "Rain",
    "Matrix", "Confetti", "FallingPetals", "FallingPetalsInstant",
    "FallingPetalsSnow", "Snow", "Bloom", "OrangeBloom",
    "BlueBloom", "HallOfMirrors", "TileN", "Sepia",
    "CustomScreenScroll", "JPEG", "NumbersAbovePulses",
    "Mosaic", "ScreenWaves", "Funk", "Grain", "Blizzard",
    "Drawing", "Aberration", "Blur", "RadialBlur",
    "Fisheye", "Dots", "Diamonds", "Balloons",
    "Tutorial", "DisableAll"
]

EXTRA_FIELDS = {
    "WavyRows":    {"intensity": 100, "speedPerc": 100},
    # add other preset‐specific extras here
}

def random_hex_color() -> str:
    return f"{random.randint(0, 0xFFFFFF):06X}"

def generate_vfx_presets(amount, rooms, bar, beat, blacklist):
    out = []
    for _ in range(amount):
        p = random.choice([pr for pr in PRESETS if pr not in blacklist])
        entry = {
            "type":    "SetVFXPreset",
            "bar":      bar,
            "beat":     beat,
            "y":        0,
            "rooms":    rooms,
            "preset":   p,
            "enable":   True,
            "duration": 0,
            "ease":     "Linear",
        }
        extras = EXTRA_FIELDS.get(p, {})
        for k, v in extras.items():
            if k == "color":
                entry[k] = random_hex_color()
            elif k == "threshold":
                entry[k] = round(random.uniform(0, 1), 2)
            elif k in ("intensity", "speedPerc"):
                entry[k] = random.randint(0, 200)
            elif k in ("floatX", "floatY"):
                entry[k] = round(random.uniform(0, 5), 2)
        out.append(entry)
    return out

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # 1) read uploaded file
        f = request.files["levelfile"]
        raw = f.read().decode("utf-8")
        cleaned = re.sub(r",\s*([\]}])", r"\1", raw)
        lvl = json.loads(cleaned)

        # 2) parse form inputs
        amount    = int(request.form["amount"])
        rooms_raw = request.form.get("rooms", "")
        rooms     = [int(r) for r in rooms_raw.split(",") if r]
        bar       = int(request.form["bar"])
        beat      = float(request.form["beat"])
        blacklist = [
            s.strip() for s in request.form["blacklist"].split(",") if s.strip()
        ]

        # 3) generate & inject
        vfx = generate_vfx_presets(amount, rooms, bar, beat, blacklist)
        lvl.setdefault("events", []).extend(vfx)
        out_json = json.dumps(lvl, indent=4)

        # 4) send as downloadable file
        return send_file(
            io.BytesIO(out_json.encode("utf-8")),
            as_attachment=True,
            download_name="output.rdlevel",
            mimetype="application/json"
        )

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
