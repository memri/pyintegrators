# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/indexers.FaceClusteringIndexer.Utils.ipynb (unless otherwise specified).

__all__ = ['confidence2clusters', 'group_clusters', 'sparse_mx_to_indices_values', 'sparse_mx_to_torch_sparse_tensor',
           'indices_values_to_sparse_tensor', 'build_symmetric_adj', 'row_normalize', 'peaks_to_edges',
           'confidence_to_peaks', 'peaks_to_labels', 'build_knns', 'edge_to_connected_graph', 'knns2ordered_nbrs',
           'read_meta', 'read_probs', 'fast_knns2spmat', 'l2norm', 'knn_faiss']

# Cell
import torch
import ipdb
import numpy as np
import scipy.sparse as sp
from collections import Counter
import cv2
import os
from pathlib import Path
from mmcv.runner import load_checkpoint

# Cell

def confidence2clusters(confidences, dists, nbrs, tau):
    pred_dist2peak, pred_peaks = confidence_to_peaks(dists, nbrs, confidences, max_conn=1)
    cluster_labels = peaks_to_labels(pred_peaks, pred_dist2peak, tau=tau, inst_num=dists.shape[0])
    return cluster_labels

def group_clusters(photos, cluster_labels, min_cluster_size=2):
    clusters = [c for c in set(cluster_labels) if list(cluster_labels).count(c) >= min_cluster_size]
    return [np.array(photos)[np.where(cluster_labels == c)[0]] for c in clusters]

def sparse_mx_to_indices_values(sparse_mx):
    sparse_mx = sparse_mx.tocoo().astype(np.float32)
    indices = np.vstack((sparse_mx.row, sparse_mx.col)).astype(np.int64)
    values = sparse_mx.data
    shape = np.array(sparse_mx.shape)
    return indices, values, shape

def sparse_mx_to_torch_sparse_tensor(sparse_mx):
    """Convert a scipy sparse matrix to a torch sparse tensor."""
    indices, values, shape = sparse_mx_to_indices_values(sparse_mx)
    return indices_values_to_sparse_tensor(indices, values, shape)

def indices_values_to_sparse_tensor(indices, values, shape):
    indices = torch.from_numpy(indices)
    values = torch.from_numpy(values)
    shape = torch.Size(shape)
    return torch.sparse.FloatTensor(indices, values, shape)

def build_symmetric_adj(adj, self_loop=True):
    adj = adj + adj.T.multiply(adj.T > adj) - adj.multiply(adj.T > adj)
    if self_loop:
        adj = adj + sp.eye(adj.shape[0])
    return adj

def row_normalize(mx):
    """Row-normalize sparse matrix"""
    rowsum = np.array(mx.sum(1))
    # if rowsum <= 0, keep its previous value
    rowsum[rowsum <= 0] = 1
    r_inv = np.power(rowsum, -1).flatten()
    r_inv[np.isinf(r_inv)] = 0.
    r_mat_inv = sp.diags(r_inv)
    mx = r_mat_inv.dot(mx)
    return mx

def peaks_to_edges(peaks, dist2peak, tau):
    edges = []
    for src in peaks:
        dsts = peaks[src]
        dists = dist2peak[src]
        for dst, dist in zip(dsts, dists):
            if src == dst or dist >= 1 - tau:
                continue
            edges.append([src, dst])
    return edges

def confidence_to_peaks(dists, nbrs, confidence, max_conn=1):
    # Note that dists has been sorted in ascending order
    assert dists.shape[0] == confidence.shape[0]
    assert dists.shape == nbrs.shape

    num, _ = dists.shape
    dist2peak = {i: [] for i in range(num)}
    peaks = {i: [] for i in range(num)}

    for i, nbr in enumerate(nbrs):
        nbr_conf = confidence[nbr]
        for j, c in enumerate(nbr_conf):
            nbr_idx = nbr[j]
            if i == nbr_idx or c <= confidence[i]:
                continue
            dist2peak[i].append(dists[i, j])
            peaks[i].append(nbr_idx)
            if len(dist2peak[i]) >= max_conn:
                break
    return dist2peak, peaks

def _find_parent(parent, u):
    idx = []
    # parent is a fixed point
    while (u != parent[u]):
        idx.append(u)
        u = parent[u]
    for i in idx:
        parent[i] = u
    return u

def peaks_to_labels(peaks, dist2peak, tau, inst_num):
    edges = peaks_to_edges(peaks, dist2peak, tau)
    pred_labels = edge_to_connected_graph(edges, inst_num)
    return pred_labels

