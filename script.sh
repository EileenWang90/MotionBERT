# train
# 2022.12.1 19:00 4v100 一个epoch6分钟，60个epoch大概6-7小时
# 2080Ti的话需要改小batchsize
# fintune 60 epochs; from scratch 120 epochs
python train.py --config configs/pose3d/MB_train_h36m.yaml --resume checkpoint/pose3d/MB_train_h36m/latest_epoch.bin --checkpoint checkpoint/pose3d/MB_train_h36m |& tee train_scratch.log
python train.py --config configs/pose3d/MB_ft_h36m.yaml --pretrained checkpoint/pretrain/ --checkpoint checkpoint/pose3d/FT_MB_release_MB_ft_h36m |& tee train_finetune.log

# test
python train.py --config configs/pose3d/MB_ft_h36m.yaml --evaluate checkpoint/pose3d/FT_MB_release_MB_ft_h36m/best_epoch.bin |& tee test_finetune.log
python train.py --config configs/pose3d/MB_train_h36m.yaml --evaluate checkpoint/pose3d/MB_train_h36m/best_epoch.bin |& tee test_scratch.log

# 12.17 ResScale
python train.py --config configs/pose3d/MB_train_h36m.yaml --checkpoint checkpoint/pose3d/MB_train_h36m |& tee train_scratch_resscale.log