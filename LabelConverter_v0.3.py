import os
import random
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox
#from tqdm import tqdm
from lxml import etree as ET
from PIL import Image
import math

# 初始化Tkinter窗口
root = tk.Tk()
root.title("LabelConverter v0.3 by zsp")
root.geometry('500x660')
# 创建变量以存储用户选择的文件夹路径
source_folder = ""
destination_folder = ""
image_folder = ""
predefined_classes_file = ""
pi = 3.1415926
# 创建字典来存储类别和索引映射
classes = {}
classeslist = []
#progress_var = tk.DoubleVar()
result_text = tk.StringVar()
# 添加一个全局变量，用于跟踪处理文件的进度
processed_files = 0
# 函数：浏览源文件夹
def random_color():
    return "#{:02x}{:02x}{:02x}".format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
def browse_source_folder():
    global source_folder
    source_folder = filedialog.askdirectory()
    source_folder_label.config(text=source_folder)

# 函数：浏览目标文件夹
def browse_destination_folder():
    global destination_folder
    destination_folder = filedialog.askdirectory()
    destination_folder_label.config(text=destination_folder)

# 函数：浏览图片文件夹
def browse_image_folder():
    global image_folder
    image_folder = filedialog.askdirectory()
    image_folder_label.config(text=image_folder)

# 函数：浏览类名列表txt文件
def browse_predefined_classes_file():
    global predefined_classes_file
    predefined_classes_file = filedialog.askopenfilename()
    predefined_classes_file_label.config(text=predefined_classes_file)

def write_xml(img_id, sh, sw, sd, destination_folder, labeldicts):
    # 创建Annotation根节点
    root = ET.Element('annotation', {'verified': 'no'})
    ET.SubElement(root, 'folder').text = os.path.basename(image_folder)
    # 创建filename子节点，无扩展名
    ET.SubElement(root, 'filename').text = str(img_id+'.jpg')
    ET.SubElement(root, 'path').text = str(image_folder+'/'+img_id+'.jpg')

    source = ET.SubElement(root,'source')
    ET.SubElement(source, 'database').text = "Unknown"
    # 创建size子节点
    size = ET.SubElement(root,'size')
    ET.SubElement(size, 'width').text = str(sw)
    ET.SubElement(size, 'height').text = str(sh)
    ET.SubElement(size, 'depth').text = str(sd)
    ET.SubElement(root, 'segmented').text = "0"

    for labeldict in labeldicts:
        objects = ET.SubElement(root, 'object')
        #ET.SubElement(objects, 'type').text = 'bndbox'
        ET.SubElement(objects, 'name').text = labeldict['name']
        ET.SubElement(objects, 'pose').text = 'Unspecified'
        ET.SubElement(objects, 'truncated').text = '0'
        ET.SubElement(objects, 'difficult').text = '0'
        bndbox = ET.SubElement(objects,'bndbox')
        ET.SubElement(bndbox, 'xmin').text = str(int(labeldict['xmin']+0.5))
        ET.SubElement(bndbox, 'ymin').text = str(int(labeldict['ymin']+0.5))
        ET.SubElement(bndbox, 'xmax').text = str(int(labeldict['xmax']+0.5))
        ET.SubElement(bndbox, 'ymax').text = str(int(labeldict['ymax']+0.5))
    tree = ET.ElementTree(root)
    tree.write(destination_folder, encoding='utf-8', pretty_print=True)#每个元素会自动换行和缩进

#函数：执行格式转换的核心代码
def core_code_roxml2yolo_rotation(source_folder, destination_folder):
    global processed_files
    processed_files = 0
    file_count = len(os.listdir(source_folder))
    #for xml_file in tqdm(os.listdir(source_folder), desc="Converting", unit=" file"):
    for xml_file in os.listdir(source_folder):
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
                    if angle > pi:
                        angle -= pi

                    degree = int(round(angle / pi * 180))
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
            progress.set(f"{processed_files}"+'/'+f"{file_count}")

