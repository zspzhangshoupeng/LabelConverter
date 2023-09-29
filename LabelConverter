import os
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox
from xml.etree import ElementTree as ET
from tkinter.ttk import Progressbar
from tqdm import tqdm
import math

# 初始化Tkinter窗口
root = tk.Tk()
root.title("Lable Converter v0.1 by zsp")
root.geometry('500x500')
# 创建变量以存储用户选择的文件夹路径
source_folder = ""
destination_folder = ""

# 创建字典来存储类别和索引映射
classes = {}
progress_var = tk.DoubleVar()
result_text = tk.StringVar()
# 添加一个全局变量，用于跟踪处理文件的进度
processed_files = 0
# 函数：浏览源文件夹
def browse_source_folder():
    global source_folder
    source_folder = filedialog.askdirectory()
    source_folder_label.config(text=source_folder)

# 函数：浏览目标文件夹
def browse_destination_folder():
    global destination_folder
    destination_folder = filedialog.askdirectory()
    destination_folder_label.config(text=destination_folder)

#函数：执行格式转换的核心代码
def core_code_roxml2yolo_rotation(source_folder, destination_folder):
    global processed_files
    for xml_file in tqdm(os.listdir(source_folder), desc="Converting", unit=" file"):
        if xml_file.endswith(".xml"):
            xml_path = os.path.join(source_folder, xml_file)
            tree = ET.parse(xml_path)
            root = tree.getroot()
            yolo_file = os.path.splitext(xml_file)[0] + ".txt"
            yolo_path = os.path.join(destination_folder, yolo_file)

            width = float(root.find("size").find("width").text)
            height = float(root.find("size").find("height").text)

            with open(yolo_path, "w") as yolo_file:
                for obj in root.findall('object'):
                    obj_name = obj.find('name').text
                    class_index = classes[obj_name]
                    # ---核心功能代码---
                    rbb = obj.find('robndbox')
                    cx = float(rbb.find('cx').text)/ width
                    cy = float(rbb.find('cy').text)/ height
                    w = float(rbb.find('w').text)/ width
                    h = float(rbb.find('h').text)/ height
                    angle = float(rbb.find('angle').text)
                    if angle > math.pi:
                        angle -= math.pi

                    degree = int(round(angle / math.pi * 180))
                    if h > w:
                        w, h = h, w
                    degree = degree + 90 if degree < 90 else degree - 90
                    cv_degree = degree
                    cv_degree = 0 if cv_degree == 180 else cv_degree

                    assert cv_degree >= 0 and cv_degree < 180
                    yolo_file.write(
                        f"{class_index} {cx :.6f} {cy :.6f} {w :.6f} {h :.6f} {cv_degree:.0f}\n")
                    # 如果需要改类名为原始字符串，class_index替换为-->class_name
                    # ---核心功能代码END---
            processed_files += 1
            progress_var.set((processed_files / len(xml_file)) * 100)


#函数：执行格式转换的核心代码
def core_code_voc2yolo(source_folder, destination_folder):
    global processed_files
    for xml_file in tqdm(os.listdir(source_folder), desc="Converting", unit=" file"):
        if xml_file.endswith(".xml"):
            xml_path = os.path.join(source_folder, xml_file)
            tree = ET.parse(xml_path)
            root = tree.getroot()
            yolo_file = os.path.splitext(xml_file)[0] + ".txt"
            yolo_path = os.path.join(destination_folder, yolo_file)

            width = float(root.find("size").find("width").text)
            height = float(root.find("size").find("height").text)

            with open(yolo_path, "w") as yolo_file:
                for obj in root.findall("object"):
                    obj_name = obj.find("name").text
                    bbox = obj.find("bndbox")
                    xmin = float(bbox.find("xmin").text)
                    ymin = float(bbox.find("ymin").text)
                    xmax = float(bbox.find("xmax").text)
                    ymax = float(bbox.find("ymax").text)

                    class_index = classes[obj_name]
                    x_center = (xmin + xmax) / (2.0 * width)
                    y_center = (ymin + ymax) / (2.0 * height)
                    box_width = (xmax - xmin) / width
                    box_height = (ymax - ymin) / height

                    yolo_line = f"{class_index} {x_center:.6f} {y_center:.6f} {box_width:.6f} {box_height:.6f}\n"
                    yolo_file.write(yolo_line)
                    # 更新进度条
            processed_files += 1
            progress_var.set((processed_files / len(xml_file)) * 100)

