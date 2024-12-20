# import keras_ocr
# from matplotlib import pyplot as plt

# pipline = keras_ocr.pipeline.Pipeline()

# images = [
#     keras_ocr.tools.read(url) for url in [
#         'https://www.codeproject.com/KB/recipes/OCR-Chain-Code/image013.jpg'
#     ]
# ]

# prediction_groups = pipline.recognize(images)

# # Plot the predictions
# fig, axs = plt.subplt(nnrows=len(images), figsize=(20, 20))
# for ax, image, predictions in zip(axs, images, prediction_groups):
#     keras_ocr.tools.drawAnnotations(image=image, predictions=predictions, ax=ax)

import cv2
import easyocr

reader = easyocr.Reader(['en'])
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 800)

def preprocess_image(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # _, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_OTSU)
    return gray


ret, frame = cap.read()
# frame = cv2.resize(frame, (800, 800))
pre_img = preprocess_image(frame)
results = reader.readtext(pre_img)

for (bbox, text, prob) in results:
    # print(f'Text: {text}, Probability: {prob}')
    cv2.rectangle(frame, bbox[0], bbox[2], (0, 255, 0), 1)
    cv2.putText(frame, text, tuple(map(int, bbox[0])), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

cv2.imshow("Frame", frame)

if cv2.waitKey(0) & 0xFF == ord('q'):
    cap.release()
    cv2.destroyAllWindows()
