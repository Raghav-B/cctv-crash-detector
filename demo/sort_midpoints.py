class object_sorter:
    min_thresh_dist = 40
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

    # Index 0 is a tuple containing the midpoint of every bounding box
    # Index 1 is a tuple containing the bottom right corner of every bounding box
    # Index 2 is the index assigned to each object for tracking purposes
    # Index 3 is a count used to see how many frames an object has existed for.
    def sort_cur_objects(self, prev_objects, cur_objects):
        i = 0
        self.cur_indexes = set()
        
        while (i < len(cur_objects)):
            j = 0
            while (j < len(prev_objects)):
                temp_dist = self.get_dist(prev_objects[j][0], cur_objects[i][0])
                if (temp_dist <= self.min_thresh_dist):
                    cur_objects[i][1] = prev_objects[j][1]
                    #cur_objects[i][3] = temp_dist
                    self.cur_indexes.add(prev_objects[j][1])
                    break
                    # We can safely break because we assume that there is only one possible point that
                    # in such close proximity to our current point to be indexed.
                # In this event find the point closest to this one
                j += 1
            i += 1

        for new_object in cur_objects:
            if new_object[1] == -1:
                new_object[1] = self.find_next_free_index()
                self.cur_indexes.add(new_object[1])

        return cur_objects

"""
If an object is concurrently detected for 3 frames, we begin to draw its vector.

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