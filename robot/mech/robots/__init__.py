import json

from robot.mech    import Serial
from spatial       import Mesh
from robot.visual  import STLParser

with open('./robot/mech/robots/abb_irb_120.json') as json_file:
  serial_dictionary = json.load(json_file)

if 'mesh_file' in serial_dictionary.keys():
  meshes = Mesh.from_file(STLParser(), f'./robot/mech/robots/meshes/{serial_dictionary["mesh_file"]}')

ABB_IRB_120 = Serial.from_dict_meshes(serial_dictionary, meshes or [])
