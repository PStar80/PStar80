#!/usr/bin/env python3
"""Generate an aggregate-only blue GitHub contribution calendar.

Uses the job's built-in GITHUB_TOKEN; never asks for private repo permissions.
No repository names, commit messages, credentials or personal events are queried.
On API/validation failure, exit nonzero so the previous published cards survive.
"""
from __future__ import annotations
import calendar
import html
import json
import os
import re
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path

COLORS=['#0B2030','#103E62','#1269A0','#109ED9','#25D6FF']
LEVELS=['NONE','FIRST_QUARTILE','SECOND_QUARTILE','THIRD_QUARTILE','FOURTH_QUARTILE']
QUERY='''query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{totalContributions weeks{firstDay contributionDays{date weekday contributionCount contributionLevel}}}}}}'''


def fetch_calendar(username: str) -> dict:
    token=os.environ.get('GH_TOKEN','').strip()
    if not token: raise RuntimeError('GH_TOKEN is required; use the built-in Actions token.')
    payload=json.dumps({'query':QUERY,'variables':{'login':username}}).encode()
    req=urllib.request.Request('https://api.github.com/graphql',data=payload,headers={'Authorization':f'Bearer {token}','Content-Type':'application/json','Accept':'application/vnd.github+json','User-Agent':'PStar80-blue-profile-activity'})
    with urllib.request.urlopen(req,timeout=40) as response:
        result=json.load(response)
    if result.get('errors'): raise RuntimeError('GitHub contribution query failed; previous published card is unchanged.')
    user=result.get('data',{}).get('user')
    if not user: raise RuntimeError('GitHub user not returned.')
    return user['contributionsCollection']['contributionCalendar']


def validate(data: dict) -> list[dict]:
    weeks=data.get('weeks')
    if not isinstance(weeks,list) or not 51<=len(weeks)<=54: raise ValueError('Unexpected calendar week count')
    days=[]
    for week in weeks:
        date.fromisoformat(week['firstDay'])
        for d in week['contributionDays']:
            dt=date.fromisoformat(d['date'])
            if type(d['contributionCount']) is not int or d['contributionCount']<0: raise ValueError('Invalid count')
            if d['contributionLevel'] not in LEVELS: raise ValueError('Unknown activity intensity')
            if d['weekday'] != (dt.weekday()+1)%7: raise ValueError('Weekday mismatch')
            if not 0<=(dt-date.fromisoformat(week['firstDay'])).days<7: raise ValueError('Day outside week')
            days.append(d)
    if not 360<=len(days)<=367: raise ValueError('Unexpected calendar date range')
    dates=[date.fromisoformat(d['date']) for d in days]
    if len(set(dates))!=len(dates): raise ValueError('Duplicate dates')
    if dates != sorted(dates): raise ValueError('Dates not ordered')
    if (dates[-1]-dates[0]).days+1!=len(dates): raise ValueError('Missing days')
    if sum(d['contributionCount'] for d in days)!=data['totalContributions']: raise ValueError('Calendar total mismatch')
    return days


def text(x,y,value,size=18,fill='#A4BDCF',weight=400,anchor='start'):
    return f'<text x="{x}" y="{y}" font-family="Segoe UI,Arial,sans-serif" font-size="{size}" fill="{fill}" font-weight="{weight}" text-anchor="{anchor}">{html.escape(str(value))}</text>'


