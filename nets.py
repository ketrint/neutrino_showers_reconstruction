import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.nn import Sequential
import torch_geometric
from torch_geometric.nn import MessagePassing
from torch_geometric.utils import add_self_loops, degree
import torch_geometric.transforms as T
import torch_cluster
from torch_geometric.nn import NNConv, GCNConv, GraphConv
from torch_geometric.nn import PointConv, EdgeConv, SplineConv

from torch_geometric.nn.inits import reset


class EdgeConv(MessagePassing):   
    def __init__(self, nn, aggr='max', **kwargs):
        super(EdgeConv, self).__init__(aggr=aggr, **kwargs)
        self.nn = nn
        self.reset_parameters()


    def reset_parameters(self):
        reset(self.nn)


    def forward(self, x, edge_index, dist):
        print(x.shape, edge_index.shape, dist.shape)
        """"""
        x = x.unsqueeze(-1) if x.dim() == 1 else x
      
        return self.propagate(edge_index, x=x, dist=dist)


    def message(self, x_i, x_j, dist):
        print(x_i.shape, len(dist))
        return self.nn(torch.cat([x_i, x_j - x_i, dist], dim=1))

    def __repr__(self):
        return '{}(nn={})'.format(self.__class__.__name__, self.nn)      



class EmulsionConv(MessagePassing):
    def __init__(self, in_channels, out_channels, edge_dim):
        super().__init__(aggr='add')
        self.mp = torch.nn.Linear(in_channels * 2 + edge_dim, out_channels)

    def forward(self, x, edge_index, orders, dist):
        for order in orders:
            x = self.propagate(
                torch.index_select(
                    edge_index[:, order],
                    0,
                    torch.LongTensor([1, 0]).to(x.device)
                ), 
                x=x,
                dist=dist[order]
            )
        return x

    def message(self, x_j, x_i, dist):
        return self.mp(torch.cat([x_i, x_j - x_i, dist], dim=1))

    def update(self, aggr_out, x):
        return aggr_out + x


class GraphNN_KNN_v1(nn.Module):
    def __init__(self, k, dim_out=10):
        super().__init__()
        self.k = k
        self.emconv = EmulsionConv(self.k, self.k)
        self.wconv1 = EdgeConv(Sequential(nn.Linear(20, 10)), 'max')
        self.wconv2 = EdgeConv(Sequential(nn.Linear(20, 10)), 'max')
        self.wconv3 = EdgeConv(Sequential(nn.Linear(20, 10)), 'max')
        self.output = nn.Linear(10, dim_out)

    def forward(self, data):
        x, edge_index, orders = data.x, data.edge_index, data.mask
        x = self.emconv(x=x, edge_index=edge_index, orders=orders)
        x1 = self.wconv1(x=x, edge_index=edge_index)
        x2 = self.wconv2(x=x1, edge_index=edge_index)
        x3 = self.wconv3(x=x2, edge_index=edge_index)
        return self.output(x3)
    
class GraphNN_KNN_v0_v1(nn.Module):
    def __init__(self, k, dim_out=10):
        super().__init__()
        self.k = k       
        self.wconv1 = EdgeConv(Sequential(nn.Linear(20, 10)), 'max')       
        self.output = nn.Linear(10, dim_out)

    def forward(self, data):
        x, edge_index, orders = data.x, data.edge_index, data.mask
        x1 = self.wconv1(x=x, edge_index=edge_index)
        return self.output(x1)
    
    
class GraphNN_KNN_v0_v2(nn.Module):
    def __init__(self, k, dim_out=10):
        super().__init__()
        self.k = k       
        self.wconv1 = EdgeConv(Sequential(nn.Linear(20, 10)), 'max') 
        self.wconv2 = EdgeConv(Sequential(nn.Linear(20, 10)), 'max')
        self.output = nn.Linear(10, dim_out)

    def forward(self, data):
        x, edge_index, orders = data.x, data.edge_index, data.mask
        x1 = self.wconv1(x=x, edge_index=edge_index)
        x2 = self.wconv2(x=x1, edge_index=edge_index)
        return self.output(x2)
    
