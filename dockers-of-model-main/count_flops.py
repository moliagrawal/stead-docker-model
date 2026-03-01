import torch
from thop import profile
from model import Model   # Import your STEAD model

def count_gflops():
    # 1. Build model
    model = Model()
    model.eval()

    # 2. Define dummy input (Batch, Channels, Time, Height, Width)
    dummy_input = torch.randn(1, 3, 16, 32, 32)

    # 3. Compute FLOPs and Params
    flops, params = profile(model, inputs=(dummy_input,), verbose=False)

    # 4. Convert to human readable
    gflops = flops / 1e9
    mparams = params / 1e6
    print(f"GFLOPs: {gflops:.3f}")
    print(f"Params: {mparams:.3f} M")

if __name__ == "__main__":
    count_gflops()
