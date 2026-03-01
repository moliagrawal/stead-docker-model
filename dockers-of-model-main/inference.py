# This is the basic code with normal camera

# import torch
# import cv2
# import numpy as np
# import time
# from model import Model

# # === Configuration ===
# T = 16
# FRAME_SIZE = (32, 32)
# CHANNELS_REQUIRED = 192
# THRESHOLD = 0.7

# # === Load Model and Measure Time ===
# start_model_load = time.time()
# model = Model()
# model.load_state_dict(torch.load('model.pth', map_location='cpu'))
# model.eval()
# model_load_time = time.time() - start_model_load
# print(f" Model loaded and ready in {model_load_time:.3f} seconds.")

# # === Open Camera ===
# cap = cv2.VideoCapture(0)
# frames = []
# frame_counter = 0  # Counts total frames processed

# while True:
#     ret, frame = cap.read()
#     if not ret:
#         print(" Failed to capture frame.")
#         break

#     frame_counter += 1
#     start_total = time.time()

#     # Resize and normalize
#     frame_resized = cv2.resize(frame, FRAME_SIZE)
#     frame_tensor = torch.tensor(frame_resized, dtype=torch.float32).permute(2, 0, 1).unsqueeze(0) / 255.0
#     frames.append(frame_tensor)

#     if len(frames) == T:
#         # Prepare sequence
#         start_index = frame_counter - T + 1
#         end_index = frame_counter
#         frames_tensor = torch.cat(frames).permute(1, 0, 2, 3).unsqueeze(0)
#         sequence = frames_tensor.repeat(1, CHANNELS_REQUIRED // 3, 1, 1, 1)

#         # Inference
#         start_infer = time.time()
#         with torch.no_grad():
#             logits, _ = model(sequence)
#             prediction = torch.sigmoid(logits).item()
#         infer_time = time.time() - start_infer
#         total_time = time.time() - start_total
 
#         label = 'Suspicious' if prediction > THRESHOLD else 'Normal'
#         color = (0, 0, 255) if prediction > THRESHOLD else (0, 255, 0)

#         # Log with frame range
#         print(f" Action Detected: {label} (Confidence: {prediction:.2f}) "
#               f"| Frames: {start_index}-{end_index} | Inference: {infer_time:.3f}s | Total: {total_time:.3f}s")

#         # Display label on screen
#         cv2.putText(frame, f'{label} ({prediction:.2f})', (20, 40),
#                     cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)

#         frames = []  # Reset sequence

#     cv2.imshow('Real-time Surveillance', frame)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# cap.release()
# cv2.destroyAllWindows()





# This is not working properly, so we have to check it what's the issue

# import torch
# import cv2
# import numpy as np
# import time
# from pytorchvideo.models.hub import x3d_xs
# import torchvision.transforms as T
# from model import Model  # Your custom STEAD model

# # === Configuration ===
# T_FRAMES = 16
# THRESHOLD = 0.7

# # === Load X3D Model for Feature Extraction ===
# x3d = x3d_xs(pretrained=True)
# x3d.eval()
# x3d_feature_extractor = torch.nn.Sequential(*list(x3d.children())[:-1])  # Remove final classifier layer

# # === Preprocessing Transform for X3D ===
# x3d_transform = T.Compose([
#     T.ToPILImage(),
#     T.Resize((182, 182)),
#     T.CenterCrop((182, 182)),
#     T.ToTensor(),
#     T.Normalize([0.45, 0.45, 0.45], [0.225, 0.225, 0.225])
# ])

# # === Load Your STEAD Model ===
# start_model_load = time.time()
# model = Model()  # Should accept [1, C] where C = feature size from X3D
# model.load_state_dict(torch.load('model.pth', map_location='cpu'))
# model.eval()
# model_load_time = time.time() - start_model_load
# print(f" Model loaded and ready in {model_load_time:.3f} seconds.")

# # === Start Webcam Capture ===
# cap = cv2.VideoCapture(0)
# frames = []
# frame_counter = 0

# while True:
#     ret, frame = cap.read()
#     if not ret:
#         print(" Failed to capture frame.")
#         break

#     frame_counter += 1
#     frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert to RGB for torchvision
#     transformed = x3d_transform(frame_rgb)  # Shape: [3, H, W]
#     frames.append(transformed)

#     if len(frames) == T_FRAMES:
#         start_index = frame_counter - T_FRAMES + 1
#         end_index = frame_counter
#         start_total = time.time()

#         video_tensor = torch.stack(frames, dim=1).unsqueeze(0)  # [1, 3, T, H, W]

