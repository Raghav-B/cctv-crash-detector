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
        self.cur_indexes = set()

        i = 0
        while (i < len(cur_objects)):
            j = 0
            while (j < len(prev_objects)):
                # Getting distance between each pair of objects in the prev_frame_objects and cur_frame_objects
                temp_dist = self.get_dist(prev_objects[j][0], cur_objects[i][0])
                
                # If this conditional is true, it means we've identified an object in cur_frame_objects
                # as an old one in prev_frame_objects.
                if (temp_dist <= self.min_thresh_dist):
                    # This triggers if two objects happen to be VERY close together and so the algo is
                    # getting confused. This conditional ensures that the algo continues searching for
                    # the appropriate old object by skipping the current one.
                    if (prev_objects[j][1] in self.cur_indexes) == True:
                        j += 1
                        print("close detection")
                        continue
                    
                    # Adding the index to our set of currently in-use indexes so we can assign
                    # unused indexes to new items
                    self.cur_indexes.add(prev_objects[j][1])

                    cur_objects[i][1] = prev_objects[j][1]
                    
                    # Incrementing the frame count of the object, unless the object's frame count is
                    # already 3.
                    #if (prev_objects[j][2] < 3):
                    #    cur_objects[i][2] = prev_objects[j][2] + 1
                    #elif (prev_objects[j][2] == 3):
                    #    cur_objects[i][2] = 3
                    cur_objects[i][2] = prev_objects[j][2] + 1

                    break
                    # We can safely break because we assume that there is only one possible point that
                    # in such close proximity to our current point to be indexed.
                
                j += 1
            i += 1
        
        # This iterates through the cur_frame_objects again and sees which ones have not 
        # been assigned an index
        for new_object in cur_objects:
            if new_object[1] == -1:
                new_object[1] = self.find_next_free_index()
                self.cur_indexes.add(new_object[1])
            
        return cur_objects

"""
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