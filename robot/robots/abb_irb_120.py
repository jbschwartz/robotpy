import math

from ..mech import Joint, Serial

robot = Serial([
  Joint(math.radians( -90),    0, math.radians(   0),  290, { 'low': math.radians(-165), 'high': math.radians(165) }),
  Joint(math.radians(   0),  270, math.radians( -90),    0, { 'low': math.radians(-110), 'high': math.radians(110) }),
  Joint(math.radians( -90),   70, math.radians(   0),    0, { 'low': math.radians(-110), 'high': math.radians(70) }),
  Joint(math.radians(  90),    0, math.radians(   0),  302, { 'low': math.radians(-160), 'high': math.radians(160) }),
  Joint(math.radians( -90),    0, math.radians(   0),    0, { 'low': math.radians(-120), 'high': math.radians(120) }),
  Joint(math.radians(   0),    0, math.radians( 180),   72, { 'low': math.radians(-400), 'high': math.radians(400) })
])