# 函数：执行转换功能
def convert_to_yolo1():
    if not source_folder or not destination_folder:
        messagebox.showerror("Error", "请选择源文件夹和目标文件夹")
        return

    # 1. 遍历源文件夹，构建类别索引映射，并按字母顺序排序
    global classes
    classes = {}
    class_index = 0

    for xml_file in os.listdir(source_folder):
        if xml_file.endswith(".xml"):
            tree = ET.parse(os.path.join(source_folder, xml_file))
            root = tree.getroot()
            for obj in root.findall("object"):
                obj_name = obj.find("name").text
                if obj_name not in classes:
                    classes[obj_name] = class_index
                    class_index += 1
    #classes = {k: v for k, v in sorted(classes.items())}
    # 重新映射类别索引为0开始的正整数
    classes = {key: index for index, key in enumerate(sorted(classes.keys()))}
    # 2. 再次遍历源文件夹，转换VOC格式为YOLO格式
    core_code_voc2yolo(source_folder, destination_folder)
    messagebox.showinfo("Info", "转换完成")

    # 3. 统计每个类别的数量并显示标签对应的索引号
    class_counts = {key: 0 for key in classes}
    for xml_file in os.listdir(source_folder):
        if xml_file.endswith(".xml"):
            tree = ET.parse(os.path.join(source_folder, xml_file))
            root = tree.getroot()
            for obj in root.findall("object"):
                obj_name = obj.find("name").text
                class_index = classes[obj_name]
                class_counts[obj_name] += 1
    # 清空之前的表格数据
    for item in result_tree.get_children():
        result_tree.delete(item)

    # 填充表格数据
    for class_name, class_index in classes.items():
        count = class_counts.get(class_name, 0)
        result_tree.insert("", "end", values=(class_name, class_index, count))
    # 4. 更新结果文本框
    #result_text.set("\n".join([f"{key} (Index {classes[key]}): {value}" for key, value in class_counts.items()]))
# 函数：执行转换功能
def convert_to_yolo2():
    if not source_folder or not destination_folder:
        messagebox.showerror("Error", "请选择源文件夹和目标文件夹")
        return

    # 1. 遍历源文件夹，构建类别索引映射，并按字母顺序排序
    global classes
    classes = {}
    class_index = 0

    for xml_file in os.listdir(source_folder):
        if xml_file.endswith(".xml"):
            tree = ET.parse(os.path.join(source_folder, xml_file))
            root = tree.getroot()
            for obj in root.findall("object"):
                obj_name = obj.find("name").text
                if obj_name not in classes:
                    classes[obj_name] = class_index
                    class_index += 1
    #classes = {k: v for k, v in sorted(classes.items())}
    # 重新映射类别索引为0开始的正整数
    classes = {key: index for index, key in enumerate(sorted(classes.keys()))}
    # 2. 再次遍历源文件夹，转换VOC格式为YOLO格式
    core_code_roxml2yolo_rotation(source_folder, destination_folder)
    messagebox.showinfo("Info", "转换完成")

    # 3. 统计每个类别的数量并显示标签对应的索引号
    class_counts = {key: 0 for key in classes}
    for xml_file in os.listdir(source_folder):
        if xml_file.endswith(".xml"):
            tree = ET.parse(os.path.join(source_folder, xml_file))
            root = tree.getroot()
            for obj in root.findall("object"):
                obj_name = obj.find("name").text
                class_index = classes[obj_name]
                class_counts[obj_name] += 1
    # 清空之前的表格数据
    for item in result_tree.get_children():
        result_tree.delete(item)

    # 填充表格数据
    for class_name, class_index in classes.items():
        count = class_counts.get(class_name, 0)
        result_tree.insert("", "end", values=(class_name, class_index, count))
    # 4. 更新结果文本框
    #result_text.set("\n".join([f"{key} (Index {classes[key]}): {value}" for key, value in class_counts.items()]))

# 创建UI元素
source_folder_label = tk.Label(root, text="选择源文件夹：")
source_folder_label.pack()
browse_source_button = tk.Button(root, text="浏览", background="yellow", command=browse_source_folder)
browse_source_button.pack()

destination_folder_label = tk.Label(root, text="选择目标文件夹：")
destination_folder_label.pack()
browse_destination_button = tk.Button(root, text="浏览", background="yellow", command=browse_destination_folder)
browse_destination_button.pack()

convert_button = tk.Button(root, text="VOC --> YOLO", background="blue", command=convert_to_yolo1)
convert_button.pack()
convert_button2 = tk.Button(root, text="roLabelimg --> YOLO[0,180)", background="red", command=convert_to_yolo2)
convert_button2.pack()
progress_bar = Progressbar(root, variable=progress_var, maximum=100)
progress_bar.pack()

result_label = tk.Label(root, text="结果：")
result_label.pack()
#result_display = tk.Label(root, textvariable=result_text)
#result_display.pack()

# 创建结果展示表格
result_tree = ttk.Treeview(root, height=11, columns=("Class", "Index", "Count"))  # 展示11行
result_tree.heading("#1", text="Class")
result_tree.heading("#2", text="Index")
result_tree.heading("#3", text="Count")

result_tree.column("#1", width=150)
result_tree.column("#2", width=50)
result_tree.column("#3", width=50)

result_tree.pack()

root.mainloop()
