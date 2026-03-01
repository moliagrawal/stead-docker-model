# import io
# import time
# import pickle
# from concurrent import futures
# from typing import Dict, Any

# import grpc
# import numpy as np
# import torch
# import torch.nn as nn

# import refine_pb2
# import refine_pb2_grpc
# from model import Model

# T = 16
# CHANNELS_REQUIRED = 192
# THRESHOLD = 0.7
# SECOND_MODEL_PATH = r"E:\Vs Code\STEAD 2\STEAD\saved_models\ema_epoch_9.pkl"
# GRPC_BIND = "[::]:50051"

# # Optional: keep CPU threads low to avoid oversubscription on Windows
# torch.set_num_threads(1)


# def _extract_state_dict(obj: Any) -> Dict[str, torch.Tensor]:
#     """
#     Try to extract a state_dict from various pickle formats:
#     - raw state_dict (dict of tensors)
#     - dict with 'state_dict' key
#     - whole model object with .state_dict()
#     """
#     if isinstance(obj, dict):
#         # Typical: raw state_dict
#         if all(isinstance(v, torch.Tensor) for v in obj.values()):
#             return obj
#         # Common wrapper: {'state_dict': ..., ...}
#         if "state_dict" in obj and isinstance(obj["state_dict"], dict):
#             return obj["state_dict"]
#     # Whole model object
#     if hasattr(obj, "state_dict") and callable(getattr(obj, "state_dict")):
#         return obj.state_dict()
#     raise RuntimeError("Could not extract a state_dict from the loaded pickle object.")


# def _smart_load(model: nn.Module, model_path: str) -> None:
#     """
#     Load weights into model:
#     - Extract state_dict from pickle (supports multiple formats)
#     - Filter keys that don't exist or mismatch in shape
#     - Load with strict=False and print a concise summary
#     """
#     with open(model_path, "rb") as f:
#         obj = pickle.load(f)

#     ckpt_sd = _extract_state_dict(obj)
#     model_sd = model.state_dict()

#     # Filter to intersecting keys with matching shapes
#     loadable = {}
#     skipped_shape = []
#     skipped_missing = []
#     for k, v in ckpt_sd.items():
#         if k in model_sd:
#             if model_sd[k].shape == v.shape:
#                 loadable[k] = v
#             else:
#                 skipped_shape.append((k, tuple(v.shape), tuple(model_sd[k].shape)))
#         else:
#             skipped_missing.append(k)

#     # Load
#     missing_before = [k for k in model_sd.keys() if k not in loadable]
#     model.load_state_dict(loadable, strict=False)

#     # Summary (keep concise)
#     print(f"[RefineService] Loaded weights from: {model_path}")
#     print(f"[RefineService] Keys loaded: {len(loadable)} / {len(model_sd)}")
#     if skipped_shape:
#         print(f"[RefineService] Skipped (shape mismatch): {len(skipped_shape)}")
#         # Uncomment to debug specific mismatches:
#         # for k, ck, mk in skipped_shape[:10]:
#         #     print(f"  - {k}: ckpt{ck} != model{mk}")
#     if skipped_missing:
#         print(f"[RefineService] Skipped (not in model): {len(skipped_missing)}")
#     if missing_before:
#         # These are model keys that didn't get weights (will remain init/bias)
#         print(f"[RefineService] Model keys left unfilled: {len(missing_before)}")


# class RefineServicer(refine_pb2_grpc.RefineServiceServicer):
#     def __init__(self, model_path: str):
#         self.model = Model()
#         self.model.eval()
#         # If you want CUDA, change to .to('cuda') and move tensors likewise
#         # self.model.to('cuda')
#         _smart_load(self.model, model_path)

#     def Refine(self, request, context):
#         start_all = time.time()

#         # request.frames_npy is a numpy .npy byte array of shape [T,3,32,32] float32
#         buf = io.BytesIO(request.frames_npy)
#         frames = np.load(buf, allow_pickle=False)  # (T, 3, 32, 32) float32

