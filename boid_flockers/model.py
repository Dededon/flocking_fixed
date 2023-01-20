"""
Flockers
=============================================================
A Mesa implementation of Craig Reynolds's Boids flocker model.
Uses numpy arrays to represent vectors.
"""

import mesa
import numpy as np

from .boid import Boid



class BoidFlockers(mesa.Model):
    """
    Flocker model class. Handles agent creation, placement and scheduling.
    """
    jiggle = True
    use_seed_10 = True
    max_align_turn = 5
    max_cohere_turn = 3
    max_separate_turn = 1.5

    def __init__(
        self,
        population=100,
        width=500,
        height=500,
        speed=5,
        vision=10,
        separation=2,
        cohere=0.025,
        separate=0.25,
        match=0.04,
        jiggle = jiggle,
        use_seed_10 = use_seed_10,
        max_align_turn = max_align_turn,
        max_cohere_turn = max_cohere_turn,
        max_separate_turn = max_separate_turn,
        ):

        """
        Create a new Flockers model.
        Args:
            population: Number of Boids
            width, height: Size of the space.
            speed: How fast should the Boids move.
            vision: How far around should each Boid look for its neighbors
            separation: What's the minimum distance each Boid will attempt to
                    keep from any other
            cohere, separate, match: factors for the relative importance of
                    the three drives."""
        self.population = population
        self.vision = vision
        self.speed = speed
        self.separation = separation
        self.jiggle = jiggle
        self.use_seed_10 = use_seed_10
        if self.use_seed_10: 
            mesa.Model.reset_randomizer(self, seed=10), #allows us to all run similar simulations
        self.schedule = mesa.time.RandomActivation(self)
        self.space = mesa.space.ContinuousSpace(width, height, True)
        self.factors = dict(cohere=cohere, separate=separate, match=match)
        self.max_align_turn = max_align_turn
        self.max_cohere_turn = max_cohere_turn
        self.max_separate_turn = max_separate_turn;
        self.make_agents()
        self.running = True

    

    def make_agents(self):
        """
        Create self.population agents, with random positions and starting headings.
        """
        for i in range(self.population):
            x = self.random.random() * self.space.x_max
            y = self.random.random() * self.space.y_max
            pos = np.array((x, y))
            velocity = np.random.random(2) * 2 - 1
            velocity /= np.linalg.norm(velocity) # Need to be normalized to unit vector
            boid = Boid(
                i,
                self,
                pos,
                self.speed,
                velocity,
                self.vision,
                self.separation, 
                **self.factors
            )
            self.space.place_agent(boid, pos)
            self.schedule.add(boid)

    def step(self):
        self.schedule.step()