from . import AnimateFSM
from utils import magnitude, EPSILON

from statemachine import State

class AttackFSM(AnimateFSM):
    """Three-state FSM for walking, stopping, and attacking in
       a top-down environment."""
    
    standing = State(initial=True)
    moving   = State()
    attacking = State()
    shooting = State()
    hurting = State()
    
    move = (standing.to(moving) 
            | moving.to.itself(internal=True) 
            | attacking.to(moving)
            | shooting.to(moving)
            | hurting.to(moving))
    
    stop = (moving.to(standing) 
            | standing.to.itself(internal=True) 
            | attacking.to(standing)
            | shooting.to(standing)
            | hurting.to(standing))
    
    attack = (standing.to(attacking) 
              | moving.to(attacking) 
              | attacking.to.itself(internal=True)
              | shooting.to(attacking)
              | hurting.to(attacking))

    shoot = (standing.to(shooting)
             | moving.to(shooting)
             | attacking.to(shooting)
             | hurting.to(shooting)
             | shooting.to.itself(internal=True))
    
    endAttack = (attacking.to(standing) | attacking.to(moving))
    endShoot = (shooting.to(standing) | shooting.to(moving))
    
    hurt = ((standing).to(hurting) 
        | moving.to(hurting) 
        | attacking.to(hurting) 
        | shooting.to(hurting)
        | hurting.to.itself(internal=True))
    
    endHurt = (hurting.to(standing) 
               | hurting.to(moving) 
               | hurting.to(attacking)
               | hurting.to(shooting))
    
    def __init__(self, obj):
        super().__init__(obj)
        self.attackTimer = 0
        self.attackDuration = 0
        self.shootTimer = 0
        self.shootDuration = 0
        self.hurtTimer = 0
        self.hurtDuration = 0
    
    def update(self, seconds=0):
        """Override update to decrement timer properly"""
        if self.attackTimer > 0:
            self.attackTimer -= seconds
        if self.shootTimer > 0:
            self.shootTimer -= seconds
        if self.hurtTimer > 0:
            self.hurtTimer -= seconds
        self.updateState()
    
    def updateState(self):
        #if hurt animation is finished, retur to standing/moving.
        if self =="hurting":
            if self.hurtTimer <= 0:
                if self.hasVelocity():
                    self.move()
                else:
                    self.endHurt()
            return

        if self == "shooting":
            if self.shootTimer <= 0:
                if self.hasVelocity():
                    self.move()
                else:
                    self.endShoot()
            return
        
        # If attack animation is finished, return to standing/moving
        if self == "attacking" and self.attackTimer <= 0:
            if self.hasVelocity():
                self.move()
            else:
                self.endAttack()

        # Handle normal movement states
        elif self.hasVelocity() and self != "moving" and self != "attacking" and self != "shooting":
            self.move()
        elif not self.hasVelocity() and self != "standing" and self != "attacking" and self != "shooting":
            self.stop()
    
    def hasVelocity(self):
        return magnitude(self.obj.velocity) > EPSILON
    
    def startAttack(self):
        """Called when attack key is pressed"""
        self.attack()
        # Calculate duration in seconds: frames / fps
        nFrames = self.obj.nFramesList.get("attacking", 4)
        fps = self.obj.framesPerSecondList.get("attacking", 8)
        self.attackDuration = nFrames / max(fps, 1)
        self.attackTimer = self.attackDuration

    def startShoot(self):
        """Called when shoot key is pressed"""
        self.shoot()
        nFrames = self.obj.nFramesList.get("shooting", 1)
        fps = self.obj.framesPerSecondList.get("shooting", 8)
        self.shootDuration = nFrames / max(fps, 1)
        self.shootTimer = self.shootDuration

    def startHurt(self):
        """Called when hurt - if no hurt animation, just use standing animation parameters"""
        
        if "hurting" not in self.obj.rowList:
            self.obj.rowList["hurting"] = self.obj.rowList.get("standing", 0)
        if "hurting" not in self.obj.nFramesList:
            self.obj.nFramesList["hurting"] = self.obj.nFramesList.get("standing", 1)
        if "hurting" not in self.obj.framesPerSecondList:
            self.obj.framesPerSecondList["hurting"] = self.obj.framesPerSecondList.get("standing", 8)

        self.hurt()
        # Also calculates duration in seconds: frames / fps
        nFrames = self.obj.nFramesList.get("hurting", 1)
        fps = self.obj.framesPerSecondList.get("hurting", 8)
        self.hurtDuration = nFrames / max(fps, 1)
        self.hurtTimer = self.hurtDuration