from boid_flockers.server import server

# What have I done:
# 1. Fix the speed and velocity initialization logic
# 2. Improve the cluster issue of the agents: the logic in the NetLogo code to process
# the issue of separation is different from the python example.
# the original author hardcoded the aggregation rule of turning rate, making it static and inflexible
# The NetLogo version has parameter max-turn to limit the turning rate
# 3. Altered separation range

server.launch()