class GraphNN_KNN_v0_v3(nn.Module):
    def __init__(self, k, dim_out=10):
        super().__init__()
        self.k = k       
        self.wconv1 = EdgeConv(Sequential(nn.Linear(20, 10)), 'max') 
        self.wconv2 = EdgeConv(Sequential(nn.Linear(20, 10)), 'max')
        self.wconv3 = EdgeConv(Sequential(nn.Linear(20, 10)), 'max')
        self.output = nn.Linear(10, dim_out)

    def forward(self, data):
        x, edge_index, orders = data.x, data.edge_index, data.mask
        x1 = self.wconv1(x=x, edge_index=edge_index)
        x2 = self.wconv2(x=x1, edge_index=edge_index)
        x3 = self.wconv2(x=x2, edge_index=edge_index)
        return self.output(x3)
    
class GraphNN_KNN_v1_v0(nn.Module):
    def __init__(self, k, dim_out=10):
        super().__init__()
        self.k = k       
        self.emconv1 = EmulsionConv(self.k, self.k)
        self.output = nn.Linear(10, dim_out)

    def forward(self, data):
        x, edge_index, orders = data.x, data.edge_index, data.mask
        x = self.emconv1(x=x, edge_index=edge_index, orders=orders)
        return self.output(x)
    
class GraphNN_KNN_v2_v0(nn.Module):
    def __init__(self, k, dim_out=10):
        super().__init__()
        self.k = k       
        self.emconv1 = EmulsionConv(self.k, self.k)
        self.emconv2 = EmulsionConv(self.k, self.k)
        self.output = nn.Linear(10, dim_out)

    def forward(self, data):
        x, edge_index, orders = data.x, data.edge_index, data.mask
        x = self.emconv1(x=x, edge_index=edge_index, orders=orders)
        x = self.emconv2(x=x, edge_index=edge_index, orders=orders)
        return self.output(x)
    
class GraphNN_KNN_v3_v0(nn.Module):
    def __init__(self, k, dim_out=10):
        super().__init__()
        self.k = k       
        self.emconv1 = EmulsionConv(self.k, self.k)
        self.emconv2 = EmulsionConv(self.k, self.k)
        self.emconv3 = EmulsionConv(self.k, self.k)
        self.output = nn.Linear(10, dim_out)

    def forward(self, data):
        x, edge_index, orders = data.x, data.edge_index, data.mask
        x = self.emconv1(x=x, edge_index=edge_index, orders=orders)
        x = self.emconv2(x=x, edge_index=edge_index, orders=orders)
        x = self.emconv3(x=x, edge_index=edge_index, orders=orders)
        return self.output(x)
        
    
class GraphNN_KNN_v2(nn.Module):
    def __init__(self, k, dim_out=10):
        super().__init__()
        self.k = k
        self.emconv1 = EmulsionConv(self.k, self.k)
        self.emconv2 = EmulsionConv(self.k, self.k)
        self.wconv1 = EdgeConv(Sequential(nn.Linear(20, 10)), 'max')
        self.wconv2 = EdgeConv(Sequential(nn.Linear(20, 10)), 'max')
        self.wconv3 = EdgeConv(Sequential(nn.Linear(20, 10)), 'max')
        self.output = nn.Linear(10, dim_out)

    def forward(self, data):
        x, edge_index, orders = data.x, data.edge_index, data.mask
        x = self.emconv1(x=x, edge_index=edge_index, orders=orders)
        x = self.emconv2(x=x, edge_index=edge_index, orders=orders)
        x1 = self.wconv1(x=x, edge_index=edge_index)
        x2 = self.wconv2(x=x1, edge_index=edge_index)
        x3 = self.wconv3(x=x2, edge_index=edge_index) 

        return self.output(x3)
    