def build_knns(knn_prefix, feats, knn_method, k,num_process=None, is_rebuild=False, feat_create_time=None):
    knn_prefix = os.path.join(knn_prefix, '{}_k_{}'.format(knn_method, k))
    index_path = knn_prefix + '.index'
    index = knn_faiss(feats, k, index_path, omp_num_threads=num_process, rebuild_index=True)
    knns = index.knns
    return knns

def edge_to_connected_graph(edges, num):
    parent = list(range(num))
    for u, v in edges:
        p_u = _find_parent(parent, u)
        p_v = _find_parent(parent, v)
        parent[p_u] = p_v

    for i in range(num):
        parent[i] = _find_parent(parent, i)
    remap = {}
    uf = np.unique(np.array(parent))
    for i, f in enumerate(uf):
        remap[f] = i
    cluster_id = np.array([remap[f] for f in parent])
    return cluster_id

def knns2ordered_nbrs(knns, sort=True):
    if isinstance(knns, list):
        knns = np.array(knns)
    nbrs = knns[:, 0, :].astype(np.int32)
    dists = knns[:, 1, :]
    if sort:
        # sort dists from low to high
        nb_idx = np.argsort(dists, axis=1)
        idxs = np.arange(nb_idx.shape[0]).reshape(-1, 1)
        dists = dists[idxs, nb_idx]
        nbrs = nbrs[idxs, nb_idx]
    return dists, nbrs

def read_meta(fn_meta, start_pos=0, verbose=True):
    lb2idxs = {}
    idx2lb = {}
    with open(fn_meta) as f:
        for idx, x in enumerate(f.readlines()[start_pos:]):
            lb = int(x.strip())
            if lb not in lb2idxs:
                lb2idxs[lb] = []
            lb2idxs[lb] += [idx]
            idx2lb[idx] = lb

    inst_num = len(idx2lb)
    cls_num = len(lb2idxs)
    if verbose:
        print('[{}] #cls: {}, #inst: {}'.format(fn_meta, cls_num, inst_num))
    return lb2idxs, idx2lb

def read_probs(path, inst_num, feat_dim, dtype=np.float32, verbose=False):
    assert (inst_num > 0 or inst_num == -1) and feat_dim > 0
    count = -1
    if inst_num > 0:
        count = inst_num * feat_dim
    probs = np.fromfile(path, dtype=dtype, count=count)

    if feat_dim > 1:
        probs = probs.reshape(inst_num, feat_dim)
    if verbose:
        print('[{}] shape: {}'.format(path, probs.shape))
    return probs

def fast_knns2spmat(knns, k, th_sim=0.7, use_sim=False, fill_value=None):
    # convert knns to symmetric sparse matrix
    from scipy.sparse import csr_matrix
    eps = 1e-5
    n = len(knns)
    if isinstance(knns, list):
        knns = np.array(knns)
    nbrs = knns[:, 0, :]
    dists = knns[:, 1, :]
    # assert -eps <= dists.min() <= dists.max(
    # ) <= 1 + eps, "min: {}, max: {}".format(dists.min(), dists.max())
    if use_sim:
        sims = 1. - dists
    else:
        sims = dists
    if fill_value is not None:
        print('[fast_knns2spmat] edge fill value:', fill_value)
        sims.fill(fill_value)
    row, col = np.where(sims >= th_sim)
    # remove the self-loop
    idxs = np.where(row != nbrs[row, col])
    row = row[idxs]
    col = col[idxs]
    data = sims[row, col]
    col = nbrs[row, col]  # convert to absolute column
    assert len(row) == len(col) == len(data)
    spmat = csr_matrix((data, (row, col)), shape=(n, n))
    return spmat

def l2norm(vec):
    vec /= np.linalg.norm(vec, axis=1).reshape(-1, 1)
    return vec

# Cell
class knn_faiss():
    def __init__(self, feats, k, index_key='', nprobe=128, omp_num_threads=None,
                 rebuild_index=True, verbose=True,**kwargs):
        import faiss
        if omp_num_threads is not None:
            faiss.omp_set_num_threads(omp_num_threads)
        self.verbose = verbose
        feats = feats.astype('float32')
        _, dim = feats.shape
        index = faiss.IndexFlatIP(dim)
        index.add(feats)
        sims, nbrs = index.search(feats, k=k)
        self.knns = [(np.array(nbr, dtype=np.int32), 1 - np.array(sim, dtype=np.float32))
                     for nbr, sim in zip(nbrs, sims)]