# no inter depth
# python train.py --config configs/pose3d/MB_train_h36m_f9s3_branch_interKD_para2.yaml --checkpoint checkpoint/pose3d/MB_train_h36m_f9s3_branch_interKD_para2 |& tee ./checkpoint/pose3d/train_f9s3_branch_interKD_para2.log
# python train.py --config configs/pose3d/MB_train_h36m_f9s3_branch_interKD_para2.yaml --evaluate checkpoint/pose3d/MB_train_h36m_f9s3_branch_interKD_para2/best_epoch.bin |& tee ./checkpoint/pose3d/MB_train_h36m_f9s3_branch_interKD_para2/test_f9s3_branch_interKD_para2.log

# python train.py --config configs/pose3d/MB_train_h36m_f9s3_branch_interKD_para3.yaml --checkpoint checkpoint/pose3d/MB_train_h36m_f9s3_branch_interKD_para3 |& tee ./checkpoint/pose3d/train_f9s3_branch_interKD_para3.log
# python train.py --config configs/pose3d/MB_train_h36m_f9s3_branch_interKD_para3.yaml --evaluate checkpoint/pose3d/MB_train_h36m_f9s3_branch_interKD_para3/best_epoch.bin |& tee ./checkpoint/pose3d/MB_train_h36m_f9s3_branch_interKD_para3/test_f9s3_branch_interKD_para3.log

# python train.py --config configs/pose3d/MB_train_h36m_f9s3_branch_interKD_para4.yaml --checkpoint checkpoint/pose3d/MB_train_h36m_f9s3_branch_interKD_para4 |& tee ./checkpoint/pose3d/train_f9s3_branch_interKD_para4.log
# python train.py --config configs/pose3d/MB_train_h36m_f9s3_branch_interKD_para4.yaml --evaluate checkpoint/pose3d/MB_train_h36m_f9s3_branch_interKD_para4/best_epoch.bin |& tee ./checkpoint/pose3d/MB_train_h36m_f9s3_branch_interKD_para4/test_f9s3_branch_interKD_para4.log

# python train.py --config configs/pose3d/MB_train_h36m_f9s3_branch_interKD_para5.yaml --checkpoint checkpoint/pose3d/MB_train_h36m_f9s3_branch_interKD_para5 |& tee ./checkpoint/pose3d/train_f9s3_branch_interKD_para5.log
# python train.py --config configs/pose3d/MB_train_h36m_f9s3_branch_interKD_para5.yaml --evaluate checkpoint/pose3d/MB_train_h36m_f9s3_branch_interKD_para5/best_epoch.bin |& tee ./checkpoint/pose3d/MB_train_h36m_f9s3_branch_interKD_para5/test_f9s3_branch_interKD_para5.log

# # inter depth
# mkdir -p checkpoint/pose3d/MB_train_h36m_f9s3_branch_interKD1_para2
# python train.py --config configs/pose3d/MB_train_h36m_f9s3_branch_interKD1_para2.yaml --checkpoint checkpoint/pose3d/MB_train_h36m_f9s3_branch_interKD1_para2 |& tee ./checkpoint/pose3d/MB_train_h36m_f9s3_branch_interKD1_para2/train_f9s3_branch_interKD1_para2.log
# python train.py --config configs/pose3d/MB_train_h36m_f9s3_branch_interKD1_para2.yaml --evaluate checkpoint/pose3d/MB_train_h36m_f9s3_branch_interKD1_para2/best_epoch.bin |& tee ./checkpoint/pose3d/MB_train_h36m_f9s3_branch_interKD1_para2/test_f9s3_branch_interKD1_para2.log
# mkdir -p checkpoint/pose3d/MB_train_h36m_f9s3_branch_interKD1_para3
# python train.py --config configs/pose3d/MB_train_h36m_f9s3_branch_interKD1_para3.yaml --checkpoint checkpoint/pose3d/MB_train_h36m_f9s3_branch_interKD1_para3 |& tee ./checkpoint/pose3d/MB_train_h36m_f9s3_branch_interKD1_para3/train_f9s3_branch_interKD1_para3.log
# python train.py --config configs/pose3d/MB_train_h36m_f9s3_branch_interKD1_para3.yaml --evaluate checkpoint/pose3d/MB_train_h36m_f9s3_branch_interKD1_para3/best_epoch.bin |& tee ./checkpoint/pose3d/MB_train_h36m_f9s3_branch_interKD1_para3/test_f9s3_branch_interKD1_para3.log
# mkdir -p checkpoint/pose3d/MB_train_h36m_f9s3_branch_interKD1_para4
# python train.py --config configs/pose3d/MB_train_h36m_f9s3_branch_interKD1_para4.yaml --checkpoint checkpoint/pose3d/MB_train_h36m_f9s3_branch_interKD1_para4 |& tee ./checkpoint/pose3d/MB_train_h36m_f9s3_branch_interKD1_para4/train_f9s3_branch_interKD1_para4.log
# python train.py --config configs/pose3d/MB_train_h36m_f9s3_branch_interKD1_para4.yaml --evaluate checkpoint/pose3d/MB_train_h36m_f9s3_branch_interKD1_para4/best_epoch.bin |& tee ./checkpoint/pose3d/MB_train_h36m_f9s3_branch_interKD1_para4/test_f9s3_branch_interKD1_para4.log
# mkdir -p checkpoint/pose3d/MB_train_h36m_f9s3_branch_interKD1_para5
# python train.py --config configs/pose3d/MB_train_h36m_f9s3_branch_interKD1_para5.yaml --checkpoint checkpoint/pose3d/MB_train_h36m_f9s3_branch_interKD1_para5 |& tee ./checkpoint/pose3d/MB_train_h36m_f9s3_branch_interKD1_para5/train_f9s3_branch_interKD1_para5.log
# python train.py --config configs/pose3d/MB_train_h36m_f9s3_branch_interKD1_para5.yaml --evaluate checkpoint/pose3d/MB_train_h36m_f9s3_branch_interKD1_para5/best_epoch.bin |& tee ./checkpoint/pose3d/MB_train_h36m_f9s3_branch_interKD1_para5/test_f9s3_branch_interKD1_para5.log

