"""
OBJECT TRACKING IMPLEMENTATION

It is extremely important to properly track objects across subsequent frames because by default, objects
do not necessarily retain their original indexes across frames. I.E. It is entirely possible that an object
with index 0 in the intitial frame is detected with index 1 in the next frame.

Our solution to this is fairly simple, but is nonetheless effective. In essense the pseudo code looks something
like this:

1 For every new object detected in the current frame:
    1.1 For every old object from the previous frame:
        1.1.1 Find an old object such that the distance between this old object and new object is the least
              among all combinations of old object and new object pairs.
    1.2 The old object with the least distance to the new object is most certainly the same object. This 
        is because an object can only move so far between subsequent frames so this distance will almost
        always be smaller than the distance between 2 different objects.
    1.3 Assign the new object the index of the corresponding old object.
    1.4 Update new object's number of frames detected and vectors accordingly.

However, the above algorithm only works if we assume that the number of objects across two frames will remain
constant. As soon as objects start disappearing and appearing, this algorithm will break down as objects detected
for the first time can be assigned the wrong index.

To solve this, we check if an old object has already been assigned to a new object. If this is the case and there
is a conflict between assigning two new objects to a single old object, we will compare the distances between
the two pairs and decide which new object the old object actually corresponds to. The incorrect new object is 
then marked as "not found" and will later be assigned a completely new index.

To facilitate assigning of new indexes, we use a simple set to store the indexes currently in use. To find an unused
index that is currently available, we simply start at index 0 and keep increasing the index until we find the
smallest unused index. This is what the find_next_free_index() function does.

Doing all of the above requires a myriad of information that is stored in prev_frame_objects and cur_frame_objects.
The structure of these lists has been detailed below:

prev_frame_objects structure:
Index 0: Tuple for the midpoint of the object
Index 1: Index of the object, used for unique indentification of objects
Index 2: Number of frames object has been consecutively detected for
Index 3: Deque to store midpoints of the object over the past 5 frames. Used for vector calculation
Index 4: Points to the in-array index of the new object that this old object has been assigned to. This
         is used to fix any conflicts between 2 or more new objects that have been assigned to the same
         old object. 
Index 5: Magnitude of object from previous frame

Structure for cur_frame_objects is the same, except that Index 4 is instead used as a flag to determine
whether the object has been assigned to a corresponding old object. This is useful for assigning completely
newly detected objects with an unused index.

OBJECT VECTOR CALCULATION

Every object in 


"""


class object_tracker:
    def __init__(self):
        self.cur_indexes = set() # Keeping track of currently in-use object indexes.
        self.init_index = -1 # Used when assigning indexes to objects in the very first frame

    # 
    def get_init_index(self):
        self.init_index += 1
        return self.init_index

    # A bit slow, because it runs linearly every frame, not so much an issue when there are only
    # very few objects to be detected on screen.
    def find_next_free_index(self):
        start = 0
        while True:
            if (start in self.cur_indexes) == True:
                start += 1
            else:
                return start

    def get_dist(self, prev_point, cur_point):
        y_square = (cur_point[1] - prev_point[1]) ** 2
        x_square = (cur_point[0] - prev_point[0]) ** 2
        return ((x_square + y_square) ** 0.5)

    def sort_cur_objects(self, prev_objects, cur_objects):
        # The int in prev_objects shows whether a previous object has already been identified as a new object
        # The int in cur_objects shows whether a new object has been identified as an old object.
        self.cur_indexes = set()

        for i in range(0, len(cur_objects)):
            min_dist = 99999 # Or initial value. I prefer making this a massively unreasonable value
            min_dist_index = None # Just initialize like this

            for j in range(0, len(prev_objects)):
                check_dist = self.get_dist(prev_objects[j][0], cur_objects[i][0])
                if (check_dist <= min_dist):
                    min_dist = check_dist
                    min_dist_index = j

            if (prev_objects[min_dist_index][4] != -1): # If the object had already been previously identified...
                # Get distance of current used old object and new object which this old object points to
                first_dist = self.get_dist(prev_objects[min_dist_index][0], cur_objects[prev_objects[min_dist_index][4]][0])
                # Get distance of current used old object and current new object we're checking for
                second_dist = self.get_dist(prev_objects[min_dist_index][0], cur_objects[i][0])

                # If current new object is actually the old used object
                if (second_dist <= first_dist):
                    self.cur_indexes.add(prev_objects[min_dist_index][1])
                    # Assign index correctly
                    cur_objects[i][1] = prev_objects[min_dist_index][1]
                    # Set previous new object as not unused
                    cur_objects[prev_objects[min_dist_index][4]][4] = -1
                    # Set current new object as used
                    cur_objects[i][4] = min_dist_index
                    # Make current old object point to the current new object
                    prev_objects[min_dist_index][4] = i
                
                # If previous new object was actually the old used object
                else:
                    cur_objects[i][4] = -1
                    continue

            else:
                self.cur_indexes.add(prev_objects[min_dist_index][1])
                cur_objects[i][1] = prev_objects[min_dist_index][1]
                prev_objects[min_dist_index][4] = i # Old object has been identified as a new object
                cur_objects[i][4] = min_dist_index

        for i in range(0, len(cur_objects)):
            if (cur_objects[i][4] != -1):
                corres_prev_obj = cur_objects[i][4]
                if (prev_objects[corres_prev_obj][2] < 5):
                    cur_objects[i][3] = prev_objects[corres_prev_obj][3].copy()
                    cur_objects[i][3].append(cur_objects[i][0])
                else: # If object has been detected for at least 5 frames.
                    cur_objects[i][3] = prev_objects[corres_prev_obj][3].copy()
                    cur_objects[i][3].popleft()
                    cur_objects[i][3].append(cur_objects[i][0])

                    # We make the current object store the previous objects vector
                    vector = [prev_objects[corres_prev_obj][3][-1][0] - prev_objects[corres_prev_obj][3][0][0], \
                        prev_objects[corres_prev_obj][3][-1][1] - prev_objects[corres_prev_obj][3][0][1]] # (x, y)
                    vector_mag = (vector[0]**2 + vector[1]**2)**(1/2)
                    cur_objects[i][5] = vector_mag
                
                cur_objects[i][2] = prev_objects[corres_prev_obj][2] + 1

        # This iterates through the cur_frame_objects again and sees which ones have not 
        # been assigned an index
        for new_object in cur_objects:
            if new_object[4] == -1:
                new_object[1] = self.find_next_free_index()
                self.cur_indexes.add(new_object[1])
            else:
                new_object[4] = -1
        
        return cur_objects