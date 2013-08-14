#!/usr/bin/env python3

import sys
import math
import struct
from Vector import Vector

laser = Vector(0,0,1)
wheel_axis = Vector(0,0,1)

# radius of wheel in mm, 1=inner,2=laser,3=outer
r_delta = 0.0675 * 25.4
r2 = 0.625 * 25.4
r1 = r2 - r_delta
r3 = r2 + r_delta

# dist_Ht - dist from laser target to screen in inches
# dist_Hb - dist from laser target to mirror below in inches
# dist_Wc - dist from laser target to center of screen in inches
dist_Ht = 0.265 * 25.4
dist_Hb = 1.405 * 25.4
dist_Wc = 2.500 * 25.4


# jv4779 vector in x,y px format
target_path_px = [
  [[-139.5,-40.5],[3,3],[3,-3],[-3,-3],[-3,3]],
  [[-136.5,-19.5],[0,51],[-3,9],[-6,3],[-6,0]],
  [[-118.5,-19.5],[18,42],[18,-42]],
  [[-22.5,1.5],[-45,0],[30,-42],[0,63]],
  [[-7.5,-40.5],[42,0],[-30,63]],
  [[52.5,-40.5],[42,0],[-30,63]],
  [[151.5,-19.5],[-3,9],[-6,6],[-9,3],[-3,0],[-9,-3],[-6,-6],[-3,-9],[0,-3],[3,-9],[6,-6],[9,-3],[3,0],[9,3],[6,6],[3,12],[0,15],[-3,15],[-6,9],[-9,3],[-6,0],[-9,-3],[-3,-6]]
]

#target_path_px = [
#  [[-45,45],[90,0],[0,-90],[-90,0],[0,90]]
#]

#target_path_px = [
#  [[-1.75*90,0],[3.5*90,0]]
#]

#target_path_px = [
#  [[-1.75*90,1.0*90],[3.5*90,0]]
#]

# convert from px into mm and absolute coords
target_path = []
target_path_len = []
for path_px in target_path_px:
	path_rel = [[j/90.0*25.4 for j in i] for i in path_px]
	p_abs = [0,0]
	path = []
	for p in path_rel:
		p_abs = [p_abs[0]+p[0],p_abs[1]+p[1]]
		path.append(p_abs)
	length=0.0
	for current, next in zip(path, path[1:]):
		length += math.sqrt(math.pow(current[0]-next[0],2) + math.pow(current[1]-next[1],2))
	target_path.append(path)
	target_path_len.append(length)

def image_xy_to_normal(x,y,Wc_adjust=0.0):
	return Vector(y,-2.0*dist_Hb - dist_Ht, dist_Wc - x).normalized()

def image_xy_to_theta_phi(x,y,Wc_adjust=0.0):
	#y=-y
	theta = math.atan( (dist_Ht + 2.0 * dist_Hb) / float(dist_Wc + Wc_adjust - x) )
	if y<0:
		phi = math.atan((dist_Wc + Wc_adjust - x)/float(y))
	else:
		phi = -math.radians(90) - math.atan(y/float(dist_Wc + Wc_adjust - x))
	return theta, phi

def image_xy_to_theta_phi_degrees(x,y,Wc_adjust=0.0):
	return [math.degrees(x) for x in image_xy_to_theta_phi(x,y,Wc_adjust)]

# convert 3d polar cord into cartesion x,y,z
def cart(r,theta,phi):
	x=r*math.sin(theta)*math.cos(phi)
	y=r*math.sin(theta)*math.sin(phi)
	z=r*math.cos(theta)
	return Vector(x,y,z)

if 0:
	for i in [[-1.75,1],[0,0],[1.75,-1]]:
		(x,y)=i
		theta,phi=image_xy_to_theta_phi(x,y)
		n = cart(1,theta,phi)
		print("polar %f,%f=%s %s"%(x,y,[theta,phi],n))
	
		n = image_xy_to_normal(x,y)
		print("vect %f,%f=%s %s"%(x,y,n,n.normalized()))
	
	sys.exit()

def facet(v1,v2,v3):
	n = (v2-v1).cross(v3-v1).normalized()

	print("  facet normal %s" % n.str())
	print("    outer loop")
	print("      vertex %s" % v1.str())
	print("      vertex %s" % v2.str())
	print("      vertex %s" % v3.str())
	print("    endloop")
	print("  endfacet")

# set target.z based on where its x,y would lye on plane with point p and normal n
def set_z_on_plane(target,n,p):
	z=((-n.x*(target.x-p.x)-n.y*(target.y-p.y))/n.z)+p.z
	return Vector(target.x,target.y,z)

