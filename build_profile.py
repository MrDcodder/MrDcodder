#!/usr/bin/env python3
"""Builds dark.svg, light.svg, README.md. Usage: python build_profile.py [--photo me.jpg] [--out .]
Without --photo, a procedural head-and-shoulders ASCII silhouette is used.
With --photo (needs Pillow), your picture is converted to SVG characters."""
import argparse, math, random
from xml.sax.saxutils import escape as E

ap = argparse.ArgumentParser(); ap.add_argument('--photo'); ap.add_argument('--out', default='.')
A = ap.parse_args()

W, H = 1180, 610
FONT = "ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace"
P = {
 'dark': dict(bg1='#030712', bg2='#0B1220', panel='#0F172A', po=.35, tx='#F8FAFC', mu='#94A3B8',
              a1='#22D3EE', a2='#7C3AED', a3='#10B981', grid='#94A3B8', pill='#1E293B', sh=0),
 'light': dict(bg1='#FFFFFF', bg2='#EEF6FF', panel='#FFFFFF', po=.6, tx='#0F172A', mu='#475569',
               a1='#0E7490', a2='#2563EB', a3='#059669', grid='#2563EB', pill='#DBEAFE', sh=1)}

# ---- profile data (from GitHub profile + user) ----
NAME, USER = 'Diwyesh Nerkar', 'MrDcodder'
ROLES = ['Full-Stack Developer', 'Computer Engineering Student']
EDU = 'Computer Engineering · AIEM'
INTERN = 'CodeAlpha · BridgeAura (Fluxatic Global)'
FOCUS = 'Full-stack web apps · auth · databases'
STACK = ['TypeScript', 'HTML', 'CSS', 'Express', 'SQLite', 'Tailwind', 'JWT']
PROJ = [('URITOMO', 'Full-stack social app · Express, SQLite, JWT, Tailwind'),
        ('E-COMMERCE', 'Store with listings, cart, auth & orders · CodeAlpha'),
        ('BRIDGEAURA', 'Internship project · Fluxatic Global')]
GH = 'github.com/' + USER
ARIA = (f'{NAME} ({USER}): full-stack developer and Computer Engineering student. Stack: '
        + ', '.join(STACK) + '. Projects: Uritomo social app, E-Commerce full-stack store, BridgeAura internship project.')

# ---- ASCII portrait ----
RAMP = ' .:-=+*#%@'; COLS, ROWS, CW, LH = 64, 40, 5.04, 9

def lum_grid():
    if A.photo:
        from PIL import Image, ImageOps
        im = Image.open(A.photo).convert('L'); w, h = im.size
        ar = (COLS * CW) / (ROWS * LH); cw = min(w, int(h * ar)); ch = int(cw / ar); l = (w - cw) // 2
        im = ImageOps.autocontrast(im.crop((l, 0, l + cw, ch))).resize((COLS, ROWS)); d = list(im.getdata())
        return [[d[r * COLS + c] / 255 for c in range(COLS)] for r in range(ROWS)]
    rnd = random.Random(7); g = []
    for r in range(ROWS):
        row = []
        for c in range(COLS):
            x = (c + .5) * CW - COLS * CW / 2; y = (r + .5) * LH; v = 0
            for cx, cy, rx, ry, b in ((0, 128, 62, 80, 1), (0, 395, 158, 170, .8)):
                e = (x / rx) ** 2 + ((y - cy) / ry) ** 2
                if e < 1: v = max(v, b * (.3 + .5 * e ** 1.2 - .18 * x / rx))
            if 190 < y < 235 and abs(x) < 26: v = max(v, .35)
            if v == 0 and rnd.random() < .035: v = .12
            row.append(max(0, min(1, v)))
        g.append(row)
    return g

GRID = lum_grid()
ROWSTR = [''.join(RAMP[int(v * 9.99)] for v in r).replace(' ', '\u00a0') for r in GRID]

