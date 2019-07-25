class object_tracker:
    def __init__(self):
        self.cur_indexes = set()
        self.init_index = -1

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
            # At the end of this loop we should be left with the index with the least distance
            # Yup, we know that we are able to identify items with the least distance

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

            # Read description below to see what's going on here
            #if (prev_objects[min_dist_index][2] < 5): # change this to 3
            #    cur_objects[i][3] = prev_objects[min_dist_index][3].copy()
            #    cur_objects[i][3].append(cur_objects[i][0])
            #else:
            #    cur_objects[i][3] = prev_objects[min_dist_index][3].copy()
            #    cur_objects[i][3].popleft()
            #    cur_objects[i][3].append(cur_objects[i][0])
            
            #cur_objects[i][2] = prev_objects[min_dist_index][2] + 1

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
        
"""
For the crash detection right, what I'm thinking of doing is storing the past 3 vectors for each object. When I'm about to pop an old vector (1st vector) and push a new vector (4th vector), I first check the euclidean distance between the old vectors and the new vector. This is where I'm thinking of a few different options:
1. Find distance between 3rd vector and 4th vector 
2. Find distance between mean vector of first 3 vectors and 4th vector
3. Find distance between mean vector of first 3 vectors and mean vector of some combination of the 4 vectors.

After finding the distance, we can output a probability of crash based on the distance between the two vectors. In flask you could probably create a slider that sets the threshold for crash notification. For example, if the probability of crash is above 90%, only then the user is informed in the UI, otherwise the UI keeps a silent log of all potential crashes regardless of probability of crash
I'm thinking 2nd option because averaging the vectors should help reduce random error, but not sure. Or I store 6 vectors and compare first 3 and next 3? This will further reduce errors I suppose
I think the 6 vector option is not bad, what do you guys think
"""