import tkinter as tk
from tkinter import filedialog, messagebox
import requests
import threading
import webbrowser
import cloudinary
import cloudinary.uploader
from PIL import Image  # Import PIL to handle image size
import time
import os

from pymsgbox import prompt


# Function to get API key
def get_api_key():
    return "22f8004a1e9280dc4101c420359fb142.ef6MQqRiNmBNR7Wf"  # Replace with your actual API key


# Function to expand text using GLM-4-Flash model
def expand_text_with_ai(prompt, duration):
    api_key = get_api_key()
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    # Updated prompt with detailed guidelines
    system_message = {
        "role": "system",
        "content":
            f"""请根据以下详细指南生成{duration}秒的视频内容描述，专注于视频内容，避免无关描述，并包含具体的时间轴信息。要求输出字符数量精简到500个字符以内,确保每个部分都有详细的专业描述。
                视频主题与时间轴：中心主题及特征，精确描述{duration}秒内每秒内容。
                视觉风格：艺术风格，主色调及情感，动画效果增强故事。
                元素描述：主要元素外观、表情、动作；背景环境；附加装饰。
                构图与镜头：镜头类型与情感影响；视觉焦点变化；空间层次感。
                技术要求：画风一致。
                情感与叙事：传达情感，叙事情节。
                风格与文化：文化元素，历史背景，特殊艺术风格。
                详细时间轴模板：视频主题:...时间轴:0秒...，1秒...，2秒...，3秒...，4秒...，5秒...，6秒...,7秒...,8秒...,9秒...,10秒...。
                其他要求：视频用途，动态或静态效果，音频与视觉协同。
                请根据上述指南，生成专业且紧凑的视频内容描述。"""
    }
    payload = {
        "model": "glm-4-flash",
        "messages": [system_message, {"role": "user", "content": prompt}],
        "max_tokens": 512  # Limit the number of tokens to control the length
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        response_data = response.json()
        content = response_data["choices"][0]["message"]["content"]
        return content[:512]  # Truncate to ensure it fits within the required length
    else:
        raise Exception(f"请求失败：{response.text}")


# Function to generate text from image using GLM-4V-Flash model
def describe_image(api_key, image_url):
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "glm-4v-flash",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url
                        }
                    },
                    {
                        "type": "text",
                        "text": "请根据以下详细指南生成图生文描述，专注于图像内容，避免无关描述。\n1. **主题核心**\n   - **主题概述**：明确图像的中心主题，例如人物、动物、风景或事件，并指出数量和主要特征。\n   - **背景细节**：详细描述背景，包括时间、地点、季节和氛围，以及它们对主题的影响。\n2. **视觉风格**\n   - **风格定义**：确定艺术风格，并描述其在图像中的体现。\n   - **色彩与情感**：选择主色调（冷、暖或黑白），并描述其情感氛围（忧郁、快乐、神秘、浪漫等），包括颜色的具体数值（如RGB或HEX）。\n   - **光影效果**：描述光线效果，如高对比度或柔和光线，以及光源（自然光或人工光），包括光源的位置（X,Y）和光线的方向。\n3. **元素描述**\n   - **主体特征**：详细描述主要元素，如人物、动物、物体的外观、表情、姿态和动作，包括大小、位置（X,Y）和比例。\n   - **环境描绘**：描述背景环境、结构和材质，考虑远中近景的关系，包括环境的具体尺寸和位置（X,Y）。\n   - **装饰细节**：列出图像中的附加元素和装饰，增强生动感和细节，包括数量、颜色、大小和位置（X,Y）。\n4. **构图与视角**\n   - **视角选择**：描述图像的视角，如正面、侧面、俯视、仰视，及其对情感表达的影响，包括视角的具体角度。\n   - **视觉焦点**：确定图像的视觉焦点，是否集中在特定细节或场景元素上，包括焦点的大小和位置（X,Y）。\n   - **空间层次**：设定前景、中景和背景的层次感，通过景深或布局增强空间感，包括各层次的具体比例和位置（X,Y）。\n5. **技术要求**\n   - **清晰度与分辨率**：图像分辨率要求1080x1080，高细节表现，包括细节的清晰度，如纹理、光影反射等。\n   - **风格一致性**：确保所有元素风格一致，避免风格冲突，包括元素之间的比例和协调性。\n   - **图像比例**：根据用途设定1:1比例，考虑实际用途，包括图像的长宽比和各元素的比例。\n6. **情感与情境**\n   - **情感传达**：图像应传达的情感或气氛，确保视觉元素如色调、构图、光线等能够强化这些情感的表达，包括情感的具体描述。\n   - **叙事性**：图像是否需要叙事感，展示特定情节或故事背景，包括情节的具体细节和发展。\n7. **风格与文化元素**\n   - **文化特色**：是否需要加入文化、历史或地方特色元素，包括元素的具体特征和象征意义。\n   - **时代背景**：设定图像的历史背景，如古代、现代、未来或特定时期，包括时代背景的具体特征。\n   - **特殊风格**：添加特殊艺术风格的需求，包括风格的具体细节和表现手法。\n8. **其他要求**\n   - **用途与平台**：明确图像用途和平台，确保符合视觉和尺寸要求，包括平台的具体要求和图像的用途。\n   - **动态与静态**：考虑图像是否需要动态效果或保持静态美感，包括动态效果的具体描述。"
                    }
                ]
            }
        ]
    }
    print(f"Sending payload to API: {payload}")  # Debugging: Print the payload
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        response_data = response.json()
        return response_data["choices"][0]["message"]["content"]
    else:
        raise Exception(f"请求失败：{response.text}")


