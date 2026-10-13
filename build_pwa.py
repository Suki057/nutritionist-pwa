# -*- coding: utf-8 -*-
import markdown, io, os

BASE = "/Users/a13249605744/WorkBuddy/营养师-三级考证"
SRC  = os.path.join(BASE, "考点整理_草稿.md")
EXAM_DATE = "2026-12-26"

with io.open(SRC, encoding="utf-8") as f:
    md_text = f.read()
md = markdown.Markdown(extensions=["tables", "toc", "fenced_code"])
body_html = md.convert(md_text)

# ---------- 进度表 ----------
schedule = [
    {"phase":"第一阶段 · 打基础（精读+理解+章节题）","span":"10/13 – 11/15（约34天）",
     "goal":"按重要度通读9章理论，建立框架，标注高频数据，每章配套章节题。",
     "weeks":[
        ["第1周","10/13–10/18","Ch1职业道德(速读+刷题)｜Ch2医学基础：解剖略读+食物消化吸收(重点)+不同人群生理特点","攻克消化液对比表；记内因子→B12→巨幼贫"],
        ["第2周","10/19–10/25","Ch3营养学基础①：能量及宏量营养素(蛋白质/脂肪/碳水/能量、DRIs、膳食指南八准则)","背必需氨基酸口诀；卡价4/9/4、供能比"],
        ["第3周","10/26–11/01","Ch3营养学基础②：矿物质+维生素(两张速查表+缺乏病)","背矿物质/维生素缺乏病口诀；分脂溶/水溶"],
        ["第4周","11/02–11/08","Ch4食物营养学基础：植物性(谷类/大豆)+动物性(畜禽/鱼/蛋/奶)","记各食物核心营养特点与消化率陷阱"],
        ["第5周","11/09–11/15","Ch5膳食营养指导(重点中的重点)+Ch7公共营养基础：营养教育/社区/缺乏病/慢性病","熟记平衡膳食宝塔五层与八准则"],
     ]},
    {"phase":"第二阶段 · 巩固强化（技能精读+理论重点+错题）","span":"11/16 – 12/13（约28天）",
     "goal":"精读6个技能模块(可操作/可计算考点)，回刷理论高频章错题，整理错题本。",
     "weeks":[
        ["第6周","11/16–11/22","Ch6人群营养(整章，孕妇→老年；★婴儿营养考点密集，反复做章节题)","记各人群'营养需求特点'而非死背数值"],
        ["第7周","11/23–11/29","Ch7营养缺乏病/慢性病收尾+Ch8食品卫生(污染/卫生/中毒)+Ch9法规(刷题)","背食物中毒分类表；食物中毒章多刷题"],
        ["第8周","11/30–12/06","技能模块1膳食调查和评价+模块2人体营养状况测定(体格测量/公式)","练BMI、腰围、皮褶厚度；24h回顾/称重/记账法"],
        ["第9周","12/07–12/13","技能模块3营养咨询教育+模块4膳食指导和食谱编制(★整节精读，计算重点)","练食谱编制步骤与营养评价调整"],
     ]},
    {"phase":"第三阶段 · 冲刺刷题（整套模拟+查漏+背诵）","span":"12/14 – 12/25（约12天）",
     "goal":"做整套模拟卷，错题本过一遍，背口诀与速查表，调整作息。12/26考试。",
     "weeks":[
        ["第10周","12/14–12/20","技能模块5食品营养评价+模块6社区营养干预(刷题)｜理论高频错题重刷(Ch3/4/6/8)","完成第1~2套模拟卷；标记薄弱章"],
        ["第11周","12/21–12/25","第3~5套模拟卷+错题本全过+背矿物质/维生素/食物/中毒速查表与口诀","考前3天只看重点章+口诀；12/26上考场"],
     ]},
]

def sched_html():
    out=[]
    for ph in schedule:
        out.append('<div class="phase">')
        out.append('<div class="phase-head"><h3>%s</h3><span class="phase-span">%s</span></div>'%(ph["phase"],ph["span"]))
        out.append('<p class="phase-goal">%s</p>'%ph["goal"])
        out.append('<table class="sched"><thead><tr><th>周</th><th>日期</th><th>重点内容</th><th>关键动作</th></tr></thead><tbody>')
        for w in ph["weeks"]:
            out.append('<tr><td class="wk">%s</td><td class="dt">%s</td><td>%s</td><td class="act">%s</td></tr>'%(w[0],w[1],w[2],w[3]))
        out.append('</tbody></table></div>')
    return "\n".join(out)

