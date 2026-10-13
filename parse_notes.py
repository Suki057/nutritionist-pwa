#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
解析《公共营养师》三色笔记.pdf -> notes_data.json  (PWA 数据源)

修复点（相对旧版）：
  1. 剔除页脚「第 N 页」（位于 y≈780，正文最多到 y≈758）——按坐标过滤。
  2. 跳过封面/目录（pdf 第 1~3 页）。
  3. 按 y 容差合并下标（维生素B1 / B2 / B6 / K / CH3 等，下标比正文低 ~5px）。
  4. 把 PDF 的物理换行合并成逻辑段落（上一行不是新条目标记就并入同段）。
  5. 段落内保留逐字符颜色 run：red / blue / blue2 / green / blk。
     颜色语义：RED=小节标题，BLUE/BLUE2=条目标签(1.生理功能：)，GREEN=重点内容，BLK=普通正文。
  6. 识别 PDF 表格(pdfplumber.find_tables)，渲染为真正的表格，避免压成一坨文字。

输出结构：
{
 "基础": [ {no,title, sections:[{title, content:ITEM[]}]} ],
 "技能": [ {no,title, groups:[{title, intro:ITEM[], units:[{no,title,content:ITEM[]}]}]} ]
}
ITEM = PARA | TABLE
  PARA  = [[text,color], ...]              # 一个逻辑段落（颜色 run 列表）
  TABLE = {"table": [[CELL,...], ...]}     # CELL = [[text,color],...]