# ---- helpers ----
def rv(d, dur=.6): return f'<animate attributeName="opacity" from="0" to="1" begin="{d}s" dur="{dur}s" fill="freeze"/>'
def G(d, body): return f'<g opacity="0">{rv(d)}{body}</g>'
def T(x, y, s, fs, fill, anc='start', w=400, ls=0):
    return f'<text x="{x}" y="{y}" font-size="{fs}" fill="{fill}" text-anchor="{anc}" font-weight="{w}" letter-spacing="{ls}">{E(s)}</text>'

def typed(texts, x, y, fs, fill, cur, tag):
    cw = fs * .6; D = 9; n = len(texts); typ = .1; ev = {0.0, 1.0}
    def w(i, t):
        s0, s1 = i / n, (i + 1) / n
        if not (s0 <= t < s1): return 0
        return min(len(texts[i]), int((t - s0) / typ * len(texts[i]) + 1e-9)) * cw
    for i, s in enumerate(texts):
        for k in range(1, len(s) + 1): ev.add(round(i / n + typ * k / len(s), 5))
        ev.add(round((i + 1) / n, 5))
    ts = sorted(ev); ts[-1] = 1.0
    kt = ';'.join(str(t) for t in ts)
    out = '<defs>'; body = ''
    for i, s in enumerate(texts):
        vals = ';'.join(f'{w(i, min(t, .999999)):.1f}' for t in ts)
        out += (f'<clipPath id="{tag}{i}"><rect x="{x}" y="{y - fs}" width="0" height="{fs * 1.5:.0f}">'
                f'<animate attributeName="width" values="{vals}" keyTimes="{kt}" calcMode="discrete" dur="{D}s" repeatCount="indefinite"/></rect></clipPath>')
        body += f'<g clip-path="url(#{tag}{i})">{T(x, y, s, fs, fill, w=600)}</g>'
    cx = ';'.join(f'{x + (w(0, min(t, .999999)) if t < .5 else w(1, min(t, .999999))) + 1:.1f}' for t in ts)
    body += (f'<rect y="{y - fs + 2}" width="2" height="{fs}" fill="{cur}"><animate attributeName="x" values="{cx}" keyTimes="{kt}" calcMode="discrete" dur="{D}s" repeatCount="indefinite"/>'
             f'<animate attributeName="opacity" values="1;0" dur="1s" calcMode="discrete" repeatCount="indefinite"/></rect>')
    return out + '</defs>' + body

def pills(items, x, y, p):
    out = ''; cx = x
    for i, s in enumerate(items):
        w = len(s) * 7.4 + 30
        out += (f'<g><animateTransform attributeName="transform" type="translate" values="0 0;0 -1.5;0 0" dur="{4 + i % 3}s" begin="{i * .3}s" repeatCount="indefinite"/>'
                f'<rect x="{cx:.1f}" y="{y}" width="{w:.1f}" height="24" rx="12" fill="{p["pill"]}" fill-opacity=".55" stroke="url(#bd)" stroke-opacity=".7"/>'
                f'<circle cx="{cx + 12:.1f}" cy="{y + 12}" r="3" fill="{p["a3"]}"><animate attributeName="opacity" values="1;.35;1" dur="3s" begin="{i * .4}s" repeatCount="indefinite"/></circle>'
                f'{T(round(cx + 22, 1), y + 16, s, 12, p["tx"])}</g>')
        cx += w + 8
    return out