# ---------- JS 源码 ----------
JS_SRC = r"""
// 倒计时
(function(){var d=new Date('%sT09:00:00');function u(){var n=new Date();var x=Math.ceil((d-n)/86400000);
var el=document.getElementById('cd');if(el)el.textContent=x>0?('距 12-26 考试还有 '+x+' 天'):'今天考试，加油！';}
u();setInterval(u,3600000);})();
// 章节 -> 可折叠 details
(function(){
  var hb=document.getElementById('handbook-body');if(!hb)return;
  var hs=Array.prototype.slice.call(hb.querySelectorAll('h2'));
  var chips=[];
  hs.forEach(function(h){
    var m=h.textContent.match(/【重要度：([★]+)】/);if(!m)return;
    var lv=m[1].length;
    var rawName=h.textContent.replace(/【重要度：([★]+)】/,'').replace(/^第.{1,3}章\s*/,'').trim();
    var det=document.createElement('details');det.className='chap lv'+lv;if(lv===3)det.open=true;
    var nodes=[h];var n=h.nextElementSibling;
    while(n&&!n.matches('h2')){nodes.push(n);n=n.nextElementSibling;}
    nodes.forEach(function(nd){det.appendChild(nd);});
    h.parentNode.insertBefore(det,h);
    h.innerHTML=h.innerHTML.replace(/【重要度：([★]+)】/,'')+'<span class="badge lv'+lv+'">'+m[1]+'</span>';
    if(h.id)det.id=h.id;
    var icon=lv===3?'🔴':(lv===2?'🟠':'🔵');
    chips.push('<a href="#'+h.id+'">'+icon+rawName.slice(0,8)+'</a>');
  });
  var q=document.getElementById('quick');
  chips.forEach(function(c){q.insertAdjacentHTML('beforeend',c);});
})();
// 点快捷跳转时展开对应 details
document.getElementById('quick').addEventListener('click',function(e){
  var a=e.target.closest('a');if(!a)return;var id=a.getAttribute('href').slice(1);
  var el=document.getElementById(id);if(el&&el.tagName==='DETAILS')el.open=true;
});
// Service Worker 注册（离线 + 可安装）
if('serviceWorker' in navigator){window.addEventListener('load',function(){
  navigator.serviceWorker.register('sw.js').catch(function(){});});}
// 安装提示
var deferred=null;
window.addEventListener('beforeinstallprompt',function(e){e.preventDefault();deferred=e;
  document.getElementById('instBtn').style.display='block';});
document.getElementById('instBtn').addEventListener('click',function(){
  if(!deferred)return;deferred.prompt();deferred.userChoice.then(function(){deferred=null;
  document.getElementById('instBtn').style.display='none';});});
document.getElementById('instX').addEventListener('click',function(){
  document.getElementById('installHint').style.display='none';});
""" % EXAM_DATE

# ---------- 移动端页面 ----------
HEAD = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#1f9d6b">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="营养三级">
<link rel="manifest" href="manifest.webmanifest">
<link rel="apple-touch-icon" href="icon-192.png">
<title>营养师三级 · 应试宝典</title>
"""

CSS = """
:root{
  --green:#1f9d6b; --green-d:#157a52; --cream:#fbfaf5; --ink:#23291f; --line:#e7e3d6;
  --red:#d83a3a; --orange:#e08a2e; --blue:#3f72b0; --soft:#f1f8f3;
}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html,body{margin:0;padding:0}
body{font-family:"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;
  background:var(--cream);color:var(--ink);line-height:1.72;font-size:16px;
  padding-bottom:env(safe-area-inset-bottom)}
a{color:var(--green-d);text-decoration:none}
.appbar{position:sticky;top:0;z-index:20;background:var(--green);color:#fff;
  padding:calc(10px + env(safe-area-inset-top)) 14px 10px;box-shadow:0 2px 8px rgba(0,0,0,.15)}
.appbar h1{margin:0;font-size:18px;display:flex;align-items:center;gap:8px}
.appbar .cd{margin-top:6px;display:inline-block;background:#fff;color:var(--green-d);
  font-size:13px;font-weight:700;padding:3px 12px;border-radius:14px}
.quick{position:sticky;top:0;z-index:15;background:#fff;border-bottom:1px solid var(--line);
  display:flex;gap:8px;overflow-x:auto;padding:8px 12px;-webkit-overflow-scrolling:touch}
.quick a{flex:0 0 auto;font-size:13px;background:var(--soft);color:var(--green-d);
  padding:5px 12px;border-radius:14px;white-space:nowrap}
