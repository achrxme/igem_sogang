import numpy as np
import cv2

# 카메라를 제어할 수 있는 객체
capture = cv2.VideoCapture(0)

# 카메라 길이 너비 조절
capture.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

# 이미지 처리하기
def preprocessing(frame):
    #frame_fliped = cv2.flie(frame, 1)
    # 사이즈 조정 티쳐블 머신에서 사용한 이미지 사이즈로 변경해준다.
    size = (224, 224)
    frame_resized = cv2.resize(frame, size, interpolation=cv2.INTER_AREA)
    
    # 이미지 정규화
    # astype : 속성
    frame_normalized = (frame_resized.astype(np.float32) / 127.0) - 1

    # 이미지 차원 재조정 - 예측을 위해 reshape 해줍니다.
    # keras로 만든 모델에 공급할 올바른 모양의 배열 생성
    frame_reshaped = frame_normalized.reshape((1, 224, 224, 3))
    #print(frame_reshaped)
    return frame_reshaped

def grip_test(model):

    def predict(frame):
        prediction = model.predict(frame)
        return prediction

    cnt = [0,0,0]
    while True:
        ret, frame = capture.read()

        if cv2.waitKey(10) > 0: 
            break
        preprocessed = preprocessing(frame)
        prediction = predict(preprocessed)
        #prediction[0,0] : 1번째 정확도

        if (prediction[0,0] >0.7):
            print('grip success')
            cnt[0] += 1
            if cnt[0] > 20:
                return 'success'
            #cv2.putText(frame, 'hand off', (0, 25), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 0))
        elif(prediction[0,1] >0.7):
            cnt[1] += 1
            if cnt[1] > 20:
                return 'fail'
            #cv2.putText(frame, 'hand on', (0, 25), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 0))
            print('grip fail')
        else:
            cnt[2] += 1
            if cnt[2] > 30:
                return 'trash data' 
            print('trash data')

        cv2.imshow("VideoFrame", frame)