#         with torch.no_grad():
#             # Extract features using X3D
#             x3d_features = x3d_feature_extractor(video_tensor)  # [1, C, 1, 1, 1]
#             x3d_features = x3d_features.flatten(start_dim=1)    # [1, C]

#             # Predict using STEAD model
#             logits, _ = model(x3d_features)
#             prediction = torch.sigmoid(logits).item()

#         infer_time = time.time() - start_total

#         label = 'Suspicious' if prediction > THRESHOLD else 'Normal'
#         color = (0, 0, 255) if prediction > THRESHOLD else (0, 255, 0)

#         print(f" Action Detected: {label} (Confidence: {prediction:.2f}) "
#               f"| Frames: {start_index}-{end_index} | Inference: {infer_time:.3f}s")

#         # Display on the screen
#         cv2.putText(frame, f'{label} ({prediction:.2f})', (20, 40),
#                     cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)

#         frames = []  # Reset buffer

#     cv2.imshow('Real-time Surveillance', frame)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# cap.release()
# cv2.destroyAllWindows()






# New one with 1 Frames at a time means one framew in and one frame out

# import torch
# import cv2
# import numpy as np
# import os
# import time
# from model import Model

# # === Configuration ===
# T = 16
# FRAME_SIZE = (32, 32)
# CHANNELS_REQUIRED = 192
# THRESHOLD = 0.7
# VIDEO_PATH = 'clip_326.mp4'   # your mp4 path
# OUTPUT_DIR = 'npy_frames'
# os.makedirs(OUTPUT_DIR, exist_ok=True)

# # === Load Model ===
# model = Model()
# model.load_state_dict(torch.load('model.pth', map_location='cpu'))
# model.eval()
# print("Model loaded.")

# # === Load video ===
# cap = cv2.VideoCapture(VIDEO_PATH)
# frame_idx = 0
# frames = []

# while True:
#     ret, frame = cap.read()
#     if not ret:
#         break

#     # Preprocess: Resize and normalize
#     frame_resized = cv2.resize(frame, FRAME_SIZE)
#     frame_tensor = torch.tensor(frame_resized, dtype=torch.float32).permute(2, 0, 1) / 255.0
#     frames.append(frame_tensor)
    
#     # Save preprocessed .npy
#     np.save(os.path.join(OUTPUT_DIR, f"frame_{frame_idx:04d}.npy"), frame_tensor.numpy())
#     frame_idx += 1

# cap.release()
# print(f"Total {frame_idx} frames saved as .npy in '{OUTPUT_DIR}'")

# # === Run inference on sequences of 16 frames ===
# results = []
# for i in range(len(frames) - T + 1):
#     clip_frames = frames[i:i + T]
    
#     # Stack into (T, C, H, W)
#     clip_tensor = torch.stack(clip_frames)  # (T, 3, 32, 32)
#     clip_tensor = clip_tensor.permute(1, 0, 2, 3).unsqueeze(0)  # (1, 3, 16, 32, 32)
#     clip_tensor = clip_tensor.repeat(1, CHANNELS_REQUIRED // 3, 1, 1, 1)  # (1, 192, 16, 32, 32)

#     with torch.no_grad():
#         start_time = time.time()
#         logits, _ = model(clip_tensor)
#         pred = torch.sigmoid(logits).item()
#         infer_time = time.time() - start_time

#     label = 'Suspicious' if pred > THRESHOLD else 'Normal'
#     print(f"Clip {i}-{i+T-1}: {label} (Confidence: {pred:.2f}) | Inference Time: {infer_time:.3f}s")
#     results.append({
#         'clip': f"{i}-{i+T-1}",
#         'label': label,
#         'confidence': round(pred, 3),
#         'inference_time': round(infer_time, 3)
#     })

# # === Optional: Save results to file ===
# import csv
# with open("inference_results.csv", "w", newline="") as f:
#     writer = csv.DictWriter(f, fieldnames=['clip', 'label', 'confidence', 'inference_time'])
#     writer.writeheader()
#     writer.writerows(results)

# print("Inference completed and results saved to 'inference_results.csv'.")





# This one with 16 Frames/Sec means in one second

# import torch
# import cv2
# import numpy as np
# import time
# from model import Model
# import os

# # === Config ===
# T = 16
# FRAME_SIZE = (32, 32)
# CHANNELS_REQUIRED = 192
# THRESHOLD = 0.7
# OUTPUT_DIR = 'npy_frames'
# os.makedirs(OUTPUT_DIR, exist_ok=True)
# VIDEO_PATH = "clip_326.mp4"

# # === Load model ===
# model = Model()
# model.load_state_dict(torch.load('model.pth', map_location='cpu'))
# model.eval()
# print("Model loaded.")