#函数：执行格式转换的核心代码
def core_code_roxml2dotaxml(source_folder, destination_folder):
    global processed_files
    processed_files = 0
    file_count = len(os.listdir(source_folder))
    #for xml_file in tqdm(os.listdir(source_folder), desc="Converting", unit=" file"):
    for xml_file in os.listdir(source_folder):
        if xml_file.endswith(".xml"):
            edit_xml(os.path.join(source_folder, xml_file), os.path.join(destination_folder, xml_file))
            processed_files += 1
            progress.set(f"{processed_files}"+'/'+f"{file_count}")

#-------------
def edit_xml(roxml_file, dotaxml_file):

    tree = ET.parse(roxml_file)
    objs = tree.findall('object')
    for ix, obj in enumerate(objs):
        x0 = ET.Element("x0")  # 创建节点
        y0 = ET.Element("y0")
        x1 = ET.Element("x1")
        y1 = ET.Element("y1")
        x2 = ET.Element("x2")
        y2 = ET.Element("y2")
        x3 = ET.Element("x3")
        y3 = ET.Element("y3")
        # obj_type = obj.find('bndbox')
        # type = obj_type.text
        # print(xml_file)

        if (obj.find('robndbox') == None):
            obj_bnd = obj.find('bndbox')
            obj_xmin = obj_bnd.find('xmin')
            obj_ymin = obj_bnd.find('ymin')
            obj_xmax = obj_bnd.find('xmax')
            obj_ymax = obj_bnd.find('ymax')
            #以防有负值坐标
            xmin = max(float(obj_xmin.text),0)
            ymin = max(float(obj_ymin.text),0)
            xmax = max(float(obj_xmax.text),0)
            ymax = max(float(obj_ymax.text),0)
            obj_bnd.remove(obj_xmin)  # 删除节点
            obj_bnd.remove(obj_ymin)
            obj_bnd.remove(obj_xmax)
            obj_bnd.remove(obj_ymax)
            x0.text = str(xmin)
            y0.text = str(ymax)
            x1.text = str(xmax)
            y1.text = str(ymax)
            x2.text = str(xmax)
            y2.text = str(ymin)
            x3.text = str(xmin)
            y3.text = str(ymin)
        else:
            obj_bnd = obj.find('robndbox')
            obj_bnd.tag = 'bndbox'  # 修改节点名
            obj_cx = obj_bnd.find('cx')
            obj_cy = obj_bnd.find('cy')
            obj_w = obj_bnd.find('w')
            obj_h = obj_bnd.find('h')
            obj_angle = obj_bnd.find('angle')
            cx = float(obj_cx.text)
            cy = float(obj_cy.text)
            w = float(obj_w.text)
            h = float(obj_h.text)
            angle = float(obj_angle.text)
            obj_bnd.remove(obj_cx)  # 删除节点
            obj_bnd.remove(obj_cy)
            obj_bnd.remove(obj_w)
            obj_bnd.remove(obj_h)
            obj_bnd.remove(obj_angle)

            x0.text, y0.text = rotatePoint(cx, cy, cx - w / 2, cy - h / 2, -angle)
            x1.text, y1.text = rotatePoint(cx, cy, cx + w / 2, cy - h / 2, -angle)
            x2.text, y2.text = rotatePoint(cx, cy, cx + w / 2, cy + h / 2, -angle)
            x3.text, y3.text = rotatePoint(cx, cy, cx - w / 2, cy + h / 2, -angle)


        # obj.remove(obj_type)  # 删除节点
        obj_bnd.append(x0)  # 新增节点
        obj_bnd.append(y0)
        obj_bnd.append(x1)
        obj_bnd.append(y1)
        obj_bnd.append(x2)
        obj_bnd.append(y2)
        obj_bnd.append(x3)
        obj_bnd.append(y3)

        tree.write(dotaxml_file, method='xml', encoding='utf-8')  # 更新xml文件