class GraphNN_KNN_v3(nn.Module):
    def __init__(self, k, dim_out=10, edge_dim=1):
        super().__init__()
        self.k = k
        self.emconv1 = EmulsionConv(self.k, self.k, edge_dim)
        self.emconv2 = EmulsionConv(self.k, self.k, edge_dim)
        self.emconv3 = EmulsionConv(self.k, self.k, edge_dim)
        self.wconv1 = EdgeConv(Sequential(nn.Linear(21, 10)), 'max')
        self.wconv2 = EdgeConv(Sequential(nn.Linear(21, 10)), 'max')
        self.wconv3 = EdgeConv(Sequential(nn.Linear(21, 10)), 'max')
        self.output = nn.Linear(10, dim_out)

    def forward(self, data):
        x, edge_index, orders, dist = data.x, data.edge_index, data.mask, data.edge_attr
        x = self.emconv1(x=x, edge_index=edge_index, orders=orders, dist=dist)
        x = self.emconv2(x=x, edge_index=edge_index, orders=orders, dist=dist)
        x = self.emconv3(x=x, edge_index=edge_index, orders=orders, dist=dist)
        x1 = self.wconv1(x=x, edge_index=edge_index, dist=dist)
        x2 = self.wconv2(x=x1, edge_index=edge_index, dist=dist)
        x3 = self.wconv3(x=x2, edge_index=edge_index, dist=dist)
     
        return self.output(x3)
    
class GraphNN_KNN_v4(nn.Module):
    def __init__(self, k, dim_out=10):
        super().__init__()
        self.k = k
        self.emconv1 = EmulsionConv(self.k, self.k)
        self.emconv2 = EmulsionConv(self.k, self.k)
        self.emconv3 = EmulsionConv(self.k, self.k)
        self.emconv4 = EmulsionConv(self.k, self.k)
        self.wconv1 = EdgeConv(Sequential(nn.Linear(20, 10)), 'max')
        self.wconv2 = EdgeConv(Sequential(nn.Linear(20, 10)), 'max')
        self.wconv3 = EdgeConv(Sequential(nn.Linear(20, 10)), 'max')
        self.output = nn.Linear(10, dim_out)

    def forward(self, data):
        x, edge_index, orders = data.x, data.edge_index, data.mask
        x = self.emconv1(x=x, edge_index=edge_index, orders=orders)
        x = self.emconv2(x=x, edge_index=edge_index, orders=orders)
        x = self.emconv3(x=x, edge_index=edge_index, orders=orders)
        x = self.emconv4(x=x, edge_index=edge_index, orders=orders)
        x1 = self.wconv1(x=x, edge_index=edge_index)
        x2 = self.wconv2(x=x1, edge_index=edge_index)
        x3 = self.wconv3(x=x2, edge_index=edge_index)
     
        return self.output(x3)

    
class GraphNN_KNN_v5(nn.Module):
    def __init__(self, k, dim_out=10):
        super().__init__()
        self.k = k
        self.emconv1 = EmulsionConv(self.k, self.k)
        self.emconv2 = EmulsionConv(self.k, self.k)
        self.emconv3 = EmulsionConv(self.k, self.k)
        self.emconv4 = EmulsionConv(self.k, self.k)
        self.emconv5 = EmulsionConv(self.k, self.k)
        self.wconv1 = EdgeConv(Sequential(nn.Linear(20, 10)), 'max')
        self.wconv2 = EdgeConv(Sequential(nn.Linear(20, 10)), 'max')
        self.wconv3 = EdgeConv(Sequential(nn.Linear(20, 10)), 'max')
        self.output = nn.Linear(10, dim_out)

    def forward(self, data):
        x, edge_index, orders = data.x, data.edge_index, data.mask
        x = self.emconv1(x=x, edge_index=edge_index, orders=orders)
        x = self.emconv2(x=x, edge_index=edge_index, orders=orders)
        x = self.emconv3(x=x, edge_index=edge_index, orders=orders)
        x = self.emconv4(x=x, edge_index=edge_index, orders=orders)
        x = self.emconv5(x=x, edge_index=edge_index, orders=orders)
        x1 = self.wconv1(x=x, edge_index=edge_index)
        x2 = self.wconv2(x=x1, edge_index=edge_index)
        x3 = self.wconv3(x=x2, edge_index=edge_index)
        return self.output(x3)
    