# # === Open video ===
# cap = cv2.VideoCapture(VIDEO_PATH)
# frames = []
# frame_idx = 0
# frame_counter = 0

# results = []

# while True:
#     ret, frame = cap.read()
#     if not ret:
#         break

#     frame_counter += 1

#     # Resize and normalize
#     frame_resized = cv2.resize(frame, FRAME_SIZE)
#     frame_tensor = torch.tensor(frame_resized, dtype=torch.float32).permute(2, 0, 1) / 255.0
#     frames.append(frame_tensor)
#     # Save preprocessed .npy
#     np.save(os.path.join(OUTPUT_DIR, f"frame_{frame_idx:04d}.npy"), frame_tensor.numpy())
#     frame_idx += 1


#     if len(frames) == T:
#         # Prepare tensor for model
#         frames_tensor = torch.stack(frames)  # (16, 3, 32, 32)
#         frames_tensor = frames_tensor.permute(1, 0, 2, 3).unsqueeze(0)  # (1, 3, 16, 32, 32)
#         sequence = frames_tensor.repeat(1, CHANNELS_REQUIRED // 3, 1, 1, 1)  # (1, 192, 16, 32, 32)

#         # Inference
#         start = time.time()
#         with torch.no_grad():
#             logits, _ = model(sequence)
#             prediction = torch.sigmoid(logits).item()
#         infer_time = time.time() - start

#         label = "Suspicious" if prediction > THRESHOLD else "Normal"
#         start_index = frame_counter - T + 1
#         end_index = frame_counter

#         print(f"[{start_index}-{end_index}] {label} (Confidence: {prediction:.2f}) | Inference: {infer_time:.3f}s")

#         results.append({
#             "clip": f"{start_index}-{end_index}",
#             "label": label,
#             "confidence": round(prediction, 3),
#             "inference_time": round(infer_time, 3)
#         })

#         frames = []  # Clear buffer like in live processing

# cap.release()

# # === Save results to CSV ===
# import csv
# with open("video_realtime_results.csv", "w", newline="") as f:
#     writer = csv.DictWriter(f, fieldnames=["clip", "label", "confidence", "inference_time"])
#     writer.writeheader()
#     writer.writerows(results)

# print(" Processing done. Results saved to 'video_realtime_results.csv'.")





# This one is for live camera stream

# import torch
# import cv2
# import numpy as np
# import time
# from model import Model
# import os
# import csv

# # === Config ===
# T = 16
# FRAME_SIZE = (32, 32)
# CHANNELS_REQUIRED = 192
# THRESHOLD = 0.7
# OUTPUT_DIR = 'npy_frames_live'
# os.makedirs(OUTPUT_DIR, exist_ok=True)

# # === Load model ===
# model = Model()
# model.load_state_dict(torch.load('model.pth', map_location='cpu'))
# model.eval()
# print("Model loaded.")

# # === Open webcam ===
# cap = cv2.VideoCapture(0)  # 0 = default camera
# frames = []
# frame_counter = 0
# frame_idx = 0
# results = []

# print("Starting live inference. Press 'q' to quit.")

# while True:
#     ret, frame = cap.read()
#     if not ret:
#         print("Failed to read from camera.")
#         break

#     frame_counter += 1

#     # Resize and normalize
#     frame_resized = cv2.resize(frame, FRAME_SIZE)
#     frame_tensor = torch.tensor(frame_resized, dtype=torch.float32).permute(2, 0, 1) / 255.0
#     frames.append(frame_tensor)

#     # Save preprocessed frame (optional)
#     np.save(os.path.join(OUTPUT_DIR, f"frame_{frame_idx:04d}.npy"), frame_tensor.numpy())
#     frame_idx += 1

#     if len(frames) == T:
#         frames_tensor = torch.stack(frames)  # (16, 3, 32, 32)
#         frames_tensor = frames_tensor.permute(1, 0, 2, 3).unsqueeze(0)  # (1, 3, 16, 32, 32)
#         sequence = frames_tensor.repeat(1, CHANNELS_REQUIRED // 3, 1, 1, 1)  # (1, 192, 16, 32, 32)

#         start = time.time()
#         with torch.no_grad():
#             logits, _ = model(sequence)
#             prediction = torch.sigmoid(logits).item()
#         infer_time = time.time() - start

#         label = "Suspicious" if prediction > THRESHOLD else "Normal"
#         start_index = frame_counter - T + 1
#         end_index = frame_counter

#         print(f"[{start_index}-{end_index}] {label} (Confidence: {prediction:.2f}) | Inference: {infer_time:.3f}s")

#         # Show on live window
#         display_text = f"{label} ({prediction:.2f})"
#         cv2.putText(frame, display_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0,
#                     (0, 0, 255) if label == "Suspicious" else (0, 255, 0), 2)