# # inter head
# mkdir -p checkpoint/ablation/MB_train_h36m_f9s3_branch_interKD1_para3_h4
# python train.py --config configs/pose3d/ablation/MB_train_h36m_f9s3_branch_interKD1_para3_h4.yaml --checkpoint checkpoint/ablation/MB_train_h36m_f9s3_branch_interKD1_para3_h4 |& tee ./checkpoint/ablation/MB_train_h36m_f9s3_branch_interKD1_para3_h4/train_f9s3_branch_interKD1_para3_h4.log
# python train.py --config configs/pose3d/ablation/MB_train_h36m_f9s3_branch_interKD1_para3_h4.yaml --evaluate checkpoint/ablation/MB_train_h36m_f9s3_branch_interKD1_para3_h4/best_epoch.bin |& tee ./checkpoint/ablation/MB_train_h36m_f9s3_branch_interKD1_para3_h4/test_f9s3_branch_interKD1_para3_h4.log
# mkdir -p checkpoint/ablation/MB_train_h36m_f9s3_branch_interKD1_para3_h16
# python train.py --config configs/pose3d/ablation/MB_train_h36m_f9s3_branch_interKD1_para3_h16.yaml --checkpoint checkpoint/ablation/MB_train_h36m_f9s3_branch_interKD1_para3_h16 |& tee ./checkpoint/ablation/MB_train_h36m_f9s3_branch_interKD1_para3_h16/train_f9s3_branch_interKD1_para3_h16.log
# python train.py --config configs/pose3d/ablation/MB_train_h36m_f9s3_branch_interKD1_para3_h16.yaml --evaluate checkpoint/ablation/MB_train_h36m_f9s3_branch_interKD1_para3_h16/best_epoch.bin |& tee ./checkpoint/ablation/MB_train_h36m_f9s3_branch_interKD1_para3_h16/test_f9s3_branch_interKD1_para3_h16.log

# # inter d
# mkdir -p checkpoint/ablation/MB_train_h36m_f9s3_branch_interKD1_para3_d64
# python train.py --config configs/pose3d/ablation/MB_train_h36m_f9s3_branch_interKD1_para3_d64.yaml --checkpoint checkpoint/ablation/MB_train_h36m_f9s3_branch_interKD1_para3_d64 |& tee ./checkpoint/ablation/MB_train_h36m_f9s3_branch_interKD1_para3_d64/train_f9s3_branch_interKD1_para3_d64.log
# python train.py --config configs/pose3d/ablation/MB_train_h36m_f9s3_branch_interKD1_para3_d64.yaml --evaluate checkpoint/ablation/MB_train_h36m_f9s3_branch_interKD1_para3_d64/best_epoch.bin |& tee ./checkpoint/ablation/MB_train_h36m_f9s3_branch_interKD1_para3_d64/test_f9s3_branch_interKD1_para3_d64.log
# mkdir -p checkpoint/ablation/MB_train_h36m_f9s3_branch_interKD1_para3_d256
# python train.py --config configs/pose3d/ablation/MB_train_h36m_f9s3_branch_interKD1_para3_d256.yaml --checkpoint checkpoint/ablation/MB_train_h36m_f9s3_branch_interKD1_para3_d256 |& tee ./checkpoint/ablation/MB_train_h36m_f9s3_branch_interKD1_para3_d256/train_f9s3_branch_interKD1_para3_d256.log
# python train.py --config configs/pose3d/ablation/MB_train_h36m_f9s3_branch_interKD1_para3_d256.yaml --evaluate checkpoint/ablation/MB_train_h36m_f9s3_branch_interKD1_para3_d256/best_epoch.bin |& tee ./checkpoint/ablation/MB_train_h36m_f9s3_branch_interKD1_para3_d256/test_f9s3_branch_interKD1_para3_d256.log

