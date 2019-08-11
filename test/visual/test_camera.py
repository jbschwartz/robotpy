import math, unittest

from robot.spatial import Vector3
from robot.visual  import Camera

class TestCamera(unittest.TestCase):
  def setUp(self):
    self.camera = Camera()

  def test_default_camera_is_initialized_correctly(self):
    self.assertIsNotNone(getattr(self.camera, 'position', None))
    self.assertIsNotNone(getattr(self.camera, 'camera_to_world', None))
    self.assertIsNotNone(getattr(self.camera, 'world_to_camera', None))

    self.assertAlmostEqual(self.camera.position, Vector3().Y())

  def test_camera_orbit_does_not_change_distance_to_target(self):
    target = Vector3(4, 5, 6)
    initial_position = self.camera.position

    initial_distance = (target - initial_position).length()

    self.camera.orbit(target, 1, 2)

    final_position = self.camera.position
    final_distance = (target - final_position).length()

    self.assertAlmostEqual(initial_distance, final_distance)

  def test_camera_roll_does_not_change_camera_position(self):
    initial_position = self.camera.position
    self.camera.roll(math.radians(10))
    self.camera.roll(-math.radians(35))

    self.assertAlmostEqual(initial_position, self.camera.position)

  def test_camera_track_moves_in_camera_space_x_and_y(self):
    initial_position = self.camera.position
    initial_z_axis   = self.camera.camera_to_world(Vector3.Z(), as_type="vector")

    track_amount_camera_space = Vector3(10, -10)
    track_amount_world_space  = self.camera.camera_to_world(track_amount_camera_space, as_type="vector")

    self.camera.track(track_amount_camera_space.x, track_amount_camera_space.y)

    final_postion = self.camera.position
    final_z_axis  = self.camera.camera_to_world(Vector3.Z(), as_type="vector")

    # Check that the motion is orthogonal to the camera's Z axis
    delta = final_postion - initial_position
    dot = delta * initial_z_axis

    self.assertAlmostEqual(dot, 0)

    self.assertAlmostEqual(initial_position + track_amount_world_space, self.camera.position)
    self.assertAlmostEqual(initial_z_axis, final_z_axis)