"""
import pdfplumber, json, re, collections

PDF = '/Users/a13249605744/Desktop/《公共营养师》三色笔记.pdf'
OUT = 'notes_data.json'
FOOTER_Y = 770          # top 超过此值视为页脚
TOL = 7                 # 行内 y 容差（合并上下标）
SKIP_PAGES = {0, 1, 2}  # 封面 + 目录两页（0-based）

CN = '一二三四五六七八九十'
RE_CH = re.compile(r'^第([' + CN + r']+)章\s*(.*)$')
RE_SEC = re.compile(r'^第([' + CN + r']+)节\s*(.*)$')
RE_MOD = re.compile(r'^职业模块\s*(\d+)\s*(.*)$')
RE_GRP = re.compile(r'^培训课程\s*(\d+)\s*(.*)$')
RE_UNIT = re.compile(r'^学习单元\s*(\d+)\s*(.*)$')
RE_DOTS = re.compile(r'(\.{3,}|…{2,})')
RE_BLOCK = re.compile(
    r'^(（[' + CN + r']+）|[' + CN + r']+、|[①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭]|（\d+）|\(\d+\)|\d+\.(?!\d))')
SKIP_EXACT = {'基础知识', '专业技能', '技能知识', '基础知识部分', '专业技能部分',
              '公共营养师', '三色笔记', '目录', '公共营养师（三级）', '公共营养师(三级)'}


def cn2int(s):
    m = {c: i + 1 for i, c in enumerate(CN)}
    if s == '十':
        return 10
    if len(s) == 1:
        return m.get(s, 0)
    if s.startswith('十'):
        return 10 + m.get(s[1:], 0)
    if s.endswith('十'):
        return m.get(s[0], 0) * 10
    if '十' in s:
        a, b = s.split('十')
        return m.get(a, 0) * 10 + m.get(b, 0)
    return 0


def color_key(v):
    if v is None or isinstance(v, (int, float)):
        return 'blk'
    t = list(v)
    if len(t) < 3:
        return 'blk'
    r, g, b = t[0], t[1], t[2]
    if r > 0.8 and g < 0.3 and b < 0.3:
        return 'red'
    if b > 0.6 and r < 0.3 and g < 0.3:
        return 'blue2' if b < 0.9 else 'blue'
    if g > 0.5 and r < 0.3 and b < 0.5:
        return 'green'
    return 'blk'


def chars_to_runs(chars):
    """把已排好序的字符列表压成颜色 run，并去掉首尾空白、折叠连续空格。"""
    runs = []
    for c in chars:
        col = color_key(c['non_stroking_color'])
        if runs and runs[-1][1] == col:
            runs[-1][0] += c['text']
        else:
            runs.append([c['text'], col])
    runs = [[re.sub(r'[ \u3000]{2,}', ' ', t).strip(), c] for t, c in runs]
    return [[t, c] for t, c in runs if t]


def page_lines(page):
    """把一页的字符合并成「视觉行」：返回 [(top, runs), ...]。"""
    # 保留空格字符（用于分隔「学习单元1 24h回顾法」这类标题），仅剔除空字符
    cs = [c for c in page.chars if c['top'] <= FOOTER_Y and (c['text'] or '') != '']
    cs.sort(key=lambda c: (c['top'], c['x0']))
    clusters = []
    for c in cs:
        if clusters and abs(c['top'] - clusters[-1]['ref']) <= TOL:
            clusters[-1]['cs'].append(c)
        else:
            clusters.append({'ref': c['top'], 'cs': [c]})
    out = []
    for cl in clusters:
        csx = sorted(cl['cs'], key=lambda c: c['x0'])
        runs = chars_to_runs(csx)
        if runs:
            out.append((cl['ref'], runs))
    return out


def line_text(runs):
    return ''.join(t for t, _ in runs)


def merge_paragraphs(lines):
    """把若干视觉行(每行=run列表) 合并成逻辑段落列表。"""
    paras = []
    for runs in lines:
        txt = line_text(runs)
        if not txt:
            continue
        if RE_BLOCK.match(txt.strip()) or not paras:
            paras.append([list(r) for r in runs])
        else:
            last = paras[-1]
            for t, c in runs:
                if last and last[-1][1] == c:
                    last[-1][0] += t
                else:
                    last.append([t, c])
    return paras


def cell_runs(all_chars, bbox):
    """取落在单元格 bbox 内的字符，先按 y 分子行、再按 x 排序，压成 run。"""
    if not bbox:
        return []
    x0, top, x1, bottom = bbox
    M = 1.5
    sel = []
    for c in all_chars:
        cx = (c['x0'] + c['x1']) / 2.0
        cy = (c['top'] + c['bottom']) / 2.0
        if x0 - M <= cx <= x1 + M and top - M <= cy <= bottom + M:
            sel.append(c)
    sel.sort(key=lambda c: (c['top'], c['x0']))
    subs = []
    for c in sel:
        if subs and abs(c['top'] - subs[-1]['ref']) <= 6:
            subs[-1]['cs'].append(c)
        else:
            subs.append({'ref': c['top'], 'cs': [c]})
    out = []
    for s in subs:
        out.extend(chars_to_runs(sorted(s['cs'], key=lambda c: c['x0'])))
    return out


def page_tables(page):
    """返回本页表格 [{top,bottom,data,emitted}]。"""
    out = []
    try:
        tabs = page.find_tables()
    except Exception:
        tabs = []
    for t in tabs:
        b = t.bbox
        if b[1] >= FOOTER_Y:
            continue
        data = []
        for row in t.rows:
            cells = []
            for cell in row.cells:
                cells.append(cell_runs(page.chars, cell))
            if any(cells):
                data.append(cells)
        if len(data) >= 1 and data:
            out.append({'top': b[1], 'bottom': b[3], 'data': data, 'emitted': False})
    out.sort(key=lambda t: t['top'])
    return out


def main():
    pdf = pdfplumber.open(PDF)
    basic, skill = [], []
    cur = {'ch': None, 'sec': None, 'mod': None, 'grp': None, 'unit': None}
    buf = []
    pending = []
    stats = {'lines': 0, 'paras': 0, 'tables': 0, 'skip': 0}

    def container():
        if cur['unit'] is not None:
            return cur['unit'], 'content'
        if cur['grp'] is not None:
            return cur['grp'], 'intro'
        if cur['sec'] is not None:
            return cur['sec'], 'content'
        if cur['ch'] is not None:
            cur['ch'].setdefault('intro', [])
            return cur['ch'], 'intro'
        if cur['mod'] is not None:
            cur['mod'].setdefault('intro', [])
            return cur['mod'], 'intro'
        return None, None

    def put(items):
        if not items:
            return
        obj, key = container()
        if obj is None:
            buf.extend(items)
        else:
            obj[key].extend(items)

    def flush():
        if not pending:
            return
        paras = merge_paragraphs(pending)
        pending.clear()
        stats['paras'] += len(paras)
        put(paras)

    for pi, page in enumerate(pdf.pages):
        if pi in SKIP_PAGES:
            continue
        tables = page_tables(page)
        for top, runs in page_lines(page):
            txt = line_text(runs).strip()
            if not txt:
                continue
            stats['lines'] += 1
            # ① 先判标题（优先级高于表格，避免表格 bbox 边缘吞掉「学习单元N」等标题）
            m = RE_CH.match(txt)
            if m and len(txt) < 40:
                flush()
                ch = {'no': cn2int(m.group(1)), 'title': m.group(2).strip(), 'sections': []}
                basic.append(ch)
                cur.update({'ch': ch, 'sec': None, 'mod': None, 'grp': None, 'unit': None})
                continue
            m = RE_SEC.match(txt)
            if m and len(txt) < 40:
                flush()
                sec = {'title': m.group(2).strip(), 'content': []}
                cur['ch']['sections'].append(sec)
                cur.update({'sec': sec, 'unit': None})
                continue
            m = RE_MOD.match(txt)
            if m and len(txt) < 40:
                flush()
                mod = {'no': int(m.group(1)), 'title': m.group(2).strip(), 'groups': []}
                skill.append(mod)
                cur.update({'mod': mod, 'grp': None, 'unit': None, 'sec': None, 'ch': None})
                continue
            m = RE_GRP.match(txt)
            if m and len(txt) < 40:
                flush()
                grp = {'title': '培训课程%s %s' % (m.group(1), m.group(2).strip()),
                       'intro': [], 'units': []}
                cur['mod']['groups'].append(grp)
                cur.update({'grp': grp, 'unit': None})
                continue
            m = RE_UNIT.match(txt)
            if m and len(txt) < 60:
                flush()
                unit = {'no': '学习单元%s' % m.group(1),
                        'title': '学习单元%s %s' % (m.group(1), m.group(2).strip()),
                        'content': []}
                cur['grp']['units'].append(unit)
                cur.update({'unit': unit})
                continue
            # ② 表格：在某张表 bbox 内的行 -> 首次遇到时整表输出，其余跳过
            hit = None
            for t in tables:
                if t['top'] - 1 <= top <= t['bottom'] + 1:
                    hit = t
                    break
            if hit is not None:
                if not hit['emitted']:
                    flush()
                    put([{'table': hit['data']}])
                    hit['emitted'] = True
                    stats['tables'] += 1
                continue
            # ③ 过滤目录残行/分隔页
            if RE_DOTS.search(txt) or txt in SKIP_EXACT:
                stats['skip'] += 1
                continue
            pending.append(runs)

    flush()
    if buf:
        put(buf)
        sys_warn = 'WARN: buf 非空 (%d) —— 有正文未能归属到任何章节' % len(buf)
        print(sys_warn)

    out = {'基础': basic, '技能': skill}
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, separators=(',', ':'))

    cc = collections.Counter()

    def walk(o):
        if isinstance(o, dict):
            if 'table' in o:
                for row in o['table']:
                    for cell in row:
                        for t, c in cell:
                            cc[c] += len(t)
            else:
                for v in o.values():
                    walk(v)
        elif isinstance(o, list):
            if o and isinstance(o[0], list) and len(o[0]) == 2 and isinstance(o[0][0], str):
                for t, c in o:
                    cc[c] += len(t)
            else:
                for v in o:
                    walk(v)
    walk(out)
    print('basic chapters:', len(basic), 'skill modules:', len(skill),
          'sections:', sum(len(c['sections']) for c in basic),
          'groups:', sum(len(m['groups']) for m in skill),
          'units:', sum(len(g['units']) for m in skill for g in m['groups']))
    print('lines=%d paras=%d tables=%d skipped=%d' %
          (stats['lines'], stats['paras'], stats['tables'], stats['skip']))
    print('color chars:', dict(cc))


if __name__ == '__main__':
    main()
