import numpy as np

from segment_anything import sam_model_registry, SamPredictor
import cv2

def click_event(event, x, y, flags, param):
    global clicked_x, clicked_y, label
    if event == cv2.EVENT_LBUTTONDOWN:
        clicked_x, clicked_y, label = x, y, 1
    if event == cv2.EVENT_RBUTTONDOWN:
        clicked_x, clicked_y, label = x, y, 0

def show_point(image,label):
    if label == 1:
        cv2.circle(image, (clicked_x, clicked_y), 5, (255, 0, 0), -1) 
    elif label == 0:
        cv2.circle(image, (clicked_x, clicked_y), 5, (0, 0, 255), -1) 


img = cv2.imread(r'F:\Learning\segment-anything\fruits.jpg')
# image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
img = cv2.resize(img, (1000, 800))
image = img


sam_checkpoint = "model/sam_vit_b_01ec64.pth"
model_type = "vit_b"
device = "cuda"
coords = []
labels = []
option = 1
sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)
sam.to(device=device)
predictor = SamPredictor(sam)
predictor.set_image(image)


# cv2.imshow('Image1', image)
# cv2.setMouseCallback('Image1', click_event)

while True:
    cv2.imshow('Image1', image)
    cv2.setMouseCallback('Image1', click_event)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    if 'clicked_x' in globals() and 'clicked_y' in globals() and "label" in globals(): 
        coords.append([clicked_x, clicked_y])
        labels.append(label)
        if option == 1:
            input_point = np.array(coords)
            input_label = np.array(labels)

            masks, scores, logits = predictor.predict(
                point_coords=input_point,
                point_labels=input_label,
                multimask_output=True,
            )
            option = 0

        elif option == 0:
            input_point = np.array(coords)
            input_label = np.array(labels)
            mask_input = logits[np.argmax(scores), :, :]  # Choose the model's best mask

            masks, scores, logits  = predictor.predict(
                point_coords=input_point,
                point_labels=input_label,
                mask_input=mask_input[None, :, :],
                multimask_output=False,
            )

        mask = masks[-1]

        # 获取轮廓
        h,w = mask.shape[-2:]
        mask = mask.reshape(h,w,1)
        white = np.zeros([h,w,1],dtype="uint8")
        white[:,:,0] = 255
        x = mask * white

        canny = cv2.Canny(x,50,100)
 
        im = image.copy()
        # 画一个实心圆
        show_point(image,label)
        # 找到边缘轮廓
        contours, _ = cv2.findContours(canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 初始化最大面积和对应的最大轮廓
        max_area = 0
        max_contour = None

        # 遍历每个轮廓
        for contour in contours:
        # 计算轮廓的面积
            area = cv2.contourArea(contour)
            
            # 如果当前面积大于最大面积，则更新最大面积和对应的最大轮廓
            if area > max_area:
                max_area = area
                max_contour = contour
        # 使用矩形框绘制最大轮廓
        x, y, w, h = cv2.boundingRect(max_contour)
        cv2.rectangle(im, (x, y), (x + w, y + h), (0, 255, 0), 2)
        # 在原图上绘制边缘线
        cv2.drawContours(im, contours, -1, (0, 255, 0), 2)
        # 显示带有边缘的照片
        cv2.imshow('Image2', im)
        # 重置点击坐标
        del clicked_x, clicked_y, label

cv2.destroyAllWindows()
