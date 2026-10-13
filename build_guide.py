# -*- coding: utf-8 -*-
import markdown, io, os, re

SRC = "/Users/a13249605744/WorkBuddy/营养师-三级考证/考点整理_草稿.md"
OUT = "/Users/a13249605744/WorkBuddy/营养师-三级考证/公共营养师三级_应试手册.html"
EXAM_DATE = "2026-12-26"

# ---- 1. 转换笔记 Markdown 为 HTML ----
with io.open(SRC, encoding="utf-8") as f:
    md_text = f.read()

md = markdown.Markdown(extensions=["tables", "toc", "fenced_code"])
body_html = md.convert(md_text)
toc_html = md.toc  # 由 toc 扩展生成

# ---- 2. 进度表数据（74天：2026-10-13 ~ 2026-12-26）----
# 每天 1.5~2h；三阶段：打基础(理论9章) -> 巩固(技能6模块+重点强化) -> 冲刺(模拟+背诵)
schedule = [
    {
        "phase": "第一阶段 · 打基础（精读 + 理解 + 章节题）",
        "span": "10/13 – 11/15（约 34 天）",
        "goal": "按重要度通读 9 章理论，建立知识框架，标注高频数据，每章配套做章节练习题。",
        "weeks": [
            ["第1周", "10/13–10/18", "Ch1 职业道德（速读+刷50题）｜Ch2 医学基础：解剖略读 + 食物消化吸收(重点) + 不同人群生理特点", "攻克消化液对比表；记'内因子→B12→巨幼贫'因果链"],
            ["第2周", "10/19–10/25", "Ch3 营养学基础①：能量及宏量营养素（蛋白质/脂肪/碳水/能量、DRIs、膳食指南八准则）", "背必需氨基酸口诀；记卡价 4/9/4、供能比"],
            ["第3周", "10/26–11/01", "Ch3 营养学基础②：矿物质 + 维生素（两张速查表 + 缺乏病）", "背矿物质/维生素缺乏病口诀；区分脂溶/水溶"],
            ["第4周", "11/02–11/08", "Ch4 食物营养学基础：植物性食物(谷类/大豆) + 动物性食物(畜禽/鱼/蛋/奶)", "记各食物核心营养特点与消化率陷阱"],
            ["第5周", "11/09–11/15", "Ch5 膳食营养指导(重点中的重点) + Ch7 公共营养基础：营养教育/社区管理/缺乏病/慢性病", "熟记平衡膳食宝塔五层与八准则"],
        ],
    },
    {
        "phase": "第二阶段 · 巩固强化（技能精读 + 理论重点 + 错题）",
        "span": "11/16 – 12/13（约 28 天）",
        "goal": "精读 6 个技能模块（可操作/可计算考点为主），回刷理论高频章错题，整理错题本。",
        "weeks": [
            ["第6周", "11/16–11/22", "Ch6 人群营养（整章，孕妇→老年；★婴儿营养考点密集，反复做章节题）", "记各人群'营养需求特点'而非死记数值"],
            ["第7周", "11/23–11/29", "Ch7 营养缺乏病/慢性病收尾 + Ch8 食品卫生(污染/卫生要求/食物中毒) + Ch9 法规(刷题)", "背食物中毒分类表；食物中毒章节多刷题"],
            ["第8周", "11/30–12/06", "技能模块1 膳食调查和评价 + 模块2 人体营养状况测定（体格测量/指标公式）", "练 BMI、腰围、皮褶厚度；掌握24h回顾/称重/记账法"],
            ["第9周", "12/07–12/13", "技能模块3 营养咨询教育 + 模块4 膳食指导和食谱编制（★整节精读，计算重点）", "练食谱编制步骤与营养评价调整"],
        ],
    },
    {
        "phase": "第三阶段 · 冲刺刷题（整套模拟 + 查漏 + 背诵）",
        "span": "12/14 – 12/25（约 12 天）",
        "goal": "做整套模拟卷，错题本过一遍，背诵口诀与速查表，调整作息。12/26 考试。",
        "weeks": [
            ["第10周", "12/14–12/20", "技能模块5 食品营养评价 + 模块6 社区营养干预(刷题)｜理论高频错题重刷(Ch3/4/6/8)", "完成第1~2套模拟卷；标记薄弱章"],
            ["第11周", "12/21–12/25", "第3~5套模拟卷 + 错题本全过 + 背矿物质/维生素/食物/中毒速查表与口诀", "考前3天只看重点章+口诀；12/26 上考场"],
        ],
    },
]

