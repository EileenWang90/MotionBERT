import torch
import torch.nn as nn
import math
import warnings
import random
import numpy as np
from collections import OrderedDict
from functools import partial
from itertools import repeat
from lib.model.drop import DropPath

class Scale(nn.Module):
    """
    Scale vector by element multiplications.
    """
    def __init__(self, dim, init_value=1.0, trainable=True):
        super().__init__()
        self.scale = nn.Parameter(init_value * torch.ones(dim), requires_grad=trainable)

    def forward(self, x):
        return x * self.scale

class SepConv(nn.Module):
    r"""
    Inverted separable convolution from MobileNetV2: https://arxiv.org/abs/1801.04381.
    """
    def __init__(self, dim, expansion_ratio=2,
        act1_layer=nn.GELU, act2_layer=nn.Identity, 
        bias=False, kernel_size=7, padding=3,
        **kwargs, ):
        super().__init__()
        med_channels = int(expansion_ratio * dim)
        self.pwconv1 = nn.Linear(dim, med_channels, bias=bias)
        self.act1 = act1_layer()
        self.dwconv = nn.Conv2d(
            med_channels, med_channels, kernel_size=kernel_size,
            padding=padding, groups=med_channels, bias=bias) # depthwise conv
        self.act2 = act2_layer()
        self.pwconv2 = nn.Linear(med_channels, dim, bias=bias)


    def forward(self, x, seqlen=8):
        if self.mode == 'temporal':
            qkv = self.qkv(x).reshape(B, N, 3, self.num_heads, C // self.num_heads).permute(2, 0, 3, 1, 4)
            q, k, v = qkv[0], qkv[1], qkv[2]   # make torchscript happy (cannot use tensor as tuple)
            x = self.forward_temporal(q, k, v, seqlen=seqlen)
        elif self.mode == 'spatial':
            qkv = self.qkv(x).reshape(B, N, 3, self.num_heads, C // self.num_heads).permute(2, 0, 3, 1, 4)
            q, k, v = qkv[0], qkv[1], qkv[2]   # make torchscript happy (cannot use tensor as tuple)
            x = self.forward_spatial(q, k, v)

        B, N, C = x.shape
        x = self.pwconv1(x)
        x = self.act1(x)
        x = x.permute(0, 3, 1, 2)
        x = self.dwconv(x)
        x = x.permute(0, 2, 3, 1)
        x = self.act2(x)
        x = self.pwconv2(x)
        return x

def _no_grad_trunc_normal_(tensor, mean, std, a, b):
    # Cut & paste from PyTorch official master until it's in a few official releases - RW
    # Method based on https://people.sc.fsu.edu/~jburkardt/presentations/truncated_normal.pdf
    def norm_cdf(x):
        # Computes standard normal cumulative distribution function
        return (1. + math.erf(x / math.sqrt(2.))) / 2.

    if (mean < a - 2 * std) or (mean > b + 2 * std):
        warnings.warn("mean is more than 2 std from [a, b] in nn.init.trunc_normal_. "
                      "The distribution of values may be incorrect.",
                      stacklevel=2)

    with torch.no_grad():
        # Values are generated by using a truncated uniform distribution and
        # then using the inverse CDF for the normal distribution.
        # Get upper and lower cdf values
        l = norm_cdf((a - mean) / std)
        u = norm_cdf((b - mean) / std)

        # Uniformly fill tensor with values from [l, u], then translate to
        # [2l-1, 2u-1].
        tensor.uniform_(2 * l - 1, 2 * u - 1)

        # Use inverse cdf transform for normal distribution to get truncated
        # standard normal
        tensor.erfinv_()

        # Transform to proper mean, std
        tensor.mul_(std * math.sqrt(2.))
        tensor.add_(mean)

        # Clamp to ensure it's in the proper range
        tensor.clamp_(min=a, max=b)
        return tensor


def trunc_normal_(tensor, mean=0., std=1., a=-2., b=2.):
    # type: (Tensor, float, float, float, float) -> Tensor
    r"""Fills the input Tensor with values drawn from a truncated
    normal distribution. The values are effectively drawn from the
    normal distribution :math:`\mathcal{N}(\text{mean}, \text{std}^2)`
    with values outside :math:`[a, b]` redrawn until they are within
    the bounds. The method used for generating the random values works
    best when :math:`a \leq \text{mean} \leq b`.
    Args:
        tensor: an n-dimensional `torch.Tensor`
        mean: the mean of the normal distribution
        std: the standard deviation of the normal distribution
        a: the minimum cutoff value
        b: the maximum cutoff value
    Examples:
        >>> w = torch.empty(3, 5)
        >>> nn.init.trunc_normal_(w)
    """
    return _no_grad_trunc_normal_(tensor, mean, std, a, b)


class MLP(nn.Module):
    def __init__(self, in_features, hidden_features=None, out_features=None, act_layer=nn.GELU, drop=0.):
        super().__init__()
        out_features = out_features or in_features
        hidden_features = hidden_features or in_features
        self.fc1 = nn.Linear(in_features, hidden_features)
        self.act = act_layer()
        self.fc2 = nn.Linear(hidden_features, out_features)
        self.drop = nn.Dropout(drop)

    def forward(self, x):
        x = self.fc1(x)
        x = self.act(x)
        x = self.drop(x)
        x = self.fc2(x)
        x = self.drop(x)
        return x


class Attention(nn.Module):
    def __init__(self, dim, num_heads=8, qkv_bias=False, qk_scale=None, attn_drop=0., proj_drop=0., st_mode='vanilla'):
        super().__init__()
        self.num_heads = num_heads
        head_dim = dim // num_heads
        # NOTE scale factor was wrong in my original version, can set manually to be compat with prev weights
        self.scale = qk_scale or head_dim ** -0.5

        self.attn_drop = nn.Dropout(attn_drop)
        self.proj = nn.Linear(dim, dim)
        self.mode = st_mode
        if self.mode == 'parallel':
            self.ts_attn = nn.Linear(dim*2, dim*2)
            self.qkv = nn.Linear(dim, dim * 3, bias=qkv_bias)
        else:
            self.qkv = nn.Linear(dim, dim * 3, bias=qkv_bias)
        self.proj_drop = nn.Dropout(proj_drop)

        self.attn_count_s = None
        self.attn_count_t = None

    def forward(self, x, seqlen=1):  # x.shape (BF, J, dim_feat)?
        B, N, C = x.shape  # B=BF, N=J, C=dim_feat
        
        if self.mode == 'series':
            qkv = self.qkv(x).reshape(B, N, 3, self.num_heads, C // self.num_heads).permute(2, 0, 3, 1, 4)  #(3, B, self.num_heads, N, C // self.num_heads)
            q, k, v = qkv[0], qkv[1], qkv[2]   # make torchscript happy (cannot use tensor as tuple) 
            x = self.forward_spatial(q, k, v)  # (B, self.num_heads, N, C // self.num_heads) 即 (BF, self.num_heads, J, dim_feat // self.num_heads)
            qkv = self.qkv(x).reshape(B, N, 3, self.num_heads, C // self.num_heads).permute(2, 0, 3, 1, 4)
            q, k, v = qkv[0], qkv[1], qkv[2]   # make torchscript happy (cannot use tensor as tuple)
            x = self.forward_temporal(q, k, v, seqlen=seqlen)
        elif self.mode == 'parallel':
            qkv = self.qkv(x).reshape(B, N, 3, self.num_heads, C // self.num_heads).permute(2, 0, 3, 1, 4)
            q, k, v = qkv[0], qkv[1], qkv[2]   # make torchscript happy (cannot use tensor as tuple)
            x_t = self.forward_temporal(q, k, v, seqlen=seqlen)
            x_s = self.forward_spatial(q, k, v)
            
            alpha = torch.cat([x_s, x_t], dim=-1)
            alpha = alpha.mean(dim=1, keepdim=True)
            alpha = self.ts_attn(alpha).reshape(B, 1, C, 2)
            alpha = alpha.softmax(dim=-1)
            x = x_t * alpha[:,:,:,1] + x_s * alpha[:,:,:,0]
        elif self.mode == 'coupling':
            qkv = self.qkv(x).reshape(B, N, 3, self.num_heads, C // self.num_heads).permute(2, 0, 3, 1, 4)
            q, k, v = qkv[0], qkv[1], qkv[2]   # make torchscript happy (cannot use tensor as tuple)
            x = self.forward_coupling(q, k, v, seqlen=seqlen)
        elif self.mode == 'vanilla':  # 也即 'spatial'
            qkv = self.qkv(x).reshape(B, N, 3, self.num_heads, C // self.num_heads).permute(2, 0, 3, 1, 4)
            q, k, v = qkv[0], qkv[1], qkv[2]   # make torchscript happy (cannot use tensor as tuple)
            x = self.forward_spatial(q, k, v)
        elif self.mode == 'temporal':
            qkv = self.qkv(x).reshape(B, N, 3, self.num_heads, C // self.num_heads).permute(2, 0, 3, 1, 4)
            q, k, v = qkv[0], qkv[1], qkv[2]   # make torchscript happy (cannot use tensor as tuple)
            x = self.forward_temporal(q, k, v, seqlen=seqlen)
        elif self.mode == 'spatial':
            qkv = self.qkv(x).reshape(B, N, 3, self.num_heads, C // self.num_heads).permute(2, 0, 3, 1, 4)
            q, k, v = qkv[0], qkv[1], qkv[2]   # make torchscript happy (cannot use tensor as tuple)
            x = self.forward_spatial(q, k, v)
        else:
            raise NotImplementedError(self.mode)
        x = self.proj(x)
        x = self.proj_drop(x)
        return x
    
    def reshape_T(self, x, seqlen=1, inverse=False):
        if not inverse:
            N, C = x.shape[-2:]
            x = x.reshape(-1, seqlen, self.num_heads, N, C).transpose(1,2)
            x = x.reshape(-1, self.num_heads, seqlen*N, C) #(B, H, TN, c)
        else:
            TN, C = x.shape[-2:]
            x = x.reshape(-1, self.num_heads, seqlen, TN // seqlen, C).transpose(1,2)
            x = x.reshape(-1, self.num_heads, TN // seqlen, C) #(BT, H, N, C)
        return x 

    def forward_coupling(self, q, k, v, seqlen=8):
        BT, _, N, C = q.shape
        q = self.reshape_T(q, seqlen)
        k = self.reshape_T(k, seqlen)
        v = self.reshape_T(v, seqlen)

        attn = (q @ k.transpose(-2, -1)) * self.scale
        attn = attn.softmax(dim=-1)
        attn = self.attn_drop(attn)

        x = attn @ v
        x = self.reshape_T(x, seqlen, inverse=True)
        x = x.transpose(1,2).reshape(BT, N, C*self.num_heads)
        return x

    def forward_spatial(self, q, k, v):
        B, _, N, C = q.shape  # (B, self.num_heads, N, C // self.num_heads) 即 (BF, self.num_heads, J, dim_feat // self.num_heads)
        attn = (q @ k.transpose(-2, -1)) * self.scale  # 对最后两维进行矩阵乘
        attn = attn.softmax(dim=-1)
        attn = self.attn_drop(attn)

        x = attn @ v
        x = x.transpose(1,2).reshape(B, N, C*self.num_heads)
        return x
        
    def forward_temporal(self, q, k, v, seqlen=8):
        B, _, N, C = q.shape  # (B, self.num_heads, N, C // self.num_heads) 即 (BF, self.num_heads, J, dim_feat // self.num_heads)
        qt = q.reshape(-1, seqlen, self.num_heads, N, C).permute(0, 2, 3, 1, 4) #(B, H, N, T, C)  (B, F, self.num_heads, J, dim_feat // self.num_heads)->(B, self.num_heads, J, F,  dim_feat // self.num_heads)
        kt = k.reshape(-1, seqlen, self.num_heads, N, C).permute(0, 2, 3, 1, 4) #(B, H, N, T, C)  N=head, N=joints, C=dim_feat // self.num_heads
        vt = v.reshape(-1, seqlen, self.num_heads, N, C).permute(0, 2, 3, 1, 4) #(B, H, N, T, C)

        attn = (qt @ kt.transpose(-2, -1)) * self.scale
        attn = attn.softmax(dim=-1)
        attn = self.attn_drop(attn)

        x = attn @ vt #(B, H, N, T, C)-> permute (B, T, N, H, C)
        x = x.permute(0, 3, 2, 1, 4).reshape(B, N, C*self.num_heads)  # (B, N, dim_feat) dim_feat=C*self.num_heads 即 (BF, J, dim_feat)
        return x

    def count_attn(self, attn): #
        attn = attn.detach().cpu().numpy()
        attn = attn.mean(axis=1)
        attn_t = attn[:, :, 1].mean(axis=1)
        attn_s = attn[:, :, 0].mean(axis=1)
        if self.attn_count_s is None:
            self.attn_count_s = attn_s
            self.attn_count_t = attn_t
        else:
            self.attn_count_s = np.concatenate([self.attn_count_s, attn_s], axis=0)
            self.attn_count_t = np.concatenate([self.attn_count_t, attn_t], axis=0)

class Block(nn.Module):

    def __init__(self, dim, num_heads, mlp_ratio=4., mlp_out_ratio=1., qkv_bias=True, qk_scale=None, drop=0., attn_drop=0.,
                 drop_path=0., act_layer=nn.GELU, norm_layer=nn.LayerNorm, st_mode='stage_st', att_fuse=False, 
                 res_scale_init_value=None, layer_scale_init_value=None):
        super().__init__()
        # assert 'stage' in st_mode
        self.st_mode = st_mode
        self.norm1_s = norm_layer(dim)  # dim=dim_feat
        self.norm1_t = norm_layer(dim)
        self.attn_s = Attention(
            dim, num_heads=num_heads, qkv_bias=qkv_bias, qk_scale=qk_scale, attn_drop=attn_drop, proj_drop=drop, st_mode="spatial")
        self.attn_t = Attention(
            dim, num_heads=num_heads, qkv_bias=qkv_bias, qk_scale=qk_scale, attn_drop=attn_drop, proj_drop=drop, st_mode="temporal")
        
        # # Hybrid: Add conv
        # self.SepConv_s = SepConv(
        #     dim, expansion_ratio=2, act1_layer=nn.GELU, act2_layer=nn.Identity, bias=False, kernel_size=7, padding=3) 
        # self.SepConv_t = SepConv(
        #     dim, expansion_ratio=2, act1_layer=nn.GELU, act2_layer=nn.Identity, bias=False, kernel_size=7, padding=3) 
        

        # NOTE: drop path for stochastic depth, we shall see if this is better than dropout here
        self.drop_path = DropPath(drop_path) if drop_path > 0. else nn.Identity()
        self.norm2_s = norm_layer(dim)
        self.norm2_t = norm_layer(dim)
        mlp_hidden_dim = int(dim * mlp_ratio)
        mlp_out_dim = int(dim * mlp_out_ratio)
        self.mlp_s = MLP(in_features=dim, hidden_features=mlp_hidden_dim, out_features=mlp_out_dim, act_layer=act_layer, drop=drop)
        self.mlp_t = MLP(in_features=dim, hidden_features=mlp_hidden_dim, out_features=mlp_out_dim, act_layer=act_layer, drop=drop)
        self.att_fuse = att_fuse
        if self.att_fuse:
            self.ts_attn = nn.Linear(dim*2, dim*2)

        # Res_scale in MetaFormer https://arxiv.org/pdf/2210.13452.pdf   First from NormFormer
        '''res_scale_init_values (list, tuple, float or None): Init value for Layer Scale. Default: [None, None, 1.0, 1.0].
            None means not use the layer scale. From: https://arxiv.org/abs/2110.09456.'''
        self.res_scale1 = Scale(dim=dim, init_value=res_scale_init_value) \
            if res_scale_init_value else nn.Identity()
        self.res_scale2 = Scale(dim=dim, init_value=res_scale_init_value) \
            if res_scale_init_value else nn.Identity()
        # Layer_scale in MetaFormer https://arxiv.org/pdf/2210.13452.pdf   First from CaiT
        '''layer_scale_init_values (list, tuple, float or None): Init value for Layer Scale. Default: None.
            None means not use the layer scale. Form: https://arxiv.org/abs/2103.17239.'''
        self.layer_scale1 = Scale(dim=dim, init_value=layer_scale_init_value) \
            if layer_scale_init_value else nn.Identity()
        self.layer_scale2 = Scale(dim=dim, init_value=layer_scale_init_value) \
            if layer_scale_init_value else nn.Identity()
        
    def forward(self, x, seqlen=1):  # x.shape (BF, J, dim_feat)
        if self.st_mode=='stage_st':
            x = self.res_scale1(x) + self.layer_scale1(self.drop_path(self.attn_s(self.norm1_s(x), seqlen)))
            x = self.res_scale2(x) + self.layer_scale2(self.drop_path(self.mlp_s(self.norm2_s(x))))
            x = self.res_scale1(x) + self.layer_scale1(self.drop_path(self.attn_t(self.norm1_t(x), seqlen)))
            x = self.res_scale2(x) + self.layer_scale2(self.drop_path(self.mlp_t(self.norm2_t(x))))
        elif self.st_mode=='stage_ts':
            x = self.res_scale1(x) + self.layer_scale1(self.drop_path(self.attn_t(self.norm1_t(x), seqlen)))
            x = self.res_scale2(x) + self.layer_scale2(self.drop_path(self.mlp_t(self.norm2_t(x))))
            x = self.res_scale1(x) + self.layer_scale1(self.drop_path(self.attn_s(self.norm1_s(x), seqlen)))  # SepConv_s
            x = self.res_scale2(x) + self.layer_scale2(self.drop_path(self.mlp_s(self.norm2_s(x))))
        elif self.st_mode=='stage_para':
            x_t = self.res_scale1(x) + self.layer_scale1(self.drop_path(self.attn_t(self.norm1_t(x), seqlen)))
            x_t = self.res_scale2(x_t) + self.layer_scale2(self.drop_path(self.mlp_t(self.norm2_t(x_t))))
            x_s = self.res_scale1(x) + self.layer_scale1(self.drop_path(self.attn_s(self.norm1_s(x), seqlen)))
            x_s = self.res_scale2(x_s) + self.layer_scale2(self.drop_path(self.mlp_s(self.norm2_s(x_s))))
            # 每经过 st+ts 就fuse，fuse后继续分成两个分支计算st和ts
            if self.att_fuse: 
                #             x_s, x_t: [BF, J, dim]
                alpha = torch.cat([x_s, x_t], dim=-1)
                BF, J = alpha.shape[:2]
                # alpha = alpha.mean(dim=1, keepdim=True)
                alpha = self.ts_attn(alpha).reshape(BF, J, -1, 2)
                alpha = alpha.softmax(dim=-1)
                x = x_t * alpha[:,:,:,1] + x_s * alpha[:,:,:,0]
            else:
                x = (x_s + x_t)*0.5
        elif self.st_mode=='stage_t':
            x = self.res_scale1(x) + self.layer_scale1(self.drop_path(self.attn_t(self.norm1_t(x), seqlen)))
            x = self.res_scale2(x) + self.layer_scale2(self.drop_path(self.mlp_t(self.norm2_t(x))))
        elif self.st_mode=='stage_s':
            x = self.res_scale1(x) + self.layer_scale1(self.drop_path(self.attn_s(self.norm1_s(x), seqlen)))  
            x = self.res_scale2(x) + self.layer_scale2(self.drop_path(self.mlp_s(self.norm2_s(x))))
        elif self.st_mode=='None':
            x = x
        else:
            raise NotImplementedError(self.st_mode)
        return x
    

mode_map={"para":["stage_s", "stage_t"], 
    "seq-st-st":["stage_st", "None"], 
    "seq-ts-ts":["stage_ts", "None"], 
    "seq-tt-ss":["stage_t", "stage_s"], 
    "seq-ss-tt":["stage_s", "stage_t"]}

class DSTformer(nn.Module):
    def __init__(self, dim_in=3, dim_out=3, dim_feat=256, dim_rep=512,
                 depth=2, num_heads=8, mlp_ratio=4, 
                 num_joints=17, maxlen=243, 
                 qkv_bias=True, qk_scale=None, drop_rate=0., attn_drop_rate=0., drop_path_rate=0., norm_layer=nn.LayerNorm, 
                 att_fuse=True, res_scale_init_values=None, layer_scale_init_values=None, 
                 intermediate=False, run_mode="train", branch_size=5, cho_branch=0):  # st_mode1="stage_st", st_mode2="stage_ts",
        super().__init__()
        self.dim_out = dim_out
        self.dim_feat = dim_feat
        self.joints_embed = nn.Linear(dim_in, dim_feat)
        self.pos_drop = nn.Dropout(p=drop_rate)
        dpr = [x.item() for x in torch.linspace(0, drop_path_rate, depth)]  # stochastic depth decay rule
        self.intermediate = intermediate
        self.depth = depth
        self.run_mode = run_mode
        self.branch_size = branch_size
        self.cho_branch = cho_branch
        # self.st_mode0 = mode_map[self.run_mode][0]
        # self.st_mode1 = mode_map[self.run_mode][1]
        self.blocks_paras = nn.ModuleList([
            Block(
                dim=dim_feat, num_heads=num_heads, mlp_ratio=mlp_ratio, qkv_bias=qkv_bias, qk_scale=qk_scale,
                drop=drop_rate, attn_drop=attn_drop_rate, drop_path=dpr[i], norm_layer=norm_layer, 
                res_scale_init_value=res_scale_init_values[i], layer_scale_init_value=layer_scale_init_values[i],
                st_mode="stage_s")
            for i in range(depth)])
        self.blocks_parat = nn.ModuleList([
            Block(
                dim=dim_feat, num_heads=num_heads, mlp_ratio=mlp_ratio, qkv_bias=qkv_bias, qk_scale=qk_scale,
                drop=drop_rate, attn_drop=attn_drop_rate, drop_path=dpr[i], norm_layer=norm_layer, 
                res_scale_init_value=res_scale_init_values[i], layer_scale_init_value=layer_scale_init_values[i],
                st_mode="stage_t")  
            for i in range(depth)])
        if self.branch_size >=2:
            self.blocks_st = nn.ModuleList([
                Block(
                    dim=dim_feat, num_heads=num_heads, mlp_ratio=mlp_ratio, qkv_bias=qkv_bias, qk_scale=qk_scale,
                    drop=drop_rate, attn_drop=attn_drop_rate, drop_path=dpr[i], norm_layer=norm_layer, 
                    res_scale_init_value=res_scale_init_values[i], layer_scale_init_value=layer_scale_init_values[i],
                    st_mode="stage_st")
                for i in range(depth)])
        if self.branch_size >=3:
            self.blocks_ts = nn.ModuleList([
                Block(
                    dim=dim_feat, num_heads=num_heads, mlp_ratio=mlp_ratio, qkv_bias=qkv_bias, qk_scale=qk_scale,
                    drop=drop_rate, attn_drop=attn_drop_rate, drop_path=dpr[i], norm_layer=norm_layer, 
                    res_scale_init_value=res_scale_init_values[i], layer_scale_init_value=layer_scale_init_values[i],
                    st_mode="stage_ts")
                for i in range(depth)])
        if self.branch_size >=4:
            self.blocks_sstt1 = nn.ModuleList([
                Block(
                    dim=dim_feat, num_heads=num_heads, mlp_ratio=mlp_ratio, qkv_bias=qkv_bias, qk_scale=qk_scale,
                    drop=drop_rate, attn_drop=attn_drop_rate, drop_path=dpr[i], norm_layer=norm_layer, 
                    res_scale_init_value=res_scale_init_values[i], layer_scale_init_value=layer_scale_init_values[i],
                    st_mode="stage_s")
                for i in range(depth)])
            self.blocks_sstt2 = nn.ModuleList([
                Block(
                    dim=dim_feat, num_heads=num_heads, mlp_ratio=mlp_ratio, qkv_bias=qkv_bias, qk_scale=qk_scale,
                    drop=drop_rate, attn_drop=attn_drop_rate, drop_path=dpr[i], norm_layer=norm_layer, 
                    res_scale_init_value=res_scale_init_values[i], layer_scale_init_value=layer_scale_init_values[i],
                    st_mode="stage_t")
                for i in range(depth)])
        if self.branch_size >=5:
            self.blocks_ttss1 = nn.ModuleList([
                Block(
                    dim=dim_feat, num_heads=num_heads, mlp_ratio=mlp_ratio, qkv_bias=qkv_bias, qk_scale=qk_scale,
                    drop=drop_rate, attn_drop=attn_drop_rate, drop_path=dpr[i], norm_layer=norm_layer, 
                    res_scale_init_value=res_scale_init_values[i], layer_scale_init_value=layer_scale_init_values[i],
                    st_mode="stage_t")
                for i in range(depth)])
            self.blocks_ttss2 = nn.ModuleList([
                Block(
                    dim=dim_feat, num_heads=num_heads, mlp_ratio=mlp_ratio, qkv_bias=qkv_bias, qk_scale=qk_scale,
                    drop=drop_rate, attn_drop=attn_drop_rate, drop_path=dpr[i], norm_layer=norm_layer, 
                    res_scale_init_value=res_scale_init_values[i], layer_scale_init_value=layer_scale_init_values[i],
                    st_mode="stage_s")
                for i in range(depth)])
        self.norm = norm_layer(dim_feat)
        if dim_rep:
            self.pre_logits = nn.Sequential(OrderedDict([
                ('fc', nn.Linear(dim_feat, dim_rep)),
                ('act', nn.Tanh())
            ]))
        else:
            self.pre_logits = nn.Identity()
        self.head = nn.Linear(dim_rep, dim_out) if dim_out > 0 else nn.Identity()            
        self.temp_embed = nn.Parameter(torch.zeros(1, maxlen, 1, dim_feat))
        self.pos_embed = nn.Parameter(torch.zeros(1, num_joints, dim_feat))
        trunc_normal_(self.temp_embed, std=.02)
        trunc_normal_(self.pos_embed, std=.02)
        self.apply(self._init_weights)
        self.att_fuse = att_fuse
        if self.att_fuse:
            # only for para branch
            self.para_attn = nn.ModuleList([nn.Linear(dim_feat*2, 2) for i in range(depth)])
            for i in range(depth):
                self.para_attn[i].weight.data.fill_(0)
                self.para_attn[i].bias.data.fill_(0.5)
            # for all branches
            self.branch_attn = nn.Linear(dim_feat*self.branch_size, self.branch_size)
            self.branch_attn.weight.data.fill_(0)
            self.branch_attn.bias.data.fill_(0.5)
        # Output prediction layers.
        if self.intermediate:
            # if dim_rep:
            #     self.intermediate_pred = nn.ModuleList([nn.Sequential(nn.Linear(dim_feat, dim_rep), nn.Tanh(), nn.Linear(dim_rep, dim_out)) for _ in range(self.branch_size)])
            # else:
            #     self.intermediate_pred = nn.ModuleList([nn.Sequential(nn.Linear(dim_rep, dim_out)) for _ in range(self.branch_size)])
            if dim_rep:
                self.intermediate_pred = nn.ModuleList([nn.Sequential(norm_layer(dim_feat), nn.Linear(dim_feat, dim_rep), nn.Tanh(), nn.Linear(dim_rep, dim_out)) for _ in range(self.depth)])
            else:
                self.intermediate_pred = nn.ModuleList([nn.Sequential(nn.Linear(dim_feat, dim_out)) for _ in range(self.self.depth)])

    def _init_weights(self, m):
        if isinstance(m, nn.Linear):
            trunc_normal_(m.weight, std=.02)
            if isinstance(m, nn.Linear) and m.bias is not None:
                nn.init.constant_(m.bias, 0)
        elif isinstance(m, nn.LayerNorm):
            nn.init.constant_(m.bias, 0)
            nn.init.constant_(m.weight, 1.0)

    def get_classifier(self):
        return self.head
    
    def get_run_mode(self):
        print("self.run_mode:", self.run_mode, "self.cho_branch:", self.cho_branch)

    def set_run_mode(self, run_mode="train", cho_branch=0):
        if run_mode=="train":
            self.run_mode = "train"
        elif run_mode=="eval":
            self.run_mode = "eval"
            if cho_branch >= 0 and cho_branch <=self.branch_size:
                self.cho_branch = cho_branch
            else:
                raise NotImplementedError(self.cho_branch)
        else:
            raise NotImplementedError(self.run_mode)  

    def reset_classifier(self, dim_out, global_pool=''):
        self.dim_out = dim_out
        self.head = nn.Linear(self.dim_feat, dim_out) if dim_out > 0 else nn.Identity()

    def forward(self, x, return_rep=False):   
        B, F, J, C = x.shape
        x = x.reshape(-1, J, C)  # (BF, J, C)=(BF, J, dim_in)   C = dim_in
        BF = x.shape[0]
        x = self.joints_embed(x)  # (BF, J, dim_feat)
        x = x + self.pos_embed  # (BF, J, dim_feat) = (BF, J, dim_feat) + (1, J, dim_feat)  broadcast
        _, J, C = x.shape  # C = dim_feat
        x = x.reshape(-1, F, J, C) + self.temp_embed[:,:F,:,:]  # (B, F, J, dim_feat) = (B, F, J, dim_feat) + (1, F, 1, dim_feat)
        x = x.reshape(BF, J, C)  # (BF, J, dim_feat)
        x = self.pos_drop(x)  # dropout

        intermediate_list = []
        if self.run_mode == "train" or self.cho_branch == 0 : # if self.cho_branch==0 and self.run_mode=="eval"
            # 5 branch: "para" "seq-st-st" "seq-ts-ts" "seq-tt-ss" "seq-ss-tt"
            # branch1 para
            x_list = [x.clone() for i in range(self.branch_size)]
            for idx, (blk0, blk1) in enumerate(zip(self.blocks_paras, self.blocks_parat)):
                x_s = blk0(x_list[0], F)
                x_t = blk1(x_list[0], F)
                if self.att_fuse:  #并不是 所有模块走完再fuse的！！即非(st-st-st-st-st)+(ts-ts-ts-ts-ts)后fuse
                    att = self.para_attn[idx]
                    alpha = torch.cat([x_s, x_t], dim=-1)
                    BF, J = alpha.shape[:2]
                    alpha = att(alpha)
                    alpha = alpha.softmax(dim=-1)
                    x_list[0] = x_s * alpha[:,:,0:1] + x_t * alpha[:,:,1:2]
                else:  
                    x_list[0] = (x_s + x_t)*0.5   

                if self.intermediate:
                    pred = x_list[0].clone().reshape(B, F, J, -1)
                    pred = self.intermediate_pred[idx](pred)
                    intermediate_list.append(pred)

            # branch2 seqst
            if self.branch_size>=2:
                for idx, blk in enumerate(self.blocks_st):
                    x_list[1] = blk(x_list[1], F)
            # branch3 seqts
            if self.branch_size>=3:
                for idx, blk in enumerate(self.blocks_ts):
                    x_list[2] = blk(x_list[2], F)
            # branch4 seqsstt
            if self.branch_size>=4:            
                for idx, (blk0, blk1) in enumerate(zip(self.blocks_sstt1, self.blocks_sstt2)):
                    x_list[3] = blk0(x_list[3], F)
                    x_list[3] = blk1(x_list[3], F)
            # branch5 seqttss 
            if self.branch_size>=5:
                for idx, (blk0, blk1) in enumerate(zip(self.blocks_ttss1, self.blocks_ttss2)):
                    x_list[4] = blk0(x_list[4], F)
                    x_list[4] = blk1(x_list[4], F)

            # if self.att_fuse:  #所有branch走完再fuse
            #     att = self.branch_attn
            #     alpha = torch.cat(x_list, dim=-1)
            #     BF, J = alpha.shape[:2]  # BF,J,C
            #     alpha = att(alpha)
            #     alpha = alpha.softmax(dim=-1)
            #     # x = x1 * alpha[:,:,0:1] + x2 * alpha[:,:,1:2] + x3 * alpha[:,:,2:3] + x4 * alpha[:,:,3:4] + x5 * alpha[:,:,4:5] 
            #     for i in range(self.branch_size+1):  # 可以变成残差连接？ 目前没改成残差连接
            #         if i==self.branch_size:
            #             x -= x
            #         else:
            #             x += x_list[i] * alpha[:,:,i:(i+1)] 
            # else:
            #     for i in range(self.branch_size+1):  # 可以变成残差连接？ 目前没改成残差连接
            #         if i==self.branch_size:
            #             x -= x 
            #         else: 
            #             x += x_list[i]
            #     x /= self.branch_size

            # if self.att_fuse:  #所有branch走完再fuse
            #     att = self.branch_attn
            #     alpha = torch.cat([x_list[0], x_list[1], x_list[2], x_list[3], x_list[4]], dim=-1)
            #     BF, J = alpha.shape[:2]
            #     alpha = att(alpha)
            #     alpha = alpha.softmax(dim=-1)
            #     x = x_list[0] * alpha[:,:,0:1] + x_list[1] * alpha[:,:,1:2] + x_list[2] * alpha[:,:,2:3] + x_list[3] * alpha[:,:,3:4] + x_list[4] * alpha[:,:,4:5] 
            # else:  
            #     x = (x_list[0] + x_list[1] + x_list[2] + x_list[3] + x_list[4])*0.2

            # x=x_list[0]
            # x = self.norm(x)    # 前面少了这步呀！！
            # x = x.reshape(B, F, J, -1)

            if self.run_mode == "train" and self.intermediate: 
                # for i in range(self.branch_size+1):
                #     if i==0:
                #         x = self.pre_logits(x)         # [B, F, J, dim_feat]->[B, F, J, dim_rep]
                #         x = self.head(x)
                #         intermediate_list.append(x)
                #     elif i==1:
                #         x_list[0] = x_list[0].reshape(B, F, J, -1)
                #         pred = self.intermediate_pred[i-1](x_list[0])
                #         intermediate_list.append(pred)
                #     elif self.branch_size>=i and i==2:
                #         x_list[1] = x_list[1].reshape(B, F, J, -1)
                #         pred = self.intermediate_pred[i-1](x_list[1])
                #         intermediate_list.append(pred)
                #     elif self.branch_size>=i and i==3:
                #         x_list[2] = x_list[2].reshape(B, F, J, -1)
                #         pred = self.intermediate_pred[i-1](x_list[2])
                #         intermediate_list.append(pred)
                #     elif self.branch_size>=i and i==4:
                #         x_list[3] = x_list[3].reshape(B, F, J, -1)
                #         pred = self.intermediate_pred[i-1](x_list[3])
                #         intermediate_list.append(pred)
                #     elif self.branch_size>=i and i==5:
                #         x_list[4] = x_list[4].reshape(B, F, J, -1)
                #         pred = self.intermediate_pred[i-1](x_list[4])
                #         intermediate_list.append(pred)
                x=x_list[0]
                x = self.norm(x)    # 前面少了这步呀！！
                x = x.reshape(B, F, J, -1)
                x = self.pre_logits(x)         # [B, F, J, dim_feat]->[B, F, J, dim_rep]
                if return_rep:
                    return x
                x = self.head(x)
                intermediate_list.append(x)
                return intermediate_list
            else:  # if self.cho_branch==0 and self.run_mode=="eval"
                x=x_list[0]
                x = self.norm(x)    # 前面少了这步呀！！
                x = x.reshape(B, F, J, -1)
                x = self.pre_logits(x)         # [B, F, J, dim_feat]->[B, F, J, dim_rep]
                if return_rep:
                    return x
                x = self.head(x)
                return x

        elif self.cho_branch != 0 and self.run_mode == "eval":
            # "para" "seq-st-st" "seq-ts-ts" "seq-tt-ss" "seq-ss-tt"
            if self.cho_branch==1:  # "para"
                for idx, (blk0, blk1) in enumerate(zip(self.blocks_paras, self.blocks_parat)):
                    x_st = blk0(x, F)
                    x_ts = blk1(x, F)
                    if self.att_fuse:  # fuse(st-ts)*5
                        att = self.para_attn[idx]
                        alpha = torch.cat([x_st, x_ts], dim=-1)
                        BF, J = alpha.shape[:2]
                        alpha = att(alpha)
                        alpha = alpha.softmax(dim=-1)
                        x = x_st * alpha[:,:,0:1] + x_ts * alpha[:,:,1:2]
                    else:  
                        x = (x_st + x_ts)*0.5
            elif self.branch_size>=self.cho_branch and self.cho_branch==2:  # "seq-st-st"
                for idx, blk in enumerate(self.blocks_st):
                    x = blk(x, F)
            elif self.branch_size>=self.cho_branch and self.cho_branch==3:  # "seq-ts-ts"
                for idx, blk in enumerate(self.blocks_ts):
                    x = blk(x, F)
            elif self.branch_size>=self.cho_branch and self.cho_branch==4:  # "seq-tt-ss"
                for idx, (blk0, blk1) in enumerate(zip(self.blocks_sstt1, self.blocks_sstt2)):
                    x = blk0(x, F)
                    x = blk1(x, F)
            elif self.branch_size>=self.cho_branch and self.cho_branch==5:  # "seq-ss-tt"
                for idx, (blk0, blk1) in enumerate(zip(self.blocks_ttss1, self.blocks_ttss2)):
                    x = blk0(x, F)
                    x = blk1(x, F)               
            else:
                raise NotImplementedError(self.cho_branch)

            x = self.norm(x)
            x = x.reshape(B, F, J, -1)
            x = self.pre_logits(x)         # [B, F, J, dim_feat]->[B, F, J, dim_rep]
            if return_rep:
                return x
            x = self.head(x)
            return x
        else:
            raise NotImplementedError(self.run_mode)

    def get_representation(self, x):
        return self.forward(x, return_rep=True)
    