def build_arc(start_rad, end_rad, total_segments, zero_segments, zero_level, normals):

	phi_delta = (end_rad-start_rad)/float(total_segments)
	zero_delta = zero_segments*phi_delta

	zero_normals = [Vector(0,0,1)] * zero_segments
	#normal = cart(1,math.pi/4,math.pi)

	(a1,a2,a3,b1,b2,b3) = build_arc_normals(start_rad, start_rad+zero_delta,
		zero_segments, zero_level, zero_normals)
	(c1,c2,c3,d1,d2,d3) = build_arc_normals(start_rad+zero_delta, end_rad-zero_delta,
		total_segments-2*zero_segments, 0, normals)
	(e1,e2,e3,f1,f2,f3) = build_arc_normals(end_rad-zero_delta, end_rad,
		zero_segments, zero_level, zero_normals)

	# fill in lead in and arc
	facet( c3, b3, b2 )
	facet( c2, c3, b2 )
	facet( c2, b2, b1 )
	facet( c1, c2, b1 )

	# fill arc and lead out	
	facet( d2, d1, e1 )
	facet( e2, d2, e1 )
	facet( d3, d2, e2 )
	facet( e3, d3, e2 )

def build_arc_normals(start_rad, end_rad, total_segments, z_start, normals):

	theta = math.pi/2.0
	phi_delta = (end_rad-start_rad)/float(total_segments)

	first = True
	l1 = cart(r1,theta,start_rad)
	l2 = cart(r2,theta,start_rad)
	l3 = cart(r3,theta,start_rad)

	l2.z = z_start

	for i in range(0,total_segments):
		d2 = start_rad + phi_delta * (i+1)
		d1 = d2 - phi_delta / 2.0
	
		p1 = cart(r1,theta,d1)
		p2 = cart(r2,theta,d2)
		p3 = cart(r3,theta,d1)

		n = normals[i]
		n = n.reflectedNormal(laser)
		n = n.rotateAxis(wheel_axis,d1-math.radians(90))

		p1 = set_z_on_plane(p1,n,l2)
		p2 = set_z_on_plane(p2,n,l2)
		p3 = set_z_on_plane(p3,n,l2)

		if first:
			l1 = set_z_on_plane(l1,n,p1)
			l3 = set_z_on_plane(l3,n,p3)
			start1 = l1
			start2 = l2
			start3 = l3
			first = False

		# bottom on plane triangle
		facet( l2, p2, p3 )
		# top on plane trinagle
		facet( p1, p2, l2 )

		# top infill
		facet( l2, p3, l3 )
		# bottom infill
		facet( l1, p1, l2 )

		l1 = p1
		l2 = p2
		l3 = p3

	p1 = cart(r1,theta,end_rad)
	p3 = cart(r3,theta,end_rad)

	p1 = set_z_on_plane(p1,n,l1)
	p3 = set_z_on_plane(p3,n,l3)

	# top infill
	facet( l2, p3, l3 )
	# bottom infill
	facet( l1, p1, l2 )

	return (start1,start2,start3,p1,l2,p3)

print("solid name")

total_path_len = sum(target_path_len)
total_paths = len(target_path)

degree_per_step = 0.5
zero_segments = 2
total_segments = 360 / float(degree_per_step)
image_sements = total_segments - 2*zero_segments*total_paths - 1
path_len_per_segment = total_path_len / float(image_sements)

#print("total_path_len=%f total_segments=%d"%(total_path_len,total_segments))
#print("image_sements=%d path_len_per_segment=%f"%(image_sements,path_len_per_segment))

start_rad = math.radians(90)

current=0
previous=0
calc_segments=0

for path in target_path:
	normals = []
	for p1, p2 in zip(path, path[1:]):
		#print("p1=%f,%f p2=%f,%f"%(p1[0],p1[1],p2[0],p2[1]))
		d=math.sqrt(math.pow(p2[0]-p1[0],2)+math.pow(p2[1]-p1[1],2))
		while d + previous >= current:
			c = current - previous
			x_c = (p2[0]-p1[0])*c/d+p1[0]
			y_c = (p2[1]-p1[1])*c/d+p1[1]
			#print("previous=%f current=%f d=%f c=%f,%f"%(previous,current,d,x_c,y_c))
			#(theta,phi) = image_xy_to_theta_phi(x_c,y_c)
			#print("theta=%f phi=%f"%(math.degrees(theta),math.degrees(phi)))
			#n = cart(1,theta,phi)
			n = image_xy_to_normal(x_c,y_c)
			#print("n=%s"%n)
			normals.append(n)
			current += path_len_per_segment
		previous += d
	path_segments = len(normals) + 2*zero_segments
	calc_segments += path_segments
	#print("path_segments=%d calc_segments=%d"%(path_segments,calc_segments))
	end_rad = start_rad - math.radians(degree_per_step)*path_segments
	build_arc(start_rad, end_rad, path_segments, zero_segments, -2.0, normals)
	start_rad = end_rad

#print("calc_segments=%d"%calc_segments)

print("endsolid name")


