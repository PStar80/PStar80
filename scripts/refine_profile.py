#!/usr/bin/env python3
"""Idempotently refine the existing blue-metal profile assets; no external packages.

Only the allowlisted SVG files are changed. Original embedded artwork is retained.
Run from the repository root. Animation is illustrative, not live system telemetry.
"""
from __future__ import annotations
import html
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = [f'{name}{suffix}.svg' for name in ('hero','overview','systems','projects','connect','linkedin','github','email') for suffix in ('','-mobile')]
VERSION = 'data-profile-refinement="2"'
CYAN, WHITE, MUTED = '#25D6FF', '#F0F7FC', '#A4BDCF'

MOTION = '''<style>
.hub-stream{animation:hub-data 6s linear infinite}
.hub-halo{opacity:.16;animation:hub-breathe 7s ease-in-out infinite}
.hub-ring{animation:hub-data 18s linear infinite}
.hub-dust{animation:hub-drift 11s ease-in-out infinite}
.route-main{animation:hub-data 7s linear infinite}
.route-agent{opacity:.12;animation:agent-window 14s ease-in-out infinite}
@keyframes hub-data{to{stroke-dashoffset:-100}}
@keyframes hub-breathe{0%,100%{opacity:.10}50%{opacity:.28}}
@keyframes hub-drift{0%,100%{transform:translateY(0);opacity:.12}50%{transform:translateY(-6px);opacity:.5}}
@keyframes agent-window{0%,48%,90%,100%{opacity:.12}62%,76%{opacity:.85}}
@media(prefers-reduced-motion:reduce){.hub-stream,.hub-halo,.hub-ring,.hub-dust,.route-main,.route-agent{animation:none!important}.hub-dust{display:none}.hub-stream,.route-main{opacity:.35}.route-agent{opacity:.45}}
</style>'''

def text(x, y, value, size=18, color=WHITE, weight=400, anchor='start'):
    return f'<text x="{x}" y="{y}" font-family="Segoe UI,Arial,sans-serif" font-size="{size}" fill="{color}" font-weight="{weight}" text-anchor="{anchor}">{html.escape(value)}</text>'

def rect(x,y,w,h,fill='#071A29',stroke='#26718A'):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}"/>'

def frame(x,y,w,h):
    s=rect(x+2,y+2,w-4,h-4,'url(#surface)','url(#metal)')+rect(x+7,y+7,w-14,h-14,'url(#grid)','#163349')
    d=f'M{x+2} {y+2}H{x+w-2}V{y+h-2}H{x+2}Z'
    s+=f'<path d="{d}" pathLength="100" fill="none" stroke="{CYAN}" stroke-width="1.5" opacity=".5" stroke-dasharray="6 94" class="sweep"/>'
    for xx,yy,dx,dy in ((x+9,y+9,1,1),(x+w-9,y+9,-1,1),(x+9,y+h-9,1,-1),(x+w-9,y+h-9,-1,-1)):
        s+=f'<path d="M{xx+12*dx} {yy}H{xx}V{yy+12*dy}" fill="none" stroke="#A9C9DD" opacity=".65"/>'
    return s

def hero_motion(s, mobile):
    x,y,w,h = (20,139,440,138) if mobile else (485,28,446,172)
    scale=max(w/649,h/173); tx=x+(w-649*scale)/2; ty=y+(h-173*scale)/2
    definitions=f'''<clipPath id="hubClip"><rect x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath>
<radialGradient id="hubHalo"><stop stop-color="#6BE8FF"/><stop offset="1" stop-color="#25D6FF" stop-opacity="0"/></radialGradient>'''
    s=s.replace('</defs>',definitions+'</defs>',1)
    overlay=f'<g id="hub-motion" clip-path="url(#hubClip)"><g transform="translate({tx:.5f} {ty:.5f}) scale({scale:.7f})">'
    overlay+='<ellipse cx="301" cy="57" rx="73" ry="53" fill="url(#hubHalo)" class="hub-halo"/>'
    paths=['M82 78C136 69 129 112 180 100S224 96 257 113','M166 45C215 43 196 94 246 104L273 117','M347 115C417 115 386 55 428 44','M371 111C429 86 441 122 477 84S524 80 548 68','M415 125C451 123 485 142 514 132']
    for i,d in enumerate(paths):
        overlay+=f'<path d="{d}" fill="none" stroke="#74E7FF" stroke-width="1.1" opacity=".15"/>'
        overlay+=f'<path d="{d}" fill="none" stroke="#D8FAFF" stroke-width="1.8" stroke-linecap="round" pathLength="100" stroke-dasharray="3 97" opacity=".88" class="hub-stream" style="animation-delay:-{i*1.35}s"/>'
    overlay+='<ellipse cx="304" cy="124" rx="103" ry="13" fill="none" stroke="#81EFFF" stroke-width="1.1" pathLength="100" stroke-dasharray="11 89" opacity=".65" class="hub-ring"/>'
    for i,(cx,cy) in enumerate(((181,26),(393,25),(486,145),(212,140),(466,28))):
        overlay+=f'<circle cx="{cx}" cy="{cy}" r="1.2" fill="#8CEAFF" opacity=".25" class="hub-dust" style="animation-delay:-{i*2}s"/>'
    return s.replace('</svg>',overlay+'</g></g></svg>')

