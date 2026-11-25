#!/usr/bin/env python3
"""Apply the account-based custom theme feature to the current JFL index.html.
Run from the repository root: python apply_custom_themes.py
The script is intentionally anchor-checked and refuses to patch unknown source layouts.
"""
from pathlib import Path
import sys

p = Path('index.html')
if not p.exists():
    sys.exit('ERROR: Run this script from the JFL repository root (index.html not found).')
s = p.read_text(encoding='utf-8')
if 'jfl_user_themes' in s and 'function bindCustomThemeEditor' in s:
    sys.exit('Custom theme feature already appears to be installed; no changes made.')

replacements = []

def replace_once(old, new, label):
    global s
    count = s.count(old)
    if count != 1:
        sys.exit(f'ERROR: Expected exactly one anchor for {label}; found {count}. No file written.')
    s = s.replace(old, new, 1)

replace_once(
    '<option value="blue">Blue · Navy &amp; Blue</option><option value="oled">OLED</option>',
    '<option value="blue">Blue · Navy &amp; Blue</option><option value="custom">Custom · My colors</option><option value="oled">OLED</option>',
    'theme selector option'
)

replace_once(
    'function setTheme(v){document.documentElement.dataset.theme=v;try{localStorage.setItem("jfl_theme",v)}catch{}}',
    '''let userTheme={primary:"#1688ed",secondary:"#102f55",tertiary:"#70c4ff"};
function applyCustomTheme(){
 const root=document.documentElement;
 root.style.setProperty("--ac",userTheme.primary);
 root.style.setProperty("--ac2",userTheme.secondary);
 root.style.setProperty("--ac3",userTheme.tertiary);
 root.style.setProperty("--menu-active",userTheme.secondary);
}
function setTheme(v){
 if(v==="custom"&&!ME){v="oled";toast(phrase("Sign in to use your saved custom theme.","Connecte-toi pour utiliser ton thème personnalisé."));}
 document.documentElement.dataset.theme=v;
 if(v==="custom")applyCustomTheme();
 else ["--ac","--ac2","--ac3","--menu-active"].forEach(k=>document.documentElement.style.removeProperty(k));
 try{localStorage.setItem("jfl_theme",v)}catch{}
}
async function loadUserTheme(){
 if(!ME){userTheme={primary:"#1688ed",secondary:"#102f55",tertiary:"#70c4ff"};return}
 const r=await sb.from("jfl_user_themes").select("primary_color,secondary_color,tertiary_color").eq("user_id",ME.id).maybeSingle();
 if(r.error){console.warn("Could not load custom theme",r.error);return}
 if(r.data)userTheme={primary:r.data.primary_color,secondary:r.data.secondary_color,tertiary:r.data.tertiary_color};
 if(document.documentElement.dataset.theme==="custom")applyCustomTheme();
}
async function saveUserTheme(){
 if(!ME)return toast(phrase("Sign in to save a personal theme.","Connecte-toi pour enregistrer un thème personnel."));
 const payload={user_id:ME.id,primary_color:userTheme.primary,secondary_color:userTheme.secondary,tertiary_color:userTheme.tertiary,updated_at:new Date().toISOString()};
 const r=await sb.from("jfl_user_themes").upsert(payload,{onConflict:"user_id"});
 if(r.error)return toast(dataError(r.error));
 setTheme("custom");toast(phrase("Your custom theme was saved to your account.","Ton thème personnalisé a été enregistré sur ton compte."));
}
function bindCustomThemeEditor(){
 ["primary","secondary","tertiary"].forEach(k=>{const el=$("theme-"+k);if(!el)return;el.value=userTheme[k];el.oninput=()=>{userTheme[k]=el.value;applyCustomTheme();const swatch=$("theme-preview-"+k);if(swatch)swatch.style.background=el.value;const code=$("theme-code-"+k);if(code)code.textContent=el.value.toUpperCase()}});
 const save=$("save-custom-theme");if(save)save.onclick=saveUserTheme;
 const preview=$("preview-custom-theme");if(preview)preview.onclick=()=>setTheme("custom");
}
''',
    'theme persistence function'
)

