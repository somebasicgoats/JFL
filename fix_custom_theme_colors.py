#!/usr/bin/env python3
"""Correct the JFL custom theme color mapping in the current repository's index.html.
Run from the repository root: python fix_custom_theme_colors.py
"""
from pathlib import Path
import sys

p = Path('index.html')
if not p.exists():
    sys.exit('ERROR: index.html not found. Run this from the JFL repository root.')
s = p.read_text(encoding='utf-8')
old = '''function applyCustomTheme(){
 const root=document.documentElement;
 root.style.setProperty("--ac",userTheme.primary);
 root.style.setProperty("--ac2",userTheme.secondary);
 root.style.setProperty("--ac3",userTheme.tertiary);
 root.style.setProperty("--menu-active",userTheme.secondary);
}'''
new = '''function applyCustomTheme(){
 const root=document.documentElement;
 // Primary controls the page background; secondary controls surfaces/cards;
 // tertiary controls the normal text color.
 root.style.setProperty("--bg",userTheme.primary);
 root.style.setProperty("--card",userTheme.secondary);
 root.style.setProperty("--card2",userTheme.secondary);
 root.style.setProperty("--tx",userTheme.tertiary);
 root.style.setProperty("--mut",userTheme.tertiary);
}'''
if s.count(old) != 1:
    sys.exit(f'ERROR: Expected one existing applyCustomTheme() block; found {s.count(old)}. No file written.')
s = s.replace(old, new, 1)
old_reset = 'else ["--ac","--ac2","--ac3","--menu-active"].forEach(k=>document.documentElement.style.removeProperty(k));'
new_reset = 'else ["--bg","--card","--card2","--tx","--mut"].forEach(k=>document.documentElement.style.removeProperty(k));'
if s.count(old_reset) != 1:
    sys.exit(f'ERROR: Expected one custom theme reset block; found {s.count(old_reset)}. No file written.')
s = s.replace(old_reset, new_reset, 1)
old_css = '''html[data-theme="custom"]{color-scheme:dark}
html[data-theme="custom"] :is(.btn:not(.ghost),.seg button.on,.switches button.on){background:var(--ac2);border-color:var(--ac);color:#fff}
html[data-theme="custom"] :is(h1,h2,.home-heading h2,.sport-table th){color:var(--ac3)}
html[data-theme="custom"] :is(input,textarea,select):focus-visible{outline:2px solid var(--ac);outline-offset:2px}
html[data-theme="custom"] ::selection{background:var(--ac2);color:#fff}'''
new_css = '''html[data-theme="custom"]{color-scheme:dark}
html[data-theme="custom"] body{background:var(--bg)!important;background-image:none!important}
html[data-theme="custom"] body:before{display:none}
html[data-theme="custom"] aside{background:var(--card)!important}
html[data-theme="custom"] :is(.card,.stat,.chip){background:var(--card2)!important}
html[data-theme="custom"] :is(.btn:not(.ghost),.seg button.on,.switches button.on){background:var(--card2);border-color:var(--bd);color:var(--tx)}
html[data-theme="custom"] :is(h1,h2,.home-heading h2,.sport-table th){color:var(--tx)}
html[data-theme="custom"] :is(input,textarea,select):focus-visible{outline:2px solid var(--tx);outline-offset:2px}
html[data-theme="custom"] ::selection{background:var(--card2);color:var(--tx)}'''
if s.count(old_css) != 1:
    sys.exit(f'ERROR: Expected one existing custom-theme CSS block; found {s.count(old_css)}. No file written.')
s = s.replace(old_css, new_css, 1)
p.write_text(s, encoding='utf-8')
print('Updated custom theme mapping in index.html: primary=page background, secondary=cards/boxes, tertiary=text.')
