#!/usr/bin/env python3
"""One-time profile layout update; no application-source changes."""
from __future__ import annotations
import html
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path.cwd()
WHITE, CYAN, MUTED, DIM = '#F0F7FC', '#25D6FF', '#A4BDCF', '#7091AA'
DESCRIPTION = 'Data engineering workbench for governed analytical products, with metadata, pipelines, dbt transformations, data quality and lineage.'
DEFS = '''<defs>
<linearGradient id="surface" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#06111C"/><stop offset=".55" stop-color="#07131F"/><stop offset="1" stop-color="#020A12"/></linearGradient>
<linearGradient id="metal" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#D8E7EE"/><stop offset=".10" stop-color="#3C596D"/><stop offset=".26" stop-color="#9DB5C4"/><stop offset=".42" stop-color="#1F3547"/><stop offset=".57" stop-color="#6B96B1"/><stop offset=".72" stop-color="#E3F4FF"/><stop offset=".84" stop-color="#365569"/><stop offset="1" stop-color="#91ACBF"/></linearGradient>
<linearGradient id="accent"><stop stop-color="#25D6FF"/><stop offset="1" stop-color="#148CFF" stop-opacity="0"/></linearGradient>
<pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse"><path d="M24 0H0V24" fill="none" stroke="#40BCFF" stroke-opacity=".055"/></pattern>
<marker id="arrow" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="5" markerHeight="5" orient="auto"><path d="M1 1L7 4L1 7" fill="none" stroke="#8CDCF0" stroke-width="1.2"/></marker>
</defs>'''
STYLE = '''<style>
.sweep{opacity:.55;animation:sweep 26s linear infinite}
.spark{opacity:.70;animation:sweep 26s linear infinite}
.route-main{animation:flow 8s linear infinite}
.route-agent{opacity:.25;animation:agent 14s ease-in-out infinite}
@keyframes sweep{to{stroke-dashoffset:-100}}
@keyframes flow{to{stroke-dashoffset:-100}}
@keyframes agent{0%,45%,90%,100%{opacity:.22}60%,75%{opacity:.8}}
@media(prefers-reduced-motion:reduce){.sweep,.spark,.route-main,.route-agent{animation:none!important}.route-agent{opacity:.45}}
</style>'''
ICONS = {
 'bolt':'<path d="M14 1L3 14h8l-1 9 11-14h-8z"/>',
 'chart':'<path d="M2 2v20h21M6 18v-5m5 5V9m5 9V4m5 14V7"/>',
 'db':'<ellipse cx="12" cy="5" rx="9" ry="4"/><path d="M3 5v14c0 5 18 5 18 0V5M3 12c0 5 18 5 18 0"/>',
 'clock':'<circle cx="12" cy="12" r="10"/><path d="M12 5v8l5 3"/>',
 'agent':'<rect x="3" y="6" width="18" height="15" rx="3"/><path d="M12 6V2m-4 10v3m8-3v3M8 18h8M0 11h3m18 0h3"/>',
 'pulse':'<path d="M1 13h5l3-9 5 17 3-8h6"/>',
 'git':'<circle cx="6" cy="4" r="3"/><circle cx="6" cy="21" r="3"/><circle cx="19" cy="7" r="3"/><path d="M6 7v11m13-8c0 6-13 4-13 8"/>',
 'docker':'<path d="M2 13h20c-1 9-17 10-20 0zM4 8h4v4H4zm5 0h4v4H9zm5 0h4v4h-4zm-5-5h4v4H9zm12 5l2 4 3-2"/>',
 'code':'<path d="M7 5L1 12l6 7M17 5l6 7-6 7M14 3l-4 18"/>'}

def txt(x,y,s,size=18,color=WHITE,weight=400,anchor='start'):
    return f'<text x="{x:g}" y="{y:g}" font-size="{size:g}" fill="{color}" font-weight="{weight}" text-anchor="{anchor}">{html.escape(s)}</text>'

