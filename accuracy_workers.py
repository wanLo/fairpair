from scipy.stats import norm
from scipy import integrate
import mpmath
import numpy as np
import torch

from fairpair import *

import sys
sys.path.append('../GNNRank/')
from src.param_parser import ArgsNamespace # just import the class, not the parser
from src.Trainer import Trainer

def get_cutoff_accuracy(trial:int, N=400, Nm=200):
    accuracy = []
    H = FairPairGraph()
    H.generate_groups(N, Nm) # same size groups
    H.group_assign_scores(nodes=H.nodes, loc=0, scale=1) # general score distribution
    sampler = RandomSampling(H, warn=False)
    ranker = RankRecovery(H)
    ranking = None
    for j in range(101):
        sampler.apply(iter=100, k=1)
        for cutoff in [0.3, 0.4, 0.5, 0.6, 0.7, 0.8]:
            # make sure to use separate directories for each thread
            ranking, other_nodes = ranker.apply(rank_using='fairPageRank', cutoff=cutoff, path=f'data/tmp{trial}')
            if len(other_nodes) == 0:
                tau = weighted_tau(H, ranking)
                accuracy.append((trial, j*100, cutoff, tau))
    return accuracy


def get_simulated_cutoff(trial:int, method:rankCentrality, N=400, Nm=200):
    accuracy = []
    H = FairPairGraph()
    H.generate_groups(N, Nm) # same size groups
    H.group_assign_scores(nodes=H.nodes, loc=0, scale=1) # general score distribution
    sampler = RandomSampling(H, warn=False)
    ranking = None
    for j in range(101):
        sampler.apply(iter=10, k=1)
        for cutoff in [0.4]:
            if method == 'fairPageRank':
                name = method
                ranker = RankRecovery(H)
                ranking, other_nodes = ranker.apply(rank_using='fairPageRank', cutoff=cutoff, path=f'data/tmp{trial}')
            else:
                name = method.__name__
                # simulate cut-off
                G = FairPairGraph()
                edges = H.edges(data='weight')
                edges = [(outgoing, incoming, 1) for outgoing, incoming, weight in edges if weight>=cutoff]
                G.add_weighted_edges_from(edges)
                ranker = RankRecovery(G)
                ranking, other_nodes = ranker.apply(rank_using=method) # by default, apply rankCentrality method
            if len(other_nodes) == 0:
                tau = weighted_tau(H, ranking)
                accuracy.append((trial, j*10, cutoff, tau, name))
    return accuracy


def get_method_accuracy(trial:int, method=rankCentrality, N=400, Nm=200):
    accuracy = []
    H = FairPairGraph()
    H.generate_groups(N, Nm) # same size groups
    H.assign_skills(loc=0, scale=0.86142674) # general skill distribution
    H.assign_bias(nodes=H.minority_nodes, loc=-1.43574282, scale=0.43071336) # add bias to unprivileged group
    sampler = RandomSampling(H, warn=False)
    ranker = RankRecovery(H)
    ranking = None
    for j in range(11):
        sampler.apply(iter=100, k=1)
        if method == 'fairPageRank':
            name = method
            ranking, other_nodes = ranker.apply(rank_using=method, path=f'data/tmp{trial}')
        else:
            name = method.__name__
            ranking, other_nodes = ranker.apply(rank_using=method) # by default, apply rankCentrality method
        if len(other_nodes) == 0:
            tau = weighted_tau(H, ranking)
            accuracy.append((trial, j*100, tau, 'Overall', name))
            #tau = weighted_tau(H, ranking, H.majority)
            #accuracy.append((trial, j*10, tau, 'Priviledged', name))
            #tau = weighted_tau(H, ranking, H.minority)
            #accuracy.append((trial, j*10, tau, 'Unpriviledged', name))
            #tau = weighted_tau_separate(H, ranking, H.majority)
            #accuracy.append((trial, j*10, tau[0], 'Priviledged within-group', name))
            #accuracy.append((trial, j*10, tau[1], 'Between groups', name))
            #tau = weighted_tau_separate(H, ranking, H.minority, calc_between=False)
            #accuracy.append((trial, j*10, tau[0], 'Unpriviledged within-group', name))
    return accuracy


def get_GNNRank_accuracy(trial:int):
    accuracy = []
    args = ArgsNamespace(AllTrain=True, ERO_style='uniform', F=70, Fiedler_layer_num=5, K=20, N=350, SavePred=False, all_methods=['DIGRAC', 'ib'],
                     alpha=1.0, baseline='syncRank', cuda=True, data_path='/home/jovyan/GNNRank/src/../data/', dataset='fairPair_test/',
                     debug=False, device=torch.device(type='cuda'), dropout=0.5, early_stopping=200, epochs=1000, eta=0.1, fill_val=0.5, hidden=8, hop=2,
                     load_only=False, log_root='/home/jovyan/GNNRank/src/../logs/', lr=0.01, no_cuda=False, num_trials=1, optimizer='Adam', p=0.05,
                     pretrain_epochs=50, pretrain_with='dist', regenerate_data=True, season=1990, seed=31, seeds=[10], sigma=1.0, tau=0.5, test_ratio=1,
                     train_ratio=1, train_with='proximal_baseline', trainable_alpha=False, upset_margin=0.01, upset_margin_coeff=0, upset_ratio_coeff=1.0, weight_decay=0.0005)
    torch.manual_seed(args.seed)

    H = FairPairGraph()
    H.generate_groups(400, 200) # same size groups
    H.assign_skills(loc=0, scale=0.86142674) # general skill distribution
    #H.assign_bias(nodes=H.minority_nodes, loc=-1.43574282, scale=0.43071336) # add bias to unprivileged group
    sampler = RandomSampling(H, warn=False)
    ranking = None
    for j in range(11):
        sampler.apply(iter=100, k=1)
        if (nx.is_strongly_connected(H)):
            adj = nx.linalg.graphmatrix.adjacency_matrix(H, weight='weight') # returns a sparse matrix
            trainer = Trainer(args, random_seed=10, save_name_base='test', adj=adj) # initialize with the given adjacency matrix
            save_path_best, save_path_latest = trainer.train(model_name='ib')
            score, pred_label = trainer.predict_nn(model_name='ib', model_path=save_path_best, A=adj, GNN_variant='proximal_baseline')
            ranking = {key: 1-score for key, score in enumerate(score.cpu().detach().numpy())}
            tau = weighted_tau(H, ranking)
            accuracy.append((trial, j*100, tau, 'Overall'))
            #tau = weighted_tau(H, ranking, H.majority)
            #accuracy.append((trial, j*10, tau, 'Priviledged'))
            #tau = weighted_tau(H, ranking, H.minority)
            #accuracy.append((trial, j*10, tau, 'Unpriviledged'))
            #tau = weighted_tau_separate(H, ranking, H.majority)
            #accuracy.append((trial, j*10, tau[0], 'Priviledged within-group'))
            #accuracy.append((trial, j*10, tau[1], 'Between groups'))
            #tau = weighted_tau_separate(H, ranking, H.minority, calc_between=False)
            #accuracy.append((trial, j*10, tau[0], 'Unpriviledged within-group'))
    return accuracy