#         frames_tensor = torch.from_numpy(frames)  # [T,3,32,32]
#         frames_tensor = frames_tensor.permute(1, 0, 2, 3).unsqueeze(0)  # [1,3,T,32,32]
#         sequence = frames_tensor.repeat(1, CHANNELS_REQUIRED // 3, 1, 1, 1)
#         # If using CUDA:
#         # sequence = sequence.to('cuda')

#         with torch.no_grad():
#             start_inf = time.time()
#             logits, _ = self.model(sequence)
#             pred = torch.sigmoid(logits).item()
#             inf_time = time.time() - start_inf

#         label = "Suspicious" if pred > THRESHOLD else "Normal"
#         detail = (
#             f"clip {request.start_index}-{request.end_index} | "
#             f"ema_epoch_9 refine | pred={pred:.3f} | infer={inf_time:.3f}s | "
#             f"total={time.time()-start_all:.3f}s"
#         )
#         print(f"[RefineService] {detail}")

#         return refine_pb2.RefineResult(label=label, confidence=pred, detail=detail)


# def serve():
#     try:
#         server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
#         refine_pb2_grpc.add_RefineServiceServicer_to_server(
#             RefineServicer(SECOND_MODEL_PATH), server
#         )
#         server.add_insecure_port(GRPC_BIND)
#         server.start()
#         print(f"[RefineService] gRPC server running on {GRPC_BIND}")
#         server.wait_for_termination()
#     except Exception as e:
#         # If anything goes wrong during init, make it obvious.
#         print(f"[RefineService] FATAL during startup: {e}")
#         raise


# if __name__ == "__main__":
#     serve()


# this one with the saved frames and videos in the folder
# 



# This is the code but it's output is not showing properly
# import os
# import io
# import time
# import pickle
# from concurrent import futures
# from typing import Dict, Any

# import grpc
# import numpy as np
# import torch
# import torch.nn as nn
# import cv2  # Added for frame resizing and video writing

# import refine_pb2
# import refine_pb2_grpc
# from model import Model

# T = 16
# CHANNELS_REQUIRED = 192
# THRESHOLD = 0.7
# SECOND_MODEL_PATH = r"E:\Vs Code\STEAD 2\STEAD\saved_models\ema_epoch_9.pkl"
# GRPC_BIND = "[::]:50051"
# OUTPUT_DIR = r"E:\Vs Code\STEAD 2\STEAD\outputs"

# torch.set_num_threads(1)


# def _extract_state_dict(obj: Any) -> Dict[str, torch.Tensor]:
#     if isinstance(obj, dict):
#         if all(isinstance(v, torch.Tensor) for v in obj.values()):
#             return obj
#         if "state_dict" in obj and isinstance(obj["state_dict"], dict):
#             return obj["state_dict"]
#     if hasattr(obj, "state_dict") and callable(getattr(obj, "state_dict")):
#         return obj.state_dict()
#     raise RuntimeError("Could not extract a state_dict from the loaded pickle object.")


# def _smart_load(model: nn.Module, model_path: str) -> None:
#     with open(model_path, "rb") as f:
#         obj = pickle.load(f)

#     ckpt_sd = _extract_state_dict(obj)
#     model_sd = model.state_dict()

#     loadable = {}
#     skipped_shape = []
#     skipped_missing = []
#     for k, v in ckpt_sd.items():
#         if k in model_sd:
#             if model_sd[k].shape == v.shape:
#                 loadable[k] = v
#             else:
#                 skipped_shape.append((k, tuple(v.shape), tuple(model_sd[k].shape)))
#         else:
#             skipped_missing.append(k)

#     missing_before = [k for k in model_sd.keys() if k not in loadable]
#     model.load_state_dict(loadable, strict=False)

#     print(f"[RefineService] Loaded weights from: {model_path}")
#     print(f"[RefineService] Keys loaded: {len(loadable)} / {len(model_sd)}")
#     if skipped_shape:
#         print(f"[RefineService] Skipped (shape mismatch): {len(skipped_shape)}")
#     if skipped_missing:
#         print(f"[RefineService] Skipped (not in model): {len(skipped_missing)}")
#     if missing_before:
#         print(f"[RefineService] Model keys left unfilled: {len(missing_before)}")


# class RefineServicer(refine_pb2_grpc.RefineServiceServicer):
#     def __init__(self, model_path: str):
#         self.model = Model()
#         self.model.eval()
#         _smart_load(self.model, model_path)

