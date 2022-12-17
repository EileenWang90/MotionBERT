# 3D Human Pose Estimation

## Data

1. Download the finetuned Stacked Hourglass detections and our preprocessed H3.6M data (.pkl) [here](https://1drv.ms/u/s!AvAdh0LSjEOlgSMvoapR8XVTGcVj) and put it to `data/motion3d`.

  > Note that the preprocessed data is only intended for reproducing our results more easily. If you want to use the dataset, please register to the [Human3.6m website](http://vision.imar.ro/human3.6m/) and download the dataset in its original format. Please refer to [LCN](https://github.com/CHUNYUWANG/lcn-pose#data) for how we prepare the H3.6M data.

2. Slice the motion clips (len=243, stride=81)

   ```bash
   python tools/convert_h36m.py
   ```

## Running

**Train from scratch:**

```bash
python train.py \
--config configs/pose3d/MB_train_h36m.yaml \
--checkpoint checkpoint/pose3d/MB_train_h36m
```

Note: Increasing the initial feature dimension (`MB_train_h36m_wide.yaml`) would additionally lower the error (MPJPE=38.8mm) at the cost of model size and training time.

**Finetune from pretrained MotionBERT:**

```bash
python train.py \
--config configs/pose3d/MB_ft_h36m.yaml \
--pretrained checkpoint/pretrain/MB_release \
--checkpoint checkpoint/pose3d/FT_MB_release_MB_ft_h36m
```

**Evaluate:**

```bash
python train.py \
--config configs/pose3d/MB_train_h36m.yaml \
--evaluate checkpoint/pose3d/MB_train_h36m_best_epoch.bin         
```

**遇到问题**
```bash
Traceback (most recent call last):
  File "train.py", line 378, in <module>
    train_with_config(args, opts)
  File "train.py", line 326, in train_with_config
    train_epoch(args, model_pos, train_loader_3d, losses, optimizer, has_3d=True, has_gt=True) 
  File "train.py", line 154, in train_epoch
    for idx, (batch_input, batch_gt) in tqdm(enumerate(train_loader)):    
  File "/home/ytwang/anaconda3/lib/python3.8/site-packages/torch/utils/data/dataloader.py", line 349, in __iter__
    self._iterator._reset(self)
  File "/home/ytwang/anaconda3/lib/python3.8/site-packages/torch/utils/data/dataloader.py", line 852, in _reset
    data = self._get_data()
  File "/home/ytwang/anaconda3/lib/python3.8/site-packages/torch/utils/data/dataloader.py", line 1029, in _get_data
    raise RuntimeError('Pin memory thread exited unexpectedly')
RuntimeError: Pin memory thread exited unexpectedly
```










