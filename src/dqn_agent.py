"""DQN Agent with epsilon-greedy exploration."""
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from pathlib import Path

from .network import QNetwork
from .replay_buffer import ReplayBuffer


class DQNAgent:
    """Deep Q-Network agent."""

    def __init__(self, obs_shape, n_actions, config):
        self.n_actions = n_actions
        self.gamma = config["agent"]["gamma"]
        self.batch_size = config["agent"]["batch_size"]
        self.use_target_network = config["agent"]["use_target_network"]
        self.target_update_freq = config["agent"]["target_update_freq"]
        self.device = torch.device(config.get("device", "cpu"))

        # Epsilon schedule
        self.epsilon = config["agent"]["epsilon_start"]
        self.epsilon_end = config["agent"]["epsilon_end"]
        self.epsilon_decay_steps = config["agent"]["epsilon_decay_steps"]
        self.epsilon_decay = (self.epsilon - self.epsilon_end) / self.epsilon_decay_steps

        # Networks
        self.q_network = QNetwork(obs_shape, n_actions).to(self.device)
        self.target_network = QNetwork(obs_shape, n_actions).to(self.device)
        self.target_network.load_state_dict(self.q_network.state_dict())
        self.target_network.eval()

        # Optimizer
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=config["agent"]["lr"])

        # Replay buffer
        self.buffer = ReplayBuffer(config["agent"]["buffer_size"])

        # Step counter
        self.total_steps = 0

    def select_action(self, state, evaluate=False):
        """Epsilon-greedy action selection."""
        if not evaluate and np.random.random() < self.epsilon:
            return np.random.randint(self.n_actions)

        with torch.no_grad():
            state_t = torch.FloatTensor(state).unsqueeze(0).to(self.device)
            q_values = self.q_network(state_t)
            return q_values.argmax(dim=1).item()

    def store_transition(self, state, action, reward, next_state, done):
        """Store transition in replay buffer."""
        self.buffer.push(state, action, reward, next_state, done)

    def update(self):
        """Perform one gradient update step."""
        if len(self.buffer) < self.batch_size:
            return None

        # Sample batch
        states, actions, rewards, next_states, dones = self.buffer.sample(self.batch_size)

        states_t = torch.FloatTensor(states).to(self.device)
        actions_t = torch.LongTensor(actions).to(self.device)
        rewards_t = torch.FloatTensor(rewards).to(self.device)
        next_states_t = torch.FloatTensor(next_states).to(self.device)
        dones_t = torch.FloatTensor(dones).to(self.device)

        # Current Q values
        q_values = self.q_network(states_t).gather(1, actions_t.unsqueeze(1)).squeeze(1)

        # Target Q values
        with torch.no_grad():
            if self.use_target_network:
                next_q_values = self.target_network(next_states_t).max(dim=1)[0]
            else:
                next_q_values = self.q_network(next_states_t).max(dim=1)[0]
            target = rewards_t + self.gamma * next_q_values * (1 - dones_t)

        # Loss and update
        loss = nn.MSELoss()(q_values, target)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        # Update epsilon
        self.total_steps += 1
        self.epsilon = max(self.epsilon_end, self.epsilon - self.epsilon_decay)

        # Update target network
        if self.use_target_network and self.total_steps % self.target_update_freq == 0:
            self.target_network.load_state_dict(self.q_network.state_dict())

        return loss.item()

    def save(self, path):
        """Save model checkpoint."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        torch.save({
            "q_network": self.q_network.state_dict(),
            "target_network": self.target_network.state_dict(),
            "optimizer": self.optimizer.state_dict(),
            "epsilon": self.epsilon,
            "total_steps": self.total_steps,
        }, path)

    def load(self, path):
        """Load model checkpoint."""
        checkpoint = torch.load(path, map_location=self.device, weights_only=True)
        self.q_network.load_state_dict(checkpoint["q_network"])
        self.target_network.load_state_dict(checkpoint["target_network"])
        self.optimizer.load_state_dict(checkpoint["optimizer"])
        self.epsilon = checkpoint["epsilon"]
        self.total_steps = checkpoint["total_steps"]