.quick a.all{background:var(--green);color:#fff}
main{padding:12px 12px 90px;max-width:760px;margin:0 auto}
.hero{background:linear-gradient(120deg,#1f9d6b,#2bbd86);color:#fff;border-radius:14px;
  padding:16px;margin-bottom:14px}
.hero h2{margin:0 0 6px;font-size:19px}
.hero p{margin:0;font-size:13.5px;color:#eafff5}
.sect-title{font-size:17px;color:var(--green-d);margin:20px 4px 10px;font-weight:800}
.phase{background:#fff;border:1px solid var(--line);border-radius:12px;padding:12px 14px;margin-bottom:12px;box-shadow:0 1px 4px rgba(0,0,0,.03)}
.phase-head{display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap;border-bottom:2px solid var(--orange);padding-bottom:6px}
.phase-head h3{margin:0;font-size:15.5px;color:var(--green-d)}
.phase-span{font-size:12px;color:#b5701a;font-weight:700}
.phase-goal{font-size:12.5px;color:#6a7160;margin:6px 0 10px}
table.sched{width:100%;border-collapse:collapse;font-size:12.5px}
table.sched th{background:var(--soft);color:var(--green-d);text-align:left;padding:6px;font-weight:700}
table.sched td{padding:6px;border-top:1px solid var(--line);vertical-align:top}
table.sched .wk{font-weight:800;color:var(--green-d);white-space:nowrap}
table.sched .dt{white-space:nowrap;color:#b5701a;font-weight:700}
table.sched .act{color:var(--green);font-size:12px}
.note{background:var(--soft);border-left:4px solid var(--green);padding:10px 12px;border-radius:0 10px 10px 0;font-size:13.5px;margin:6px 0 14px}
details.chap{background:#fff;border:1px solid var(--line);border-left:6px solid var(--blue);
  border-radius:12px;margin-bottom:10px;box-shadow:0 1px 4px rgba(0,0,0,.03);overflow:hidden}
details.chap.lv3{border-left-color:var(--red)}
details.chap.lv2{border-left-color:var(--orange)}
details.chap.lv1{border-left-color:var(--blue)}
details.chap>summary{list-style:none;cursor:pointer;padding:13px 14px;font-size:16px;font-weight:700;display:flex;align-items:center;gap:8px}
details.chap>summary::-webkit-details-marker{display:none}
details.chap>summary::before{content:"▸";color:var(--green);font-size:13px;transition:transform .15s}
details.chap[open]>summary::before{transform:rotate(90deg)}
details.chap>:not(summary){padding:0 14px 14px}
.badge{flex:0 0 auto;font-size:11px;color:#fff;padding:2px 8px;border-radius:10px}
.badge.lv3{background:var(--red)}.badge.lv2{background:var(--orange)}.badge.lv1{background:var(--blue)}
#handbook-body>h1{display:none}
#handbook-body>h2{font-size:18px;color:var(--green-d);margin:16px 0 8px}
details.chap h3{font-size:14.5px;color:var(--green-d);margin:14px 0 6px;border-left:4px solid var(--orange);padding-left:7px}
details.chap ul{margin:4px 0 12px;padding-left:20px}
details.chap li{margin:4px 0}
details.chap blockquote{background:#fff7e6;border-left:4px solid var(--orange);margin:8px 0;padding:7px 12px;color:#7a5a2a;font-size:13px;border-radius:0 8px 8px 0}
table{border-collapse:collapse;width:100%;margin:8px 0 14px;font-size:12.5px}
th{background:var(--soft);color:var(--green-d);border:1px solid var(--line);padding:6px;text-align:left}
td{border:1px solid var(--line);padding:6px;vertical-align:top}
tbody tr:nth-child(even){background:#faf8f1}
hr{border:none;border-top:1px dashed var(--line);margin:8px 0}
#installHint{position:fixed;left:0;right:0;bottom:0;z-index:40;background:#23311f;color:#eafff0;
  font-size:13px;padding:10px 12px calc(10px + env(safe-area-inset-bottom));display:flex;align-items:center;gap:10px;
  box-shadow:0 -2px 10px rgba(0,0,0,.25)}
#installHint .txt{flex:1;line-height:1.5}
#installHint button{background:var(--green);color:#fff;border:none;border-radius:20px;padding:8px 16px;font-size:13px;font-weight:700;white-space:nowrap}
#installHint .x{background:none;color:#9fb89f;border:none;font-size:18px;padding:0 4px}
@media print{details.chap{break-inside:avoid}}
"""

handbook = '<div id="handbook-body">' + body_html + '</div>'

HTML = (HEAD + '<style>' + CSS + '</style></head><body>'
  '<header class="appbar"><h1>🌿 营养师三级 · 应试宝典</h1>'
  '<span class="cd" id="cd">距考试 — 天</span></header>'
  '<nav class="quick" id="quick"><a class="all" href="#top">顶部</a>'
  '<a href="#sched">进度表</a><a href="#handbook">考点手册</a></nav>'
  '<main id="top">'
    '<div class="hero"><h2>74天冲刺计划</h2>'
    '<p>2026-10-13 起 · 每天 1.5–2 小时 · 三阶段法（打基础→巩固→冲刺）</p></div>'
    '<div class="sect-title" id="sched">📅 备考进度表</div>'
    '<p class="note">今天起到 12/26 考试共 <b>74 个学习日</b>。工作日 1.5h、周末 2h，约 120+ 小时。计划可依进度微调。</p>'
    + sched_html() +
    '<div class="sect-title" id="handbook">📚 考点手册（三色笔记重整）</div>'
    '<p class="note">红=必背 ★★★ ｜ 橙=重点 ★★ ｜ 蓝=一般 ★。点章节标题展开/收起。先框架→速查表→口诀→避易错。</p>'
    + handbook +
  '</main>'
  '<div id="installHint"><span class="txt">📲 添加到主屏幕：安卓点浏览器菜单→<b>安装应用</b>；iPhone 点<b>分享→添加到主屏幕</b></span>'
  '<button id="instBtn" style="display:none">安装</button><button class="x" id="instX">×</button></div>'
  '<script>' + JS_SRC + '</script>'
  '</body></html>')

with io.open(os.path.join(BASE,"index.html"),"w",encoding="utf-8") as f:
    f.write(HTML)

# ---------- manifest ----------
manifest = """{
  "name":"营养师三级 · 应试宝典",
  "short_name":"营养三级",
  "description":"公共营养师三级考试备考：74天进度表 + 考点速查",
  "start_url":".",
  "scope":".",
  "display":"standalone",
  "orientation":"portrait",
  "background_color":"#fbfaf5",
  "theme_color":"#1f9d6b",
  "icons":[
    {"src":"icon-192.png","sizes":"192x192","type":"image/png"},
    {"src":"icon-512.png","sizes":"512x512","type":"image/png"},
    {"src":"icon-512.png","sizes":"512x512","type":"image/png","purpose":"any maskable"}
  ]
}"""
with io.open(os.path.join(BASE,"manifest.webmanifest"),"w",encoding="utf-8") as f:
    f.write(manifest)

# ---------- service worker ----------
sw = """const CACHE='nutri3-v1';
const ASSETS=['./','./index.html','./manifest.webmanifest','./icon-192.png','./icon-512.png'];
self.addEventListener('install',function(e){e.waitUntil(caches.open(CACHE).then(function(c){return c.addAll(ASSETS);}).then(function(){return self.skipWaiting();}));});
self.addEventListener('activate',function(e){e.waitUntil(caches.keys().then(function(ks){return Promise.all(ks.map(function(k){return k!==CACHE?caches.delete(k):null;}));}).then(function(){return self.clients.claim();}));});
self.addEventListener('fetch',function(e){if(e.request.method!=='GET')return;
  e.respondWith(caches.match(e.request).then(function(r){return r||fetch(e.request).then(function(resp){var cp=resp.clone();caches.open(CACHE).then(function(c){c.put(e.request,cp);});return resp;}).catch(function(){return caches.match('./index.html');});}));});
"""
with io.open(os.path.join(BASE,"sw.js"),"w",encoding="utf-8") as f:
    f.write(sw)

# ---------- 图标 ----------
try:
    from PIL import Image, ImageDraw, ImageFont
    def make_icon(size, path):
        img=Image.new("RGB",(size,size),(31,157,107))
        d=ImageDraw.Draw(img)
        m=int(size*0.30); d.ellipse([m,m,size-m,size-m],fill=(255,255,255))
        fnt=None
        for p in ["/System/Library/Fonts/PingFang.ttc","/System/Library/Fonts/STHeiti Light.ttc","/System/Library/Fonts/Supplemental/Songti.ttc"]:
            try:
                fnt=ImageFont.truetype(p, int(size*0.34)); break
            except Exception: pass
        if fnt is None: fnt=ImageFont.load_default()
        txt="营"
        bb=d.textbbox((0,0),txt,font=fnt); tw=bb[2]-bb[0]; th=bb[3]-bb[1]
        d.text(((size-tw)/2-bb[0],(size-th)/2-bb[1]),txt,fill=(31,157,107),font=fnt)
        img.save(path)
    make_icon(192, os.path.join(BASE,"icon-192.png"))
    make_icon(512, os.path.join(BASE,"icon-512.png"))
    print("icons ok")
except Exception as e:
    print("icon error:", e)

print("DONE index.html bytes=", len(HTML))
