## Dependencies
- Python 3.6+
- PyTorch 1.0+
- NumPy 1.17.2+

## Reproduce the Results
To reproduce the results of RQE and HRQE on WN18RR, FB15k237, WN18 and FB15K,
please run the following commands.

```shell script
#################################### WN18RR ####################################
# RQE
CUDA_VISIBLE_DEVICES=2 nohup python train_models.py --model RQE --dataset WN18RR --train_times 40000 --nbatches 10 --alpha 0.02 --dimension 300 --lmbda 0.25 --lmbda_two 0.25 --ent_neg_rate 2 --valid_step 2000 >./logs/RQE-WN18RR-0.out 2>&1 &

# HRQE
CUDA_VISIBLE_DEVICES=3 nohup python train_models.py  --model HRQE --dataset WN18RR --train_times 50000 --nbatches 10 --alpha 0.1 --dimension 300 --lmbda 0.3 --lmbda_two 0.01 --ent_neg_rate 1 --valid_step 2000 >./logs/HRQE-WN18RR-0.out 2>&1 &


#################################### FB15K237 ####################################
# RQE
CUDA_VISIBLE_DEVICES=3 nohup python train_models.py --model RQE --dataset FB15K237 --train_times 8000 --nbatches 100 --alpha 0.02 --dimension 500 --lmbda 0.5 --lmbda_two 0.01 --ent_neg_rate 10 --valid_step 400 >./logs/RQE-FB15K237-0.out 2>&1 &

# HRQE
CUDA_VISIBLE_DEVICES=2 nohup python train_models.py  --model HRQE --dataset FB15K237 --train_times 5000 --nbatches 100 --alpha 0.05 --dimension 500 --lmbda 0.5 --lmbda_two 0.01 --ent_neg_rate 10 --valid_step 400 >./logs/HRQE-FB15K237-0.out 2>&1 &


#################################### WN18 ####################################
# RQE
CUDA_VISIBLE_DEVICES=0 nohup python train_models.py --model RQE --dataset WN18 --train_times 4000 --nbatches 10 --alpha 0.04 --dimension 300 --lmbda 0.03 --lmbda_two 0.0 --ent_neg_rate 10 --valid_step 400 >./logs/RQE-WN18-0.out 2>&1 &

# HRQE
CUDA_VISIBLE_DEVICES=2 nohup python train_models.py --model HRQE --dataset WN18 --train_times 8000 --nbatches 10 --alpha 0.05 --dimension 300 --lmbda 0.05 --lmbda_two 0.01 --ent_neg_rate 10 --valid_step 1000 >./logs/HRQE-WN18-0.out 2>&1 & #


#################################### FB15K ####################################
# RQE
CUDA_VISIBLE_DEVICES=3 nohup python train_models.py --model RQE --dataset FB15K --train_times 2000 --nbatches 100 --alpha 0.02 --dimension 400 --lmbda 0.05 --lmbda_two 0.0 --ent_neg_rate 10 --valid_step 200 >./logs/RQE-FB15K-0.out 2>&1 &

# HRQE
CUDA_VISIBLE_DEVICES=2 nohup python train_models.py --model HRQE --dataset FB15K --train_times 4000 --nbatches 100 --alpha 0.02 --dimension 400 --lmbda 0.05 --lmbda_two 0.0 --ent_neg_rate 10 --valid_step 400 >./logs/HRQE-FB15K-0.out 2>&1 &
```



## Acknowledgement

This code is based on the OpenKE project.

We refer to the code of [QuatE](https://github.com/cheungdaven/QuatE). Thanks for their contributions.
