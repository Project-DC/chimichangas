# Agent class representing the NN for REINFORCE algorithm

# Import required libraries
import torch
import torch.nn as nn
from torch.distributions import Categorical
import torch.nn.functional as F
import numpy as np


class Agent(nn.Module):
    """
    Agent class for the model - REINFORCE

    Data members
    ============
    device (torch.device)
        : Device on which NN will be trained
    fc1    (torch.nn.Linear)
        : First dense layer of NN
    fc2    (torch.nn.Linear)
        : Second dense (output) layer of NN
    """

    def __init__(self, s_size, a_size, device, h_size=30):
        """
        Initializer for Agent class

        Params
        ======
        s_size (int)
            : State size of the agent
        a_size (int)
            : Number of possible actions that agent can take
        device (torch.device)
            : Device on which model will be trained
        h_size (int)
            : Number of neurons in hidden layer (optional)
        """

        super(Agent, self).__init__()
        self.device = device

        self.fc1 = nn.Linear(s_size, h_size)
        self.fc2 = nn.Linear(h_size, a_size)

    def forward(self, x):
        """
        Forward propagation

        Params
        ======
        x (torch.Tensor)
            : Input to neural network (state of the agent)

        Returns
        =======
        x     (torch.Tensor)
            : Input processed through NN
        embed (torch.Tensor)
            : Embedding of the agent from NN
        """

        # Pass through various layers and extract embeddings of first layer
        x = self.fc1(x)
        embed = x.clone()
        x = F.relu(x)
        x = self.fc2(x)

        # Return softmax of all the activations in final layer to return probability of choosing an action
        # also return the embedding for the agent
        return F.softmax(x, dim=1), embed.detach()

    def act(self, state, topk, is_rebel):
        """
        Take an action

        Params
        ======
        state (numpy.ndarray)
            : Input to neural network (state of the agent)

        Returns
        =======
        action           (numpy.ndarray)
            : Action taken at a particular state
        log_prob(action) (numpy.ndarray)
            : Log probability of that action
        embedding        (torch.Tensor)
            : Embedding from NN
        """

        state = torch.from_numpy(state).float().unsqueeze(0).to(self.device)
        probs, embed = self.forward(state)
        probs = probs.cpu()
        embed = embed.cpu()

        if is_rebel:
            values, indices = torch.topk(probs, k=13)
            return indices.detach().numpy()[0], indices.detach().numpy()[0][-1], torch.log(values), embed

        if topk > 1:
            values, indices = torch.topk(probs, k=topk)
            return indices.detach().numpy()[0], indices.detach().numpy()[0][0], torch.log(values), embed

        m = Categorical(probs)
        action = m.sample()
        return np.array([action.item()]), action.item(), np.array([m.log_prob(action)]), embed