def rect(x,y,w,h,fill='#071A29',stroke='#26718A',sw=1):
    return f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:g}"/>'

def line(x1,y1,x2,y2,color='#22485C'):
    return f'<path d="M{x1:g} {y1:g}H{x2:g}" stroke="{color}"/>' if y1==y2 else f'<path d="M{x1:g} {y1:g}L{x2:g} {y2:g}" stroke="{color}"/>'

def icon(name,x,y,size=25):
    return f'<g transform="translate({x:g} {y:g}) scale({size/24:g})" fill="none" stroke="{CYAN}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</g>'

def frame(x,y,w,h,delay=0):
    s=rect(x+2,y+2,w-4,h-4,'url(#surface)','url(#metal)',2)+rect(x+7,y+7,w-14,h-14,'url(#grid)','#163349')
    d=f'M{x+2:g} {y+2:g}H{x+w-2:g}V{y+h-2:g}H{x+2:g}Z'
    for cls,col,sw,dash,op,offset in [('sweep',CYAN,1.5,'6 94',.55,0),('spark','#E6FAFF',1.5,'1.2 98.8',.7,.1)]:
        s+=f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{sw}" opacity="{op}" pathLength="100" stroke-dasharray="{dash}" class="{cls}" style="animation-delay:-{delay+offset:g}s"/>'
    for xx,yy,dx,dy in ((x+9,y+9,1,1),(x+w-9,y+9,-1,1),(x+9,y+h-9,1,-1),(x+w-9,y+h-9,-1,-1)):
        s+=f'<path d="M{xx+12*dx:g} {yy:g}H{xx:g}V{yy+12*dy:g}" fill="none" stroke="#A9C9DD" opacity=".65"/>'
    return s

def heading(x,y,w,title,ico=None):
    s=icon(ico,x+25,y+22) if ico else ''
    s+=txt(x+(63 if ico else 26),y+43,title,25,WHITE,650)
    s+=line(x+25,y+62,x+w-25,y+62)
    s+=rect(x+25,y+61,70,2,'url(#accent)','none',0)
    return s

def shell(w,h,title,desc,body):
    s=f'<svg xmlns="http://www.w3.org/2000/svg" font-family="Segoe UI,Arial,sans-serif" data-profile-refinement="2" data-profile-layout="3" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">\n<title id="title">{html.escape(title)}</title><desc id="desc">{html.escape(desc)}</desc>\n{DEFS}\n{STYLE}\n{body}\n</svg>\n'
    ET.fromstring(s)
    return s

def route(d,agent=False):
    s=f'<path d="{d}" fill="none" stroke="#26718A" stroke-width="1.2" marker-end="url(#arrow)"/>'
    return s+f'<path d="{d}" fill="none" stroke="{CYAN}" stroke-width="1.6" pathLength="100" stroke-dasharray="8 92" opacity=".65" class="{"route-agent" if agent else "route-main"}"/>'

def node(x,y,w,h,title,sub,ts=20,ss=17):
    return rect(x,y,w,h)+txt(x+w/2,y+25,title,ts,WHITE,600,'middle')+txt(x+w/2,y+48,sub,ss,MUTED,400,'middle')