#     def Refine(self, request, context):
#         start_all = time.time()

#         buf = io.BytesIO(request.frames_npy)
#         frames = np.load(buf, allow_pickle=False)  # (T, 3, 32, 32) float32


#         os.makedirs(OUTPUT_DIR, exist_ok=True)
#         resized_frames = []
#         for i, frame in enumerate(frames):
#             frame_rgb = (frame.transpose(1, 2, 0) * 255).astype(np.uint8)
#             frame_resized = cv2.resize(frame_rgb, (640, 480), interpolation=cv2.INTER_LINEAR)
#             cv2.imwrite(f"{OUTPUT_DIR}/frame_{request.start_index + i:04d}.png", cv2.cvtColor(frame_resized, cv2.COLOR_RGB2BGR))
#             resized_frames.append(frame_resized)

#         # Save video
#         video_path = f"{OUTPUT_DIR}/clip_{request.start_index}-{request.end_index}.avi"
#         out = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'XVID'), 15, (640, 480))
#         for f in resized_frames:
#             out.write(cv2.cvtColor(f, cv2.COLOR_RGB2BGR))
#         out.release()
#         print(f"[RefineService] Saved frames and video to: {OUTPUT_DIR}")

#         frames_tensor = torch.from_numpy(frames)  # [T,3,32,32]
#         frames_tensor = frames_tensor.permute(1, 0, 2, 3).unsqueeze(0)  # [1,3,T,32,32]
#         sequence = frames_tensor.repeat(1, CHANNELS_REQUIRED // 3, 1, 1, 1)

#         with torch.no_grad():
#             start_inf = time.time()
#             logits, _ = self.model(sequence)
#             pred = torch.sigmoid(logits).item()
#             inf_time = time.time() - start_inf

#         label = "Suspicious" if pred > THRESHOLD else "Normal"
#         detail = (
#             f"clip {request.start_index}-{request.end_index} | "
#             f"ema_epoch_9 refine | pred={pred:.3f} | infer={inf_time:.3f}s | "
#             f"total={time.time()-start_all:.3f}s"
#         )
#         print(f"[RefineService] {detail}")

#         return refine_pb2.RefineResult(label=label, confidence=pred, detail=detail)


# def serve():
#     try:
#         server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
#         refine_pb2_grpc.add_RefineServiceServicer_to_server(
#             RefineServicer(SECOND_MODEL_PATH), server
#         )
#         server.add_insecure_port(GRPC_BIND)
#         server.start()
#         print(f"[RefineService] gRPC server running on {GRPC_BIND}")
#         server.wait_for_termination()
#     except Exception as e:
#         print(f"[RefineService] FATAL during startup: {e}")
#         raise


# if __name__ == "__main__":
#     serve()




# This one is for folder with different video and frames inside output
import os
import io
import time
import pickle
from concurrent import futures
from typing import Dict, Any

import grpc
import numpy as np
import torch
import torch.nn as nn
import cv2

import refine_pb2
import refine_pb2_grpc
from model import Model

T = 16
CHANNELS_REQUIRED = 192
THRESHOLD = 0.7
SECOND_MODEL_PATH = r"E:\Vs Code\STEAD 2\STEAD\saved_models\ema_epoch_9.pkl" 
GRPC_BIND = "[::]:50051"
OUTPUT_DIR = r"E:\Vs Code\STEAD 2\STEAD\outputs"

torch.set_num_threads(1)


def _extract_state_dict(obj: Any) -> Dict[str, torch.Tensor]:
    if isinstance(obj, dict):
        if all(isinstance(v, torch.Tensor) for v in obj.values()):
            return obj
        if "state_dict" in obj and isinstance(obj["state_dict"], dict):
            return obj["state_dict"]
    if hasattr(obj, "state_dict") and callable(getattr(obj, "state_dict")):
        return obj.state_dict()
    raise RuntimeError("Could not extract a state_dict from the loaded pickle object.")