def render_schedule():
    out = []
    for ph in schedule:
        out.append('<div class="phase">')
        out.append('<div class="phase-head"><h3>%s</h3><span class="phase-span">%s</span></div>' % (ph["phase"], ph["span"]))
        out.append('<p class="phase-goal">目标：%s</p>' % ph["goal"])
        out.append('<table class="sched"><thead><tr><th>周次</th><th>日期</th><th>学习内容与重点</th><th>本周关键动作</th></tr></thead><tbody>')
        for w in ph["weeks"]:
            out.append('<tr><td class="wk">%s</td><td class="dt">%s</td><td>%s</td><td class="act">%s</td></tr>' % (w[0], w[1], w[2], w[3]))
        out.append('</tbody></table></div>')
    return "\n".join(out)

sched_html = render_schedule()

# ---- 3. 组装最终 HTML ----
CSS = """
:root{
  --paper:#fffdf8; --ink:#2b2b2b; --line:#ece4d6;
  --red:#d83a3a; --orange:#e08a2e; --blue:#3f72b0; --green:#3f9d6b;
  --card:#ffffff; --soft:#fbf6ec;
}
*{box-sizing:border-box}
body{margin:0;font-family:"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;
  background:var(--paper);color:var(--ink);line-height:1.75;font-size:15.5px}
a{color:var(--blue);text-decoration:none}
.wrap{display:flex;max-width:1280px;margin:0 auto}
/* 侧栏目录 */
nav{position:sticky;top:0;align-self:flex-start;width:280px;height:100vh;overflow:auto;
  background:#2b2622;color:#e9e2d4;padding:18px 14px;border-right:3px solid var(--orange)}
nav h4{margin:6px 0 10px;font-size:13px;letter-spacing:2px;color:#f3c98b}
nav .toc-title{font-size:15px;color:#fff;margin:0 0 4px}
nav ul{list-style:none;margin:0;padding:0;font-size:13px}
nav ul li{padding:3px 0;border-bottom:1px solid #3a342d}
nav ul ul{display:none}
nav a{color:#cdbfa6}
nav a:hover{color:#ffd9a0}
/* 主区 */
main{flex:1;min-width:0;padding:0 34px 80px}
header.top{background:linear-gradient(120deg,#3a2f25,#5a4632);color:#fff;padding:26px 34px;margin-bottom:8px}
header.top h1{margin:0;font-size:26px;letter-spacing:1px}
header.top p{margin:6px 0 0;color:#e9d9bf;font-size:14px}
.countdown{display:inline-block;margin-top:12px;background:#fff3df;color:#9a5b16;
  padding:6px 14px;border-radius:20px;font-weight:700;font-size:14px}
.legend{display:flex;gap:14px;flex-wrap:wrap;margin:18px 0;font-size:13px}
.legend span{padding:4px 12px;border-radius:14px;color:#fff}
.lv3b{background:var(--red)}.lv2b{background:var(--orange)}.lv1b{background:var(--blue)}
/* 进度表 */
.phase{margin:26px 0;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px 20px;box-shadow:0 2px 10px rgba(0,0,0,.04)}
.phase-head{display:flex;justify-content:space-between;align-items:baseline;flex-wrap:wrap;gap:8px;border-bottom:2px solid var(--orange);padding-bottom:8px}
.phase-head h3{margin:0;color:#5a4632;font-size:18px}
.phase-span{font-size:13px;color:#9a5b16;font-weight:700}
.phase-goal{font-size:13.5px;color:#6a6256;margin:8px 0 14px}
table.sched{width:100%;border-collapse:collapse;font-size:13.5px}
table.sched th{background:var(--soft);color:#5a4632;text-align:left;padding:8px 10px;border:1px solid var(--line)}
table.sched td{padding:8px 10px;border:1px solid var(--line);vertical-align:top}
table.sched .wk{font-weight:700;color:#5a4632;white-space:nowrap}
table.sched .dt{white-space:nowrap;color:#9a5b16;font-weight:600}
table.sched .act{color:#3f9d6b;font-size:13px}
/* 章节卡片 */
section.chapter{background:var(--card);border:1px solid var(--line);border-left:6px solid var(--blue);
  border-radius:10px;padding:16px 22px;margin:20px 0;box-shadow:0 1px 6px rgba(0,0,0,.03)}
section.chapter.lv3{border-left-color:var(--red)}
section.chapter.lv2{border-left-color:var(--orange)}
section.chapter.lv1{border-left-color:var(--blue)}
section.chapter h2{margin:0 0 4px;font-size:20px;color:#2b2622}
.badge{display:inline-block;margin-left:10px;padding:2px 10px;border-radius:12px;font-size:12px;color:#fff;vertical-align:middle}
.badge.lv3{background:var(--red)}.badge.lv2{background:var(--orange)}.badge.lv1{background:var(--blue)}
section.chapter h3{font-size:15px;color:#5a4632;margin:16px 0 6px;border-left:4px solid var(--green);padding-left:8px}
section.chapter ul{margin:6px 0 12px;padding-left:22px}
section.chapter li{margin:4px 0}
blockquote{background:#fff7e6;border-left:4px solid var(--orange);margin:10px 0;padding:8px 14px;color:#7a5a2a;border-radius:0 8px 8px 0;font-size:14px}
table{border-collapse:collapse;width:100%;margin:10px 0 16px;font-size:13.5px}
th{background:var(--soft);color:#5a4632;border:1px solid var(--line);padding:7px 9px;text-align:left}
td{border:1px solid var(--line);padding:7px 9px;vertical-align:top}
tbody tr:nth-child(even){background:#fcf8f0}
hr{border:none;border-top:1px dashed var(--line);margin:10px 0}
.note-tip{background:#f3f8f4;border-left:4px solid var(--green);padding:10px 14px;border-radius:0 8px 8px 0;font-size:14px}
/* 打印 */
@media print{
  nav{display:none}main{padding:0}body{font-size:12px}
  section.chapter, .phase{box-shadow:none;page-break-inside:avoid}
  header.top{background:#5a4632 !important;-webkit-print-color-adjust:exact;print-color-adjust:exact}
}
@media(max-width:880px){.wrap{flex-direction:column}nav{position:relative;width:100%;height:auto}}
"""