#         results.append({
#             "clip": f"{start_index}-{end_index}",
#             "label": label,
#             "confidence": round(prediction, 3),
#             "inference_time": round(infer_time, 3)
#         })

#         frames = []  # Clear buffer

#     # Show current frame
#     cv2.imshow("Live Anomaly Detection", frame)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# cap.release()
# cv2.destroyAllWindows()

# # === Save results to CSV ===
# with open("live_camera_results.csv", "w", newline="") as f:
#     writer = csv.DictWriter(f, fieldnames=["clip", "label", "confidence", "inference_time"])
#     writer.writeheader()
#     writer.writerows(results)

# print("Live processing finished. Results saved to 'live_camera_results.csv'.")




# This code is for saving frames if suspicious is found
# import torch
# import cv2
# import numpy as np
# import time
# from model import Model
# import os
# import csv
# import pickle

# # === Config ===
# T = 16
# FRAME_SIZE = (32, 32)
# DISPLAY_SIZE = (640, 480)  # Resize for display and saving
# CHANNELS_REQUIRED = 192
# THRESHOLD = 0.5
# OUTPUT_DIR = 'npy_frames_live'
# SUSPICIOUS_CLIPS_DIR = 'suspicious_clips'

# os.makedirs(OUTPUT_DIR, exist_ok=True)
# os.makedirs(SUSPICIOUS_CLIPS_DIR, exist_ok=True)

# # === Load model ===
# model = Model()
# model.load_state_dict(torch.load('E:/Vs Code/STEAD 2/STEAD/saved_models/modelbase50.pkl', map_location='cpu',weights_only=False))
# model.eval()
# print("Model loaded.")


# # === Open webcam ===
# cap = cv2.VideoCapture(0)
# frames = []
# raw_frames = []  # To store the original frames (not resized) for video saving
# frame_counter = 0
# frame_idx = 0
# results = []

# print("Starting live inference. Press 'q' to quit.")

# while True:
#     ret, frame = cap.read()
#     if not ret:
#         print("Failed to read from camera.")
#         break

#     frame_counter += 1

#     # Resize for processing
#     frame_resized = cv2.resize(frame, FRAME_SIZE)
#     frame_tensor = torch.tensor(frame_resized, dtype=torch.float32).permute(2, 0, 1) / 255.0
#     frames.append(frame_tensor)
#     raw_frames.append(cv2.resize(frame, DISPLAY_SIZE))  # Save display-sized raw frame

#     # Save preprocessed frame (optional)
#     np.save(os.path.join(OUTPUT_DIR, f"frame_{frame_idx:04d}.npy"), frame_tensor.numpy())
#     frame_idx += 1

#     if len(frames) == T:
#         # Prepare model input
#         frames_tensor = torch.stack(frames)  # (16, 3, 32, 32)
#         frames_tensor = frames_tensor.permute(1, 0, 2, 3).unsqueeze(0)  # (1, 3, 16, 32, 32)
#         sequence = frames_tensor.repeat(1, CHANNELS_REQUIRED // 3, 1, 1, 1)  # (1, 192, 16, 32, 32)

#         start = time.time()
#         with torch.no_grad():
#             logits, _ = model(sequence)
#             prediction = torch.sigmoid(logits).item()
#         infer_time = time.time() - start

#         label = "Suspicious" if prediction > THRESHOLD else "Normal"
#         start_index = frame_counter - T + 1
#         end_index = frame_counter

#         print(f"[{start_index}-{end_index}] {label} (Confidence: {prediction:.2f}) | Inference: {infer_time:.3f}s")

#         # Show live text
#         display_text = f"{label} ({prediction:.2f})"
#         cv2.putText(frame, display_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0,
#                     (0, 0, 255) if label == "Suspicious" else (0, 255, 0), 2)

#         results.append({
#             "clip": f"{start_index}-{end_index}",
#             "label": label,
#             "confidence": round(prediction, 3),
#             "inference_time": round(infer_time, 3)
#         })

#         # === Save Suspicious Clip as Images ===
#         if label == "Suspicious":
#             clip_folder = os.path.join(SUSPICIOUS_CLIPS_DIR, f"suspicious_{start_index:04d}_{end_index:04d}")
#             os.makedirs(clip_folder, exist_ok=True)
#             for i, f in enumerate(raw_frames):
#                 frame_path = os.path.join(clip_folder, f"frame_{i+1:04d}.jpg")
#                 cv2.imwrite(frame_path, f)
#             print(f"> Saved suspicious frames to folder: {clip_folder}")


#         # Reset buffers
#         frames = []
#         raw_frames = []