# Add the custom theme editor to the signed-in account view.
replace_once(
    "function acctView(){if(ME)return '<div class=\"card\"><h2>'+ic(\"user\",18)+' '+playerLink(ME.name)+'</h2><div class=\"sub\">'+(isAdmin?t(\"adminacc\"):t(\"playeracc\"))+'</div><button class=\"btn ghost\" id=\"lo\" style=\"margin-top:8px\">'+t(\"logout\")+'</button></div><div class=\"card\"><h2>'+t(\"chpw\")+'</h2>",
    "function acctView(){if(ME)return '<div class=\"card\"><h2>'+ic(\"user\",18)+' '+playerLink(ME.name)+'</h2><div class=\"sub\">'+(isAdmin?t(\"adminacc\"):t(\"playeracc\"))+'</div><button class=\"btn ghost\" id=\"lo\" style=\"margin-top:8px\">'+t(\"logout\")+'</button></div><div class=\"card\"><h2>'+phrase(\"Personal theme\",\"Thème personnel\")+'</h2><p class=\"hint\">'+phrase(\"Choose three colors. Changes preview immediately; save them to your account to use them on other devices.\",\"Choisis trois couleurs. L’aperçu change immédiatement; enregistre-les sur ton compte pour les retrouver sur tes autres appareils.\")+'</p><div class=\"grid\">'+[[\"primary\",\"Primary\",\"Principal\"],[\"secondary\",\"Secondary\",\"Secondaire\"],[\"tertiary\",\"Tertiary\",\"Tertiaire\"]].map(([k,en,fr])=>'<label>'+phrase(en,fr)+'<div class=\"row\"><input id=\"theme-'+k+'\" type=\"color\" value=\"'+userTheme[k]+'\"><code id=\"theme-code-'+k+'\">'+userTheme[k].toUpperCase()+'</code></div></label>').join(\"\")+'</div><div class=\"row\"><button class=\"btn ghost\" id=\"preview-custom-theme\">'+phrase(\"Preview custom theme\",\"Aperçu du thème\")+'</button><button class=\"btn\" id=\"save-custom-theme\">'+phrase(\"Save to my account\",\"Enregistrer sur mon compte\")+'</button></div></div><div class=\"card\"><h2>'+t(\"chpw\")+'</h2>",
    'account theme editor'
)

replace_once(
    'async function loadMe(){var ss=(await sb.auth.getSession()).data.session;if(!ss){setMe(null);return}var r=await sb.from("profiles").select("*").eq("id",ss.user.id).maybeSingle();setMe(r.data?{id:ss.user.id,name:r.data.name,admin:r.data.is_admin}:null)}',
    'async function loadMe(){var ss=(await sb.auth.getSession()).data.session;if(!ss){setMe(null);return}var r=await sb.from("profiles").select("*").eq("id",ss.user.id).maybeSingle();setMe(r.data?{id:ss.user.id,name:r.data.name,admin:r.data.is_admin}:null);await loadUserTheme()}',
    'account theme loading'
)

replace_once(
    'try{$("theme").value=localStorage.getItem("jfl_theme")||"oled"}catch{$("theme").value="oled"} setTheme($("theme").value);$("theme").onchange=e=>setTheme(e.target.value);',
    'try{$("theme").value=localStorage.getItem("jfl_theme")||"oled"}catch{$("theme").value="oled"} setTheme($("theme").value);$("theme").onchange=e=>setTheme(e.target.value);',
    'theme initialization anchor'
)

replace_once(
    'else if(tab==="acct"){v.innerHTML=acctView();if($("li")){$("li").onclick=logIn;',
    'else if(tab==="acct"){v.innerHTML=acctView();if(ME)bindCustomThemeEditor();if($("li")){$("li").onclick=logIn;',
    'account view binding'
)

# Add custom theme-specific focus/selection treatment while keeping the existing dark base.
replace_once(
    '</head>',
    '''<style>
html[data-theme="custom"]{color-scheme:dark}
html[data-theme="custom"] :is(.btn:not(.ghost),.seg button.on,.switches button.on){background:var(--ac2);border-color:var(--ac);color:#fff}
html[data-theme="custom"] :is(h1,h2,.home-heading h2,.sport-table th){color:var(--ac3)}
html[data-theme="custom"] :is(input,textarea,select):focus-visible{outline:2px solid var(--ac);outline-offset:2px}
html[data-theme="custom"] ::selection{background:var(--ac2);color:#fff}
</style>
</head>''',
    'custom theme CSS insertion'
)

p.write_text(s,encoding='utf-8')
print('Updated index.html with account-based custom themes.')
