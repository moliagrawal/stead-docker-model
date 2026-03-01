# Code for converting .pth file into .pkl file
import torch
import pickle
import os

pth_file = "ema_epoch_9.pth"   # your .pth file name

# Create output file name in the same directory
base, _ = os.path.splitext(pth_file)
pkl_file = base + ".pkl"

# Load PyTorch checkpoint
checkpoint = torch.load(pth_file, map_location="cpu")

# Save as .pkl
with open(pkl_file, "wb") as f:
    pickle.dump(checkpoint, f)

print(f"Converted {pth_file} → {pkl_file}")




# Code for converting .pkl file into .pth file
# import torch
# import pickle
# import os

# pkl_file = "ema_epoch_9.pkl"   # your .pkl file name

# # Create output file name in the same directory
# base, _ = os.path.splitext(pkl_file)
# pth_file = base + ".pth"

# # Load Pickle checkpoint
# with open(pkl_file, "rb") as f:
#     checkpoint = pickle.load(f)

# # Save as .pth
# torch.save(checkpoint, pth_file)

# print(f"Converted {pkl_file} → {pth_file}")