#     # Show current frame
#     display_frame = cv2.resize(frame, DISPLAY_SIZE)
#     cv2.imshow("Live Anomaly Detection", display_frame)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# cap.release()
# cv2.destroyAllWindows()

# # === Save results to CSV ===
# with open("live_camera_results.csv", "w", newline="") as f:
#     writer = csv.DictWriter(f, fieldnames=["clip", "label", "confidence", "inference_time"])
#     writer.writeheader()
#     writer.writerows(results)

# print("Live processing finished. Results saved to 'live_camera_results.csv'.")




# This is the code after converting .pkl into .pth 

# import torch
# import cv2
# import numpy as np
# import time
# from model import Model
# import os
# import csv
# import pickle

# # === Config ===
# T = 16
# FRAME_SIZE = (32, 32)
# DISPLAY_SIZE = (640, 480)  # Resize for display and saving
# CHANNELS_REQUIRED = 192
# THRESHOLD = 0.7
# OUTPUT_DIR = 'npy_frames_live'
# SUSPICIOUS_CLIPS_DIR = 'suspicious_clips'

# os.makedirs(OUTPUT_DIR, exist_ok=True)
# os.makedirs(SUSPICIOUS_CLIPS_DIR, exist_ok=True)

# # === Load model ===
# model = Model()
# model.eval()

# # Load weights from .pkl file
# with open('E:/Vs Code/STEAD 2/STEAD/saved_models/modelbase50.pkl', 'rb') as f:
#     state_dict = pickle.load(f)

# model.load_state_dict(state_dict)
# print("Model loaded.")

# # === Open webcam ===
# # cap = cv2.VideoCapture(0) # This is for your normal webcam
# cap = cv2.VideoCapture("rtsp://192.168.1.1:7070/webcam") # This is for Drone as you can see the RSTP in it
# frames = []
# raw_frames = []  # To store the original frames (not resized) for video saving
# frame_counter = 0
# frame_idx = 0
# results = []

# print("Starting live inference. Press 'q' to quit.")

# while True:
#     ret, frame = cap.read()
#     if not ret:
#         print("Failed to read from camera.")
#         break

#     frame_counter += 1

#     # Resize for processing
#     frame_resized = cv2.resize(frame, FRAME_SIZE)
#     frame_tensor = torch.tensor(frame_resized, dtype=torch.float32).permute(2, 0, 1) / 255.0
#     frames.append(frame_tensor)
#     raw_frames.append(cv2.resize(frame, DISPLAY_SIZE))  # Save display-sized raw frame

#     # Save preprocessed frame (optional) this code is for saving every .npy files
#     # np.save(os.path.join(OUTPUT_DIR, f"frame_{frame_idx:04d}.npy"), frame_tensor.numpy())
#     # frame_idx += 1

#     # === Save only latest 32 frames at a time ===
#     current_npy_path = os.path.join(OUTPUT_DIR, f"frame_{frame_idx:04d}.npy")
#     np.save(current_npy_path, frame_tensor.numpy())

#     # Maintain only the last 32 npy files
#     existing_files = sorted(os.listdir(OUTPUT_DIR))
#     if len(existing_files) > 32:
#         files_to_delete = existing_files[:len(existing_files) - 32]
#         for file in files_to_delete:
#             os.remove(os.path.join(OUTPUT_DIR, file))

#     frame_idx += 1

#     if len(frames) == T:
#         # Prepare model input
#         frames_tensor = torch.stack(frames)  # (16, 3, 32, 32)
#         frames_tensor = frames_tensor.permute(1, 0, 2, 3).unsqueeze(0)  # (1, 3, 16, 32, 32)
#         sequence = frames_tensor.repeat(1, CHANNELS_REQUIRED // 3, 1, 1, 1)  # (1, 192, 16, 32, 32)

#         start = time.time()
#         with torch.no_grad():
#             logits, _ = model(sequence)
#             prediction = torch.sigmoid(logits).item()
#         infer_time = time.time() - start

#         label = "Suspicious" if prediction > THRESHOLD else "Normal"
#         start_index = frame_counter - T + 1
#         end_index = frame_counter

#         print(f"[{start_index}-{end_index}] {label} (Confidence: {prediction:.2f}) | Inference: {infer_time:.3f}s")

#         # Show live text
#         display_text = f"{label} ({prediction:.2f})"
#         cv2.putText(frame, display_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0,
#                     (0, 0, 255) if label == "Suspicious" else (0, 255, 0), 2)

#         results.append({
#             "clip": f"{start_index}-{end_index}",
#             "label": label,
#             "confidence": round(prediction, 3),
#             "inference_time": round(infer_time, 3)
#         })