def shell(w,h,body,desc):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">
<title id="title">Engineering Activity — PStar80</title><desc id="desc">{html.escape(desc)}</desc>
<defs><linearGradient id="surface" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#06111C"/><stop offset="1" stop-color="#020A12"/></linearGradient><linearGradient id="metal" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#D8E7EE"/><stop offset=".23" stop-color="#3C596D"/><stop offset=".5" stop-color="#91ACBF"/><stop offset=".72" stop-color="#E3F4FF"/><stop offset="1" stop-color="#365569"/></linearGradient><pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse"><path d="M24 0H0V24" fill="none" stroke="#40BCFF" stroke-opacity=".04"/></pattern></defs>
<style>.edge{{animation:edge 28s linear infinite}}@keyframes edge{{to{{stroke-dashoffset:-100}}}}@media(prefers-reduced-motion:reduce){{.edge{{animation:none!important}}}}</style>
<rect x="2" y="2" width="{w-4}" height="{h-4}" fill="url(#surface)" stroke="url(#metal)" stroke-width="2"/><rect x="7" y="7" width="{w-14}" height="{h-14}" fill="url(#grid)" stroke="#163349"/>
<path d="M2 2H{w-2}V{h-2}H2Z" pathLength="100" fill="none" stroke="#25D6FF" opacity=".65" stroke-width="1.6" stroke-dasharray="7 93" class="edge"/>
{body}
</svg>'''


def grid(weeks,x,y,step=16,cell=12,labels=True):
    b=''; last_month=None; last_label=-100
    for i,week in enumerate(weeks):
        first=date.fromisoformat(week['contributionDays'][0]['date'])
        month=first.month
        if labels and month!=last_month:
            if i-last_label>=3:
                b+=text(x+i*step,y-13,calendar.month_abbr[month],14,'#A4BDCF')
                last_label=i
            last_month=month
        for d in week['contributionDays']:
            c=COLORS[LEVELS.index(d['contributionLevel'])]
            count=d['contributionCount']; title=f"{d['date']}: {count} contribution{'s' if count!=1 else ''}"
            b+=f'<rect x="{x+i*step}" y="{y+d["weekday"]*step}" width="{cell}" height="{cell}" fill="{c}" stroke="#234154" stroke-width=".5"><title>{title}</title></rect>'
    for row,label in ((1,'M'),(3,'W'),(5,'F')):
        b+=text(x-15,y+row*step+cell-1,label,12,'#7091AA',anchor='end')
    return b


def render(data,days,updated,mobile=False):
    w,h=(480,484) if mobile else (960,330)
    total=sum(d['contributionCount'] for d in days); active=sum(d['contributionCount']>0 for d in days)
    start,end=days[0]['date'],days[-1]['date']
    b=text(27,44,'Engineering Activity',26,'#F0F7FC',650)
    if mobile:
        b+=text(27,72,f'Updated {updated} UTC',14)
        b+=text(27,107,f'{total:,} contributions',23,'#25D6FF',600)
        b+=text(27,131,f'{active} active days · last 12 months',17)
        b+=grid(data['weeks'][:27],51,165,15,11)
        b+=grid(data['weeks'][27:],51,309,15,11)
        b+=text(27,443,'Less',14)
        for i,c in enumerate(COLORS): b+=f'<rect x="{63+i*17}" y="432" width="12" height="12" fill="{c}" stroke="#234154"/>'
        b+=text(151,443,'More',14)
        b+=text(27,467,'GitHub-reported counts · no repository details',15)
    else:
        b+=text(932,43,f'Updated {updated} UTC',14,anchor='end')
        b+='<path d="M26 62H934" stroke="#22485C"/>'
        b+=text(27,96,f'{total:,} contributions',24,'#25D6FF',600)
        b+=text(327,96,f'{active} active days',20,'#F0F7FC',500)
        b+=text(933,96,f'{start} — {end}',15,anchor='end')
        step=min(16,864/len(data['weeks']))
        b+=grid(data['weeks'],54,145,step,12)
        b+=text(27,284,'GitHub-reported counts · no repository details',16)
        b+=text(757,284,'Less',14)
        for i,c in enumerate(COLORS): b+=f'<rect x="{798+i*17}" y="273" width="12" height="12" fill="{c}" stroke="#234154"/>'
        b+=text(888,284,'More',14)
        b+=text(27,310,'Daily refresh · activity totals depend on GitHub visibility.',15,'#7091AA')
    desc=f'{total:,} GitHub-reported contributions on {active} days from {start} to {end}. Updated {updated} UTC. Counts visible to the GitHub Actions token may differ from the native profile calendar. No private repository details are requested or shown.'
    return shell(w,h,b,desc)


def write_assets(data:dict,output:Path,updated:str|None=None):
    days=validate(data)
    stamp=updated or datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')
    output.mkdir(parents=True,exist_ok=True)
    for mobile in (False,True):
        name='engineering-activity-mobile.svg' if mobile else 'engineering-activity.svg'
        (output/name).write_text(render(data,days,stamp,mobile),encoding='utf-8')
    summary={'source':'GitHub GraphQL contributionCalendar','scope':'Aggregate counts returned to the built-in repository Actions token; may differ from native profile. No repository details queried.','updated_utc':stamp,'from':days[0]['date'],'through':days[-1]['date'],'total_contributions':sum(d['contributionCount'] for d in days),'active_days':sum(d['contributionCount']>0 for d in days),'calendar_days':len(days),'weeks':len(data['weeks'])}
    (output/'engineering-activity.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary))


def main():
    username=os.environ.get('PROFILE_USER') or os.environ.get('GITHUB_REPOSITORY_OWNER')
    if not username or not re.fullmatch(r'[A-Za-z0-9-]{1,39}',username): raise ValueError('Invalid PROFILE_USER')
    write_assets(fetch_calendar(username),Path(os.environ.get('OUTPUT_DIR','dist')))

if __name__=='__main__': main()
