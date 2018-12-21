import torch
import torch.nn as nn
import torch.nn.functional as F


class CNNEncoder(nn.Module):
    def __init__(self, input_size, feature_maps=[50, 50, 50, 25, 25],
                 window_sizes=[1, 2, 3, 4, 5], dropout=0.0,
                 activation="relu"):

        assert len(feature_maps) == len(window_sizes)
        assert activation in ["relu", "tanh", "sigmoid"]
        super(CNNEncoder, self).__init__()

        self._dropout = dropout
        if activation == "relu":
            self._activation = nn.ReLU()
        elif activation == "tanh":
            self._activation = nn.Tanh()
        else:
            self._activation = nn.Sigmoid()

        def padding(ws):
            if ws == 1:
                return (0, 0)
            elif ws == 2:
                return (1, 0)
            if ws % 2 == 0:
                return (ws // 2, 0)
            else:
                return (ws // 2, 0)

        self._filters = nn.ModuleList(
            [nn.Conv2d(1, fm, (ws, input_size), padding=padding(ws))
             for fm, ws in zip(feature_maps, window_sizes)])

        self._output_size = sum(feature_maps)

    @property
    def output_size(self):
        return self._output_size

    def forward(self, inputs):
        inputs = inputs.unsqueeze(1)
        feature_maps = []
        for fltr in self._filters:
            preactivation = fltr(inputs).squeeze(3)
            act = self._activation(
                F.max_pool2d(preactivation, (1, preactivation.size(2))))
            feature_maps.append(act.squeeze(2))

        feature_maps = torch.cat(feature_maps, 1)
        feature_maps = F.dropout(
            feature_maps, p=self._dropout, training=self.training)

        return feature_maps

    def initialize_parameters(self):
        for name, param in self.named_parameters():
            if "weight" in name:
                nn.init.xavier_normal_(param)
            elif "bias" in name:
                nn.init.constant_(param, 1.)    
            else:
                nn.init.normal_(param)    