def build(name):
    p = P[name]; tx, mu, a1, a2, a3 = p['tx'], p['mu'], p['a1'], p['a2'], p['a3']
    rnd = random.Random(3)
    s = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{E(ARIA)}">'
         f'<title>{E(NAME)} · {USER}</title><style>text{{font-family:{FONT}}}</style><defs>'
         f'<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{p["bg1"]}"/><stop offset="1" stop-color="{p["bg2"]}"/></linearGradient>'
         f'<linearGradient id="bd" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{W}" y2="0" spreadMethod="reflect"><stop offset="0" stop-color="{a2}"/><stop offset=".5" stop-color="{a1}"/><stop offset="1" stop-color="{a3}"/>'
         f'<animateTransform attributeName="gradientTransform" type="translate" values="0 0;{W} 0" dur="14s" repeatCount="indefinite"/></linearGradient>'
         f'<linearGradient id="pg" gradientUnits="userSpaceOnUse" x1="0" y1="110" x2="0" y2="470" spreadMethod="reflect"><stop offset="0" stop-color="{a1}"/><stop offset="1" stop-color="{a2}"/>'
         f'<animateTransform attributeName="gradientTransform" type="translate" values="0 0;0 90" dur="9s" repeatCount="indefinite"/></linearGradient>'
         f'<pattern id="gr" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M32 0H0V32" fill="none" stroke="{p["grid"]}" stroke-opacity=".07"/></pattern>'
         f'<filter id="sh" x="-5%" y="-5%" width="110%" height="115%"><feDropShadow dx="0" dy="6" stdDeviation="8" flood-color="#0F172A" flood-opacity=".12"/></filter></defs>')
    s += f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="24" fill="url(#bg)" stroke="url(#bd)" stroke-width="1.5"/><rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="24" fill="url(#gr)"/>'
    for _ in range(10):
        x, y = rnd.randint(40, W - 40), rnd.randint(70, H - 30)
        s += (f'<circle cx="{x}" cy="{y}" r="1.3" fill="{a1}" opacity=".45"><animateMotion path="M0 0 L{rnd.randint(-24, 24)} {rnd.randint(-34, -8)} L0 0" dur="{rnd.randint(10, 18)}s" repeatCount="indefinite"/></circle>')
    # header
    s += G(.1, ''.join(f'<circle cx="{x}" cy="30" r="6" fill="{c}"/>' for x, c in ((50, '#FF5F57'), (70, '#FEBC2E'), (90, '#28C840')))
           + T(116, 35, f'{USER.lower()}@github:~', 13, mu)
           + f'<circle cx="1054" cy="30" r="4" fill="{a3}"><animate attributeName="opacity" values="1;.3;1" dur="2.4s" repeatCount="indefinite"/></circle>'
           + T(1152, 35, '[ ONLINE ]', 12, a3, 'end', 600, 1.5)
           + f'<line x1="28" x2="{W - 28}" y1="52" y2="52" stroke="{mu}" stroke-opacity=".25"/>')
    card = lambda x, w: (f'<rect x="{x}" y="64" width="{w}" height="518" rx="18" fill="{p["panel"]}" fill-opacity="{p["po"]}" stroke="url(#bd)" stroke-opacity=".8"'
                         + (' filter="url(#sh)"' if p['sh'] else '') + '/>')
    # LEFT
    s += G(.2, card(28, 420) + T(238, 94, 'VISUAL.MAP', 12, a1, 'middle', 700, 4))
    x0 = 238 - COLS * CW / 2
    rows = ''.join(f'<text x="{x0:.1f}" y="{110 + LH * (i + 1)}" font-size="8.4" fill="url(#pg)" opacity="0">'
                   f'<animate attributeName="opacity" from="0" to="1" begin="{.6 + i * .035:.3f}s" dur=".25s" fill="freeze"/>{r}</text>' for i, r in enumerate(ROWSTR))
    s += (f'<g>{rows}<animateTransform attributeName="transform" type="translate" values="0 0;0 -3;0 0" dur="7s" repeatCount="indefinite"/>'
          f'<animate attributeName="opacity" values="1;1;.88;1;1" keyTimes="0;.6;.62;.64;1" dur="11s" repeatCount="indefinite"/></g>'
          f'<rect x="{x0:.1f}" y="110" width="{COLS * CW:.1f}" height="2" fill="{a1}" opacity=".3"><animate attributeName="y" values="110;468;110" dur="6s" repeatCount="indefinite"/></rect>')
    s += G(2.2, f'<line x1="56" x2="420" y1="488" y2="488" stroke="{mu}" stroke-opacity=".25"/>'
           + T(238, 512, '[ PROFILE / ENGINEERING ]', 11, mu, 'middle', 400, 3)
           + T(238, 540, ROLES[0], 18, a1, 'middle', 700)
           + T(238, 566, '~/profile $ build --ship', 12, tx, 'middle')
           + f'<rect x="352" y="556" width="7" height="12" fill="{a3}"><animate attributeName="opacity" values="1;0" dur="1s" calcMode="discrete" repeatCount="indefinite"/></rect>')
    # RIGHT
    L, V = 638, 662
    lab = lambda t, y: T(L, y, t, 11, mu, 'end', 600, 2)
    s += G(.3, card(468, 684) + T(810, 96, 'SYSTEM.INFO', 13, a1, 'middle', 700, 5)
           + T(496, 130, f'{USER.lower()}@github:~$', 12, a3, w=600) + T(496 + 19 * 7.2 + 8, 130, './profile.sh', 12, tx)
           + f'<line x1="496" x2="1124" y1="146" y2="146" stroke="{mu}" stroke-opacity=".25"/>')
    s += G(1.0, lab('NAME', 196) + T(V, 196, NAME, 28, tx, w=700))
    s += G(1.4, lab('ROLE', 238) + typed(ROLES, V, 238, 18, a1, a3, 'r'))
    s += G(1.8, lab('EDUCATION', 274) + T(V, 274, EDU, 14, tx) + lab('INTERNSHIPS', 306) + T(V, 306, INTERN, 14, tx))
    s += G(2.1, lab('FOCUS', 338) + T(V, 338, FOCUS, 14, tx))
    s += G(2.4, lab('STACK', 371) + pills(STACK[:4], V, 355, p) + pills(STACK[4:], V, 387, p))
    s += G(2.8, f'<line x1="496" x2="1124" y1="428" y2="428" stroke="{mu}" stroke-opacity=".25"/>' + T(810, 450, 'SELECTED PROJECTS', 11, mu, 'middle', 600, 4)
           + ''.join(T(L, 478 + 22 * i, n, 12, a1, 'end', 700) + T(V, 478 + 22 * i, d, 12.5, tx) for i, (n, d) in enumerate(PROJ)))
    s += G(3.2, f'<line x1="496" x2="1124" y1="540" y2="540" stroke="{mu}" stroke-opacity=".25"/>' + lab('GITHUB', 563) + T(V, 563, GH, 13, a1, w=600))
    return s + '</svg>'