# Function to generate video from text
def generate_video_from_text(prompt):
    api_key = get_api_key()
    url = "https://open.bigmodel.cn/api/paas/v4/videos/generations"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "cogvideox-flash",
        "prompt": prompt,
        "quality": "quality",
        "with_audio": True,
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        response_data = response.json()
        return response_data.get("id")
    else:
        raise Exception(f"请求失败：{response.text}")


# Function to select the closest video size based on image dimensions
def select_video_size(image_path):
    # Define available sizes and their aspect ratios
    sizes = {
        "720x480": 720 / 480,
        "1024x1024": 1024 / 1024,
        "1280x960": 1280 / 960,
        "960x1280": 960 / 1280,
        "1920x1080": 1920 / 1080,
        "1080x1920": 1080 / 1920,
        "2048x1080": 2048 / 1080
    }

    # Open the image to get its dimensions
    with Image.open(image_path) as img:
        width, height = img.size
        aspect_ratio = width / height

    # Find the closest size
    closest_size = min(sizes, key=lambda size: abs(sizes[size] - aspect_ratio))
    return closest_size


# Function to generate video from image
def generate_video_from_image(image_path, prompt):
    api_key = get_api_key()
    url = "https://open.bigmodel.cn/api/paas/v4/videos/generations"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    image_url = upload_image_to_cloudinary(image_path)
    if not image_url:
        raise Exception("Image upload failed, cannot proceed with video generation.")

    # Select the closest video size
    video_size = select_video_size(image_path)

    payload = {
        "model": "cogvideox-flash",
        "image_url": image_url,
        "prompt": prompt,
        "quality": "quality",
        "with_audio": True,
        "size": video_size,
        "duration": 10,
        "fps": 30
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses
        response_data = response.json()
        print(f"Video generation response: {response_data}")  # Debugging: Print the response
        return response_data.get("id")
    except requests.exceptions.RequestException as e:
        print(f"Video generation request failed: {e}")
        raise Exception(f"请求失败：{response.text}")


cloudinary.config(
    cloud_name='dafb74pxg',  # Replace with your Cloudinary cloud name
    api_key='421823869779871',  # Replace with your Cloudinary API key
    api_secret='QmGIoTm0dVpUBCSEPdCFeEW03Tw',  # Replace with your Cloudinary API secret
    secure=True
)


# Function to upload image to Cloudinary and get URL
def upload_image_to_cloudinary(image_path):
    try:
        response = cloudinary.uploader.upload(image_path)
        image_url = response['secure_url']
        print(f"Image URL: {image_url}")  # Debugging: Print the image URL
        return image_url
    except Exception as e:
        print(f"Upload failed: {e}")
        messagebox.showerror("Upload Error", f"Failed to upload image: {e}")
        return None


# Function to log URLs to a text file
def log_urls(image_url, video_url):
    with open("url_log.txt", "a") as log_file:
        log_file.write(f"Image URL: {image_url}\n")
        log_file.write(f"Video URL: {video_url}\n")
        log_file.write("-" * 40 + "\n")


# Function to check video generation status
def check_video_status(video_id):
    api_key = get_api_key()
    url = f"https://open.bigmodel.cn/api/paas/v4/async-result/{video_id}"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses
        response_data = response.json()
        # print(f"Video status response: {response_data}")  # Debugging: Print the response
        if response_data["task_status"] == "SUCCESS":
            video_url = response_data["video_result"][0]["url"]
            return video_url
        elif response_data["task_status"] == "FAIL":
            raise Exception("Video generation failed")
        else:
            return None  # Still processing
    except requests.exceptions.RequestException as e:
        print(f"Video status request failed: {e}")
        raise Exception(f"请求失败：{response.text}")


# Function to handle AI text expansion
def handle_ai_expansion():
    prompt = text_entry.get("1.0", tk.END).strip()
    image_url = image_url_entry.get().strip()
    if not prompt:
        messagebox.showerror("错误", "请输入文本描述")
        return

    def expand():
        try:
            status_label.config(text="正在进行AI细化...")
            ai_expand_button.config(state=tk.DISABLED)  # Disable the button
            duration = 10 if image_url else 6
            expanded_text = expand_text_with_ai(prompt, duration)
            expanded_text_box.delete("1.0", tk.END)
            expanded_text_box.insert(tk.END, expanded_text)
            status_label.config(text="AI细化完成")
        except Exception as e:
            messagebox.showerror("错误", str(e))
            status_label.config(text="AI细化失败")
        finally:
            root.after(10000, lambda: ai_expand_button.config(state=tk.NORMAL))  # Re-enable after 10 seconds

    threading.Thread(target=expand).start()


# Function to handle image upload and description
def handle_image_upload():
    image_path = filedialog.askopenfilename(title="选择图像文件", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    if not image_path:
        messagebox.showerror("错误", "请选择图像文件")
        return

    def upload_and_describe():  # 定义一个函数来处理上传和描述
        try:
            status_label.config(text="正在上传图片...")
            image_url = upload_image_to_cloudinary(image_path)
            if image_url:
                image_url_entry.delete(0, tk.END)
                image_url_entry.insert(0, image_url)
                # Clear AI expansion output and describe the image
                expanded_text_box.delete("1.0", tk.END)
                status_label.config(text="正在生成图像描述...")
                # Generate text description from image
                description1 = describe_image(get_api_key(), image_url)
                description = expand_text_with_ai(f"将这个照片描述改写成视频:{description1}", 10)
                expanded_text_box.insert(tk.END, description)
                status_label.config(text="图像描述生成完成")
        except Exception as e:
            messagebox.showerror("错误", str(e))
            status_label.config(text="图像描述生成失败")

    threading.Thread(target=upload_and_describe).start()


# Function to handle video generation
def handle_video_generation():
    prompt = expanded_text_box.get("1.0", tk.END).strip()
    image_url = image_url_entry.get().strip()

    if not prompt:
        messagebox.showerror("错误", "请先进行AI细化")
        return

    def generate():
        try:
            status_label.config(text="正在生成视频...")
            video_generation_button.config(state=tk.DISABLED)  # Disable the button
            if image_url:
                # Use the existing image URL for video generation
                video_id = generate_video_from_image_url(image_url, prompt)
            else:
                # If no image URL, generate video from text
                video_id = generate_video_from_text(prompt)
            video_url = None
            while not video_url:
                video_url = check_video_status(video_id)
                if not video_url:
                    time.sleep(10)  # Wait for 10 seconds before checking again
            video_url_entry.delete(0, tk.END)
            video_url_entry.insert(0, video_url)
            status_label.config(text="视频生成完成")
            # Log the URLs
            log_urls(image_url, video_url)
        except Exception as e:
            messagebox.showerror("错误", str(e))
            status_label.config(text="视频生成失败")
        finally:
            root.after(10000, lambda: video_generation_button.config(state=tk.NORMAL))  # Re-enable after 10 seconds

    threading.Thread(target=generate).start()


# Function to generate video from an existing image URL
def generate_video_from_image_url(image_url, prompt):
    api_key = get_api_key()
    url = "https://open.bigmodel.cn/api/paas/v4/videos/generations"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "cogvideox-flash",
        "image_url": image_url,
        "prompt": prompt,
        "quality": "quality",
        "with_audio": True,
        "size": "1920x1080",  # Default size, adjust as needed
        "duration": 10,
        "fps": 30
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses
        response_data = response.json()
        print(f"Video generation response: {response_data}")  # Debugging: Print the response
        return response_data.get("id")
    except requests.exceptions.RequestException as e:
        print(f"Video generation request failed: {e}")
        raise Exception(f"请求失败：{response.text}")


# Function to preview video
def preview_video():
    video_url = video_url_entry.get()
    if video_url:
        webbrowser.open(video_url)
    else:
        messagebox.showerror("错误", "没有可预览的视频链接")


# Function to download video
def download_video():
    video_url = video_url_entry.get()
    if video_url:
        # 从视频 URL 输入框中获取视频 URL
        video_url = video_url_entry.get()

        # 如果视频 URL 存在
        if video_url:
            # 保存到本地文件夹"AI视频"文件夹
            video_folder = "AI视频"
            # 如果文件夹不存在，则创建文件夹
            if not os.path.exists(video_folder):
                os.makedirs(video_folder)
            # 构建视频文件名时间加主题
            import datetime
            current_time = datetime.datetime.now()
            video_filename = os.path.join(video_folder, f"{current_time.strftime('%Y-%m-%d_%H-%M-%S')}.mp4")
            # 使用 requests 库下载视频
            response = requests.get(video_url)
            # 如果下载成功
            if response.status_code == 200:
                # 将视频内容写入文件
                with open(video_filename, "wb") as file:
                    file.write(response.content)
            # 显示下载完成的信息消息框
            messagebox.showinfo("下载", "视频已保存到本地文件夹")
        # 如果视频 URL 不存在
        else:
            # 显示错误消息框
            messagebox.showerror("错误", "没有可下载的视频链接")


# Function to clear the image URL
def clear_image_url():
    image_url_entry.delete(0, tk.END)
    status_label.config(text="图片URL已清空")


# Set up the GUI
root = tk.Tk()
root.title("CogVideoX 视频生成")
root.geometry("600x700")

# Text Input Section
tk.Label(root, text="输入文本").pack(pady=5)
text_entry = tk.Text(root, wrap=tk.WORD, width=70, height=2)
text_entry.pack(pady=5)

# AI Expansion and Image Upload Buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=5)

ai_expand_button = tk.Button(button_frame, text="AI细化", command=handle_ai_expansion)
ai_expand_button.pack(side=tk.LEFT, padx=5)

image_upload_button = tk.Button(button_frame, text="图片上传", command=handle_image_upload)
image_upload_button.pack(side=tk.LEFT, padx=5)

clear_image_url_button = tk.Button(button_frame, text="清空图片URL", command=clear_image_url)
clear_image_url_button.pack(side=tk.LEFT, padx=5)

# Image URL Display
tk.Label(root, text="图片的URL").pack(pady=5)
image_url_entry = tk.Entry(root, width=70)
image_url_entry.pack(pady=5)

# Expanded Text Output
tk.Label(root, text="AI扩写输出").pack(pady=5)
expanded_text_box = tk.Text(root, wrap=tk.WORD, width=70, height=10)
expanded_text_box.pack(pady=5)

# Video Generation Button
video_generation_button = tk.Button(root, text="视频生成", command=handle_video_generation)
video_generation_button.pack(pady=5)

# Video URL Output
tk.Label(root, text="视频的URL").pack(pady=5)
video_url_entry = tk.Entry(root, width=70)
video_url_entry.pack(pady=5)

# Preview and Download Buttons
preview_button = tk.Button(root, text="预览", command=preview_video)
preview_button.pack(pady=5)

download_button = tk.Button(root, text="下载", command=download_video)
download_button.pack(pady=5)

# Status Label for Progress
status_label = tk.Label(root, text="", anchor="w", justify=tk.LEFT)
status_label.pack(side=tk.LEFT, padx=10, pady=10)

root.mainloop()
