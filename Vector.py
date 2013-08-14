#!/usr/bin/env python3

import math

class Vector:
    def __init__(self, initx, inity, initz):
        self.x = initx
        self.y = inity
        self.z = initz

    def str(self):
        return "%.6f %.6f %.6f" % (self.x,self.y,self.z)

    def point(self):
        return (self.x,self.y,self.z)

    def __str__(self):
        return '(%s,%s,%s)' % (self.x, self.y, self.z)

    def __repr__(self):
        return 'Vector(%s,%s,%s)' % (self.x, self.y, self.z)

    def magnitude(self):
        return math.sqrt(self.dot(self))

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)        

    def scale(self, factor):
        return Vector(factor * self.x, factor * self.y, factor * self.z)

    def dot(self, other):
        return (self.x * other.x) + (self.y * other.y) + (self.z * other.z)

    def cross(self, other):
        return Vector(self.y * other.z - self.z * other.y,
                      self.z * other.x - self.x * other.z,
                      self.x * other.y - self.y * other.x)

    def normalized(self):
        return self.scale(1.0 / self.magnitude())

    def negated(self):
        return self.scale(-1)

    def __eq__(self, other):
        return (self.x == other.x) and (self.y == other.y) and (self.z == other.z)

    def reflectThrough(self, normal):
        d = normal.scale(self.dot(normal))
        return self - d.scale(2)

    def reflectedNormal(self,reflect):
        n = self.normalized() + reflect.normalized()
        return n.normalized()

    def rotateAxis(self,k,theta):
        # Rodrigues' rotation formula
        p1 = self.scale(math.cos(theta))
        p2 = k.cross(self).scale(math.sin(theta))
        p3 = k.scale(k.dot(self)).scale(1.0 - math.cos(theta))
        return p1 + p2 + p3