README = f'''<div align="center">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="./light.svg">
  <img src="./dark.svg" alt="{ARIA}">
</picture>
</div>

## About

Full-stack developer and Computer Engineering student at AIEM. I build web apps end to end: interfaces, APIs, auth and databases. I've worked on internship projects at CodeAlpha and at BridgeAura (Fluxatic Global).

## Featured projects

| Project | What it is |
| --- | --- |
| [Uritomo](https://github.com/{USER}/Mini_Social_Media_App_URITOMO) | Full-stack social media demo: Express/SQLite backend, JWT auth, profile onboarding, posts, search, messages, notifications and a Tailwind frontend |
| [E-Commerce Full Stack](https://github.com/{USER}/E-Commerce_Full_stack) | Basic full-stack store with product listings, cart, user authentication and order management, built for the CodeAlpha Internship Program |
| [Electronics E-commerce](https://github.com/{USER}/E-commerce_Site) | Mini project for skill development: an electronics e-commerce site, front end and back end |
| [BridgeAura Internship Project](https://github.com/{USER}/BridgeAura_Inernship_Project) | Internship project at BridgeAura by Fluxatic Global (TypeScript) |

## Stack

`TypeScript` `HTML` `CSS` `Express` `SQLite` `Tailwind CSS` `JWT`

## Connect

[GitHub](https://github.com/{USER})
'''

if __name__ == '__main__':
    import os
    for n in P: open(os.path.join(A.out, f'{n}.svg'), 'w', encoding='utf-8').write(build(n))
    open(os.path.join(A.out, 'README.md'), 'w', encoding='utf-8').write(README)
