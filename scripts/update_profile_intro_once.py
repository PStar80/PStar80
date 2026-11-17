#!/usr/bin/env python3
"""Update only the profile introduction, retaining the existing embedded artwork."""
from __future__ import annotations
import copy
import html
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NS = 'http://www.w3.org/2000/svg'
VERSION = 'full-stack-v1'
WHITE, CYAN, MUTED = '#F0F7FC', '#25D6FF', '#B5CBDC'
ET.register_namespace('', NS)
ET.register_namespace('xlink', 'http://www.w3.org/1999/xlink')
LABELS = ('WORKFLOW AUTOMATION', 'DATA ENGINEERING', 'DATA VISUALIZATION', 'AI-NATIVE APPLICATIONS')
ABOUT_LINES = [
    (134, 'I build scalable full-stack applications'),
    (161, 'for workflow automation, data engineering'),
    (188, 'and interactive data visualization.'),
    (228, 'SkyCommand orchestrates work.'),
    (255, 'SkyDataStudio creates trusted data products.'),
    (282, 'MacroAnalyzer brings data to life.'),
    (322, 'From interfaces and APIs to databases and'),
    (349, 'containerized services, I build end to end.'),
    (389, 'My focus now is AI-native applications:'),
    (416, 'agentic AI, MCP-connected coding agents'),
    (443, 'and automation across the software lifecycle.'),
]
ABOUT_MARKDOWN = '''I'm **Paul Sattaur**, a full-stack software engineer based in the Greater Toronto Area, Canada. I design and build applications with scalability, maintainability and a clear user experience in mind, connecting interactive interfaces, APIs, databases, data pipelines and containerized services.

My work spans three connected areas: **workflow automation with SkyCommand**, **data engineering with SkyDataStudio**, and **interactive analytics and data visualization with MacroAnalyzer**. Together, these applications bring operational workflows, trusted analytical data and user-facing insights into a connected ecosystem.

I work across **React, JavaScript/TypeScript, Node.js, Python/FastAPI, C#/ASP.NET Core and PostgreSQL**, with **Temporal** for workflow orchestration, **Airflow and dbt** for data engineering, **ECharts/D3** for visualization, and **Docker** for containerized services. My enterprise background also includes Oracle SQL/PLSQL, Java/J2EE, requirements analysis, integrations and production troubleshooting.

My current focus is **AI-native applications and agentic automation**: integrating embedded AI agents and MCP-connected coding assistants with application workflows, configured capabilities and observable execution. I build across the stack, from the user experience through to the services and data that power it.

'''
HERO_ALT = 'Paul Sattaur — Full-Stack Applications, Agentic AI and Automation. Full-width animated orchestration artwork behind the headline. Focus areas: workflow automation, data engineering, data visualization and AI-native applications.'
ABOUT_ALT = 'About me: I build scalable full-stack applications across workflow automation, data engineering and interactive data visualization. SkyCommand orchestrates work; SkyDataStudio creates trusted data products; MacroAnalyzer makes data explorable. My focus is AI-native applications integrating agentic AI, MCP-connected coding agents and workflow automation. Technology stack: Python, JavaScript, C#/.NET, React, Node.js, PostgreSQL, Docker, Temporal, Oracle/SQL, REST APIs, Git/GitHub and TypeScript.'
DEFS = '''<defs>
<linearGradient id="surface" x2="1" y2="1"><stop stop-color="#06111C"/><stop offset=".55" stop-color="#07131F"/><stop offset="1" stop-color="#020A12"/></linearGradient>
<linearGradient id="metal" x2="1" y2="1"><stop stop-color="#D8E7EE"/><stop offset=".10" stop-color="#3C596D"/><stop offset=".26" stop-color="#9DB5C4"/><stop offset=".42" stop-color="#1F3547"/><stop offset=".57" stop-color="#6B96B1"/><stop offset=".72" stop-color="#E3F4FF"/><stop offset=".84" stop-color="#365569"/><stop offset="1" stop-color="#91ACBF"/></linearGradient>
<pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse"><path d="M24 0H0V24" fill="none" stroke="#40BCFF" stroke-opacity=".055"/></pattern>
<linearGradient id="shade"><stop stop-color="#020B14" stop-opacity=".91"/><stop offset=".36" stop-color="#020B14" stop-opacity=".63"/><stop offset=".67" stop-color="#020B14" stop-opacity=".07"/><stop offset="1" stop-color="#020B14" stop-opacity=".02"/></linearGradient>
<linearGradient id="bottomShade" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#020B14" stop-opacity="0"/><stop offset=".6" stop-color="#020B14" stop-opacity=".06"/><stop offset="1" stop-color="#020B14" stop-opacity=".8"/></linearGradient>
<radialGradient id="hubHalo"><stop stop-color="#6BE8FF"/><stop offset="1" stop-color="#25D6FF" stop-opacity="0"/></radialGradient>
</defs>'''
CSS = '''<style>
.sweep{animation:sweep 26s linear infinite}.spark{animation:sweep 26s linear infinite}
.hub-stream{animation:data 6s linear infinite}.hub-halo{opacity:.16;animation:breathe 7s ease-in-out infinite}
.hub-ring{animation:data 18s linear infinite}.hub-dust{animation:drift 11s ease-in-out infinite}
@keyframes sweep{to{stroke-dashoffset:-100}}@keyframes data{to{stroke-dashoffset:-100}}
@keyframes breathe{0%,100%{opacity:.10}50%{opacity:.26}}
@keyframes drift{0%,100%{transform:translateY(0);opacity:.16}50%{transform:translateY(-5px);opacity:.5}}
@media(prefers-reduced-motion:reduce){.sweep,.spark,.hub-stream,.hub-halo,.hub-ring,.hub-dust{animation:none!important}}
</style>'''

