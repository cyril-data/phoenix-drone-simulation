r"""Play and render a trained policy.

Author:     Sven Gronauer (sven.gronauer@tum.de)
"""
import gymnasium as gym
import time
import argparse
import os
import torch
import numpy as np

# local imports
from phoenix_drone_simulation.utils import utils


def play_after_training(actor_critic, env, noise=False):
    if not noise:
        actor_critic.eval()  # Set in evaluation mode before playing
    i = 0
    # pb.setRealTimeSimulation(1)
    while True:
        done = False
        x, info = env.reset()
        ret = 0.
        costs = 0.
        episode_length = 0
        while not done:
            obs = torch.as_tensor(x, dtype=torch.float32)
            action, *_ = actor_critic(obs)
            x, r, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            costs += info.get('cost', 0.)
            ret += r
            episode_length += 1
            time.sleep(1./120)
        i += 1
        print(
            f'Episode {i}\t Return: {ret}\t Length: {episode_length}\t Costs:{costs}')


def random_play(env_id, use_graphics):
    render_mode = "human " if use_graphics else None
    env = gym.make(env_id, render_mode=render_mode)
    i = 0
    rets = []
    TARGET_FPS = 60
    target_dt = 1.0 / TARGET_FPS
    while True:
        i += 1
        done = False
        env.reset()
        ts = time.time()
        ret = 0.
        costs = 0.
        ep_length = 0
        while not done:
            ts1 = time.time()
            action = env.action_space.sample()
            _, r, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            ret += r
            ep_length += 1
            costs += info.get('cost', 0.)
            delta = time.time() - ts1
            if delta < target_dt:
                time.sleep(target_dt-delta)  # sleep delta time
            # print(f'FPS: {1/(time.time()-ts1):0.1f}')
        rets.append(ret)
        print(f'Episode {i}\t Return: {ret}\t Costs:{costs} Length: {ep_length}'
              f'\t RetMean:{np.mean(rets)}\t RetStd:{np.std(rets)}')
        print(f'Took: {time.time()-ts:0.2f}')


if __name__ == '__main__':
    n_cpus = os.cpu_count()
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--ckpt', type=str, default=None,
                        help='Choose from: {ppo, trpo}')
    parser.add_argument('--env', type=str,
                        help='Example: HopperBulletEnv-v0')
    parser.add_argument('--random', action='store_true',
                        help='Visualize agent with random actions.')
    parser.add_argument('--noise', action='store_true',
                        help='Visualize agent with random actions.')
    parser.add_argument('--no-render', action='store_true',
                        help='Disable rendering.')
    args = parser.parse_args()
    env_id = None
    use_graphics = False if args.no_render else True

    if args.random:
        # play random policy
        assert env_id or hasattr(args, 'env'), 'Provide --ckpt or --env flag.'
        env_id = args.env if args.env else env_id
        random_play(env_id, use_graphics)
    else:
        assert args.ckpt, 'Define a checkpoint for non-random play!'
        ac, env = utils.load_actor_critic_and_env_from_disk(args.ckpt, "human")

        play_after_training(
            actor_critic=ac,
            env=env,
            noise=args.noise
        )