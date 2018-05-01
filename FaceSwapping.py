# -------------------------------------------------------------------------------
# Name:        Face Swapping
# Author:      Wa'el Ahmad Muhammad
#              Nurhan Allam Mohammed
# Created:     20/04/2018

# -------------------------------------------------------------------------------

import cv2
import numpy as np



def affine_transform(src, src_triangle, dst_triangle, size):

    # Given a pair of triangles, find the affine transform.
    warp_mat = cv2.getAffineTransform(np.float32(src_triangle), np.float32(dst_triangle))

    # Apply the Affine Transform just found to the src image
    destination = cv2.warpAffine(src, warp_mat, (size[0], size[1]), None, flags=cv2.INTER_LINEAR ,
                         borderMode=cv2.BORDER_REFLECT_101)

    return destination


# Read points from text file
def read_points(path):

    # Create an array of points.
    points = []

    # Read points
    with open(path) as file:
        for line in file:
            x, y = line.split()
            points.append((int(x), int(y)))

    return points


# Check if a point is inside a rectangle
def rect_contains_points(rectangle, point):
    if point[0] < rectangle[0]:
        return False
    elif point[1] < rectangle[1]:
        return False
    elif point[0] > rectangle[0] + rectangle[2]:
        return False
    elif point[1] > rectangle[1] + rectangle[3]:
        return False
    return True

# Calculate delaunay triangulation
def calculate_delaunay_triangle(rectangle, points):
    # Create subdiv
    subdiv = cv2.Subdiv2D(rectangle)

    # Insert points into subdiv
    for i in points:
        subdiv.insert(i)
    triangle_list = subdiv.getTriangleList()
    delaunay_triangle = []
    pt = []
    for l in triangle_list:
        pt.append((l[0], l[1]))
        pt.append((l[2], l[3]))
        pt.append((l[4], l[5]))
        pt1 = (l[0], l[1])
        pt2 = (l[2], l[3])
        pt3 = (l[4], l[5])

        if rect_contains_points(rectangle, pt1) and rect_contains_points(rectangle, pt2) and rect_contains_points(rectangle, pt3):
            index = []

            # Get face-points (from 68 face detector) by coordinates
            for j in range(0, 3):
                for k in range(0, len(points)):
                    if (abs(pt[j][0] - points[k][0]) < 1.0 and abs(pt[j][1] - points[k][1]) < 1.0):
                        index.append(k)

                        # Three points form a triangle. Triangle array corresponds to the file tri.txt in FaceMorph
            if len(index) == 3:
                delaunay_triangle.append((index[0], index[1], index[2]))

        pt = []

    return delaunay_triangle

# Warps and alpha blends triangular regions from image_1 and image_2 to image
def warp_triangle(img_1, img_2, t_1, t_2):

    # Find bounding rectangle for each triangle
    r_1 = cv2.boundingRect(np.float32([t_1]))
    r_2 = cv2.boundingRect(np.float32([t_2]))

    # Offset points by left top corner of the respective rectangles
    t1_rectangle = []
    t2_rectangle = []
    t2_rectangle_int = []

    for i in range(0, 3):
        t1_rectangle.append(((t_1[i][0] - r_1[0]), (t_1[i][1] - r_1[1])))
        t2_rectangle.append(((t_2[i][0] - r_2[0]), (t_2[i][1] - r_2[1])))
        t2_reimg_2[r_2[1]:r_2[1] + r_2[3], r_2[0]:r_2[0] + r_2[2]] = img_2[r_2[1]:r_2[1] + r_2[3], r_2[0]:r_2[0] + r_2[2]] * (
            (1.0, 1.0, 1.0) - mask)

    img_2[r_2[1]:r_2[1] + r_2[3], r_2[0]:r_2[0] + r_2[2]] = img_2[r_2[1]:r_2[1] + r_2[3], r_2[0]:r_2[0] + r_2[2]] + img2_rectangle


    
