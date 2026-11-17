#!/usr/bin/env python3
"""Create explicit still-image sources for README reduced-motion picture elements."""
from __future__ import annotations
import os
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
BASES=('hero','overview','systems','projects','portfolio','connect','linkedin','github','email')
SVG='http://www.w3.org/2000/svg'
ET.register_namespace('',SVG)
ET.register_namespace('xlink','http://www.w3.org/1999/xlink')


def freeze(source:Path,target:Path)->None:
    root=ET.fromstring(source.read_text(encoding='utf-8'))
    for parent in list(root.iter()):
        for child in list(parent):
            if child.tag.rsplit('}',1)[-1] in ('style','animate','animateTransform','animateMotion','set'):
                parent.remove(child)
        # Existing inline styles contain only animation offsets.
        parent.attrib.pop('style',None)
        classes=parent.get('class','').split()
        if 'hub-halo' in classes: parent.set('opacity','.16')
        if 'route-agent' in classes: parent.set('opacity','.45')
        if 'sweep' in classes: parent.set('opacity','.45')
        if 'spark' in classes: parent.set('opacity','.6')
    root.set('data-motion','static')
    desc=root.find(f'{{{SVG}}}desc')
    if desc is not None: desc.text=(desc.text or '')+' Static reduced-motion version.'
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(ET.tostring(root,encoding='unicode')+'\n',encoding='utf-8')


def main()->None:
    for base in BASES:
        for suffix in ('','-mobile'):
            name=f'{base}{suffix}.svg'
            freeze(ROOT/'assets'/'profile'/name,ROOT/'assets'/'static'/name)
    output=Path(os.environ.get('OUTPUT_DIR','dist'))
    for suffix in ('','-mobile'):
        freeze(output/f'engineering-activity{suffix}.svg',output/f'engineering-activity{suffix}-static.svg')
    print('Generated 18 profile and 2 calendar still-image fallbacks.')

if __name__=='__main__': main()