# 转换成四点坐标
def rotatePoint(xc, yc, xp, yp, theta):
    xoff = xp - xc;
    yoff = yp - yc;
    cosTheta = math.cos(theta)
    sinTheta = math.sin(theta)
    pResx = cosTheta * xoff + sinTheta * yoff
    pResy = - sinTheta * xoff + cosTheta * yoff
    return str(int(xc + pResx)), str(int(yc + pResy))


def core_code_dotaxml2yolo(source_folder, destination_folder):

    files = os.listdir(source_folder)
    for file in files:

        tree = ET.parse(source_folder + os.sep + file)
        root = tree.getroot()

        name = file.strip('.xml')
        output = destination_folder +'\\'+name + '.txt'
        file = open(output, 'w')

        objs = root.findall('object')
        for obj in objs:
            obj_name = obj.find('name').text
            box = obj.find('bndbox')
            x0 = int(float(box.find('x0').text))
            y0 = int(float(box.find('y0').text))
            x1 = int(float(box.find('x1').text))
            y1 = int(float(box.find('y1').text))
            x2 = int(float(box.find('x2').text))
            y2 = int(float(box.find('y2').text))
            x3 = int(float(box.find('x3').text))
            y3 = int(float(box.find('y3').text))
            for cls_index, cls_name in enumerate(classeslist):
                if obj_name == cls_name:
                    file.write("{} {} {} {} {} {} {} {} {} {}\n".format(x0, y0, x1, y1, x2, y2, x3, y3, obj_name, cls_index))
        #file.close()
#-------------
#函数：执行格式转换的核心代码
def core_code_voc2yolo(source_folder, destination_folder):
    global processed_files
    processed_files = 0
    file_count = len(os.listdir(source_folder))
    #for xml_file in tqdm(os.listdir(source_folder), desc="Converting", unit=" file"):
    for xml_file in os.listdir(source_folder):
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
            progress.set(f"{processed_files}"+'/'+f"{file_count}")

#函数：执行格式转换的核心代码
def core_code_yolo2voc(source_folder, destination_folder, image_folder):
    global processed_files
    processed_files = 0
    global img_id
    file_count = len(os.listdir(source_folder))
    # 遍历txt文件夹中的文件名
    #for txt_files in tqdm(os.listdir(source_folder), desc="Converting", unit=" file"):#此处为进度条
    for txt_files in os.listdir(source_folder):
        # 检查文件名是否存在于图片文件夹中
        base_txt_files = os.path.splitext(txt_files)[0]
        if base_txt_files in image_files:
        #if label in image_files:
            with open(source_folder +'/' + txt_files, 'r') as f:
                img_id = os.path.splitext(txt_files)[0]
                contents = f.readlines()
                labeldicts = []
                for content in contents:

                    #PIL包的写法Image.open()
                    # 图片格式，我这里是jpg，你如果是png注意修改
                    img = Image.open(image_folder + '/'+txt_files.strip('.txt') + '.jpg')
                    # 图片的高度、宽度、深度
                    sh, sw = img.size
                    sd = len(img.getbands())

                    content = content.strip('\n').split()
                    cx = float(content[1]) * sw
                    cy = float(content[2]) * sw
                    w = float(content[3]) * sw
                    h = float(content[4]) * sw
                    xmin = (cx - w / 2.0)
                    ymin = (cy - h / 2.0)
                    xmax = (cx + w / 2.0)
                    ymax = (cy + h / 2.0)
                    # 坐标的转换，class_name x_center y_center width height -> name cx cy w h

                    new_dict = {'name': classeslist[int(content[0])],
                                'xmin': xmin,
                                'ymin': ymin,
                                'xmax': xmax,
                                'ymax': ymax
                                }
                    labeldicts.append(new_dict)
                write_xml(img_id, sh, sw, sd, destination_folder + '/'+ txt_files.strip('.txt') + '.xml', labeldicts)


                # 更新进度条
            processed_files += 1
            progress.set(f"{processed_files}"+'/'+f"{file_count}")
            #print(f"{processed_files}"+'/'+f"{file_count}")
        else:
            pass

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
        row_tag = f"row_{class_name}"  # 使用类别索引创建唯一的标签
        # 配置不同行的颜色
        result_tree.tag_configure(row_tag, background=random_color())
        result_tree.insert("", "end", values=(class_name, class_index, count), tags=(row_tag,))
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
        row_tag = f"row_{class_name}"  # 使用类别索引创建唯一的标签
        # 配置不同行的颜色
        result_tree.tag_configure(row_tag, background=random_color())
        result_tree.insert("", "end", values=(class_name, class_index, count), tags=(row_tag,))


    # 4. 更新结果文本框
    #result_text.set("\n".join([f"{key} (Index {classes[key]}): {value}" for key, value in class_counts.items()]))
