import keras

def keras_model_def():
    # 모델 위치
    model_filename ='C:\\Users\\starj\\Downloads\\keras_model.h5'

    # 케라스 모델 가져오기
    model = keras.models.load_model(model_filename)
    return model