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

# test
python train.py --config configs/pose3d/MB_ft_h36m.yaml --evaluate checkpoint/pose3d/FT_MB_release_MB_ft_h36m/best_epoch.bin |& tee test_finetune.log
python train.py --config configs/pose3d/MB_train_h36m.yaml --evaluate checkpoint/pose3d/MB_train_h36m_origin/best_epoch.bin |& tee test_scratch.log





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
tensorboard --logdir ./checkpoint/pose3d/ --port 6007 --bind_all
#mu01
ssh -L 6007:127.0.0.1:6007 ytwang@gpu02
#laptop cmd
ssh -L  6007:localhost:6007 ytwang@10.134.142.143
#laptop chrome
http://127.0.0.1:6007/