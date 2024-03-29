# Robotpy

![Robotpy](http://schwartz.engineer/images/robotpy-2.gif)

Robot kinematics (and eventually dynamics) written in Python 3.

## Running

Install dependencies through `poetry`.

```
poetry install
python -m robot
```

## Testing

`python -m unittest`

### Running a Single Test File

For example, to run only the TestIntersection test class:

`python -m unittest -v test.spatial.test_intersection.TestIntersection`

## Controls

The visualization contains a relatively feature-full, CAD style camera.

### Shortcuts

See `robot/common/bindings.py` for all keyboard and mouse bindings.

#### Mouse
- Middle Mouse Drag: Orbit
- <kbd>Ctrl</kbd> + Middle Mouse Drag: Track
- <kbd>Alt</kbd> + Middle Mouse Drag: Roll
- <kbd>Shift</kbd> + Middle Mouse Drag: Scale
#### Camera Movement
- <kbd>←</kbd>: Orbit Left
- <kbd>→</kbd>: Orbit Right
- <kbd>↑</kbd>: Orbit Up
- <kbd>↓</kbd>: Orbit Down
- <kbd>Ctrl</kbd> + <kbd>←</kbd>: Track Right
- <kbd>Ctrl</kbd> + <kbd>→</kbd>: Track Left
- <kbd>Ctrl</kbd> + <kbd>↑</kbd>: Track Down
- <kbd>Ctrl</kbd> + <kbd>↓</kbd>: Track Up
- <kbd>Alt</kbd> + <kbd>←</kbd>: Roll Counter Clockwise
- <kbd>Alt</kbd> + <kbd>→</kbd>: Roll Clockwise
- <kbd>Z</kbd>: Scale In
- <kbd>Shift</kbd> + <kbd>Z</kbd>: Scale Out
#### Saved Views
- <kbd>Ctrl</kbd> + <kbd>1</kbd>: Front View
- <kbd>Ctrl</kbd> + <kbd>2</kbd>: Back View
- <kbd>Ctrl</kbd> + <kbd>3</kbd>: Left View
- <kbd>Ctrl</kbd> + <kbd>4</kbd>: Right View
- <kbd>Ctrl</kbd> + <kbd>5</kbd>: Top View
- <kbd>Ctrl</kbd> + <kbd>6</kbd>: Bottom View
- <kbd>Ctrl</kbd> + <kbd>7</kbd>: Isometric View
#### Other
- <kbd>Space</kbd>: Pause Animation
- <kbd>F</kbd>: Fit Scene
- <kbd>O</kbd>: Orbit Toggle (Free, Constrained)
- <kbd>P</kbd>: Projection Toggle (Orthographic, Perspective)

### License

This project is licensed under the MIT License. Please see `LICENSE` for details.