def text(x,y,value,size=19,color=MUTED,weight=400,anchor='start',extra=''):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}" text-anchor="{anchor}" {extra}>{html.escape(value)}</text>'

def shell(w,h,title,desc,body):
    return f'<svg xmlns="{NS}" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc" font-family="Segoe UI,Arial,sans-serif" data-profile-refinement="2" data-intro="{VERSION}">\n<title id="title">{html.escape(title)}</title><desc id="desc">{html.escape(desc)}</desc>\n{DEFS}\n{CSS}\n{body}\n</svg>\n'

def frame(x,y,w,h,background=True):
    fill='url(#surface)' if background else 'none'
    out=f'<rect x="{x+2}" y="{y+2}" width="{w-4}" height="{h-4}" fill="{fill}" stroke="url(#metal)" stroke-width="2"/>'
    out+=f'<rect x="{x+7}" y="{y+7}" width="{w-14}" height="{h-14}" fill="'+('url(#grid)' if background else 'none')+'" stroke="#163349"/>'
    out+=f'<path d="M{x+2} {y+2}H{x+w-2}V{y+h-2}H{x+2}Z" pathLength="100" fill="none" stroke="{CYAN}" stroke-width="1.6" opacity=".55" stroke-dasharray="6 94" class="sweep"/>'
    out+=f'<path d="M{x+2} {y+2}H{x+w-2}V{y+h-2}H{x+2}Z" pathLength="100" fill="none" stroke="#E6FAFF" stroke-width="1.2" opacity=".65" stroke-dasharray=".9 99.1" class="spark"/>'
    for xx,yy,dx,dy in ((x+9,y+9,1,1),(x+w-9,y+9,-1,1),(x+9,y+h-9,1,-1),(x+w-9,y+h-9,-1,-1)):
        out+=f'<path d="M{xx+12*dx} {yy}H{xx}V{yy+12*dy}" fill="none" stroke="#A9C9DD" opacity=".65"/>'
    return out

def art_href(source):
    root=ET.fromstring(source)
    for node in root.iter(f'{{{NS}}}image'):
        value=node.get('href') or node.get('{http://www.w3.org/1999/xlink}href')
        if value and value.startswith('data:image/png;base64,'): return value
    raise ValueError('Expected existing embedded PNG artwork')

