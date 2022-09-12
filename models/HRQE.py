import torch
import torch.autograd as autograd
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.autograd import Variable
import numpy as np
from .Model import Model
from numpy.random import RandomState


class HRQE(Model):
    def __init__(self, config):
        super(HRQE, self).__init__(config)
        # self.emb_s_a = nn.Embedding(self.config.entTotal, self.config.hidden_size)
        self.emb_x_a = nn.Embedding(self.config.entTotal, self.config.hidden_size)
        self.emb_y_a = nn.Embedding(self.config.entTotal, self.config.hidden_size)
        self.emb_z_a = nn.Embedding(self.config.entTotal, self.config.hidden_size)
        self.rel_s_b = nn.Embedding(self.config.relTotal, self.config.hidden_size)
        self.rel_x_b = nn.Embedding(self.config.relTotal, self.config.hidden_size)
        self.rel_y_b = nn.Embedding(self.config.relTotal, self.config.hidden_size)
        self.rel_z_b = nn.Embedding(self.config.relTotal, self.config.hidden_size)
        self.rel_w = nn.Embedding(self.config.relTotal, self.config.hidden_size)
        self.para = nn.Parameter(torch.tensor([0.5]), requires_grad=True) #定义可学习参数
        self.criterion = nn.Softplus()
        self.fc = nn.Linear(100, 50, bias=False)
        self.ent_dropout = torch.nn.Dropout(self.config.ent_dropout)
        self.rel_dropout = torch.nn.Dropout(self.config.rel_dropout)
        self.bn = torch.nn.BatchNorm1d(self.config.hidden_size)
        self.init_weights()

    def init_weights(self):
        if True:
            r, i, j, k = self.quaternion_init(self.config.entTotal, self.config.hidden_size)
            r, i, j, k = torch.from_numpy(r), torch.from_numpy(i), torch.from_numpy(j), torch.from_numpy(k)
            self.emb_x_a.weight.data = i.type_as(self.emb_x_a.weight.data)
            self.emb_y_a.weight.data = j.type_as(self.emb_y_a.weight.data)
            self.emb_z_a.weight.data = k.type_as(self.emb_z_a.weight.data)

            s, x, y, z = self.quaternion_init(self.config.relTotal, self.config.hidden_size)
            s, x, y, z = torch.from_numpy(s[:,:self.config.hidden_size]), torch.from_numpy(x), torch.from_numpy(y), torch.from_numpy(z)
            self.rel_s_b.weight.data = s.type_as(self.rel_s_b.weight.data)
            self.rel_x_b.weight.data = x.type_as(self.rel_x_b.weight.data)
            self.rel_y_b.weight.data = y.type_as(self.rel_y_b.weight.data)
            self.rel_z_b.weight.data = z.type_as(self.rel_z_b.weight.data)
            nn.init.xavier_uniform_(self.rel_w.weight.data)
        else:
            nn.init.xavier_uniform_(self.emb_s_a.weight.data)
            nn.init.xavier_uniform_(self.emb_x_a.weight.data)
            nn.init.xavier_uniform_(self.emb_y_a.weight.data)
            nn.init.xavier_uniform_(self.emb_z_a.weight.data)
            nn.init.xavier_uniform_(self.rel_s_b.weight.data)
            nn.init.xavier_uniform_(self.rel_x_b.weight.data)
            nn.init.xavier_uniform_(self.rel_y_b.weight.data)
            nn.init.xavier_uniform_(self.rel_z_b.weight.data)

    def _calc(self, x_a, y_a, z_a, x_c, y_c, z_c, s_b, x_b, y_b, z_b, rel_w, para):
    
        denominator_b = torch.sqrt(s_b ** 2 + x_b ** 2 + y_b ** 2 + z_b ** 2)
        denominator_a = torch.sqrt( x_a ** 2 + y_a ** 2 + z_a ** 2)
        denominator_c = torch.sqrt( x_c ** 2 + y_c ** 2 + z_c ** 2)
        rel_r = s_b / denominator_b
        rel_i = x_b / denominator_b
        rel_j = y_b / denominator_b
        rel_k = z_b / denominator_b

        lhs_i = x_a
        lhs_j = y_a
        lhs_k = z_a


        A = - rel_i * lhs_i - rel_j * lhs_j - rel_k * lhs_k
        B = rel_r * lhs_i + rel_j * lhs_k - lhs_j * rel_k
        C = rel_r * lhs_j + rel_k * lhs_i - lhs_k * rel_i
        D = rel_r * lhs_k + rel_i * lhs_j - lhs_i * rel_j

        B1 = -A * rel_i + rel_r * B - C * rel_k + rel_j * D
        C1 = -A * rel_j + rel_r * C - D * rel_i + rel_k * B
        D1 = -A * rel_k + rel_r * D - B * rel_j + rel_i * C


        score_r = (B1 * x_c + C1 * y_c + D1 * z_c) - para*torch.norm(denominator_a*rel_w-denominator_c,p=1,dim=-1).unsqueeze(dim=-1)/x_a.size()[1]

        return -torch.sum(score_r, -1)

    def loss(self, score, regul, regul2):
        return (
                torch.mean(self.criterion(score * self.batch_y)) + self.config.lmbda * regul +   self.config.lmbda * regul2
        )

    def forward(self):
 
        x_a = self.emb_x_a(self.batch_h)
        y_a = self.emb_y_a(self.batch_h)
        z_a = self.emb_z_a(self.batch_h)

        x_c = self.emb_x_a(self.batch_t)
        y_c = self.emb_y_a(self.batch_t)
        z_c = self.emb_z_a(self.batch_t)

        s_b = self.rel_s_b(self.batch_r)
        x_b = self.rel_x_b(self.batch_r)
        y_b = self.rel_y_b(self.batch_r)
        z_b = self.rel_z_b(self.batch_r)
        rel_w = self.rel_w(self.batch_r)
        para = self.para


        

        score = self._calc(x_a, y_a, z_a, x_c, y_c, z_c, s_b, x_b, y_b, z_b, rel_w, para)
        regul = ( torch.mean( torch.abs(x_a) ** 2)
                 + torch.mean( torch.abs(y_a) ** 2)
                 + torch.mean( torch.abs(z_a) ** 2)
                 + torch.mean( torch.abs(x_c) ** 2)
                 + torch.mean( torch.abs(y_c) ** 2)
                 + torch.mean( torch.abs(z_c) ** 2)
                 )
        regul2 =  (torch.mean( torch.abs(s_b) ** 2 )
                 + torch.mean( torch.abs(x_b) ** 2 )
                 + torch.mean( torch.abs(y_b) ** 2 )
                 + torch.mean( torch.abs(z_b) ** 2 ))

        '''
        + torch.mean(s_b ** 2)
            + torch.mean(x_b ** 2)
            + torch.mean(y_b ** 2)
            + torch.mean(z_b ** 2)
        '''

        return self.loss(score, regul, regul2)

    def predict(self):
        x_a = self.emb_x_a(self.batch_h)
        y_a = self.emb_y_a(self.batch_h)
        z_a = self.emb_z_a(self.batch_h)


        x_c = self.emb_x_a(self.batch_t)
        y_c = self.emb_y_a(self.batch_t)
        z_c = self.emb_z_a(self.batch_t)

        s_b = self.rel_s_b(self.batch_r)
        x_b = self.rel_x_b(self.batch_r)
        y_b = self.rel_y_b(self.batch_r)
        z_b = self.rel_z_b(self.batch_r)
        rel_w = self.rel_w(self.batch_r)
        para = self.para

        
        score = self._calc(x_a, y_a, z_a, x_c, y_c, z_c, s_b, x_b, y_b, z_b, rel_w, para)
        return score.cpu().data.numpy()

    def quaternion_init(self, in_features, out_features, criterion='he'):

        fan_in = in_features
        fan_out = out_features

        if criterion == 'glorot':
            s = 1. / np.sqrt(2 * (fan_in + fan_out))
        elif criterion == 'he':
            s = 1. / np.sqrt(2 * fan_in)
        else:
            raise ValueError('Invalid criterion: ', criterion)
        rng = RandomState(123)

        # Generating randoms and purely imaginary quaternions :
        kernel_shape = (in_features, out_features)

        number_of_weights = np.prod(kernel_shape)
        v_i = np.random.uniform(0.0, 1.0, number_of_weights)
        v_j = np.random.uniform(0.0, 1.0, number_of_weights)
        v_k = np.random.uniform(0.0, 1.0, number_of_weights)

        # Purely imaginary quaternions unitary
        for i in range(0, number_of_weights):
            norm = np.sqrt(v_i[i] ** 2 + v_j[i] ** 2 + v_k[i] ** 2) + 0.0001
            v_i[i] /= norm
            v_j[i] /= norm
            v_k[i] /= norm
        v_i = v_i.reshape(kernel_shape)
        v_j = v_j.reshape(kernel_shape)
        v_k = v_k.reshape(kernel_shape)

        modulus = rng.uniform(low=-s, high=s, size=kernel_shape)
        phase = rng.uniform(low=-np.pi, high=np.pi, size=kernel_shape)

        weight_r = modulus * np.cos(phase)
        weight_i = modulus * v_i * np.sin(phase)
        weight_j = modulus * v_j * np.sin(phase)
        weight_k = modulus * v_k * np.sin(phase)

        return (weight_r, weight_i, weight_j, weight_k)