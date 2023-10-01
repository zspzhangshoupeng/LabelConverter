# LabelConverter
![image](https://githubfast.com/zspzhangshoupeng/LabelConverter/assets/136520631/e758e361-8bb8-4378-9db9-690c73466167)
![image](https://githubfast.com/zspzhangshoupeng/LabelConverter/assets/136520631/19c09b32-f022-4bc3-a15d-19968e11a9cc)
使用教程可参见[CSDN](https://blog.csdn.net/zsprb1/article/details/133366640)
# 2023.9.29
#  实现功能1：
统计标签数量，展示所有出现的标签，方便发现错误标签名称，按字母顺序排列，从0开始赋值。
#  实现功能2：
水平检测框VOC转YOLO，xml[name, xmin, ymin, xmax, ymax]转txt[class_name, cx, cy, w, h]
#  实现功能3：
旋转检测框roLabelimg转YOLO，xml[name, cx, cy, w, h, angle]转txt[class_name, cx, cy, w, h, angle]
- roLabelimg用弧度单位[0, 3.14)
- YOLO--OpenCV表示法，w>h, angle用角度单位[0, 180), 顺时针方向为正角度。
# 2023.10.1
#   实现4：
YOLO逆转水平检测框VOC，txt[class_name, cx, cy, w, h]转xml[name, xmin, ymin, xmax, ymax]
- 需要打开class_name和name对应关系的字典txt。程序会自动将无序的类别，重排为字母顺序，
- predefined_classes_name.txt如
- 类别A
- 类别B
- 类别C
- 需要打开图片数据集的DataSets
- 例如
- DataSets
-   |————0001.jpg
-   |————0002.jpg
-   ...
#   待续1：
旋转检测框roLabelimg转DOTA，xml[name, cx, cy, w, h, angle]转txt[x0,y0, x1,y1, x2,y2, x3,y3, class_name, difficult]
