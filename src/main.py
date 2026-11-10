from machine import Pin
from servo import Servo
import time

# Servo angle for each floor
# Floor 1 = 160°, Floor 2 = 121°, Floor 3 = 79°, Floor 4 = 42°, Floor 5 = 7.5°
values = [160, 121, 79, 42, 7.5]

MS_PER_DEGREE = 12  # higher = slower needle (floor 1 -> 5 takes ~1.8 s)


class Button:
    def __init__(self, pin_id):
        self.pin = Pin(pin_id, Pin.IN, Pin.PULL_UP)
        self.prev = 1
        self.last = time.ticks_ms()

    def pressed(self):
        now = self.pin.value()
        t = time.ticks_ms()
        hit = (self.prev == 1 and now == 0
               and time.ticks_diff(t, self.last) > 200)
        if hit:
            self.last = t
        self.prev = now
        return hit


class Needle:
    """Moves the servo smoothly to a target angle without blocking."""

    def __init__(self, servo, angle):
        self.servo = servo
        self.angle = angle
        self.start = angle
        self.target = angle
        self.t0 = time.ticks_ms()
        self.duration = 0
        self.servo.write(angle)

    def move_to(self, target):
        # Start from wherever the needle is right now, even mid-move
        self.start = self.angle
        self.target = target
        self.t0 = time.ticks_ms()
        self.duration = abs(target - self.start) * MS_PER_DEGREE

    def update(self):
        if self.angle == self.target:
            return
        elapsed = time.ticks_diff(time.ticks_ms(), self.t0)
        if self.duration == 0 or elapsed >= self.duration:
            self.angle = self.target
        else:
            p = elapsed / self.duration
            p = p * p * (3 - 2 * p)  # ease in/out, like an elevator
            self.angle = self.start + (self.target - self.start) * p
        self.servo.write(self.angle)


needle = Needle(Servo(pin_id=16), values[0])  # start at floor 1

# (button, floor index)
buttons = [
    (Button(15), 0),  # btn_a -> floor 1
    (Button(14), 1),  # btn_b -> floor 2
    (Button(13), 2),  # btn_c -> floor 3
    (Button(12), 3),  # btn_d -> floor 4
    (Button(11), 4),  # btn_e -> floor 5
]

while True:
    for btn, floor in buttons:
        if btn.pressed():
            needle.move_to(values[floor])
    needle.update()
    time.sleep_ms(10)