class GraphNN_KNN_v1_v1(nn.Module):
    def __init__(self, k, dim_out=10):
        super().__init__()
        self.k = k
        self.emconv1 = EmulsionConv(self.k, self.k)        
        self.wconv1 = EdgeConv(Sequential(nn.Linear(20, 10)), 'max')        
        self.output = nn.Linear(10, dim_out)

    def forward(self, data):
        x, edge_index, orders = data.x, data.edge_index, data.mask
        x = self.emconv1(x=x, edge_index=edge_index, orders=orders)
        x1 = self.wconv1(x=x, edge_index=edge_index)

        return self.output(x1)
    
class GraphNN_KNN_v1_v2(nn.Module):
    def __init__(self, k, dim_out=10):
        super().__init__()
        self.k = k
        self.emconv1 = EmulsionConv(self.k, self.k)        
        self.wconv1 = EdgeConv(Sequential(nn.Linear(20, 10)), 'max') 
        self.wconv2 = EdgeConv(Sequential(nn.Linear(20, 10)), 'max') 
        self.output = nn.Linear(10, dim_out)

    def forward(self, data):
        x, edge_index, orders = data.x, data.edge_index, data.mask
        x = self.emconv1(x=x, edge_index=edge_index, orders=orders)
        x1 = self.wconv1(x=x, edge_index=edge_index)
        x2 = self.wconv1(x=x1, edge_index=edge_index)
        return self.output(x2)
    
class GraphNN_KNN_v2_v2(nn.Module):
    def __init__(self, k, dim_out=10):
        super().__init__()
        self.k = k
        self.emconv1 = EmulsionConv(self.k, self.k)  
        self.emconv2 = EmulsionConv(self.k, self.k) 
        self.wconv1 = EdgeConv(Sequential(nn.Linear(20, 10)), 'max') 
        self.wconv2 = EdgeConv(Sequential(nn.Linear(20, 10)), 'max') 
        self.output = nn.Linear(10, dim_out)

    def forward(self, data):
        x, edge_index, orders = data.x, data.edge_index, data.mask
        x = self.emconv1(x=x, edge_index=edge_index, orders=orders)
        x = self.emconv2(x=x, edge_index=edge_index, orders=orders)
        x1 = self.wconv1(x=x, edge_index=edge_index)
        x2 = self.wconv1(x=x1, edge_index=edge_index)
        return self.output(x2)
    
class GraphNN_KNN_v3_v2(nn.Module):
    def __init__(self, k, dim_out=10):
        super().__init__()
        self.k = k
        self.emconv1 = EmulsionConv(self.k, self.k)  
        self.emconv2 = EmulsionConv(self.k, self.k)
        self.emconv3 = EmulsionConv(self.k, self.k) 
        self.wconv1 = EdgeConv(Sequential(nn.Linear(20, 10)), 'max') 
        self.wconv2 = EdgeConv(Sequential(nn.Linear(20, 10)), 'max') 
        self.output = nn.Linear(10, dim_out)

    def forward(self, data):
        x, edge_index, orders = data.x, data.edge_index, data.mask
        x = self.emconv1(x=x, edge_index=edge_index, orders=orders)
        x = self.emconv2(x=x, edge_index=edge_index, orders=orders)
        x = self.emconv3(x=x, edge_index=edge_index, orders=orders)
        x1 = self.wconv1(x=x, edge_index=edge_index)
        x2 = self.wconv1(x=x1, edge_index=edge_index)
        return self.output(x2)
    
    
