import config
from  models import *
import json
import os 

from argparse import ArgumentParser
parser = ArgumentParser("Settings")
parser.add_argument("--dataset", default="WN18RR", help="Name of the dataset.")
parser.add_argument("--work_threads", default=8, type=int, help="work_threads")
parser.add_argument("--train_times", default=8000, type=int, help="Number of training epochs")
parser.add_argument("--nbatches", default=100, type=int, help="Number of batches")
parser.add_argument("--alpha", default=0.1, type=float, help="Learning rate")
parser.add_argument("--bern", default=1, type=int, help="bern or uni")
parser.add_argument('--dimension', type=int, default=256, help='')
parser.add_argument("--lmbda", default=0.5, type=float, help="")
parser.add_argument("--lmbda_two", default=0.01, type=float, help="")
parser.add_argument("--margin", default=1.0, type=float, help="")
parser.add_argument('--ent_neg_rate', default=5, type=int, help='')
parser.add_argument('--rel_neg_rate', default=0, type=int, help='')
parser.add_argument("--optim", default='adagrad', help="")
parser.add_argument('--save_steps', type=int, default=10000, help='')
parser.add_argument('--valid_steps', type=int, default=400, help='')
parser.add_argument('--early_stopping_patience', type=int, default=10, help='')
parser.add_argument("--checkpoint_dir", default="./checkpoint", type=str)
parser.add_argument("--result_dir", default="./result", type=str)
parser.add_argument("--model", default="QuatE", help="Name of the model.")
parser.add_argument("--mode", choices=["train", "predict"], default="train", type=str)
parser.add_argument("--model_name", default='', help="")
args = parser.parse_args()

if args.model_name is None or len(args.model_name.strip()) == 0:
    args.model_name = "{}_lda-{}_nneg-{}_hs-{}_lr-{}_nepochs-{}".format(args.model,
                                                                        args.dataset,
                                                                        args.train_times,
                                                                        args.nbatches,
                                                                        args.alpha,
                                                                        args.dimension,
                                                                        args.lmbda,
                                                                        args.lmbda_two,
                                                                        args.ent_neg_rate                                                                        
)
print(args)

# out_dir = os.path.abspath(os.path.join("../runs_QTransE/"))
# print("Writing to {}\n".format(out_dir))
# # Checkpoint directory
# checkpoint_dir = os.path.abspath(os.path.join(out_dir, "checkpoints"))
result_dir = os.path.abspath(os.path.join(args.checkpoint_dir, args.model_name))
if not os.path.exists(args.checkpoint_dir):
    os.makedirs(args.checkpoint_dir)
if not os.path.exists(result_dir):
    os.makedirs(result_dir)


con = config.Config()
in_path = "./benchmarks/" + args.dataset + "/"
con.set_in_path(in_path)
con.set_work_threads(args.work_threads)
con.set_train_times(args.train_times) #num_epochs
con.set_nbatches(args.nbatches)
con.set_alpha(args.alpha) #learning_rate
con.set_bern(args.bern)
con.set_dimension(args.dimension) #hidden_size
con.set_lmbda(args.lmbda)
con.set_lmbda_two(args.lmbda_two)
con.set_margin(args.margin)
con.set_ent_neg_rate(args.ent_neg_rate)
con.set_rel_neg_rate(args.rel_neg_rate)
con.set_opt_method(args.optim)
con.set_save_steps(args.save_steps)
con.set_valid_steps(args.valid_steps)
con.set_early_stopping_patience(args.early_stopping_patience)
con.set_checkpoint_dir(result_dir)
con.set_result_dir(result_dir)

# con.set_checkpoint_dir(checkpoint_dir)
# con.set_result_dir(result_dir)

# knowledge graph completion ~ link prediction
con.set_test_link(True)
con.set_test_triple(True)
con.init()

# training mode
if args.mode == "train":
    if args.model == "RQE":
        con.set_train_model(RQE)   
    elif args.model == "HRQE":
        con.set_train_model(HRQE)
    elif args.model == "QuatE":
        con.set_train_model(QuatE)
    con.train()
# prediction mode
else:
    if args.model == "RQE":
        con.set_test_model(RQE, result_dir+'/'+args.model+'.ckpt')
    elif args.model == "HRQE":
        con.set_test_model(HRQE, result_dir+'/'+args.model+'.ckpt')
    elif args.model == "QuatE":
        con.set_test_model(QuatE, result_dir+'/'+args.model+'.ckpt')
    con.test()

