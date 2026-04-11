"""Mobile Module - Extends Animated to add physics-based movement and velocity.

The Mobile class adds movement and velocity to animated objects. It handles velocity
application with max speed clamping, allowing smooth acceleration and deceleration.
Dashing bypasses max velocity constraints to allow high-speed movement bursts.

Physics Features:
- Velocity vector with magnitude-based clamping (except during dash)
- Position updates based on velocity and elapsed time
- Max velocity enforcement to prevent unrealistic speed
- Dash immunity to max velocity for temporary speed boosts
"""
from . import Animated
from utils import vec, magnitude, scale

class Mobile(Animated):
    def __init__(self, position, fileName=""):
        super().__init__(position, fileName)
        self.velocity = vec(0,0)
        self.maxVelocity = 200
    
    def update(self, seconds):
        super().update(seconds)
        # Only cap velocity if not dashing (allow dash to exceed maxVelocity)
        if not getattr(self, 'isDashing', False):
            if magnitude(self.velocity) > self.maxVelocity:
                self.velocity = scale(self.velocity, self.maxVelocity)
        self.position += self.velocity * seconds