class GraphNN_KNN_v2_v1(nn.Module):
    def __init__(self, k, dim_out=10):
        super().__init__()
        self.k = k
        self.emconv1 = EmulsionConv(self.k, self.k) 
        self.emconv2 = EmulsionConv(self.k, self.k) 
        self.wconv1 = EdgeConv(Sequential(nn.Linear(20, 10)), 'max') 
        self.output = nn.Linear(10, dim_out)

    def forward(self, data):
        x, edge_index, orders = data.x, data.edge_index, data.mask
        x = self.emconv1(x=x, edge_index=edge_index, orders=orders)
        x = self.emconv2(x=x, edge_index=edge_index, orders=orders)
        x1 = self.wconv1(x=x, edge_index=edge_index)
        return self.output(x1)
    
    
class GraphNN_KNN_v3_v1(nn.Module):
    def __init__(self, k, dim_out=10):
        super().__init__()
        self.k = k
        self.emconv1 = EmulsionConv(self.k, self.k) 
        self.emconv2 = EmulsionConv(self.k, self.k) 
        self.emconv3 = EmulsionConv(self.k, self.k)
        self.wconv1 = EdgeConv(Sequential(nn.Linear(20, 10)), 'max') 
        self.output = nn.Linear(10, dim_out)

    def forward(self, data):
        x, edge_index, orders = data.x, data.edge_index, data.mask
        x = self.emconv1(x=x, edge_index=edge_index, orders=orders)
        x = self.emconv2(x=x, edge_index=edge_index, orders=orders)
        x = self.emconv3(x=x, edge_index=edge_index, orders=orders)
        x1 = self.wconv1(x=x, edge_index=edge_index)
        return self.output(x1)


class EdgeClassifier_v1(nn.Module):
    def __init__(self, dim_out):
        super().__init__()
        self._layers = nn.ModuleList([
            nn.Linear(dim_out * 2, 10),
            nn.Tanh(),
            nn.Dropout(0.3),
            nn.Linear(10, 10),
            nn.Tanh(),
            nn.Dropout(0.3),
            nn.Linear(10, 5),
            nn.Tanh(),
            nn.Dropout(0.3),
            nn.Linear(5, 1),
            nn.Sigmoid()
        ])

    def forward(self, x):
        for layer in self._layers:
            x = layer(x)
        return x
    
    
class EdgeClassifier_v2(nn.Module):
    def __init__(self, dim_out):
        super().__init__()
        self._layers = nn.ModuleList([
            nn.Linear(dim_out * 2, 20),
            nn.Tanh(),
            nn.Dropout(0.3),
            nn.Linear(20, 20),
            nn.Tanh(),
            nn.Dropout(0.3),
            nn.Linear(20, 10),
            nn.Tanh(),
            nn.Dropout(0.3),
            nn.Linear(10, 1),
            nn.Sigmoid()
        ])

    def forward(self, x):
        for layer in self._layers:
            x = layer(x)
        return x
    
    
class EdgeClassifier_v3(nn.Module):
    def __init__(self, dim_out):
        super().__init__()
        self._layers = nn.ModuleList([
            nn.Linear(dim_out * 2, 30),
            nn.Tanh(),
            nn.Dropout(0.3),
            nn.Linear(30, 30),
            nn.Tanh(),
            nn.Dropout(0.3),
            nn.Linear(30, 10),
            nn.Tanh(),
            nn.Dropout(0.3),
            nn.Linear(10, 1),
            nn.Sigmoid()
        ])

    def forward(self, x):
        for layer in self._layers:
            x = layer(x)
        return x
    
class EdgeClassifier_v4(nn.Module):
    def __init__(self, dim_out):
        super().__init__()
        self._layers = nn.ModuleList([
            nn.Linear(dim_out * 2, 100),
            nn.Tanh(),
            nn.Dropout(0.2),
            nn.Linear(100, 100),
            nn.Tanh(),
            nn.Dropout(0.2),
            nn.Linear(100, 10),
            nn.Tanh(),
            nn.Dropout(0.2),
            nn.Linear(10, 1),
            nn.Sigmoid()
        ])

    def forward(self, x):
        for layer in self._layers:
            x = layer(x)
        return x

    
