# train
# 2022.12.1 19:00 4v100 一个epoch6分钟，60个epoch大概6-7小时
# 2080Ti的话需要改小batchsize
# fintune 60 epochs; from scratch 120 epochs
python train.py --config configs/pose3d/MB_train_h36m.yaml --resume checkpoint/pose3d/MB_train_h36m/latest_epoch.bin --checkpoint checkpoint/pose3d/MB_train_h36m |& tee train_scratch.log
python train.py --config configs/pose3d/MB_ft_h36m.yaml --pretrained checkpoint/pretrain/ --checkpoint checkpoint/pose3d/FT_MB_release_MB_ft_h36m |& tee train_finetune.log

# 2023.02.22 6 2080Ti bs2048 显存6637M 一个epoch3分钟，120个epoch大概6小时  会自动续上latest_epoch
python train.py --config configs/pose3d/MB_train_h36m_f9s3.yaml --checkpoint checkpoint/pose3d/MB_train_h36m_f9s3_para |& tee train_f9s3_para1.log
python train.py --config configs/pose3d/MB_train_h36m_f9s3.yaml --evaluate checkpoint/pose3d/MB_train_h36m_f9s3_para/best_epoch.bin  # evaluate latest_epoch.bin
# 可以调一下 dropout的大小，目前没有dropout
# 2023.02.23 2 V100 bs2048应该是总bs 显存16430M 一个epoch3分钟，120个epoch大概6小时 比较差
python train.py --config configs/pose3d/MB_train_h36m_f9s3_seqst.yaml --checkpoint checkpoint/pose3d/MB_train_h36m_f9s3_seqst |& tee ./checkpoint/pose3d/MB_train_h36m_f9s3_seqst/train_f9s3_seqst.log
python train.py --config configs/pose3d/MB_train_h36m_f9s3_seqst.yaml --evaluate checkpoint/pose3d/MB_train_h36m_f9s3_seqst/best_epoch.bin |& tee ./checkpoint/pose3d/MB_train_h36m_f9s3_seqst/test_f9s3_seqst.log 
# 2023.02.23 2 V100 bs2048 显存16430M 一个epoch3分钟，120个epoch大概6小时 
python train.py --config configs/pose3d/MB_train_h36m_f9s3_seqts.yaml --checkpoint checkpoint/pose3d/MB_train_h36m_f9s3_seqts |& tee ./checkpoint/pose3d/MB_train_h36m_f9s3_seqts/train_f9s3_seqts.log
python train.py --config configs/pose3d/MB_train_h36m_f9s3_seqts.yaml --evaluate checkpoint/pose3d/MB_train_h36m_f9s3_seqts/best_epoch.bin |& tee ./checkpoint/pose3d/MB_train_h36m_f9s3_seqts/test_f9s3_seqts.log 
# 2023.02.23 2 V100 bs2048 显存16430M 一个epoch3分钟，120个epoch大概6小时
python train.py --config configs/pose3d/MB_train_h36m_f9s3_seqttss.yaml --checkpoint checkpoint/pose3d/MB_train_h36m_f9s3_seqttss |& tee ./checkpoint/pose3d/MB_train_h36m_f9s3_seqttss/train_f9s3_seqttss.log
python train.py --config configs/pose3d/MB_train_h36m_f9s3_seqttss.yaml --evaluate checkpoint/pose3d/MB_train_h36m_f9s3_seqttss/best_epoch.bin |& tee ./checkpoint/pose3d/MB_train_h36m_f9s3_seqttss/test_f9s3_seqttss.log 
# 2023.02.23 2 V100 bs2048 显存16430M 一个epoch3分钟，120个epoch大概6小时 比较差
python train.py --config configs/pose3d/MB_train_h36m_f9s3_seqsstt.yaml --checkpoint checkpoint/pose3d/MB_train_h36m_f9s3_seqsstt |& tee ./checkpoint/pose3d/MB_train_h36m_f9s3_seqsstt/train_f9s3_seqsstt.log
python train.py --config configs/pose3d/MB_train_h36m_f9s3_seqsstt.yaml --evaluate checkpoint/pose3d/MB_train_h36m_f9s3_seqsstt/best_epoch.bin |& tee ./checkpoint/pose3d/MB_train_h36m_f9s3_seqsstt/test_f9s3_seqsstt.log 
# 2023.02.25 6 2080Ti bs2048应该是总bs 比较depth 3,5,8,10 depth越大一个epoch时长越长
python train.py --config configs/pose3d/MB_train_h36m_f9s3_seqst3.yaml --checkpoint checkpoint/pose3d/MB_train_h36m_f9s3_seqst3 |& tee ./checkpoint/pose3d/MB_train_h36m_f9s3_seqst3/train_f9s3_seqst3.log
python train.py --config configs/pose3d/MB_train_h36m_f9s3_seqst3.yaml --evaluate checkpoint/pose3d/MB_train_h36m_f9s3_seqst3/best_epoch.bin |& tee ./checkpoint/pose3d/MB_train_h36m_f9s3_seqst3/test_f9s3_seqst3.log 
python train.py --config configs/pose3d/MB_train_h36m_f9s3_seqst8.yaml --checkpoint checkpoint/pose3d/MB_train_h36m_f9s3_seqst8 |& tee ./checkpoint/pose3d/MB_train_h36m_f9s3_seqst8/train_f9s3_seqst8.log
python train.py --config configs/pose3d/MB_train_h36m_f9s3_seqst8.yaml --evaluate checkpoint/pose3d/MB_train_h36m_f9s3_seqst8/best_epoch.bin |& tee ./checkpoint/pose3d/MB_train_h36m_f9s3_seqst8/test_f9s3_seqst8.log 
python train.py --config configs/pose3d/MB_train_h36m_f9s3_seqst10.yaml --checkpoint checkpoint/pose3d/MB_train_h36m_f9s3_seqst8 |& tee ./checkpoint/pose3d/MB_train_h36m_f9s3_seqst10/train_f9s3_seqst10.log
python train.py --config configs/pose3d/MB_train_h36m_f9s3_seqst10.yaml --evaluate checkpoint/pose3d/MB_train_h36m_f9s3_seqst8/best_epoch.bin |& tee ./checkpoint/pose3d/MB_train_h36m_f9s3_seqst10/test_f9s3_seqst10.log 

