"""인물 바이블(rules/characters.md) → HTML 한 장. 윙키 스튜디오가 /characters 로 보여 준다.
  python3 engine/studio_characters.py rules/characters.md out.html
"""
import re, html, sys
E = html.escape

def inline(t):
    t = E(t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
    t = re.sub(r'(?<![\w*])\*([^*\s][^*]*?)\*(?![\w*])', r'<em class="emph">\1</em>', t)
    t = t.replace('【확인】', '<span class="ok">확인</span>')
    return t

def subline(t):
    """dialogue text -> subtitle strip with notation styling"""
    s = E(t)
    s = re.sub(r'\[(놀람|시무룩|당황)\]', r'<span class="tag">\1</span>', s)
    s = re.sub(r'(?<![\w*])\*([^*]+?)\*', r'<b class="big">\1</b>', s)
    s = re.sub(r'〈(.+?)〉', r'<span class="sfx">\1</span>', s)
    return s

def dialogue(lines):
    out = ['<div class="dlg">']
    for l in lines:
        m = re.match(r'>\s*\*\*(.+?)\*\*\s*(.*)', l)
        if not m: continue
        who, txt = m.group(1), m.group(2).strip()
        cls = 'line'
        if txt == '―':
            out.append(f'<div class="line silence"><span class="who">{E(who)}</span><span class="strip mute">― 침묵</span></div>'); continue
        if re.fullmatch(r'\(.+\)', txt):
            cls += ' inner'; txt = txt[1:-1]
        if txt.startswith('..'):
            cls += ' whisper'; txt = txt[2:]
        if '!!' in txt:
            cls += ' shout'; txt = txt.replace('!!', '!')
        out.append(f'<div class="{cls}"><span class="who">{E(who)}</span><span class="strip">{subline(txt)}</span></div>')
    out.append('</div>')
    return '\n'.join(out)

def table(rows):
    cells = [[c.strip() for c in r.strip().strip('|').split('|')] for r in rows if not re.match(r'^\|[-\s|]+\|$', r.strip())]
    h = '<div class="tbl"><table><thead><tr>' + ''.join(f'<th>{inline(c)}</th>' for c in cells[0]) + '</tr></thead><tbody>'
    for r in cells[1:]:
        h += '<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in r) + '</tr>'
    return h + '</tbody></table></div>'

def block(text):
    """generic markdown block -> html (bullets, paragraphs, tables, dialogue)"""
    lines = text.split('\n'); out = []; i = 0
    while i < len(lines):
        l = lines[i]; s = l.strip()
        if not s: i += 1; continue
        if s.startswith('|'):
            j = i
            while j < len(lines) and lines[j].strip().startswith('|'): j += 1
            out.append(table(lines[i:j])); i = j; continue
        if s.startswith('>'):
            j = i
            while j < len(lines) and lines[j].strip().startswith('>'): j += 1
            out.append(dialogue([x.strip() for x in lines[i:j]])); i = j; continue
        m = re.match(r'\((a|b|c)\)\s*(.*)', s)
        if m:
            out.append(f'<p class="sit"><span class="sitk">{ {"a":"무시당할 때","b":"자랑할 때","c":"틀린 걸 인정할 때"}[m.group(1)] }</span>{inline(m.group(2).split(". ",1)[-1] if ". " in m.group(2) else m.group(2))}</p>'); i += 1; continue
        if s.startswith('- '):
            j = i; items = []
            while j < len(lines) and lines[j].strip().startswith('- '):
                items.append(lines[j].strip()[2:]); j += 1
            out.append('<ul>' + ''.join(f'<li>{inline(x)}</li>' for x in items) + '</ul>'); i = j; continue
        out.append(f'<p>{inline(s)}</p>'); i += 1
    return '\n'.join(out)

def render(md):
    parts = re.split(r'\n## ', md)
    intro = parts[0]
    chars, rest = [], []
    for p in parts[1:]:
        title, body = p.split('\n', 1)
        if re.match(r'\d+\. ', title): chars.append((title, body))
        else: rest.append((title, body))

    COL = {'윙키':'--c1','곰 아빠':'--c2','판다':'--c3','펭귄 선생님':'--c4','거북 여사':'--c5','너구리 대리':'--c6','고양이 사장':'--c7','다람쥐 코치':'--c8','도치 실장':'--c9'}
    PITCH = {'윙키':9,'다람쥐 코치':6,'고양이 사장':4,'판다':2,'너구리 대리':0,'펭귄 선생님':-2,'도치 실장':-4,'거북 여사':-5,'곰 아빠':-7}
    PROPOSED = {'다람쥐 코치','고양이 사장','너구리 대리','도치 실장','거북 여사'}

    cards = []; overview = []; nav = []
    for idx, (title, body) in enumerate(chars, 1):
        m = re.match(r'\d+\. (.+?) \((.+)\)', title); name, meta = m.group(1), m.group(2)
        slug = f'c{idx}'
        fields = {}
        for chunk in body.split('\n#### ')[1:]:
            k, v = chunk.split('\n', 1); fields[k.strip()] = v.strip()
        F = lambda k: fields.get(k, '')
        nav.append(f'<a href="#{slug}" style="--dot:var({COL[name]})">{E(name)}</a>')
        overview.append(f'<tr><td><a href="#{slug}" class="nm" style="--dot:var({COL[name]})">{E(name)}</a></td><td class="pr">{inline(F("어떤 사람"))}</td><td>{inline(F("속마음"))}</td></tr>')
        cards.append(f'''
    <section class="card" id="{slug}" style="--me:var({COL[name]})">
      <header class="ch">
        <div><h3>{E(name)}</h3><p class="meta">{E(meta)}</p></div>
        <span class="pitch" title="말소리 음높이(반음)">{'+' if PITCH[name]>0 else ''}{PITCH[name]}{' 제안' if name in PROPOSED else ''}</span>
      </header>
      <p class="one">{inline(F("어떤 사람"))}</p>
      <p class="funny"><span class="lab">웃기는 방식</span> {inline(F("웃기는 방식"))}</p>
      <div class="principle"><span class="lab">속마음</span><p>{inline(F("속마음"))}</p></div>
      <div class="grid2">
        <div><h4>하는 행동</h4>{block(F("하는 행동"))}</div>
        <div><h4>자주 틀리는 생각</h4>{block(F("자주 틀리는 생각"))}</div>
      </div>
      <h4>말투</h4>{block(F("말투"))}
      <h4>예시 대화</h4>
      <div class="dialogs">{block(F("예시 대화"))}</div>
      <div class="grid2 foot">
        <div><h4>정보는 이렇게</h4>{block(F("정보는 이렇게"))}</div>
        <div><h4>조심할 것</h4>{block(F("조심할 것"))}</div>
      </div>
    </section>''')

    # pitch scale svg-ish via html
    scale = ''.join(f'<span class="pt" style="--x:{(PITCH[n]+8)/18*100:.1f}%;--dot:var({COL[n]})" title="{E(n)} {PITCH[n]}"><i></i><em>{E(n)}</em></span>' for n in sorted(PITCH, key=lambda k: PITCH[k]))

    restmap = {t: b for t, b in rest}
    def find(prefix):
        for t,b in rest:
            if t.startswith(prefix): return t,b
        return None,''
    _, rel = find('누구랑')
    _, glance = find('한눈에')
    _, same = find('같은 일')
    _, seeds = find('에피소드 씨앗')
    _, prop = find('정해 주실 것')
    seed_html = []
    for chunk in re.split(r'\n### ', '\n'+seeds)[1:]:
        t, b = chunk.split('\n',1)
        mt = re.match(r'(\w)\. 「(.+?)」 \((.+?)\)\s*(\*.*\*)?', t)
        head = f'<span class="sl">{mt.group(1)}</span><h3>「{E(mt.group(2))}」</h3><p class="meta">{inline(mt.group(3))}</p>' if mt else f'<h3>{inline(t)}</h3>'
        note = f'<p class="note">{inline(mt.group(4).strip("*"))}</p>' if mt and mt.group(4) else ''
        seed_html.append(f'<article class="seed">{head}{note}{block(b)}</article>')
    seed_intro = seeds.split('\n### ')[0]

    page = f'''<title>모래언덕 빌라 인물 바이블</title>
    <meta name="claude:viewport-fit-sides" content="cover">
    <link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Jua&family=Gowun+Dodum&family=IBM+Plex+Sans+KR:wght@400;600&display=swap">
    <style>
    /* 레이아웃: 사막 빌라 종이 겹 — 모래색 바탕, 인물마다 색 점, 대사는 방송 자막 띠처럼 */
    :root{{
      --bg:#f3efe6; --paper:#fffdf8; --ink:#2b2a26; --mute:#6f6a5e; --line:#ddd5c4;
      --accent:#2f7d6d; --accent-2:#e9f2ee; --strip:#ffffff; --stripInk:#24231f;
      --c1:#e2a54b; --c2:#8a5a3c; --c3:#3d3d3d; --c4:#3b6e9c; --c5:#6f8f4e; --c6:#8c7a63; --c7:#d0773f; --c8:#b5622f; --c9:#7a6f8f;
      --f-d:"Jua","Gowun Dodum",system-ui,sans-serif; --f-b:"Gowun Dodum","IBM Plex Sans KR",system-ui,sans-serif; --f-u:"IBM Plex Sans KR",system-ui,sans-serif;
    }}
    @media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#1d1c19;--paper:#262521;--ink:#ece6d8;--mute:#a7a091;--line:#3a3833;--accent:#6cc3ad;--accent-2:#23342f;--strip:#f4f1e8;--stripInk:#1d1c19;--c3:#bdbdbd;color-scheme:dark}}}}
    :root[data-theme="dark"]{{--bg:#1d1c19;--paper:#262521;--ink:#ece6d8;--mute:#a7a091;--line:#3a3833;--accent:#6cc3ad;--accent-2:#23342f;--strip:#f4f1e8;--stripInk:#1d1c19;--c3:#bdbdbd;color-scheme:dark}}
    body{{background:var(--bg);color:var(--ink);font-family:var(--f-b);font-size:16px;line-height:1.7}}
    .wrap{{max-width:1040px;margin:0 auto;padding-block:32px 80px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}}
    h1,h2,h3{{font-family:var(--f-d);font-weight:400;line-height:1.25;text-wrap:balance;margin:0}}
    h1{{font-size:clamp(30px,5vw,46px)}} h2{{font-size:26px;margin-top:56px}} h3{{font-size:22px}}
    h4{{font-family:var(--f-u);font-size:13px;letter-spacing:.06em;color:var(--mute);margin:18px 0 6px;font-weight:600}}
    p{{margin:.4em 0}} ul{{margin:.3em 0;padding-left:1.2em}} li{{margin:.2em 0}}
    code{{font-family:var(--f-u);font-size:.85em;background:var(--accent-2);padding:0 .3em;border-radius:3px}}
    .lead{{max-width:68ch;color:var(--mute)}}
    .ok{{font-family:var(--f-u);font-size:11px;background:var(--accent);color:var(--paper);padding:0 6px;border-radius:9px;margin:0 2px;vertical-align:1px}}
    .nav{{display:flex;flex-wrap:wrap;gap:8px;margin:22px 0 0}}
    .nav a,.nm{{--dot:var(--accent);display:inline-flex;align-items:center;gap:6px;text-decoration:none;color:var(--ink);font-family:var(--f-d);font-size:16px}}
    .nav a{{background:var(--paper);border:1px solid var(--line);padding:4px 12px;border-radius:20px}}
    .nav a::before,.nm::before{{content:"";width:10px;height:10px;border-radius:50%;background:var(--dot)}}
    .nav a:hover,.nav a:focus-visible{{border-color:var(--accent);outline:none}}
    .scale{{position:relative;margin:28px 0 8px;height:86px;border-bottom:2px solid var(--line)}}
    .scale .pt{{position:absolute;left:var(--x);bottom:-7px;transform:translateX(-50%);display:flex;flex-direction:column-reverse;align-items:center;gap:4px}}
    .scale .pt i{{width:12px;height:12px;border-radius:50%;background:var(--dot);border:2px solid var(--bg)}}
    .scale .pt em{{font-style:normal;font-family:var(--f-u);font-size:11px;color:var(--mute);writing-mode:vertical-rl;white-space:nowrap}}
    .scalecap{{display:flex;justify-content:space-between;font-family:var(--f-u);font-size:12px;color:var(--mute)}}
    .tbl{{overflow-x:auto;margin:10px 0}}
    table{{border-collapse:collapse;width:100%;font-size:15px}}
    th,td{{text-align:left;vertical-align:top;padding:9px 10px;border-bottom:1px solid var(--line)}}
    th{{font-family:var(--f-u);font-size:12px;color:var(--mute);font-weight:600;letter-spacing:.04em}}
    td.pr{{font-family:var(--f-d);font-size:17px}}
    .card{{background:var(--paper);border:1px solid var(--line);border-top:6px solid var(--me);border-radius:6px;padding:22px clamp(16px,3vw,30px);margin-top:28px;scroll-margin-top:16px}}
    .ch{{display:flex;justify-content:space-between;align-items:flex-start;gap:12px}}
    .meta{{color:var(--mute);font-family:var(--f-u);font-size:13px;margin:2px 0 0}}
    .pitch{{font-family:var(--f-u);font-size:12px;color:var(--mute);border:1px solid var(--line);padding:2px 9px;border-radius:12px;white-space:nowrap}}
    .one{{font-size:17px;margin-top:12px}}
    .principle{{margin:16px 0 4px;padding:14px 18px;background:var(--accent-2);border-radius:6px}}
    .principle .lab{{font-family:var(--f-u);font-size:12px;color:var(--accent);font-weight:600;letter-spacing:.06em}}
    .principle p{{font-family:var(--f-d);font-size:clamp(19px,2.6vw,23px);line-height:1.45;margin:4px 0 0}}
    .grid2{{display:grid;grid-template-columns:1fr 1fr;gap:4px 28px}} .grid2>div{{min-width:0}}
    @media (max-width:720px){{.grid2{{grid-template-columns:1fr}}}}
    .dialogs{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}}
    @media (max-width:900px){{.dialogs{{grid-template-columns:1fr}}}}
    .dialogs>*{{min-width:0}}
    .sit{{font-size:14px;color:var(--mute);margin:6px 0}}
    .sitk{{display:inline-block;font-family:var(--f-u);font-size:12px;font-weight:600;color:var(--ink);background:var(--line);padding:0 8px;border-radius:10px;margin-right:6px}}
    .dlg{{background:#8d9a8a22;border-radius:6px;padding:10px;display:flex;flex-direction:column;gap:6px}}
    .line{{display:flex;flex-direction:column;gap:2px}}
    .who{{font-family:var(--f-u);font-size:11px;color:var(--mute)}}
    .strip{{align-self:flex-start;background:var(--strip);color:var(--stripInk);font-family:var(--f-d);font-size:17px;padding:3px 10px;border-radius:2px;box-shadow:0 1px 0 #0000001a;max-width:100%}}
    .inner .strip{{background:transparent;color:var(--mute);font-style:italic;box-shadow:none;border:1px dashed var(--line)}}
    .inner .strip::before{{content:"( "}} .inner .strip::after{{content:" )"}}
    .whisper .strip{{font-size:14px;border:1px dotted var(--mute)}}
    .shout .strip{{font-size:20px;clip-path:polygon(0 8%,4% 0,96% 0,100% 10%,98% 50%,100% 92%,95% 100%,4% 100%,0 90%,2% 50%)}}
    .silence .strip.mute{{background:transparent;box-shadow:none;color:var(--mute);font-family:var(--f-u);font-size:12px;letter-spacing:.2em}}
    .tag{{font-family:var(--f-u);font-size:10px;background:var(--stripInk);color:var(--strip);padding:0 5px;border-radius:8px;margin-right:4px;vertical-align:2px}}
    .big{{font-size:1.25em}} .sfx{{font-family:var(--f-d);color:#c0392b}} .emph{{font-style:normal;font-weight:700}}
    details{{border-top:1px solid var(--line);margin-top:14px;padding-top:8px}}
    summary{{cursor:pointer;font-family:var(--f-u);font-size:13px;font-weight:600;color:var(--mute)}}
    summary:focus-visible{{outline:2px solid var(--accent);outline-offset:2px}}
    .foot{{border-top:1px solid var(--line);margin-top:14px}}
    .seeds{{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:16px}}
    @media (max-width:820px){{.seeds{{grid-template-columns:1fr}}}}
    .seed{{background:var(--paper);border:1px solid var(--line);border-radius:6px;padding:18px 20px;min-width:0}}
    .seed .sl{{font-family:var(--f-u);font-size:12px;color:var(--accent);font-weight:600}}
    .seed .note{{font-size:13px;color:var(--mute)}}

    .funny{{margin:8px 0 0;font-size:15px}} .funny .lab{{font-family:var(--f-u);font-size:12px;font-weight:600;color:var(--accent);margin-right:4px}}
    .hint{{font-size:14px;color:var(--mute)}}
    @media (prefers-reduced-motion:no-preference){{html{{scroll-behavior:smooth}}}}
    </style>
    <div class="wrap">
      <p class="meta">윙키와 친구들 · 모래언덕 빌라 · 2판 2026-11-12</p>
      <h1>인물 바이블</h1>
      <p class="lead">아홉 명을 친구가 소개하듯 적었습니다. 어떤 사람인지, 속으로 무슨 생각을 하는지, 무슨 행동을 하는지. 인물은 웃기려고 하지 않고 다들 자기 딴에는 진지합니다. 예시 대화의 띠 한 줄이 실제 자막 한 줄(14자 이하)입니다.</p>
      <nav class="nav" aria-label="인물">{''.join(nav)}</nav>

      <h2>한눈에: 아홉 명이 서로 다른 점</h2>
      {block(glance)}
      <h2>같은 일, 아홉 가지 반응</h2>
      {block(same)}

      <h2>말소리 음높이</h2>
      <p class="hint">동물 말소리의 높낮이(반음). 「제안」이 붙은 다섯은 새로 정한 값이라 들어 보고 맞춥니다. 이웃한 값은 빠르기와 크기로 같이 가릅니다.</p>
      <div class="scale" aria-hidden="true">{scale}</div>
      <div class="scalecap"><span>낮게 −8</span><span>0</span><span>높게 +10</span></div>

      <h2>인물 카드</h2>
      <p class="hint">자막 표기: <span class="strip" style="font-size:14px">보통 대사</span> · 속마음은 점선 괄호 · 작은 글씨는 속삭임 · 뾰족한 띠는 외침 · <span class="tag">놀람</span> 같은 꼬리표는 말소리 감정 · 「― 침묵」은 대사 없는 반응 컷</p>
      {''.join(cards)}

      <h2>누구랑 누가 부딪히나</h2>
      <p class="hint">이야기가 계속 나오는 짝입니다.</p>
      {block(rel)}

      <h2>에피소드 씨앗</h2>
      {block(seed_intro)}
      <div class="seeds">{''.join(seed_html)}</div>

      <h2>정해 주실 것</h2>
      {block(prop)}
    </div>'''
    return page


if __name__ == '__main__':
    page = render(open(sys.argv[1], encoding='utf-8').read())
    open(sys.argv[2], 'w', encoding='utf-8').write(page)
    print(len(page))