def architecture(s, mobile):
    # Preserve the original definitions and the already-approved Focus card.
    head=s[:s.index('</style>')+8]
    focus_start='<rect x="2" y="460"' if mobile else '<rect x="622" y="2"'
    at=s.find(focus_start)
    if at<0: raise ValueError('Expected Current Focus panel not found')
    focus=s[at:s.rfind('</svg>')]
    w,h=(480,444) if mobile else (604,332)
    body=frame(0,0,w,h)
    body+=text(27,43,'System Architecture',25,WHITE,650)
    body+=f'<path d="M25 62H{w-25}" stroke="#22485C"/>'
    body+=text(26,91,'SkyCommand · simplified execution model',17,MUTED)
    if mobile:
        xs=[26,136,246,356]; nw=98; top=118; nh=86
    else:
        xs=[26,168,310,452]; nw=126; top=110; nh=78
    labels=[('Operator','React UI'),('Core API','Node.js'),('Workflows','Temporal'),('Tools','Registered')]
    # Animation is carried only by connectors, never by text or status numbers.
    yy=top+nh/2
    for i,x in enumerate(xs[:-1]):
        start=x+nw; end=xs[i+1]
        body+=f'<path d="M{start} {yy}H{end}" stroke="#26718A" fill="none"/>'
        body+=f'<path d="M{start} {yy}H{end}" stroke="{CYAN}" stroke-width="2" fill="none" pathLength="100" stroke-dasharray="25 75" class="route-main" style="animation-delay:-{i*2}s"/>'
        body+=f'<path d="M{end-5} {yy-3}l4 3-4 3" fill="none" stroke="#B5F4FF"/>'
    for x,(title,sub) in zip(xs,labels):
        body+=rect(x,top,nw,nh)
        body+=text(x+nw/2,top+33,title,17,WHITE,600,'middle')
        body+=text(x+nw/2,top+59,sub,16,MUTED,400,'middle')
    if mobile:
        ax,ay,aw,ah=284,244,170,62
        body+=text(26,247,'Deterministic',19,CYAN,600)+text(26,273,'by default.',19,CYAN,600)
        body+=text(26,330,'AI agents branch from the workflow only when useful.',16,MUTED)
        data_y,footer_y=383,415
    else:
        ax,ay,aw,ah=424,207,154,43
        body+=text(26,222,'Deterministic by default',18,CYAN,600)
        body+=text(26,244,'Adaptive branch when useful.',16,MUTED)
        data_y,footer_y=282,307
    wx=xs[2]+nw/2
    d=f'M{wx} {top+nh}V{ay-12}H{ax+aw/2}V{ay}'
    body+=f'<path d="{d}" fill="none" stroke="#27647E" stroke-dasharray="4 4"/>'
    body+=f'<path d="{d}" fill="none" stroke="{CYAN}" stroke-width="2" class="route-agent"/>'
    body+=rect(ax,ay,aw,ah,'#071D2D','#2D7695')
    body+=text(ax+aw/2,ay+(26 if mobile else 19),'AI agent',18,WHITE,600,'middle')
    body+=text(ax+aw/2,ay+(49 if mobile else 36),'Optional node',15.5,MUTED,400,'middle')
    body+=f'<path d="M26 {data_y-25}H{w-26}" stroke="#22485C"/>'
    body+=text(26,data_y,'PostgreSQL · workflow / run metadata',17,CYAN,500)
    body+=text(26,footer_y,'Illustrated flow · not a live system-status display',16,MUTED)
    return head+body+focus+'\n</svg>'

def readable(s, name):
    def change(m):
        node=m.group(0)
        size=float(re.search(r'font-size="([\d.]+)"',node).group(1))
        target=size
        if name.startswith('overview') and size==13.6: target=15.5
        if name.startswith('systems') and size==14: target=16
        if name.startswith('projects') and size in (14.3,15,15.2,16): target=max(size,16.4)
        if name.startswith('projects') and size==18.5: target=20
        if name.startswith('projects'):
            node=node.replace('Full-stack macroeconomic','Macroeconomic analytics').replace('analytics with dashboards,','Dashboards, alerts and').replace('alerts, and time-series views.','historical time-series views.').replace('Walkthroughs and engineering discussion welcome.','Architecture and walkthroughs on request.')
        if name.startswith('overview'): node=node.replace('Oracle PL/SQL','Oracle / SQL')
        return re.sub(r'font-size="[\d.]+"',f'font-size="{target:g}"',node,count=1)
    return re.sub(r'<text\b[^>]*font-size="[\d.]+"[^>]*>.*?</text>',change,s,flags=re.S)

def refine(path):
    s=path.read_text(encoding='utf-8')
    if VERSION in s: return False
    ET.fromstring(s)
    if path.stem.startswith('systems'): s=architecture(s,'mobile' in path.stem)
    s=readable(s,path.stem)
    duration=18 if path.stem.startswith('hero') else 26
    s=s.replace('sweep 14s',f'sweep {duration}s')
    s=s.replace('.sweep { animation:', '.sweep { opacity:.55; animation:').replace('.spark { animation:', '.spark { opacity:.70; animation:')
    s=s.replace('</style>','</style>'+MOTION,1)
    if path.stem.startswith('hero'): s=hero_motion(s,'mobile' in path.stem)
    s=s.replace('<svg ',f'<svg {VERSION} ',1)
    ET.fromstring(s)
    path.write_text(s,encoding='utf-8')
    return True

def main():
    changed=[]
    for name in FILES:
        path=ROOT/name
        if not path.is_file(): raise FileNotFoundError(f'Missing required profile asset: {name}')
        if refine(path): changed.append(name)
    print('Refined assets:',', '.join(changed) if changed else 'already up to date')

if __name__=='__main__': main()