# 2023.02.26 branch 6 2080Ti 显存8983M bs1024  5 para_branch depth=3 train1epoch=06'30 eval1epoch=3' 直接需要20h了。。
python train.py --config configs/pose3d/MB_train_h36m_f9s3_branch.yaml --checkpoint checkpoint/pose3d/MB_train_h36m_f9s3_branch |& tee ./checkpoint/pose3d/MB_train_h36m_f9s3_branch/train_f9s3_branch.log
python train.py --config configs/pose3d/MB_train_h36m_f9s3_branch.yaml --evaluate checkpoint/pose3d/MB_train_h36m_f9s3_branch/best_epoch.bin |& tee ./checkpoint/pose3d/MB_train_h36m_f9s3_branch/test_f9s3_branch.log 
# 2023.02.27 branch_inter 2 V100 可用显存20G, 6 2080Ti 显存8983M,  bs1024  5 para_branch depth=3  train1epoch=06'30 eval1epoch=3' 直接需要20h了。。
python train.py --config configs/pose3d/MB_train_h36m_f9s3_branch_inter.yaml --checkpoint checkpoint/pose3d/MB_train_h36m_f9s3_branch_inter |& tee ./checkpoint/pose3d/MB_train_h36m_f9s3_branch_inter/train_f9s3_branch_inter.log
python train.py --config configs/pose3d/MB_train_h36m_f9s3_branch_inter.yaml --evaluate checkpoint/pose3d/MB_train_h36m_f9s3_branch_inter/best_epoch.bin |& tee ./checkpoint/pose3d/MB_train_h36m_f9s3_branch_inter/test_f9s3_branch_inter.log 
# --evaluate checkpoint/pose3d/MB_train_h36m_f9s3_branch_inter/lastest_epoch.bin
# 2023.02.28 branch_inter_mean并不是mean 2 V100 可用显存20G, 6 2080Ti 显存8983M,  bs1024  5 para_branch depth=3  train1epoch=7分钟 eval1epoch=3' 直接需要20h了。。
python train.py --config configs/pose3d/MB_train_h36m_f9s3_branch_inter_mean.yaml --checkpoint checkpoint/pose3d/MB_train_h36m_f9s3_branch_inter_mean |& tee ./checkpoint/pose3d/MB_train_h36m_f9s3_branch_inter_mean/train_f9s3_branch_inter_mean.log
python train.py --config configs/pose3d/MB_train_h36m_f9s3_branch_inter_mean.yaml --evaluate checkpoint/pose3d/MB_train_h36m_f9s3_branch_inter_mean/best_epoch.bin |& tee ./checkpoint/pose3d/MB_train_h36m_f9s3_branch_inter_mean/test_f9s3_branch_inter_mean.log 
# 2023.03.02 branch_inter_KD 2 V100 可用显存20G, 6 2080Ti 显存M,  bs1024 单卡V100测试是depth=1  5 para_branch depth=3  train1epoch=分钟 eval1epoch=3' 直接需要20h了。。
python train.py --config configs/pose3d/MB_train_h36m_f9s3_branch_inter_KD.yaml --checkpoint checkpoint/pose3d/MB_train_h36m_f9s3_branch_inter_KD |& tee ./checkpoint/pose3d/MB_train_h36m_f9s3_branch_inter_KD/train_f9s3_branch_inter_KD.log
python train.py --config configs/pose3d/MB_train_h36m_f9s3_branch_inter_KD.yaml --evaluate checkpoint/pose3d/MB_train_h36m_f9s3_branch_inter_KD/best_epoch.bin |& tee ./checkpoint/pose3d/MB_train_h36m_f9s3_branch_inter_KD/test_f9s3_branch_inter_KD.log 
# 2023.03.02 branch_inter_KD 2 V100 可用显存20G, 6 2080Ti 显存M,  bs1024 单卡V100测试是depth=1  5 para_branch depth=3  train1epoch=分钟 eval1epoch=3' 直接需要20h了。。
python train.py --config configs/pose3d/MB_train_h36m_f9s3_branch_inter_KDmean.yaml --checkpoint checkpoint/pose3d/MB_train_h36m_f9s3_branch_inter_KDmean |& tee ./checkpoint/pose3d/MB_train_h36m_f9s3_branch_inter_KD/train_f9s3_branch_inter_KDmean.log
python train.py --config configs/pose3d/MB_train_h36m_f9s3_branch_inter_KDmean.yaml --evaluate checkpoint/pose3d/MB_train_h36m_f9s3_branch_inter_KDmean/best_epoch.bin |& tee ./checkpoint/pose3d/MB_train_h36m_f9s3_branch_inter_KD/test_f9s3_branch_inter_KDmean.log 