def systems(mobile=False):
    w,h=(480,528) if mobile else (960,520)
    s=frame(0,0,w,h)+heading(0,0,w,'System Architecture')+txt(26,89,'Two agent paths · shared platform services',17,MUTED)
    ox,ow,ex,ew,ax,aw,tx,tw,wx,ww,bx,bw=(26,132,170,284,90,300,26,204,250,204,26,428) if mobile else (60,240,470,430,310,340,80,340,540,340,190,580)
    oc,ec,ac,tc,wc,bc=ox+ow/2,ex+ew/2,ax+aw/2,tx+tw/2,wx+ww/2,bx+bw/2
    for d in (f'M{oc} 170V184H{ac}V198',f'M{ec} 170V184H{ac}V198',f'M{ac} 252V268H{tc}V282',f'M{ac} 252V268H{wc}V282'):
        s+=route(d)
    s+=route(f'M{wc} 336V352H{bc}V368',True)+route(f'M{bx} 403H{16 if mobile else 32}V225H{ax}',True)
    s+=node(ox,108,ow,62,'Operator','React UI')+node(ex,108,ew,62,'External coding agents','External MCP connection',19 if mobile else 20)
    s+=node(ax,198,aw,54,'Node.js Core API','Registered platform services',20,16)
    s+=node(tx,282,tw,54,'Registered Tools','Normal execution contracts',18.5,14.8 if mobile else 17)
    s+=node(wx,282,ww,54,'Published Workflows','Temporal · deterministic',18 if mobile else 20,16 if mobile else 17)
    s+=rect(bx,368,bw,70)
    s+=txt(bc,396,'Embedded Agent Run → run-bound MCP',18.5 if mobile else 20,WHITE,600,'middle')
    s+=txt(bc,423,'Optional node · Project + Agent-version capabilities',15.3 if mobile else 17,MUTED,400,'middle')
    s+=line(26,451,w-26,451)+txt(26,477,'PostgreSQL · workflow / run state and results',17.5 if mobile else 18,CYAN,500)
    s+=txt(26,507 if mobile else 505,'Conceptual flow · configured permissions apply',16,MUTED)
    return shell(w,h,'SkyCommand system architecture','Full-width conceptual architecture. React UI and external coding agents through MCP use shared platform services. Temporal workflows can invoke embedded agents with run-bound MCP and configured Project and Agent-version capabilities. The connections and meanings are unchanged; this is not live telemetry.',s)

