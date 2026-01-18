from flask import Flask, request, Response

app = Flask(__name__)

# ---------------- BLOQUEO GLOBAL ANTI-NAVEGADOR / ANTI-CORS ----------------
@app.before_request
def block_browser_requests():
    h = request.headers

    browser_headers = [
        "Origin",
        "Referer",
        "Sec-Fetch-Site",
        "Sec-Fetch-Mode",
        "Sec-Fetch-Dest",
        "Sec-CH-UA",
        "Sec-CH-UA-Platform",
        "Sec-CH-UA-Mobile"
    ]

    # Bloqueo por headers explícitos de navegador
    for header in browser_headers:
        if header in h:
            return Response(
                "Forbidden: Browser or CORS request detected",
                status=403
            )

    # Bloqueo por método preflight
    if request.method == "OPTIONS":
        return Response("Forbidden", status=403)

    # Bloqueo por Accept típico de navegador
    accept = h.get("Accept", "")
    if "text/html" in accept or "application/xhtml+xml" in accept:
        return Response("Forbidden", status=403)

    # Bloqueo por User-Agent web común
    ua = h.get("User-Agent", "").lower()
    browser_signatures = [
        "mozilla",
        "chrome",
        "safari",
        "firefox",
        "edge",
        "opera"
    ]

    if any(sig in ua for sig in browser_signatures):
        return Response(
            "Forbidden: Web client detected",
            status=403
        )


# ---------------- ANILLO 1 ----------------
@app.route("/ring1", methods=["GET"])
def ring1():

    lua_payload = r'''
print("--- ANILLO 1: VALIDADO ---")

math.randomseed(
    tick() * 100000 +
    game:GetService("Players").LocalPlayer.UserId
)

local function genHexToken(len)
    local t = {}
    for i = 1, len do
        t[i] = string.format("%x", math.random(0, 15))
    end
    return table.concat(t)
end

_G.StageToken = genHexToken(32)
print("Token hexadecimal generado:", _G.StageToken)
print("Procediendo al Anillo 2...")
'''

    return Response(lua_payload, mimetype="text/plain")


# ---------------- ANILLO 2 ----------------
@app.route("/ring2", methods=["GET"])
def ring2():
    token = request.args.get("token")
    if not token:
        return Response("Unauthorized", status=403)

    lua_payload = r'''
local player = game:GetService("Players").LocalPlayer
if player and _G.StageToken then
    _G.AuthID = tostring(player.UserId)
    print("--- ANILLO 2: USUARIO VERIFICADO (" .. _G.AuthID .. ") ---")
else
    error("Fallo de verificación")
end
'''

    return Response(lua_payload, mimetype="text/plain")


# ---------------- ANILLO 3 ----------------
@app.route("/ring3", methods=["GET"])
def ring3():
    auth = request.args.get("auth")
    if not auth:
        return Response("Unauthorized", status=401)

    lua_payload = f'''
print("--- ANILLO 3: ACCESO CONCEDIDO ---")

pcall(function()
    writefile("verify.txt", "Authorized_ID_{auth}")
end)

-- [SCRIPT FINAL]

print("Carga completa.")
'''

    return Response(lua_payload, mimetype="text/plain")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