#         # === Save Suspicious Clip as Images ===
#         if label == "Suspicious":
#             clip_folder = os.path.join(SUSPICIOUS_CLIPS_DIR, f"suspicious_{start_index:04d}_{end_index:04d}")
#             os.makedirs(clip_folder, exist_ok=True)
#             for i, f in enumerate(raw_frames):
#                 frame_path = os.path.join(clip_folder, f"frame_{i+1:04d}.jpg")
#                 cv2.imwrite(frame_path, f)
#             print(f"> Saved suspicious frames to folder: {clip_folder}")

#         # Reset buffers
#         frames = []
#         raw_frames = []

#     # Show current frame
#     display_frame = cv2.resize(frame, DISPLAY_SIZE)
#     cv2.imshow("Live Anomaly Detection", display_frame)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# cap.release()
# cv2.destroyAllWindows()

# # === Save results to CSV ===
# with open("live_camera_results.csv", "w", newline="") as f:
#     writer = csv.DictWriter(f, fieldnames=["clip", "label", "confidence", "inference_time"])
#     writer.writeheader()
#     writer.writerows(results)

# print("Live processing finished. Results saved to 'live_camera_results.csv'.")




# This code is for saving all the frames and also save the video in .mp4
# import torch
# import cv2
# import numpy as np
# import time
# from model import Model
# import os
# import csv
# import pickle

# # === Config ===
# T = 16
# FRAME_SIZE = (32, 32)
# DISPLAY_SIZE = (640, 480)
# CHANNELS_REQUIRED = 192
# THRESHOLD = 0.7
# OUTPUT_DIR = 'npy_frames_live'
# SUSPICIOUS_CLIPS_DIR = 'suspicious_clips'
# ALL_FRAMES_DIR = 'all_frames_live'
# VIDEO_OUTPUT_PATH = 'output_live_feed.mp4'

# # === Create directories ===
# os.makedirs(OUTPUT_DIR, exist_ok=True)
# os.makedirs(SUSPICIOUS_CLIPS_DIR, exist_ok=True)
# os.makedirs(ALL_FRAMES_DIR, exist_ok=True)

# # === Load model ===
# model = Model()
# model.eval()

# with open('E:/Vs Code/STEAD 2/STEAD/saved_models/modelbase50.pkl', 'rb') as f:
#     state_dict = pickle.load(f)

# model.load_state_dict(state_dict)
# print("Model loaded.")

# # === Open video source ===
# cap = cv2.VideoCapture(0)  # This is for Mobile feed
# # cap = cv2.VideoCapture("http://10.96.13.169:8080/video")  # This is for Mobile feed
# # cap = cv2.VideoCapture("rtsp://192.168.1.1:7070/webcam")  # This is for Drone feed

# # === Setup video writer ===
# fourcc = cv2.VideoWriter_fourcc(*'mp4v')
# out = cv2.VideoWriter(VIDEO_OUTPUT_PATH, fourcc, 20.0, DISPLAY_SIZE)

# frames = []
# raw_frames = []
# frame_counter = 0
# frame_idx = 0
# results = []

# latest_label = "Analyzing..."
# latest_conf = 0.0

# print("Starting live inference. Press 'q' to quit.")

# while True:
#     ret, frame = cap.read()
#     if not ret:
#         print("Failed to read from camera.")
#         break

#     frame_counter += 1

#     # Resize and prepare frame
#     frame_resized = cv2.resize(frame, FRAME_SIZE)
#     frame_tensor = torch.tensor(frame_resized, dtype=torch.float32).permute(2, 0, 1) / 255.0
#     frames.append(frame_tensor)

#     # Resize for display and saving
#     display_frame = cv2.resize(frame, DISPLAY_SIZE)
#     raw_frames.append(display_frame.copy())

#     # Save all display-sized frames
#     all_frame_path = os.path.join(ALL_FRAMES_DIR, f"frame_{frame_counter:04d}.jpg")
#     cv2.imwrite(all_frame_path, display_frame)

#     # Save current .npy frame
#     np.save(os.path.join(OUTPUT_DIR, f"frame_{frame_idx:04d}.npy"), frame_tensor.numpy())
#     existing_files = sorted(os.listdir(OUTPUT_DIR))
#     if len(existing_files) > 32:
#         for file in existing_files[:len(existing_files) - 32]:
#             os.remove(os.path.join(OUTPUT_DIR, file))
#     frame_idx += 1

#     # Run inference every T frames
#     if len(frames) == T:
#         frames_tensor = torch.stack(frames)
#         frames_tensor = frames_tensor.permute(1, 0, 2, 3).unsqueeze(0)
#         sequence = frames_tensor.repeat(1, CHANNELS_REQUIRED // 3, 1, 1, 1)

