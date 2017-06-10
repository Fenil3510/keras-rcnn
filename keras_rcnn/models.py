# -*- coding: utf-8 -*-

import keras
import keras_resnet
import keras_rcnn.layers
import keras_rcnn.heads


class RCNN(keras.models.Model):
    """
    Faster R-CNN model by S Ren et, al. (2015).

    :param inputs: input tensor (e.g. an instance of `keras.layers.Input`)
    :param classes: integer, number of classes
    :param rois: integer, number of regions of interest per image
    """

    def __init__(self, inputs, classes, rois):
        if keras.backend.image_data_format() == "channels_last":
            axis = 3
        else:
            axis = 1

        # ResNet50 as body
        y = keras_resnet.ResNet50(inputs)
        features = y.layers[-2].output

        rpn_classification = keras.layers.Conv2D(
            9 * 1, (1, 1), activation="sigmoid")(features)
        rpn_regression = keras.layers.Conv2D(9 * 4, (1, 1))(features)

        rpn_prediction = keras.layers.concatenate(
            [rpn_classification, rpn_regression])

        proposals = keras_rcnn.layers.object_detection.ObjectProposal(
            rois)([rpn_regression, rpn_classification])

        slices = keras_rcnn.layers.ROI((7, 7), rois)([inputs, proposals])

        y = keras.layers.TimeDistributed(
            keras.layers.Conv2D(1024, (1, 1)))(slices)

        [score, boxes] = keras_rcnn.heads.ResHead(classes)(y)

        super(RCNN, self).__init__(inputs,
                                   [rpn_prediction, score, boxes])
