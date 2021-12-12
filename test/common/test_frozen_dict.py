import unittest

from robot.common import FrozenDict

class TestFrozenDict(unittest.TestCase):
  def setUp(self):
    self.underlying = {
      'a': 1,
      'b': 2
    }

    self.fd = FrozenDict(self.underlying)

  def test_frozen_dict_accesses_with_dot_notation(self):
    for key, value in self.underlying.items():
      with self.subTest(f'Dictionary key {key}'):
        self.assertEqual(getattr(self.fd, key), value)

  def test_frozen_dict_sets_valid_keys(self):
    for key, value in self.underlying.items():
      new_value = value ** 2
      setattr(self.fd, key, new_value)
      self.assertEqual(getattr(self.fd, key), new_value)

  def test_frozen_dict_raises_getting_invalid_keys(self):
    with self.assertRaises(AttributeError):
      getattr(self.fd, 'this_key_doesnt_exist')

  def test_frozen_dict_raises_setting_invalid_keys(self):
    with self.assertRaises(AttributeError):
      self.fd.this_key_doesnt_exist = 2

    with self.assertRaises(AttributeError):
      getattr(self.fd, 'this_key_doesnt_exist')