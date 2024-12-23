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
import pytesseract

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
pytesseract.pytesseract.tesseract_cmd = 'C:\\Users\\it01\\AppData\\Local\\Programs\\Tesseract-OCR\\tesseract.exe'


while True:
    # image = cv2.imread(r'C:\Users\it01\Documents\Python Project\BarcodeScanner\opencv_3rdparty-wechat_qrcode\test_label02.jpg')
    image = cap.read()[1]
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = cv2.threshold(image, cv2.THRESH_BINARY, thresh=100, maxval=255)[1]
    text_data = pytesseract.image_to_data(image, lang="eng", output_type=pytesseract.Output.DATAFRAME)

    n_boxes = len(text_data['text'])
    # Draw rectangle around detected text
    for i in range(n_boxes):
        if int(text_data['conf'][i]) > 50:
            print(f"{n_boxes} detected : {text_data['text'][i]} conf {text_data['conf'][i]}")
            text = text_data['text'][i]
            if text.strip() != '':
                (x, y, w, h) = (text_data['left'][i], text_data['top'][i], text_data['width'][i], text_data['height'][i])
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(image, text_data['text'][i], (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)


    cv2.imshow("Result", image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()

