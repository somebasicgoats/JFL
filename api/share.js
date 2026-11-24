import { readFileSync } from "node:fs";

const site = readFileSync(new URL("../index.html", import.meta.url), "utf8");
const [, databaseUrl, publicKey] = site.match(/SUPABASE_URL="([^"]+)",SUPABASE_KEY="([^"]+)"/);
const production = process.env.VERCEL_PROJECT_PRODUCTION_URL || "jfl-gray.vercel.app";
const canonicalOrigin = new URL("https://" + production).origin;
const normalize = value => String(value ?? "").toLowerCase().replace(/\s+/g, " ").trim();
const escape = value => String(value ?? "").replace(/[&<>"']/g, char => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
})[char]);

async function rows(table, params){
  const request = new URL("/rest/v1/"+table, databaseUrl);
  request.search = new URLSearchParams(params);
  const response = await fetch(request, {
    headers: { apikey: publicKey },
    signal: AbortSignal.timeout(4500)
  });
  if(!response.ok)throw Error("Public JFL data unavailable: "+table);
  return response.json();
}

async function optionalRows(table, params){
  try{return await rows(table, params)}catch{return []}
}

function tally(team, stat){
  return team.players.reduce((sum, player) => sum + (Number(player[stat]) || 0), 0);
}

async function matchMeta(id, settings){
  const [game] = await rows("games", { select:"id,date,type,teams", id:"eq."+id, limit:"1" });
  if(game?.teams?.length!==2||!game.teams.every(team=>Array.isArray(team.players)))return null;
  const [home, away] = game.teams;
  const teamNames = settings.team_names || {};
  const label = team => team.label || (Object.hasOwn(teamNames,team.name)?teamNames[team.name]:team.name) || "Team";
  const score = tally(home,"g")+tally(away,"o")+"–"+(tally(away,"g")+tally(home,"o"));
  const date = new Intl.DateTimeFormat("en-CA", { dateStyle:"medium", timeZone:"UTC" }).format(new Date(game.date+"T12:00:00Z"));
  const kind = game.teams[0].matchMeta?.friendly || settings["friendly:"+id] ? "Friendly" : game.type==="vs" ? "Interlevel" : "Sec 5";
  return { title:label(home)+" "+score+" "+label(away), description:date+" · "+kind+" · Match report and box score" };
}

async function playerMeta(id, settings){
  const filter = { name_key:"eq."+id, limit:"1" };
  const [[player],[position]] = await Promise.all([
    optionalRows("players", { ...filter, select:"name,first,last" }),
    optionalRows("positions", { ...filter, select:"name,primary_pos" })
  ]);
  let [profile] = player||position?[]:await optionalRows("profiles", {
    name:"ilike."+id.replace(/[\\%_*]/g,c=>"\\"+c),
    select:"name",limit:"1"
  });
  if(normalize(profile?.name)!==id)profile=null;
  const title = [player?.first,player?.last].filter(Boolean).join(" ") || player?.name || position?.name || profile?.name;
  if(!title)return null;
  const photo=settings["photo:"+id];
  let image;
  if(typeof photo==="string"){
    if(/^data:image\/webp;base64,[A-Za-z0-9+/=]+$/.test(photo)&&photo.length<1800000){
      image=new URL("/share/player/"+encodeURIComponent(id)+"?image=1",canonicalOrigin).href;
    }else{
      try{if(new URL(photo).protocol==="https:")image=photo}catch{}
    }
  }
  return {title,description:[position?.primary_pos,"Season stats, game log and awards"].filter(Boolean).join(" · "),image};
}

export default async function handler(req,res){
  if(req.method!=="GET"&&req.method!=="HEAD"){
    res.setHeader("Allow","GET, HEAD");
    return res.status(405).end();
  }
  const kind=req.query.kind,id=req.query.id;
  const match=kind==="match", player=kind==="player";
  const validId=typeof id==="string"&&(match?/^[a-f0-9-]{1,64}$/i.test(id):id===normalize(id)&&id.length>0&&id.length<=100&&!/[\u0000-\u001f]/.test(id));
  if((!match&&!player)||!validId)return res.status(404).end("Share link unavailable");
  const path="/share/"+kind+"/"+encodeURIComponent(id);
  const target="/#"+kind+"/"+encodeURIComponent(id);
  const photoKey="photo:"+id;
  const keys=match?["league-name","team_names"]:["league-name",photoKey];
  const settings=Object.fromEntries((await optionalRows("settings",{
    select:"key,value",or:"("+keys.map(key=>'key.eq."'+key.replace(/[\\"]/g,c=>"\\"+c)+'"').join(",")+")"
  })).map(row=>[row.key,row.value]));
  if(player&&req.query.image==="1"){
    const photo=settings[photoKey];
    if(typeof photo!=="string"||photo.length>=1800000||!/^data:image\/webp;base64,[A-Za-z0-9+/=]+$/.test(photo))return res.status(404).end();
    res.setHeader("Content-Type","image/webp");
    res.setHeader("Cache-Control","public, max-age=300");
    return res.status(200).end(req.method==="HEAD"?undefined:Buffer.from(photo.split(",",2)[1],"base64"));
  }
  const league=settings["league-name"]||"New Korp FC League";
  let meta;
  try{meta=match?await matchMeta(id,settings):await playerMeta(id,settings)}catch{}
  const title=meta?.title||(match?"JFL match report":"JFL player profile");
  const description=meta?.description||(match?"Scores, match details and statistics":"Season stats and game log");
  const image=meta?.image||canonicalOrigin+"/matches/jfl-preview.png";
  const url=canonicalOrigin+path;
  res.setHeader("Content-Type","text/html; charset=utf-8");
  res.setHeader("Cache-Control",meta?"public, max-age=60, s-maxage=300, stale-while-revalidate=180":"no-store");
  res.setHeader("X-Content-Type-Options","nosniff");
  return res.status(200).end(req.method==="HEAD"?undefined:`<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${escape(title)} · ${escape(league)}</title>
<link rel="canonical" href="${escape(url)}">
<meta property="og:type" content="website">
<meta property="og:url" content="${escape(url)}">
<meta property="og:site_name" content="${escape(league)}">
<meta property="og:title" content="${escape(title)}">
<meta property="og:description" content="${escape(description)}">
<meta property="og:image" content="${escape(image)}">
<meta name="theme-color" content="#FFE033">
<meta name="twitter:card" content="summary">
</head><body><h1>${escape(title)}</h1><p>${escape(description)}</p>
<a href="${escape(target)}">Open on JFL</a><script>location.replace(${JSON.stringify(target)})</script></body></html>`);
}