# 函数：执行转换功能
def convert_to_yolo3():
    if not source_folder or not destination_folder or not image_folder or not predefined_classes_file:
        messagebox.showerror("Error", "请选择源文件夹和目标文件夹和图片文件夹和字典txt")
        return
    global txt_files
    global image_files
    txt_files = set(os.path.splitext(file)[0] for file in os.listdir(source_folder))
    #print(f"{txt_files}")
    image_files = set(os.path.splitext(file)[0] for file in os.listdir(image_folder))
    #print(f"{image_files}")
    #if txt_files != image_files:
       # messagebox.showerror("Error", "txt文件夹和图片文件夹数量不一致")
       # return
    # 1. 遍历源文件夹，构建类别索引映射，并按字母顺序排序
    global classes
    global classeslist
    # 读取txt文件中的每一行
    with open(predefined_classes_file, 'r') as file:
        lines = file.readlines()
        lines = [line.strip() for line in lines]

    # 将类名按字母顺序排序
    lines.sort()

    # 为每个类名分配从0开始的索引号
    for index, class_name in enumerate(lines):
        classes[class_name] = index
    if classes is not None:
        messagebox.showinfo("Info", f"类别字典已构建成功:\n{classes}")
    classeslist = list(classes.keys())
    messagebox.showinfo("Info", f"类别列表已构建成功:\n{classeslist}")
    #classes = {k: v for k, v in sorted(classes.items())}
    # 重新映射类别索引为0开始的正整数
    #classes = {key: index for index, key in enumerate(sorted(classes.keys()))}
    # 2. 再次遍历源文件夹，转换YOLO格式为VOC格式
    core_code_yolo2voc(source_folder, destination_folder, image_folder)
    #messagebox.showinfo("Info", "转换完成")

    # 3. 统计每个类别的数量并显示标签对应的索引号
    class_counts = {key: 0 for key in classes}
    for xml_file in os.listdir(destination_folder):
        if xml_file.endswith(".xml"):
            tree = ET.parse(os.path.join(destination_folder, xml_file))
            root = tree.getroot()
            for obj in root.findall("object"):
                obj_name = obj.find("name").text
                class_counts[obj_name] += 1
    # 清空之前的表格数据
    for item in result_tree.get_children():
        result_tree.delete(item)

    # 填充表格数据
    for class_name, class_index in classes.items():
        count = class_counts.get(class_name, 0)
        row_tag = f"row_{class_name}"  # 使用类别索引创建唯一的标签
        # 配置不同行的颜色
        result_tree.tag_configure(row_tag, background=random_color())
        result_tree.insert("", "end", values=(class_name, class_index, count), tags=(row_tag,))
# 函数：执行转换功能
def convert_to_yolo4():
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

    # 2. 再次遍历源文件夹，转换YOLO格式为VOC格式
    core_code_roxml2dotaxml(source_folder, destination_folder)
    #messagebox.showinfo("Info", "转换完成")

    # 3. 统计每个类别的数量并显示标签对应的索引号
    class_counts = {key: 0 for key in classes}
    for xml_file in os.listdir(destination_folder):
        if xml_file.endswith(".xml"):
            tree = ET.parse(os.path.join(destination_folder, xml_file))
            root = tree.getroot()
            for obj in root.findall("object"):
                obj_name = obj.find("name").text
                class_counts[obj_name] += 1
    # 清空之前的表格数据
    for item in result_tree.get_children():
        result_tree.delete(item)

    # 填充表格数据
    for class_name, class_index in classes.items():
        count = class_counts.get(class_name, 0)
        row_tag = f"row_{class_name}"  # 使用类别索引创建唯一的标签
        # 配置不同行的颜色
        result_tree.tag_configure(row_tag, background=random_color())
        result_tree.insert("", "end", values=(class_name, class_index, count), tags=(row_tag,))
