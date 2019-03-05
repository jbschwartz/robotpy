import math

# pylint: disable=F0401
from .robots import abb_irb_120
from .visual import RobotPlot

if __name__ == "__main__":

  ABB_IRB_120 = abb_irb_120.robot

  show = {
    'waypoints': True,
    'ee_frame': True,
    'base_frame': True,
    'joint_angles': True
  }

  plot = RobotPlot(ABB_IRB_120, show = show)

  traj = []

  q6 = math.radians(0)
  for q0 in range(0, 90, 2):
    q6 += math.radians(6)
    traj.append([math.radians(q0)] + [math.radians(45)] * 4 + [q6])

  for q1 in range(43, 0, -2):
    q6 += math.radians(6)
    traj.append([math.radians(88), math.radians(q1)] + [math.radians(45)] * 3 + [q6])

  plot.trajectory(traj)

  plot.show(animate = True, loop = True)