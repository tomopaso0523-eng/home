// 使い方: このフォルダで npm i d3@7 topojson-client@3 world-atlas@2 → node build.js（../index.html を出力）
const fs=require('fs'),path=require('path');const nm=path.join(__dirname,'node_modules')+'/';
let h=fs.readFileSync(path.join(__dirname,'template.html'),'utf8');
const rep={__D3__:fs.readFileSync(nm+'d3/dist/d3.min.js','utf8'),__TOPO__:fs.readFileSync(nm+'topojson-client/dist/topojson-client.min.js','utf8'),__CITIES__:fs.readFileSync(path.join(__dirname,'cities.js'),'utf8'),__C50__:fs.readFileSync(nm+'world-atlas/countries-50m.json','utf8'),__C110__:fs.readFileSync(nm+'world-atlas/countries-110m.json','utf8')};
for(const [k,v] of Object.entries(rep)) h=h.split(k).join(v);
fs.writeFileSync(path.join(__dirname,'..','index.html'),h);console.log((h.length/1024).toFixed(0)+'KB');