# test
python train.py --config configs/pose3d/MB_ft_h36m.yaml --evaluate checkpoint/pose3d/FT_MB_release_MB_ft_h36m/best_epoch.bin |& tee test_finetune.log
python train.py --config configs/pose3d/MB_train_h36m.yaml --evaluate checkpoint/pose3d/MB_train_h36m_origin/best_epoch.bin |& tee -a test_scratch.log





# 12.17 ResScale
python train.py --config configs/pose3d/MB_train_h36m.yaml --checkpoint checkpoint/pose3d/MB_train_h36m |& tee train_scratch_resscale.log
python train.py --config configs/pose3d/MB_train_h36m.yaml --checkpoint checkpoint/pose3d/MB_train_h36m --evaluate checkpoint/pose3d/MB_train_h36m/best_epoch.bin |& tee train_scratch_resscale.log
# 12.17 Stage_ts 使用 SepConv_t，remove ResScale   how about other conv-related MetaFormer
python train.py --config configs/pose3d/MB_train_SepConvS_t_h36m.yaml --checkpoint checkpoint/pose3d/MB_train_SepConvS_t_h36m |& tee train_scratch_Stage_SepConvS_t.log
# try LayerScale?

# 12.22 w-mpjpe
python train.py --config configs/pose3d/MB_train_h36m.yaml --checkpoint checkpoint/pose3d/MB_train_h36m_wmpjpe |& tee train_scratch_wmpjpe.log
python train.py --config configs/pose3d/MB_train_h36m.yaml --checkpoint checkpoint/pose3d/MB_train_h36m_wmpjpe --evaluate checkpoint/pose3d/MB_train_h36m_wmpjpe/best_epoch.bin

# Tensorboard
#GPU01/GPU02
# tensorboard --logdir ./checkpoint/pose3d/ --port 6008 --bind_all
tensorboard --logdir ./checkpoint/ablation/ --port 6008 --bind_all
#mu01
ssh -L 6008:127.0.0.1:6008 ytwang@gpu02
#laptop cmd
ssh -L  6008:localhost:6008 ytwang@10.134.142.143
#laptop chrome
http://127.0.0.1:6008/