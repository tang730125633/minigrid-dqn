"""Environment utilities: wrappers and helpers for MiniGrid."""
import numpy as np
import gymnasium as gym
import minigrid
from minigrid.wrappers import ImgObsWrapper


class RewardShapingWrapper(gym.Wrapper):
    """Potential-Based Reward Shaping (PBRS) wrapper.

    Adds shaped reward: r_shaped = r_original + gamma * Phi(s') - Phi(s)
    where Phi(s) = 1 - (manhattan_distance_to_goal / max_distance)

    Reference: Ng et al., 1999 - Policy invariance under reward transformations.
    """

    def __init__(self, env, gamma=0.99, scale=1.0):
        super().__init__(env)
        self.gamma = gamma
        self.scale = scale
        self.prev_potential = None
        # Goal is always at bottom-right corner in Empty env (width-2, height-2)
        self.goal_pos = None
        self.max_distance = None

    def _get_agent_pos(self):
        """Get agent position from unwrapped env."""
        return self.unwrapped.agent_pos

    def _get_goal_pos(self):
        """Get goal position. In Empty env, goal is at (width-2, height-2)."""
        if self.goal_pos is None:
            grid = self.unwrapped.grid
            for i in range(grid.width):
                for j in range(grid.height):
                    cell = grid.get(i, j)
                    if cell is not None and cell.type == "goal":
                        self.goal_pos = np.array([i, j])
                        self.max_distance = (grid.width - 2) + (grid.height - 2)
                        return self.goal_pos
            # Fallback: bottom-right corner
            self.goal_pos = np.array([grid.width - 2, grid.height - 2])
            self.max_distance = (grid.width - 2) + (grid.height - 2)
        return self.goal_pos

    def _potential(self, agent_pos):
        """Compute potential: higher when closer to goal."""
        goal = self._get_goal_pos()
        dist = abs(agent_pos[0] - goal[0]) + abs(agent_pos[1] - goal[1])
        return self.scale * (1.0 - dist / max(self.max_distance, 1))

    def reset(self, **kwargs):
        obs, info = self.env.reset(**kwargs)
        self.goal_pos = None  # Reset goal cache
        self.prev_potential = self._potential(self._get_agent_pos())
        return obs, info

    def step(self, action):
        obs, reward, terminated, truncated, info = self.env.step(action)

        # Store original reward for evaluation
        info["original_reward"] = reward

        # Compute PBRS
        current_potential = self._potential(self._get_agent_pos())
        shaping = self.gamma * current_potential - self.prev_potential
        self.prev_potential = current_potential

        shaped_reward = reward + shaping
        info["shaped_reward"] = shaped_reward
        info["shaping_bonus"] = shaping

        return obs, shaped_reward, terminated, truncated, info


class ObsPreprocessWrapper(gym.ObservationWrapper):
    """Convert (H, W, C) uint8 image to (C, H, W) float32 normalized."""

    def __init__(self, env):
        super().__init__(env)
        old_space = env.observation_space
        self.observation_space = gym.spaces.Box(
            low=0.0,
            high=1.0,
            shape=(old_space.shape[2], old_space.shape[0], old_space.shape[1]),
            dtype=np.float32,
        )

    def observation(self, obs):
        # (H, W, C) -> (C, H, W), normalize to [0, 1]
        return np.transpose(obs, (2, 0, 1)).astype(np.float32) / 255.0


def make_env(config, reward_shaping=False):
    """Create and wrap MiniGrid environment."""
    env = gym.make(config["env"]["name"], max_steps=config["env"]["max_steps"])
    env = ImgObsWrapper(env)  # Extract image observation

    if reward_shaping:
        env = RewardShapingWrapper(
            env,
            gamma=config["agent"]["gamma"],
            scale=config["reward_shaping"].get("scale", 1.0),
        )

    env = ObsPreprocessWrapper(env)  # Must be last: converts observation format
    return env
