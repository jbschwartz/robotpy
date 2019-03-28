import math

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib as mpl
import matplotlib.animation as animation
mpl.rcParams['toolbar'] = 'None'

class RobotPlot:
  def __init__(self, robot, **kwargs):
    self.robot = robot
    self.frames = []

    self.show_flags = {
      'waypoints': False,
      'ee_frame': False,
      'base_frame': False,
      'joint_angles': False
    }

    # Check dictionary keys in show_flags to see if they're sensible?
    self.show_flags = self.show_flags if 'show' not in kwargs else { **self.show_flags, **(kwargs['show']) }

    self.scale = 50

    self.setup_plot_lib()

  def setup_plot_lib(self):
    self.fig = plt.figure(figsize=(12, 10))
  
    self.ax = []
    grid_size = (1, 1)
    if self.show_flags['joint_angles']:
      grid_size = (6, 2) 

      for i in range(0, 6):
        p = plt.subplot2grid(grid_size, (i, 1))
        p.set_xticklabels([])
        p.set_title(f'Joint #{i + 1}')
        self.ax.append(p)

    self.ax_3d = plt.subplot2grid(grid_size, (0, 0), rowspan=6, projection='3d')

    self.ax_3d.set_xlabel('X')
    self.ax_3d.set_ylabel('Y')
    self.ax_3d.set_zlabel('Z')

    self.ax_3d.set_xlim3d([-250, 250])
    self.ax_3d.set_ylim3d([-250, 250])
    self.ax_3d.set_zlim3d([0.0, 500])

  def trajectory(self, traj : list):
    joint_angles = [[], [], [], [], [], []]
    for qs in traj:
      self.frames.append(self.robot.poses(qs))
      for joint, q in zip(joint_angles, qs):
        joint.append(math.degrees(q))

    if self.show_flags['joint_angles']:
      for joint, p in zip(joint_angles,  self.ax):
        p.plot(joint)
        p.scatter(0,joint[0])

    self.generate_robot_points()
    
    first_frame_index = 0

    # Get initial robot position
    xs, ys, zs = self.robot_points[first_frame_index]
    self.robot_line = self.ax_3d.plot(xs, ys, zs=zs, color='orange', linewidth=5.0)[0]

    if self.show_flags['waypoints']:
      xs, ys, zs = [], [], []

      for frame in self.robot_points:
        xs.append(frame[0][-1])
        ys.append(frame[1][-1])
        zs.append(frame[2][-1])

      self.ax_3d.scatter(xs, ys, zs)

    if self.show_flags['ee_frame']:
      # Get intial end effector pose
      ee_axes_points = self.frame_points(self.frames[first_frame_index][6])
      self.ee_frame_lines = self.plot_frame(ee_axes_points)

  def generate_robot_points(self):
    self.robot_points = []

    # TODO: FRAMES ON FRAMES ON FRAMES ON FRAMES. Rename one, please.
    # For each frame in the animation, get the joint coordinate system positions
    for frame in self.frames:
      points = [[], [], []]

      # For each coordinate system position (i.e. joint)
      for coordinate_system in frame:
        # store the (x, y, z) position coordinate
        position = coordinate_system.position()
        for axis_position, axis_points in zip(position, points):
          axis_points.append(axis_position)

      self.robot_points.append(points)

  def frame_points(self, frame):
    pos = frame.position()
    axes = [frame.x(), frame.y(), frame.z()]

    coords = []

    for axis in axes:
      end = pos + (self.scale * axis)
      coords.append([[pos.x, end.x], [pos.y, end.y], [pos.z, end.z]])

    return coords

  def plot_frame(self, points):
    x_line = self.ax_3d.plot(points[0][0], points[0][1], zs=points[0][2], color='red')
    y_line = self.ax_3d.plot(points[1][0], points[1][1], zs=points[1][2], color='green')
    z_line = self.ax_3d.plot(points[2][0], points[2][1], zs=points[2][2], color='blue')

    return [x_line[0], y_line[0], z_line[0]]

  def update_plot(self, index):
    self.update_robot(index)

    if self.show_flags['ee_frame']:
      self.update_ee_frame(index)

    self.update_joint_plots(index)

    return [self.robot_line] + self.ee_frame_lines

  def update_robot(self, index):
    xs, ys, zs = self.robot_points[index]

    self.robot_line.set_data(xs, ys)
    self.robot_line.set_3d_properties(zs)

  def update_joint_plots(self, index):
    for ax in self.ax:
      del ax.collections[:]
      # I'm assuming there is only one line here...
      value = ax.get_lines()[0].get_ydata()[index]
      ax.scatter(index, value)

  def update_ee_frame(self, index):
    '''
    Redraw end-effector frame
    '''
    end_effector_index = 6
    axes_points = self.frame_points(self.frames[index][end_effector_index])

    # Indicies: x = 0, y = 1, z = 2
    for axis_index, axis_points in enumerate(axes_points):
      self.ee_frame_lines[axis_index].set_data(axis_points[0], axis_points[1])
      self.ee_frame_lines[axis_index].set_3d_properties(axis_points[2])

  def show(self, **kwargs):
    if not self.frames:
      # Raise error?
      plt.show()
      return

    if 'animate' in kwargs and kwargs['animate']:
      anim = animation.FuncAnimation(self.fig, self.update_plot, len(self.frames), interval=150, blit=False)

    # if 'loop' in kwargs and kwargs['loop']:
    #   # Duplicate trajectory, reverse, and append
    #   self.frames.extend(list(reversed(self.frames[0:len(self.frames)-1])))

    plt.show()