JS = """
// 倒计时
(function(){
  var d=new Date('%sT09:00:00');
  function upd(){
    var n=new Date();var diff=Math.ceil((d-n)/86400000);
    var el=document.getElementById('cd');
    if(el) el.textContent = diff>0 ? ('距 2026-12-26 考试还有 '+diff+' 天') : '今天考试日，加油！';
  }
  upd();setInterval(upd,3600000);
})();
// 给每个 h2 章节加卡片与色标
document.addEventListener('DOMContentLoaded',function(){
  var hs=document.querySelectorAll('main h2');
  hs.forEach(function(h){
    var m=h.textContent.match(/【重要度：([★]+)】/);
    if(!m) return;
    var lv=m[1].length;
    var sec=document.createElement('section');
    sec.className='chapter lv'+lv;
    h.parentNode.insertBefore(sec,h);
    while(h.nextSibling && h.nextSibling.nodeName!=='H2'){ sec.appendChild(h.nextSibling); }
    sec.insertBefore(h,sec.firstChild);
    var badge='<span class="badge lv'+lv+'">重要度 '+m[1]+'</span>';
    h.innerHTML=h.innerHTML.replace(/【重要度：([★]+)】/,'')+badge;
  });
});
""" % EXAM_DATE

HTML = """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>公共营养师（三级）应试手册 · 74天备考规划</title>
<style>%s</style></head>
<body>
<header class="top">
  <h1>公共营养师（三级）· 应试手册</h1>
  <p>基于《三色笔记》101页 + 学习计划PDF 重整 ｜ 每天 1.5–2 小时 ｜ 三阶段法</p>
  <span class="countdown" id="cd">距 2026-12-26 考试还有 — 天</span>
</header>
<div class="wrap">
  <nav>
    <p class="toc-title">目录</p>
    <h4>一、74天备考进度表</h4>
    <ul><li><a href="#sched">阶段与周次规划</a></li><li><a href="#legend">重要度色标说明</a></li></ul>
    <h4>二、考点手册（按章）</h4>
    %s
  </nav>
  <main>
    <h2 id="sched" style="color:#5a4632;font-size:22px;margin-top:6px">📅 74天备考进度表</h2>
    <p style="color:#6a6256;font-size:14px">今天 2026-10-13 起，至 2026-12-26 考试，共 <b>74 个学习日</b>。
    建议工作日 1.5h、周末 2h，全程约 120+ 小时。计划可依自身进度微调顺序。</p>
    <div class="legend" id="legend">
      <span class="lv3b">★★★ 核心必背</span>
      <span class="lv2b">★★ 重点</span>
      <span class="lv1b">★ 一般/刷题</span>
    </div>
    %s

    <h2 id="handbook" style="color:#5a4632;font-size:22px;margin-top:34px">📚 考点手册（三色笔记重整）</h2>
    <div class="note-tip">使用建议：先按进度表推进，每章先看【核心考点】建立框架，再用【速查表】横向对比记忆，最后背【口诀】、避【易错提醒】。红=必背、橙=重点、蓝=一般。</div>
    %s
  </main>
</div>
<script>%s</script>
</body></html>""" % (CSS, toc_html, sched_html, body_html, JS)

with io.open(OUT, "w", encoding="utf-8") as f:
    f.write(HTML)

print("OK ->", OUT, "bytes:", len(HTML))
