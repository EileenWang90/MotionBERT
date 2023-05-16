# calculate FLOPS
# omit batchsize


def calculate_FLOPs(vari_map):
    J=17
    Cin=2
    Cout=3
    Cfeat=vari_map[0]
    Crep=vari_map[1]
    depth=vari_map[2]
    F=vari_map[3]
    # Cfeat=128
    # Crep=256
    # depth=3
    # F=9

    FLOPs_joint_embeded=F*J*Cin*Cfeat
    FLOPs_posST_embeded=2*F*J*Cfeat

    # Spatial Transformer Block
    # (norm1+norm2) + MLP + MSA
    # FLOPs_STB=(3*F*J*Cfeat*Cfeat+2*F*J*J*Cfeat)
    FLOPs_STB=2*F*J*Cfeat + 2*F*J*Cfeat*Cfeat*4 + (3*F*J*Cfeat*Cfeat+2*F*J*J*Cfeat)
    # Temporal Transformer Block
    # (norm1+norm2) + MLP + MSA
    # FLOPs_TTB=(3*F*J*Cfeat*Cfeat+2*J*F*F*Cfeat)
    FLOPs_TTB=2*F*J*Cfeat + 2*F*J*Cfeat*Cfeat*4 + (3*F*J*Cfeat*Cfeat+2*J*F*F*Cfeat)
    FLOPs_adaptive_fusion=F*J*Cfeat*(2*2+2)
    # FLOPs_adaptive_fusion=0
    FLOPs_intermediate_supervision=F*J*Cfeat*Crep+F*J*Crep*Cout
    FLOPs_totalTB=depth*(FLOPs_STB+FLOPs_TTB+FLOPs_adaptive_fusion)

    FLOPs_regression_head=F*J*Cfeat*Crep+F*J*Crep*Cout

    print("Cfeat Crep depth F")
    print(vari_map)
    FLOPs_total=FLOPs_joint_embeded+FLOPs_posST_embeded+FLOPs_totalTB+FLOPs_regression_head
    print("FLOPs_total ","FLOPs_joint_embeded ","FLOPs_posST_embeded ","FLOPs_totalTB ","FLOPs_regression_head ")
    print(FLOPs_total/1000.0/1000.0,FLOPs_joint_embeded/1000.0/1000.0,FLOPs_posST_embeded/1000.0/1000.0,FLOPs_totalTB/1000.0/1000.0,FLOPs_regression_head/1000.0/1000.0)

    print("FLOPs_totalTB ","depth,FLOPs_STB ","FLOPs_TTB ","FLOPs_adaptive_fusion ")
    print(FLOPs_totalTB/1000.0/1000.0,depth,FLOPs_STB/1000.0/1000.0,FLOPs_TTB/1000.0/1000.0,FLOPs_adaptive_fusion/1000.0/1000.0)
    print("\n")


if __name__ == "__main__":
    # Cfeat Crep depth F
    # vari_map=[128,256,3,9]
    vari_map=[256,512,5,9]
    # calculate_FLOPs(vari_map)

    for i in [9,27,81,243]:
        vari_map[3]=i
        calculate_FLOPs(vari_map)