# 函数：执行转换功能
def convert_to_yolo5():
    if not source_folder or not destination_folder:
        messagebox.showerror("Error", "请选择源文件夹和目标文件夹")
        return

    # 1. 遍历源文件夹，构建类别索引映射，并按字母顺序排序
    global classes
    global classeslist
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
    messagebox.showinfo("Info", f"{classes}")
    classeslist = list(classes.keys())
    messagebox.showinfo("Info", f"{classeslist}")
    # 2. 再次遍历源文件夹，转换DOTA格式为YOLO格式
    core_code_dotaxml2yolo(source_folder, destination_folder)
    #messagebox.showinfo("Info", "转换完成")

    # 3. 统计每个类别的数量并显示标签对应的索引号
    class_counts = {key: 0 for key in classes}
    for xml_file in os.listdir(source_folder):
        if xml_file.endswith(".xml"):
            tree = ET.parse(os.path.join(source_folder, xml_file))
            root = tree.getroot()
            for obj in root.findall("object"):
                obj_name = obj.find("name").text
                class_counts[obj_name] += 1
    # 清空之前的表格数据
    for item in result_tree.get_children():
        result_tree.delete(item)

    # 填充表格数据
    for class_name, class_index in classes.items():
        count = class_counts.get(class_name, 0)
        row_tag = f"row_{class_name}"  # 使用类别索引创建唯一的标签
        # 配置不同行的颜色
        result_tree.tag_configure(row_tag, background=random_color())
        result_tree.insert("", "end", values=(class_name, class_index, count), tags=(row_tag,))


# 创建UI元素
source_folder_label = tk.Label(root, text="选择源文件夹：")
source_folder_label.pack()
browse_source_button = tk.Button(root, text="浏览", background="cyan", command=browse_source_folder)
browse_source_button.pack()

destination_folder_label = tk.Label(root, text="选择目标文件夹：")
destination_folder_label.pack()
browse_destination_button = tk.Button(root, text="浏览", background="yellow", command=browse_destination_folder)
browse_destination_button.pack()

image_folder_label = tk.Label(root, text="选择jpg文件夹：")
image_folder_label.pack()
browse_image_button = tk.Button(root, text="浏览", background="green", command=browse_image_folder)
browse_image_button.pack()

predefined_classes_file_label = tk.Label(root, text="选择字典txt：")
predefined_classes_file_label.pack()
browse_predefined_button = tk.Button(root, text="浏览", background="pink", command=browse_predefined_classes_file)
browse_predefined_button.pack()


convert_button = tk.Button(root, text="VOC --> YOLO", background="blue", command=convert_to_yolo1)
convert_button.pack()
convert_button2 = tk.Button(root, text="roLabelimg --> YOLO[0,180)", background="red", command=convert_to_yolo2)
convert_button2.pack()
convert_button3 = tk.Button(root, text="YOLO --> VOC", background="purple", command=convert_to_yolo3)
convert_button3.pack()
convert_button4 = tk.Button(root, text="roLabelimg --> DOTAxml", background="orange", command=convert_to_yolo4)
convert_button4.pack()
convert_button5 = tk.Button(root, text="DOTAxml --> YOLO", background="grey", command=convert_to_yolo5)
convert_button5.pack()
#progress_bar = Progressbar(root, variable=progress_var, maximum=100)
#progress_bar.pack()

progress = tk.StringVar()
progress_label = tk.Label(root, textvariable=progress)
progress_label.pack()

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
