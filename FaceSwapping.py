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
        t2_rectangle_int.append(((t_2[i][0] - r_2[0]), (t_2[i][1] - r_2[1])))

    # Get mask by filling triangle
    mask = np.zeros((r_2[3], r_2[2], 3), dtype=np.float32)
    cv2.fillConvexPoly(mask, np.int32(t2_rectangle_int), (1.0, 1.0, 1.0), 16, 0)

    # Apply warpImage to small rectangular patches
    img1_rectangle = img_1[r_1[1]:r_1[1] + r_1[3], r_1[0]:r_1[0] + r_1[2]]
    # img2_rectangle = np.zeros((r_2[3], r_2[2]), dtype = img1_rectangle.dtype)

    size = (r_2[2], r_2[3])

    img2_rectangle = affine_transform(img1_rectangle, t1_rectangle, t2_rectangle, size)

    img2_rectangle = img2_rectangle * mask

    # Copy triangular region of the rectangular patch to the output image
    img_2[r_2[1]:r_2[1] + r_2[3], r_2[0]:r_2[0] + r_2[2]] = img_2[r_2[1]:r_2[1] + r_2[3], r_2[0]:r_2[0] + r_2[2]] * (
            (1.0, 1.0, 1.0) - mask)

    img_2[r_2[1]:r_2[1] + r_2[3], r_2[0]:r_2[0] + r_2[2]] = img_2[r_2[1]:r_2[1] + r_2[3], r_2[0]:r_2[0] + r_2[2]] + img2_rectangle


if __name__ == '__main__':

    # Read images
    filename_1 = 'matthew.jpg'
    filename_2 = 'benedict.jpg'

    img_1 = cv2.imread(filename_1)
    img_2 = cv2.imread(filename_2)
    img1_warped = np.copy(img_2)

    # Read array of corresponding points
    points_1 = read_points(filename_1 + '.txt')
    points_2 = read_points(filename_2 + '.txt')

    # Find convex hull
    hull_1 = []
    hull_2 = []

    hull_index = cv2.convexHull(np.array(points_2) , returnPoints=False)

    for i in range(0 , len(hull_index)):
        hull_1.append(points_1[int(hull_index[i])])
        hull_2.append(points_2[int(hull_index[i])])

    # Find delaunay traingulation for convex hull points
    size_img2 = img_2.shape
    rectangle = (0, 0, size_img2[1], size_img2[0])

    y = calculate_delaunay_triangle(rectangle, hull_2)

    if len(y) == 0:
        quit()

    # Apply affine transformation to delaunay triangles
    for i in range(0, len(y)):
        t_1 = []
        t_2 = []

        # get points for image1, image2 corresponding to the triangles
        for j in range(0, 3):
            t_1.append(hull_1[y[i][j]])
            t_2.append(hull_2[y[i][j]])

        warp_triangle(img_1, img1_warped, t_1, t_2)

    # Calculate Mask
    hull_8U = []
    for i in range(0, len(hull_2)):
        hull_8U.append((hull_2[i][0], hull_2[i][1]))

    mask = np.zeros(img_2.shape, dtype=img_2.dtype)

    cv2.fillConvexPoly(mask, np.int32(hull_8U), (255, 255, 255))

    r = cv2.boundingRect(np.float32([hull_2]))

    center = ((r[0] + int(r[2] / 2), r[1] + int(r[3] / 2)))

    # Clone seamlessly
    output = cv2.seamlessClone(np.uint8(img1_warped), img_2, mask, center, cv2.NORMAL_CLONE)

    cv2.imshow("Image 1", img_1)
    cv2.imshow("Image 2", img_2)
    cv2.imshow("Face Swapping", output)
    cv2.waitKey(0)

    cv2.destroyAllWindows()