def featured(x,y,w,h,mobile=False):
    s=frame(x,y,w,h,5)+heading(x,y,w,'Featured: SkyCommand','bolt')
    s+=txt(x+26,y+99,'Workflow automation + optional AI agents',17.5,MUTED)
    s+=txt(x+26,y+128,'Independent platform · source kept private',16.4,DIM)
    cols=2 if mobile else 3
    start,step,th=(160,82,70) if mobile else (166,120,98)
    gap=12;tw=(w-52-(cols-1)*gap)/cols
    items=[('clock','Durable workflows'),('agent','Optional AI agents'),('pulse','Run diagnostics'),('git','Scoped Git delivery'),('docker','Docker operations'),('code','Structured results')]
    for i,(ico,label) in enumerate(items):
        xx=x+26+(i%cols)*(tw+gap);yy=y+start+(i//cols)*step
        s+=rect(xx,yy,tw,th,'#071B2A','#21465E')+icon(ico,xx+12,yy+12,23 if not mobile else 20)
        s+=txt(xx+12,yy+th-16,label,16.4 if not mobile else 17,WHITE,500)
    if mobile:
        s+=txt(x+26,y+446,'Temporal · Node.js · React',17,CYAN)+txt(x+26,y+470,'PostgreSQL · Docker',17,CYAN)+txt(x+26,y+503,'Architecture and walkthroughs on request.',16.4,MUTED)
    else:
        s+=txt(x+26,y+432,'Temporal · Node.js · React · PostgreSQL · Docker',17,CYAN)
        s+=txt(x+26,y+465,'Architecture and walkthroughs on request.',17,MUTED)
    return s

def focus(x,y,w,h):
    s=frame(x,y,w,h,2)+heading(x,y,w,'Current Focus')
    for yy,content,size,color,weight in [(104,'MCP-enabled coding',20,WHITE,600),(131,'Coding assistants use SkyCommand',16.5,MUTED,400),(180,'Embedded-agent access',20,WHITE,600),(207,'Project + Agent-version scope',17,MUTED,400),(230,'Assigned and direct capabilities',16.5,MUTED,400),(284,'Work-order coordination',21,WHITE,600),(313,'Current development method',17,CYAN,500),(344,'Scoped streams and handoffs',17.5,MUTED,400),(371,'Roles, dependencies and evidence',16.7,MUTED,400),(455,'Native work-order management',17.8,WHITE,600),(483,"Built on today's operating model",16.5,MUTED,400)]:
        s+=txt(x+26,y+yy,content,size,color,weight)
    s+=line(x+26,y+251,x+w-26,y+251)+rect(x+26,y+394,226,28)+txt(x+36,y+414,'PHASE 20 · PLANNED',16,CYAN,600)
    return s

def projects(mobile=False):
    if mobile:w,h=480,1066;s=featured(0,0,480,540,True)+focus(0,558,480,508)
    else:w,h=960,508;s=featured(0,0,604,508)+focus(620,0,340,508)
    return shell(w,h,'Featured SkyCommand and current focus','SkyCommand, the private-source workflow platform, beside Current Focus: MCP-enabled coding, embedded-agent capability scope and current work-order coordination. Native work-order management remains planned for Phase 20.',s)

def portfolio_card(x,y,w,kind):
    s=frame(x,y,w,362,8 if kind=='studio' else 14)+heading(x,y,w,'SkyDataStudio' if kind=='studio' else 'MacroAnalyzer','db' if kind=='studio' else 'chart')
    s+=rect(x+26,y+80,150,28,'#071C2A','#23617C')+txt(x+101,y+99,'PUBLIC PROJECT',13,CYAN,600,'middle')
    lines=['Data engineering workbench for','governed analytical products.','Pipelines, quality and lineage.'] if kind=='studio' else ['Macroeconomic analytics','Dashboards, alerts and','historical time-series views.']
    for i,t in enumerate(lines):s+=txt(x+26,y+143+27*i,t,20,MUTED)
    xx,yy,ww=x+26,y+216,w-52
    s+=rect(xx,yy,ww,57,'#061C2A','#21465E')
    if kind=='studio':
        boxw=100;gap=(ww-3*boxw)/2
        for i,label in enumerate(('Prepare','Transform','Publish')):
            bx=xx+i*(boxw+gap)
            s+=rect(bx+5,yy+12,boxw-10,33,'#071A29','#26718A')+txt(bx+boxw/2,yy+34,label,15,CYAN,500,'middle')
            if i<2:s+=line(bx+boxw-5,yy+28,bx+boxw+gap+5,yy+28,'#26718A')
        stack=['Python · FastAPI · PostgreSQL','Airflow · dbt · Docker']
    else:
        points=[(0,.72),(.09,.49),(.18,.64),(.28,.21),(.36,.47),(.46,.34),(.54,.51),(.65,.14),(.74,.29),(.84,.09),(.95,.20)]
        d='M'+'L'.join(f'{xx+12+a*(ww-24):g} {yy+8+b*40:g}' for a,b in points)
        s+=f'<path d="{d}" fill="none" stroke="{CYAN}" stroke-width="1.8"/>'
        stack=['React · ASP.NET Core / C#','PostgreSQL · REST APIs · ECharts']
    s+=txt(x+26,y+309,stack[0],18,WHITE,600)+txt(x+26,y+337,stack[1],17,MUTED)
    return s

def portfolio(mobile=False):
    if mobile:w,h=480,742;s=portfolio_card(0,0,480,'studio')+portfolio_card(0,380,480,'macro')
    else:w,h=960,362;s=portfolio_card(0,0,471,'studio')+portfolio_card(489,0,471,'macro')
    return shell(w,h,'SkyDataStudio and MacroAnalyzer','Two equally sized public-project cards: SkyDataStudio on the left, MacroAnalyzer on the right. SkyDataStudio is a data engineering workbench with metadata, pipelines, dbt transformations, quality and lineage. MacroAnalyzer provides macroeconomic dashboards, alerts and time-series analytics.',s)

def picture(base,alt):
    return f'''<p>
<picture>
  <source media="(prefers-reduced-motion: reduce) and (max-width: 650px)" srcset="./assets/static/{base}-mobile.svg" />
  <source media="(prefers-reduced-motion: reduce)" srcset="./assets/static/{base}.svg" />
  <source media="(max-width: 650px)" srcset="./assets/profile/{base}-mobile.svg" />
  <img src="./assets/profile/{base}.svg" width="100%" alt="{html.escape(alt,quote=True)}" />
</picture>
</p>'''

def patch_readme(s):
    pat=r'<p>\s*<picture>\s*<source[^>]*srcset="\./assets/static/projects-mobile\.svg".*?</picture>\s*</p>'
    replacement=picture('projects','Featured SkyCommand alongside Current Focus: durable workflows, optional AI agents, MCP-enabled coding, configured embedded-agent capabilities and work-order coordination. Native work-order integration is planned for Phase 20.')
    s,n=re.subn(pat,lambda m:replacement,s,flags=re.S);assert n==1,'Expected one featured row'
    old='''<p align="center">
  <a href="https://github.com/PStar80/MacroAnalyzer"><strong>MacroAnalyzer source</strong></a> ·
  <a href="https://github.com/PStar80/SkyCommand-Demo"><strong>Explore SkyCommand</strong></a> ·
  <a href="mailto:paulsattaur@hotmail.com?subject=SkyCommand%20walkthrough"><strong>Request a walkthrough</strong></a>
</p>'''
    new='''<p align="center">
  <a href="https://github.com/PStar80/SkyCommand-Demo"><strong>Explore SkyCommand</strong></a> ·
  <a href="mailto:paulsattaur@hotmail.com?subject=SkyCommand%20walkthrough"><strong>Request a walkthrough</strong></a>
</p>

'''+picture('portfolio','Public projects: SkyDataStudio on the left, MacroAnalyzer on the right. SkyDataStudio is a data engineering workbench for governed analytical products, with metadata, pipelines, dbt transformations, data quality and lineage. MacroAnalyzer is a React and ASP.NET Core/C# macroeconomic analytics application with PostgreSQL, dashboards, alerts and historical time-series views.')+'''

<p align="center">
  <a href="https://github.com/PStar80/SkyDataStudio"><strong>SkyDataStudio source</strong></a> ·
  <a href="https://github.com/PStar80/MacroAnalyzer"><strong>MacroAnalyzer source</strong></a>
</p>'''
    assert s.count(old)==1,'Expected original project links'
    s=s.replace(old,new)
    old='An additional public project in my development ecosystem. The repository is the source of truth for its current scope and implementation.'
    assert old in s,'Expected prior SkyDataStudio description'
    s=s.replace(old,DESCRIPTION+' It prepares trusted ingested data for analytical consumption, using Python/FastAPI, PostgreSQL, Airflow, dbt and Docker.')
    return s

def write_assets(root):
    for base,fun in [('systems',systems),('projects',projects),('portfolio',portfolio)]:
        for mobile in (False,True):
            name=base+('-mobile' if mobile else '')+'.svg'
            target=root/'assets'/'profile'/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(fun(mobile),encoding='utf-8')

def main():
    readme=ROOT/'README.md';new_readme=patch_readme(readme.read_text(encoding='utf-8'))
    static=ROOT/'scripts'/'create_static_assets.py';st=static.read_text(encoding='utf-8')
    anchor="BASES=('hero','overview','systems','projects','connect','linkedin','github','email')"
    assert anchor in st,'Unexpected static-generator layout'
    st=st.replace(anchor,"BASES=('hero','overview','systems','projects','portfolio','connect','linkedin','github','email')").replace('Generated 16 profile','Generated 18 profile')
    write_assets(ROOT)
    readme.write_text(new_readme,encoding='utf-8');static.write_text(st,encoding='utf-8')
    print('Reflowed 6 SVGs; updated README and still-image generator. No application source changed.')

if __name__=='__main__':main()