#         start = time.time()
#         with torch.no_grad():
#             logits, _ = model(sequence)
#             prediction = torch.sigmoid(logits).item()
#         infer_time = time.time() - start

#         latest_label = "Suspicious" if prediction > THRESHOLD else "Normal"
#         latest_conf = prediction
#         start_index = frame_counter - T + 1
#         end_index = frame_counter

#         print(f"[{start_index}-{end_index}] {latest_label} (Confidence: {prediction:.2f}) | Inference: {infer_time:.3f}s")

#         results.append({
#             "clip": f"{start_index}-{end_index}",
#             "label": latest_label,
#             "confidence": round(prediction, 3),
#             "inference_time": round(infer_time, 3)
#         })

#         # Save suspicious frames
#         if latest_label == "Suspicious":
#             clip_folder = os.path.join(SUSPICIOUS_CLIPS_DIR, f"suspicious_{start_index:04d}_{end_index:04d}")
#             os.makedirs(clip_folder, exist_ok=True)
#             for i, f in enumerate(raw_frames):
#                 frame_path = os.path.join(clip_folder, f"frame_{i+1:04d}.jpg")
#                 cv2.imwrite(frame_path, f)
#             print(f"> Saved suspicious frames to: {clip_folder}")

#         # Reset
#         frames = []
#         raw_frames = []

#     # Overlay prediction label on current frame
#     label_text = f"{latest_label} ({latest_conf:.2f})"
#     cv2.putText(display_frame, label_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0,
#                 (0, 0, 255) if latest_label == "Suspicious" else (0, 255, 0), 2)

#     # Show and save
#     cv2.imshow("Live Anomaly Detection", display_frame)
#     out.write(display_frame)

#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# cap.release()
# out.release()
# cv2.destroyAllWindows()

# # === Save CSV ===
# with open("live_camera_results.csv", "w", newline="") as f:
#     writer = csv.DictWriter(f, fieldnames=["clip", "label", "confidence", "inference_time"])
#     writer.writeheader()
#     writer.writerows(results)

# print("\n Live processing finished.")
# print(" All frames saved to:", ALL_FRAMES_DIR)
# print(" Suspicious clips saved to:", SUSPICIOUS_CLIPS_DIR)
# print(" .npy frames saved to:", OUTPUT_DIR)
# print(" Video saved to:", VIDEO_OUTPUT_PATH)
# print(" CSV saved to: live_camera_results.csv")




# New one with the another model working with it (YOWO)
import torch
import cv2
import numpy as np
import time
from model import Model
import os
import csv
import pickle
import io

# === gRPC imports (NEW) ===
import grpc
import refine_pb2
import refine_pb2_grpc

# === Config ===
T = 16
FRAME_SIZE = (32, 32)
DISPLAY_SIZE = (640, 480)
CHANNELS_REQUIRED = 192
THRESHOLD = 0.7
OUTPUT_DIR = 'npy_frames_live'
SUSPICIOUS_CLIPS_DIR = 'suspicious_clips'
ALL_FRAMES_DIR = 'all_frames_live'
VIDEO_OUTPUT_PATH = 'output_live_feed.mp4'

# === Create directories ===
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(SUSPICIOUS_CLIPS_DIR, exist_ok=True)
os.makedirs(ALL_FRAMES_DIR, exist_ok=True)

# === Load model (first stage) ===
model = Model()
model.eval()
with open('E:/Vs Code/STEAD 2/STEAD/saved_models/modelbase50.pkl', 'rb') as f:
    state_dict = pickle.load(f)
model.load_state_dict(state_dict)
print("Model loaded (first stage: modelbase50.pkl).")

# === gRPC second-stage client (NEW) ===
# Starts even if server not up yet; calls will raise on failure and we’ll catch them.
channel = grpc.insecure_channel("localhost:50051")
stub = refine_pb2_grpc.RefineServiceStub(channel)

# === Open video source ===
# cap = cv2.VideoCapture(0)  # Replace with 0 for webcam
cap = cv2.VideoCapture("http://10.96.13.169:8080/video")  # This is for Mobile feed
# cap = cv2.VideoCapture("rtsp://192.168.1.1:7070/webcam")  # This is for Drone feed

# === Setup video writer ===
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(VIDEO_OUTPUT_PATH, fourcc, 20.0, DISPLAY_SIZE)

frames = []
raw_frames = []
frame_counter = 0
frame_idx = 0
results = []

latest_label = "Analyzing..."
latest_conf = 0.0

# Second-stage (refiner) latest output for overlay (NEW)
refined_label = ""
refined_conf = 0.0