def motion():
    result='<ellipse cx="301" cy="57" rx="73" ry="53" fill="url(#hubHalo)" opacity=".16" class="hub-halo"/>'
    paths=['M82 78C136 69 129 112 180 100S224 96 257 113','M166 45C215 43 196 94 246 104L273 117','M347 115C417 115 386 55 428 44','M371 111C429 86 441 122 477 84S524 80 548 68','M415 125C451 123 485 142 514 132']
    for i,d in enumerate(paths):
        result+=f'<path d="{d}" fill="none" stroke="#9EEFFF" stroke-width="1.3" stroke-linecap="round" pathLength="100" stroke-dasharray="2.5 97.5" opacity=".78" class="hub-stream" style="animation-delay:-{i*1.35}s"/>'
    result+='<ellipse cx="304" cy="124" rx="103" ry="13" fill="none" stroke="#81EFFF" stroke-width="1" pathLength="100" stroke-dasharray="11 89" opacity=".6" class="hub-ring"/>'
    for i,(cx,cy) in enumerate(((181,26),(393,25),(486,145),(212,140),(466,28))):
        result+=f'<circle cx="{cx}" cy="{cy}" r="1.1" fill="#8CEAFF" opacity=".25" class="hub-dust" style="animation-delay:-{i*2}s"/>'
    return result