# diff frames
# inter f81s27 f27s9 f243s81
# mkdir -p checkpoint/ablation/MB_train_h36m_f9s3_branch_interKD1_para3d256_5
# python train.py --config configs/pose3d/ablation/MB_train_h36m_f9s3_branch_interKD1_para3d256_5.yaml --checkpoint checkpoint/ablation/MB_train_h36m_f9s3_branch_interKD1_para3d256_5 |& tee ./checkpoint/ablation/MB_train_h36m_f9s3_branch_interKD1_para3d256_5/train_f9s3_branch_interKD1_para3d256.log
# python train.py --config configs/pose3d/ablation/MB_train_h36m_f9s3_branch_interKD1_para3d256_5.yaml --evaluate checkpoint/ablation/MB_train_h36m_f9s3_branch_interKD1_para3d256_5/best_epoch.bin |& tee ./checkpoint/ablation/MB_train_h36m_f9s3_branch_interKD1_para3d256_5/test_f9s3_branch_interKD1_para3d256.log
# mkdir -p checkpoint/ablation/MB_train_h36m_f27s9_branch_interKD1_para3d256
# python train.py --config configs/pose3d/ablation/MB_train_h36m_f27s9_branch_interKD1_para3.yaml --checkpoint checkpoint/ablation/MB_train_h36m_f27s9_branch_interKD1_para3d256 |& tee ./checkpoint/ablation/MB_train_h36m_f27s9_branch_interKD1_para3d256/train_f27s9_branch_interKD1_para3d256.log
# python train.py --config configs/pose3d/ablation/MB_train_h36m_f27s9_branch_interKD1_para3.yaml --evaluate checkpoint/ablation/MB_train_h36m_f27s9_branch_interKD1_para3d256/best_epoch.bin |& tee ./checkpoint/ablation/MB_train_h36m_f27s9_branch_interKD1_para3d256/test_f27s9_branch_interKD1_para3d256.log
# mkdir -p checkpoint/ablation/MB_train_h36m_f81s27_branch_interKD1_para3d256
# python train.py --config configs/pose3d/ablation/MB_train_h36m_f81s27_branch_interKD1_para3.yaml --checkpoint checkpoint/ablation/MB_train_h36m_f81s27_branch_interKD1_para3d256 |& tee ./checkpoint/ablation/MB_train_h36m_f81s27_branch_interKD1_para3d256/train_f81s27_branch_interKD1_para3d256.log
# python train.py --config configs/pose3d/ablation/MB_train_h36m_f81s27_branch_interKD1_para3.yaml --evaluate checkpoint/ablation/MB_train_h36m_f81s27_branch_interKD1_para3d256/best_epoch.bin |& tee ./checkpoint/ablation/MB_train_h36m_f81s27_branch_interKD1_para3d256/test_f81s27_branch_interKD1_para3d256.log
mkdir -p checkpoint/ablation/MB_train_h36m_f243s81_branch_interKD1_para3d256
python train.py --config configs/pose3d/ablation/MB_train_h36m_f243s81_branch_interKD1_para3.yaml --checkpoint checkpoint/ablation/MB_train_h36m_f243s81_branch_interKD1_para3d256 |& tee ./checkpoint/ablation/MB_train_h36m_f243s81_branch_interKD1_para3d256/train_f243s81_branch_interKD1_para3d256.log
python train.py --config configs/pose3d/ablation/MB_train_h36m_f243s81_branch_interKD1_para3.yaml --evaluate checkpoint/ablation/MB_train_h36m_f243s81_branch_interKD1_para3d256/best_epoch.bin |& tee ./checkpoint/ablation/MB_train_h36m_f243s81_branch_interKD1_para3d256/test_f243s81_branch_interKD1_para3d256.log
