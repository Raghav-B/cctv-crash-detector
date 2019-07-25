class object_sorter:
    min_thresh_dist = 40 # This minimum distance is almost perfect right now.
    max_thresh_dist = 100 # unused for now
    cur_indexes = set()
    init_index = -1

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
                else:
                    cur_objects[i][3] = prev_objects[corres_prev_obj][3].copy()
                    cur_objects[i][3].popleft()
                    cur_objects[i][3].append(cur_objects[i][0])
                
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
        self.cur_indexes = set()
        recognized_indexes = set()
        
        
        i = 0
        while (i < len(cur_objects) and len(prev_objects) != 0):
            min_dist_so_far = 9999999#self.get_dist(prev_objects[0][0], cur_objects[i][0])
            min_dist_index = None

            j = 0

            is_cur_object_recognized = False


            while (j < len(prev_objects)):
                # Getting distance between each pair of objects in the prev_frame_objects and cur_frame_objects
                new_check_dist = self.get_dist(prev_objects[j][0], cur_objects[i][0])
                print(new_check_dist, min_dist_so_far)
                if new_check_dist <= min_dist_so_far:
                    min_dist_so_far = new_check_dist
                    min_dist_index = j

                    print("new min: " + str(min_dist_so_far))
            
                j += 1

            self.cur_indexes.add(prev_objects[min_dist_index][1])
            cur_objects[i][1] = prev_objects[min_dist_index][1]
            print(self.cur_indexes)

            # Read description below to see what's going on here
            if (prev_objects[min_dist_index][2] < 5): # change this to 3
                cur_objects[i][3] = prev_objects[min_dist_index][3].copy()
                cur_objects[i][3].append(cur_objects[i][0])
            else:
                cur_objects[i][3] = prev_objects[min_dist_index][3].copy()
                cur_objects[i][3].popleft()
                cur_objects[i][3].append(cur_objects[i][0])
            
            cur_objects[i][2] = prev_objects[min_dist_index][2] + 1
                
                # If this conditional is true, it means we've identified an object in cur_frame_objects
                # as an old one in prev_frame_objects.
                #if (temp_dist <= self.min_thresh_dist):
                    # This triggers if two objects happen to be VERY close together and so the algo is
                    # getting confused. This conditional ensures that the algo continues searching for
                    # the appropriate old object by skipping the current one.
                #    if (prev_objects[j][1] in self.cur_indexes) == True:
                #        j += 1
                #        print("close detection")
                #        continue
                    
                    # Adding the index to our set of currently in-use indexes so we can assign
                    # unused indexes to new items
                    
                    #self.cur_indexes.add(prev_objects[j][1])

                    #cur_objects[i][1] = prev_objects[j][1]
                    
                    # Read description below to see what's going on here
                    #if (prev_objects[j][2] < 5): # change this to 3
                    #    cur_objects[i][3] = prev_objects[j][3].copy()
                    #    cur_objects[i][3].append(cur_objects[i][0])
                    #else:
                    #    cur_objects[i][3] = prev_objects[j][3].copy()
                    #    cur_objects[i][3].popleft()
                    #    cur_objects[i][3].append(cur_objects[i][0])
                    
                    #    cur_objects[i][2] = prev_objects[j][2] + 1
                    #elif (prev_objects[j][2] == 3):
                    #    cur_objects[i][2] = 3
                    
                    # Incrementing the frame count of the object
                    #cur_objects[i][2] = prev_objects[j][2] + 1

                    #break
                    # We can safely break because we assume that there is only one possible point that
                    # in such close proximity to our current point to be indexed.
                
                #j += 1
            i += 1
        
        # This iterates through the cur_frame_objects again and sees which ones have not 
        # been assigned an index
        for new_object in cur_objects:
            if new_object[1] == -1:
                new_object[1] = self.find_next_free_index()
                self.cur_indexes.add(new_object[1])

If an object is concurrently detected for 3 frames, we begin to draw its vector.

Init frame is not considered the first frame, I suppose you could call it the zeroth frame... 

For a particular object
First frame:
    - Increment frame counts from 0 to 1
    - Add midpoint to deque via append()
Second frame:
    - Increment frame counts from 1 to 2
    - Add midpoint to deque via append()
Third frame:
    - Increment frame counts from 2 to 3
    - Add midpoint to deque via append()
    - Get vector from 3rd frame midpoint and first frame midpoint

Fourth frame:
    - Keep frame count at 3
    - Remove 1st frame midpoint using popleft()
    - Add midpoint to deque via append()
    - Get vector from 2nd frame midpoint and 4th frame midpoint
Fifth frame:
    - Keep frame count at 3
    - Remove 2nd frame midpoint using popleft()
    - Add midpoint to deque via append()
    - Get vector from 3rd frame midpoint and 5th frame midpoint

So this is what an object inside cur_frame_objects or prev_frame_objects will look like:
    - Index 0: Tuple containing midpoint
    - Index 1: Index of object used for object tracking
    - Index 2: Number of frames detected for
    - Index 3: Deque containing midpoints for past 3 frames. Length of this is the same as the value in Index 2
"""