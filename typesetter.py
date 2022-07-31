
from PyQt5.QtWidgets import QGraphicsItem
from PyQt5.QtSvg import QSvgGenerator
from PyQt5.QtCore import QBuffer, QSize, QRectF
from PyQt5.QtGui import QPainter
from neoscore.interface.qt.q_rich_text_item import QRichTextItem

def monkey(self):
    super().__init__()
    self.setCacheMode(QGraphicsItem.CacheMode.NoCache)
QRichTextItem.__init__ = monkey


import math
import json
import re
from neoscore.core import neoscore
from neoscore.core.brush import Brush
from neoscore.core.flowable import Flowable
from neoscore.core.music_text import MusicText, MusicFont
from neoscore.core.text import Text
from neoscore.core.units import ZERO, Mm
from neoscore.western.clef import Clef
from neoscore.western.duration import Duration
from neoscore.western.chordrest import Chordrest
from neoscore.western.key_signature import KeySignature
from neoscore.western.staff import Staff
from neoscore.western.barline import Barline, barline_style
from neoscore.western.barline_style import BarlineStyle



neoscore.setup()

flowable = Flowable((Mm(0), Mm(10)), None, Mm(500), Mm(30), Mm(10))

staff = Staff((Mm(0), Mm(10)), flowable, Mm(500))
bstaff = Staff((Mm(0), Mm(25)), flowable, Mm(500))
unit = staff.unit
bunit = staff.unit
clef = Clef(ZERO, staff, "treble")
bclef = Clef(ZERO, bstaff, "bass")
KeySignature(ZERO, staff, "c_major")
KeySignature(ZERO, bstaff, "c_major")


font = MusicFont("Bravura", Mm(1.8))





# logic about timing


tns = []
def timedObject(b, ti):
    d, o, l = ti # duration offset length
    def f(time):
        for t in b:
            if (time - o) % l > (-30 % l):
                
                col = (150, 150, 150)
            if ((time - o) % l) < d:
                col = (0, 0, 0)
            else:
                rem = (((time - o) % l) - d) / l
                c = int(200 - 50 * rem)

                col = (c, c, c)
            t.brush = Brush.from_existing(t.brush, col)
    tns.append((l, f))


# score objects we can use in text representation

def rl():
    return [MusicText((center, unit(4)), staff, "repeatLeft", font),
    MusicText((center, bunit(4)), bstaff, "repeatLeft", font)]

def rr():
    return [MusicText((center, unit(4)), staff, "repeatRight", font),
    MusicText((center, bunit(4)), bstaff, "repeatRight", font)]

def coda():
    global center
    center -= Mm(10)
    c = [MusicText((center, unit(-2)), staff, "coda", font)]
    center -= Mm(6)
    return c 

def segno():
    global center
    center -= Mm(10)
    s = [MusicText((center, unit(-2)), staff, "segno", font)]
    center -= Mm(6)
    return s

def dalSegno():
    return [MusicText((center, unit(-2)), staff, "dalSegno", font)]

def dsac():
    return [MusicText((center - Mm(10), unit(-2)), staff, "dalSegno", font), Text((center, unit(-2)), staff, 'alla coda'),
            Barline(center, [staff,bstaff])
            ]

# Read score, construct neoscore representation and timing functions


center = unit(0)
with open('score.txt') as score:
    for line in score:
        if line:
            if '\t' in line:
                for chord, s in zip(line.split('\t'), [staff, bstaff]):
                    notes = []
                    nts = []
                    accts = []
                    for n, nt, acc, acct in re.findall("([a-g](?:'+|,+)?)(?:\((\d+ \d+ \d+)\))?(?:(b|#)(?:\((\d+ \d+ \d+)\))?)?", chord):
                        notes.append(n[0] + acc + n[1:])
                        nts.append(nt)
                        if acc != '':
                            accts.append(acct)
                    
                    if notes:
                        c = Chordrest(center, s, notes, Duration(1, 4))
                        for h, n in zip(c.noteheads, nts):
                            if n != '':
                                timedObject([h], [int(d) for d in n.split(' ')])

                        for h, n in zip(c.accidentals, accts):
                            if n != '':
                                timedObject([h], [int(d) for d in n.split(' ')])
            
            else:
                f, t = re.match("(\w+)(?:\((\d+ \d+ \d+)\))?", line).groups()
                o = eval(f)()
                if t is not None:
                    timedObject(o, [int(d) for d in t.split(' ')])


            center += Mm(15)



# Create output
#
# currently done by rendering each frame as an svg, diffing them
# and using that to recreate each frame in javascript.
# More efficient would be to do this note by note, and move the
# timing and coordination logic into javascript too.


length = math.lcm(*[x[0] for x in tns])
print(f"generating {length} frames")

d = math.gcd(*[x[0] for x in tns])

count = 0

lines = {}
data = []

current_lines = []
initial = []
num_lines = None

for count in range(length):
    if (count % 100) == 0:
        print(count)
    for _, f in tns:
        f(count)
    neoscore.app_interface.clear_scene()
    for page in neoscore.document.pages:
        for obj in page.descendants:
            interfaces = getattr(obj, "interfaces", None)
            if interfaces:
                interfaces.clear()

    neoscore.document.render()
    source_rect = neoscore.app_interface.scene.sceneRect()
    generator = QSvgGenerator()
    generator.setSize(QSize(2000,2000))
    svg_buffer = QBuffer()
    generator.setOutputDevice(svg_buffer)

    painter = QPainter()
    painter.begin(generator)
    painter.setRenderHint(QPainter.Antialiasing)

    neoscore.app_interface.scene.render(painter, target=source_rect, source=source_rect)
    painter.end()
    
    changes = []
    lc = 0

    for lidx, l in enumerate(str(svg_buffer.buffer(), 'utf-8').split(' ')):
        if l not in lines:
            lines[l] = len(lines)

        if count > 0:
            if current_lines[lidx] != lines[l]:
                current_lines[lidx] = lines[l]
                changes.append((lidx, lines[l]))
        else:
            initial.append(lines[l])
            assert len(current_lines) == lidx
            current_lines.append(lines[l])

        lc += 1

    if count > 0:
        data.append(changes)
    if num_lines is None:
        num_lines = lc
    else:
        assert num_lines == lc


ld = [None] * len(lines)
for l, i in lines.items():
    ld[i] = l

for i, l in enumerate(ld):
    assert i == lines[l]


# Write output

with open('score.html', 'w') as f:
    f.write(f'''
<html>
<body>
<img id='score'/>
</body>
<script>

let score = document.getElementById('score');
var idx = 0;
let num_lines = {num_lines};
let initial = {initial};
let lines = {json.dumps([l for l in lines])};
let data = {json.dumps(data)};
var svg = []

function render() {{
    if (idx == 0) {{
        svg = initial.map(x=>lines[x]);
    }} else {{
        for(const diff of data[idx - 1]) {{
            svg[diff[0]] = lines[diff[1]];
        }}
    }}
    idx = (idx + 1) % data.length;
    score.src = 'data:image/svg+xml,' + escape(svg.join('\\n'));
    setTimeout(render, 20)
}}
render()

</script>
<body>''')