print("Starting live inference. Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to read from camera.")
        break

    frame_counter += 1

    # Resize and prepare frame
    frame_resized = cv2.resize(frame, FRAME_SIZE)
    frame_tensor = torch.tensor(frame_resized, dtype=torch.float32).permute(2, 0, 1) / 255.0
    frames.append(frame_tensor)

    # Resize for display and saving
    display_frame = cv2.resize(frame, DISPLAY_SIZE)
    raw_frames.append(display_frame.copy())

    # Save all display-sized frames
    all_frame_path = os.path.join(ALL_FRAMES_DIR, f"frame_{frame_counter:04d}.jpg")
    cv2.imwrite(all_frame_path, display_frame)

    # Save current .npy frame (rolling window of 32)
    np.save(os.path.join(OUTPUT_DIR, f"frame_{frame_idx:04d}.npy"), frame_tensor.numpy())
    existing_files = sorted(os.listdir(OUTPUT_DIR))
    if len(existing_files) > 32:
        for file in existing_files[:len(existing_files) - 32]:
            os.remove(os.path.join(OUTPUT_DIR, file))
    frame_idx += 1

    # Run inference every T frames
    if len(frames) == T:
        # Keep a copy before we reset anything so we can send to gRPC if needed
        frames_tensor_clip = torch.stack(frames)  # [T,3,32,32]

        # First-stage forward
        frames_tensor = frames_tensor_clip.permute(1, 0, 2, 3).unsqueeze(0)  # [1,3,T,32,32]
        sequence = frames_tensor.repeat(1, CHANNELS_REQUIRED // 3, 1, 1, 1)

        start = time.time()
        with torch.no_grad():
            logits, _ = model(sequence)
            prediction = torch.sigmoid(logits).item()
        infer_time = time.time() - start

        latest_label = "Suspicious" if prediction > THRESHOLD else "Normal"
        latest_conf = prediction
        start_index = frame_counter - T + 1
        end_index = frame_counter

        print(f"[{start_index}-{end_index}] 1st: {latest_label} (Conf: {prediction:.2f}) | Inference: {infer_time:.3f}s")

        results.append({
            "clip": f"{start_index}-{end_index}",
            "label": latest_label,
            "confidence": round(prediction, 3),
            "inference_time": round(infer_time, 3)
        })

        # Save suspicious frames (UNCHANGED)
        if latest_label == "Suspicious":
            clip_folder = os.path.join(SUSPICIOUS_CLIPS_DIR, f"suspicious_{start_index:04d}_{end_index:04d}")
            os.makedirs(clip_folder, exist_ok=True)
            for i, fimg in enumerate(raw_frames):
                frame_path = os.path.join(clip_folder, f"frame_{i+1:04d}.jpg")
                cv2.imwrite(frame_path, fimg)
            print(f"> Saved suspicious frames to: {clip_folder}")

            # === NEW: Send this suspicious clip to the second-stage model over gRPC ===
            try:
                # Serialize the [T,3,32,32] float32 array to .npy bytes
                buf = io.BytesIO()
                np.save(buf, frames_tensor_clip.numpy())
                req = refine_pb2.Clip(
                    frames_npy=buf.getvalue(),
                    start_index=start_index,
                    end_index=end_index
                )
                resp = stub.Refine(req)  # blocking unary call
                refined_label = resp.label
                refined_conf = resp.confidence
                print(f"[Refiner] 2nd: {resp.label} (Conf: {resp.confidence:.3f}) | {resp.detail}")
            except Exception as e:
                refined_label = "Refiner-Error"
                refined_conf = 0.0
                print(f"[Refiner] gRPC call failed: {e}")

        # Reset rolling buffers for the next clip window
        frames = []
        raw_frames = []

    # Overlay prediction labels on current frame
    # Always show first model output; if refined exists, show it too.
    label_text = f"1st: {latest_label} ({latest_conf:.2f})"
    if refined_label:
        label_text += f" | 2nd: {refined_label} ({refined_conf:.2f})"

    cv2.putText(display_frame, label_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0,
                (0, 0, 255) if latest_label == "Suspicious" else (0, 255, 0), 2)

    # Show and save
    cv2.imshow("Live Anomaly Detection", display_frame)
    out.write(display_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
out.release()
cv2.destroyAllWindows()

# === Save CSV ===
with open("live_camera_results.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["clip", "label", "confidence", "inference_time"])
    writer.writeheader()
    writer.writerows(results)

print("\n Live processing finished.")
print(" All frames saved to:", ALL_FRAMES_DIR)
print(" Suspicious clips saved to:", SUSPICIOUS_CLIPS_DIR)
print(" .npy frames saved to:", OUTPUT_DIR)
print(" Video saved to:", VIDEO_OUTPUT_PATH)
print(" CSV saved to: live_camera_results.csv")