def _smart_load(model: nn.Module, model_path: str) -> None:
    with open(model_path, "rb") as f:
        obj = pickle.load(f)

    ckpt_sd = _extract_state_dict(obj)
    model_sd = model.state_dict()

    loadable = {}
    skipped_shape = []
    skipped_missing = []
    for k, v in ckpt_sd.items():
        if k in model_sd:
            if model_sd[k].shape == v.shape:
                loadable[k] = v
            else:
                skipped_shape.append((k, tuple(v.shape), tuple(model_sd[k].shape)))
        else:
            skipped_missing.append(k)

    missing_before = [k for k in model_sd.keys() if k not in loadable]
    model.load_state_dict(loadable, strict=False)

    print(f"[RefineService] Loaded weights from: {model_path}")
    print(f"[RefineService] Keys loaded: {len(loadable)} / {len(model_sd)}")
    if skipped_shape:
        print(f"[RefineService] Skipped (shape mismatch): {len(skipped_shape)}")
    if skipped_missing:
        print(f"[RefineService] Skipped (not in model): {len(skipped_missing)}")
    if missing_before:
        print(f"[RefineService] Model keys left unfilled: {len(missing_before)}")


class RefineServicer(refine_pb2_grpc.RefineServiceServicer):
    def __init__(self, model_path: str):
        self.model = Model()
        self.model.eval()
        _smart_load(self.model, model_path)

    def Refine(self, request, context):
        start_all = time.time()

        buf = io.BytesIO(request.frames_npy)
        frames = np.load(buf, allow_pickle=False)  # (T, 3, 32, 32) float32

        # === Create separate folders ===
        frames_dir = os.path.join(OUTPUT_DIR, "frames")
        videos_dir = os.path.join(OUTPUT_DIR, "videos")
        os.makedirs(frames_dir, exist_ok=True)
        os.makedirs(videos_dir, exist_ok=True)

        resized_frames = []
        for i, frame in enumerate(frames):
            frame_rgb = (frame.transpose(1, 2, 0) * 255).astype(np.uint8)
            frame_resized = cv2.resize(frame_rgb, (640, 480), interpolation=cv2.INTER_LINEAR)

            # Save inside frames folder
            cv2.imwrite(
                f"{frames_dir}/frame_{request.start_index + i:04d}.png",
                cv2.cvtColor(frame_resized, cv2.COLOR_RGB2BGR)
            )
            resized_frames.append(frame_resized)

        # Save video inside videos folder
        video_path = f"{videos_dir}/clip_{request.start_index}-{request.end_index}.avi"
        out = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'XVID'), 15, (640, 480))
        for f in resized_frames:
            out.write(cv2.cvtColor(f, cv2.COLOR_RGB2BGR))
        out.release()

        print(f"[RefineService] Saved frames to: {frames_dir}")
        print(f"[RefineService] Saved video to: {videos_dir}")

        # === Model inference ===
        frames_tensor = torch.from_numpy(frames)  # [T,3,32,32]
        frames_tensor = frames_tensor.permute(1, 0, 2, 3).unsqueeze(0)  # [1,3,T,32,32]
        sequence = frames_tensor.repeat(1, CHANNELS_REQUIRED // 3, 1, 1, 1)

        with torch.no_grad():
            start_inf = time.time()
            logits, _ = self.model(sequence)
            pred = torch.sigmoid(logits).item()
            inf_time = time.time() - start_inf

        label = "Suspicious" if pred > THRESHOLD else "Normal"
        detail = (
            f"clip {request.start_index}-{request.end_index} | "
            f"ema_epoch_9 refine | pred={pred:.3f} | infer={inf_time:.3f}s | "
            f"total={time.time()-start_all:.3f}s"
        )
        print(f"[RefineService] {detail}")

        return refine_pb2.RefineResult(label=label, confidence=pred, detail=detail)


def serve():
    try:
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
        refine_pb2_grpc.add_RefineServiceServicer_to_server(
            RefineServicer(SECOND_MODEL_PATH), server
        )
        server.add_insecure_port(GRPC_BIND)
        server.start()
        print(f"[RefineService] gRPC server running on {GRPC_BIND}")
        server.wait_for_termination()
    except Exception as e:
        print(f"[RefineService] FATAL during startup: {e}")
        raise


if __name__ == "__main__":
    serve()