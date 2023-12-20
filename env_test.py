import gymnasium as gym
import phoenix_drone_simulation
import time

env = gym.make('DroneHoverBulletEnv-v0')
observation, info = env.reset()
random_action = env.action_space.sample()
next_observation, reward, terminated, truncated, info = env.step(random_action)

env = gym.make('DroneHoverBulletEnv-v0', render_mode="human")

while True:
    done = False
    x, _ = env.reset()
    while not done:
        random_action = env.action_space.sample()
        x, reward, terminated, truncated, info = env.step(random_action)
        done = terminated or truncated
        time.sleep(0.05)