def hero(href,mobile):
    w,h=(480,340) if mobile else (960,320)
    scale=(h-16)/173
    tx=(335-301*scale) if mobile else 8
    out=f'<defs><clipPath id="artClip"><rect x="8" y="8" width="{w-16}" height="{h-16}"/></clipPath></defs>'
    out+=f'<rect width="{w}" height="{h}" fill="#04101B"/>'
    out+=f'<g clip-path="url(#artClip)"><g transform="translate({tx:.5f} 8) scale({scale:.8f})">'
    out+=f'<image width="649" height="173" href="{href}"/>'+motion()+'</g></g>'
    out+=f'<rect x="8" y="8" width="{w-16}" height="{h-16}" fill="url(#shade)"/><rect x="8" y="8" width="{w-16}" height="{h-16}" fill="url(#bottomShade)"/>'
    x=26 if mobile else 32
    out+=text(x,34 if mobile else 39,'PSTAR80 / FULL-STACK ENGINEERING',9.6 if mobile else 11.2,'#B4DDF2',600,extra='letter-spacing="1.5"')
    name_y=82 if mobile else 105
    out+=f'<text x="{x}" y="{name_y}" font-size="{40 if mobile else 54}" fill="{WHITE}" font-weight="700" opacity=".97">Paul <tspan fill="{CYAN}">Sattaur</tspan></text>'
    out+=text(x,115 if mobile else 145,'Full-Stack Applications',20 if mobile else 25,WHITE,600,extra='opacity=".94"')
    out+=text(x,144 if mobile else 180,'Agentic AI & Automation',18.5 if mobile else 23,'#B7D9EF',400,extra='opacity=".93"')
    for i,label in enumerate(LABELS):
        bx=(26+(i%2)*218) if mobile else 32+i*226
        by=(242+(i//2)*40) if mobile else 265
        bw=208 if mobile else 216
        out+=f'<rect x="{bx}" y="{by}" width="{bw}" height="30" fill="#041724" fill-opacity=".74" stroke="#28758F" stroke-opacity=".9"/>'
        out+=text(bx+bw/2,by+20,label,12.4 if mobile else 13.8,CYAN,600,'middle')
    out+=frame(0,0,w,h,False)
    return shell(w,h,'Paul Sattaur — full-stack applications and agentic AI',HERO_ALT,out)

def get_tiles(source):
    children=list(ET.fromstring(source));tiles=[]
    for i,node in enumerate(children):
        if node.tag==f'{{{NS}}}rect' and node.get('stroke')=='#173E54' and node.get('height')=='70':
            inner=[]
            for child in children[i+1:]:
                if child.tag==f'{{{NS}}}rect': break
                if child.tag in (f'{{{NS}}}g',f'{{{NS}}}text'):
                    item=copy.deepcopy(child)
                    if item.tag==f'{{{NS}}}text' and item.get('font-weight')=='600': item.set('font-size','16')
                    inner.append(ET.tostring(item,encoding='unicode'))
            tiles.append((float(node.get('x')),float(node.get('y')),inner))
    if len(tiles)!=12: raise ValueError(f'Expected 12 unchanged technology tiles; got {len(tiles)}')
    return tiles

def overview(tiles,mobile):
    w=480 if mobile else 960; cw=480 if mobile else 472; h=1056 if mobile else 520
    out=frame(0,0,cw,520)
    out+='<g transform="translate(26 23)" fill="none" stroke="#25D6FF" stroke-width="1.6"><circle cx="12" cy="7" r="4"/><path d="M3 23v-3c0-7 18-7 18 0v3"/></g>'
    out+=text(63,43,'About Me',25,WHITE,650)+f'<path d="M26 62H{cw-26}" stroke="#22485C"/>'
    out+=text(26,98,'Full-stack systems. Built to connect.',21,WHITE,600)
    for y,line in ABOUT_LINES: out+=text(26,y,line)
    out+=f'<path d="M26 470H{cw-26}" stroke="#22485C"/>'
    out+=text(26,497,'Toronto, Canada · Full-stack engineering',16,'#87A9C2')
    fx,fy=(0,536) if mobile else (488,0)
    out+=frame(fx,fy,cw,520)
    out+=f'<g transform="translate({fx+26} {fy+23})" fill="none" stroke="#25D6FF" stroke-width="1.6"><path d="M2 7l10-5 10 5-10 5zM2 12l10 5 10-5M2 17l10 5 10-5"/></g>'
    out+=text(fx+63,fy+43,'Tech Stack',25,WHITE,650)+f'<path d="M{fx+26} {fy+62}H{fx+cw-26}" stroke="#22485C"/>'
    out+=text(fx+26,fy+95,'End-to-end application toolkit',18,MUTED)
    tw=(cw-52-18)/4
    for i,(ox,oy,inner) in enumerate(tiles):
        nx=fx+26+(i%4)*(tw+6); ny=fy+112+(i//4)*116
        out+=f'<rect x="{nx}" y="{ny}" width="{tw}" height="100" fill="#071A29" stroke="#173E54"/>'
        out+=f'<g transform="translate({nx-ox+(tw-101)/2:.3f} {ny-oy+14:.3f})">'+''.join(inner)+'</g>'
    out+=f'<path d="M{fx+26} {fy+470}H{fx+cw-26}" stroke="#22485C"/>'
    out+=text(fx+26,fy+497,'User interfaces · APIs · Data · Operations',16,'#87A9C2')
    return shell(w,h,'Full-stack engineering — about me and technology stack',ABOUT_ALT,out)

def update_readme(s):
    for name,alt in (('hero',HERO_ALT),('overview',ABOUT_ALT)):
        pattern=rf'(<img src="\./assets/profile/{name}\.svg"[^>]*\balt=")[^"]*(")'
        s,n=re.subn(pattern,lambda m:m.group(1)+html.escape(alt,quote=True)+m.group(2),s)
        if n!=1: raise ValueError(f'Expected one {name} image')
    a=s.index('### About me\n');b=s.index('### Selected work\n',a)
    return s[:a]+'### About me\n\n'+ABOUT_MARKDOWN+s[b:]

def main():
    assets=ROOT/'assets'/'profile'
    sources={n:(assets/n).read_text(encoding='utf-8') for n in ('hero.svg','hero-mobile.svg','overview.svg','overview-mobile.svg')}
    if all(f'data-intro="{VERSION}"' in s for s in sources.values()):
        print('Introduction already updated.');return
    href=art_href(sources['hero.svg'])
    if art_href(sources['hero-mobile.svg'])!=href: raise ValueError('Desktop/mobile art differs; inspect before updating')
    tiles=get_tiles(sources['overview.svg'])
    outputs={}
    for mobile,suffix in ((False,''),(True,'-mobile')):
        outputs[assets/f'hero{suffix}.svg']=hero(href,mobile)
        outputs[assets/f'overview{suffix}.svg']=overview(tiles,mobile)
    readme=ROOT/'README.md';outputs[readme]=update_readme(readme.read_text(encoding='utf-8'))
    for path,content in outputs.items():
        if path.suffix=='.svg':
            ET.fromstring(content)
            if path.stem.startswith('hero') and art_href(content)!=href: raise ValueError('Artwork changed unexpectedly')
    for path,content in outputs.items(): path.write_text(content,encoding='utf-8')
    print('Updated four introduction graphics and README; embedded artwork unchanged.')

if __name__=='__main__': main()
