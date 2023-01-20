import mesa
import numpy as np



class Boid(mesa.Agent):
    """
    A Boid-style flocker agent.
    The agent follows three behaviors to flock:
        - Cohesion: steering towards neighboring agents.
        - Separation: avoiding getting too close to any other agent.
        - Alignment: try to fly in the same direction as the neighbors.
    Boids have a vision that defines the radius in which they look for their
    neighbors to flock with. Their speed (a scalar) and velocity (a vector)
    define their movement. Separation is their desired minimum distance from
    any other Boid.
    """
    

    def __init__(
        self,
        unique_id,
        model,
        pos,
        speed,      # scalar
        velocity,   # vector
        vision,
        separation, 
        cohere=0.025,
        separate=0.25,
        match=0.04,
    ):
        """
        Create a new Boid flocker agent.
        Args:
            unique_id: Unique agent identifyer.
            pos: Starting position
            speed: Distance to move per step.
            heading: numpy vector for the Boid's direction of movement.
            vision: Radius to look around for nearby Boids.
            separation: Minimum distance to maintain from other Boids.
            cohere: the relative importance of matching neighbors' positions
            separate: the relative importance of avoiding close neighbors
            match: the relative importance of matching neighbors' headings
        """
        super().__init__(unique_id, model)
        self.pos = np.array(pos)
        self.speed = speed
        self.velocity = velocity
        self.vision = vision
        self.separation = separation
        self.cohere_factor = cohere
        self.separate_factor = separate
        self.match_factor = match

    def cohere(self, neighbors):
        """
        Return the vector toward the center of mass of the local neighbors.
        """
        cohere = np.zeros(2)
        if neighbors:
            for neighbor in neighbors:
                cohere += self.model.space.get_heading(self.pos, neighbor.pos)
            cohere /= len(neighbors)
        return cohere

    def separate(self, neighbors):
        """
        Return a vector away from any neighbors closer than separation dist.
        """
        me = self.pos
        them = (n.pos for n in neighbors)
        separation_vector = np.zeros(2)
        for other in them:
            if self.model.space.get_distance(me, other) < self.separation:
                separation_vector -= self.model.space.get_heading(me, other)
        return separation_vector

    def match_heading(self, neighbors):
        """
        Return a vector of the neighbors' average heading.
        """
        match_vector = np.zeros(2)
        if neighbors:
            for neighbor in neighbors:
                match_vector += neighbor.velocity
            match_vector /= len(neighbors)
        return match_vector

    def pretty_plot(self, neighbors, new_pos):
        """
        Adjust boid placement in gui to reduce overlap    
        """

        me = new_pos
        them = (n.pos for n in neighbors)
        
        for other in them:
            if self.model.space.get_distance(me, other) < self.separation:
                new_pos += [2*(2*self.random.random()-1),2*(2*self.random.random()-1)] #hard coding in 2 here but could be tied to other factors
        
            #print(f"{self.separation= }  ; distance: {self.model.space.get_distance(me, other)= } ")
        
        #print(f"in method: agent {self.unique_id}, method new_pos {new_pos}")
        return new_pos

    def sep_angle_limit(self, neighbors):
        angle = np.rad2deg(np.arctan(self.velocity [1]/ self.velocity[0]));
       # print(self.velocity)
       # print(np.arctan(self.velocity))
      #  print(angle)
        if len(neighbors) == 0:
            n_neighbors = 1
        else:
            n_neighbors = len(neighbors)

        new_velocity = self.velocity + (self.separate(neighbors) * self.separate_factor) / n_neighbors
        
        new_angle = np.rad2deg(np.arctan(new_velocity [1] / new_velocity [0]))

        #print(np.absolute(new_angle - angle))
        if self.model.jiggle:
            if abs(new_angle - angle) > self.model.max_separate_turn:
                new_velocity = [1, np.tan(angle + np.sign(new_angle - angle) * self.model.max_separate_turn)]
        
        new_velocity /= np.linalg.norm(new_velocity)
        self.velocity = new_velocity


    def align_angle_limit(self, neighbors):
        angle = np.rad2deg(np.arctan(self.velocity [1]/ self.velocity[0]));

        if len(neighbors) == 0:
            n_neighbors = 1
        else:
            n_neighbors = len(neighbors)

        new_velocity = self.velocity + (self.match_heading(neighbors) * self.match_factor) / n_neighbors
        
        new_angle = np.rad2deg(np.arctan(new_velocity [1] / new_velocity [0]))

        #print(np.absolute(new_angle - angle))
        if self.model.jiggle:
            if abs(new_angle - angle) > self.model.max_align_turn:
                new_velocity = [1, np.tan(angle + np.sign(new_angle - angle) * self.model.max_align_turn)]
        
        new_velocity /= np.linalg.norm(new_velocity)
        self.velocity = new_velocity

    def cohere_angle_limit(self, neighbors):
        angle = np.rad2deg(np.arctan(self.velocity [1]/ self.velocity[0]));

        if len(neighbors) == 0:
            n_neighbors = 1
        else:
            n_neighbors = len(neighbors)

        new_velocity = self.velocity + (self.cohere(neighbors) * self.cohere_factor) / n_neighbors
        
        new_angle = np.rad2deg(np.arctan(new_velocity [1] / new_velocity [0]))

        #print(np.absolute(new_angle - angle))
        if self.model.jiggle:
            if abs(new_angle - angle) > self.model.max_cohere_turn:
                new_velocity = [1, np.tan(angle + np.sign(new_angle - angle) * self.model.max_cohere_turn)]
        
        new_velocity /= np.linalg.norm(new_velocity)
        self.velocity = new_velocity

    def step(self):
        """
        Get the Boid's neighbors, compute the new vector, and move accordingly.
        """
        
        neighbors = self.model.space.get_neighbors(self.pos, self.vision, False)
        them = (n.pos for n in neighbors)
        flag = False
        for other in them:
            if self.model.space.get_distance(self.pos, other) < self.separation:
                flag = True
        #
        if len(neighbors) == 0:
            n_neighbors = 1
        else:
            n_neighbors = len(neighbors)
        # Turning Rate is essential
        if flag:
            '''
            self.velocity += (
                self.separate(neighbors) * self.separate_factor
                ) / n_neighbors
            self.velocity /= np.linalg.norm(self.velocity)
            # can check 
            '''
            self.sep_angle_limit(neighbors)

            
        else: 
            '''
            self.velocity += (
                self.cohere(neighbors) * self.cohere_factor
                + self.match_heading(neighbors) * self.match_factor
            ) / n_neighbors
            self.velocity /= np.linalg.norm(self.velocity)  
            '''
            self.align_angle_limit(neighbors)
            self.cohere_angle_limit(neighbors)
            
            
        new_pos = self.pos + self.velocity * self.speed
        #print(f"in method: agent {self.unique_id}, method new_pos {new_pos}")

        # jiggle is for the pretty_plot function to hard code the separation
        #if self.model.jiggle:
            #print(f"in step before: {self.unique_id = }, method {new_pos =}")
        #    new_pos = self.pretty_plot(neighbors, new_pos)
            #print(f"after {self.unique_id = }, method {new_pos = }")

        self.model.space.move_agent(self, new_pos)

        '''
        def step(self):
        """
        Get the Boid's neighbors, compute the new vector, and move accordingly.
        """
        
        neighbors = self.model.space.get_neighbors(self.pos, self.vision, False)
        

        self.velocity += (
            self.cohere(neighbors) * self.cohere_factor
            + self.separate(neighbors) * self.separate_factor
            + self.match_heading(neighbors) * self.match_factor
        ) / 2
        self.velocity /= np.linalg.norm(self.velocity)  # Fallacious step?
        new_pos = self.pos + self.velocity * self.speed
        #print(f"in method: agent {self.unique_id}, method new_pos {new_pos}")

        # jiggle is for the pretty_plot function to hard code the separation
        if self.model.jiggle:
            #print(f"in step before: {self.unique_id = }, method {new_pos =}")
            new_pos = self.pretty_plot(neighbors, new_pos)
            #print(f"after {self.unique_id = }, method {new_pos = }")

        self.model.space.move_agent(self, new_pos)
        '''
