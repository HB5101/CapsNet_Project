"""
Here, PrimaryCap and DigiCap layer are defined which are key layers used for constructing a Capsule Network. 
"""

import tensorflow as tf
from tensorflow import keras
import keras.backend as K
from keras import layers, Model, initializers


def PrimaryCap(inputs, dim_capsule, n_channels, kernel_size, strides, padding):
    """
    With the inputs of shape=[None, width, height, channels], PrimaryCap layer gives an (dim_capsule)-D capsule as output which is then squashed
    """
    outputs = []
    for i in range(n_channels):
        output = layers.Conv2D(filters=dim_capsule, kernel_size=kernel_size, strides=strides, padding=padding)(inputs)
        d1=output.shape[1]
        d2=output.shape[2]
        outputs.append(layers.Reshape([d1*d2, dim_capsule])(output))
       
    outputs = layers.Concatenate(axis=1)(outputs)
    prim_out = layers.Lambda(squash)(outputs)
    return prim_out
    
def squash(vectors, axis=-1):
    """
    Squash function is used so that final output vector of the capsule has length between 0 and 1. This function shrinks small vectors to zero and large vectors to unit vectors.
    """
    s_squared_norm = K.sum(K.square(vectors), axis, keepdims=True)
    scale= s_squared_norm/ (1+ s_squared_norm)/ K.sqrt(s_squared_norm)
    squashed_vec=scale*vectors
    return squashed_vec
    
class DigiCap(layers.Layer):
    """
    This is the capsule layer used to convert (input_dim_capsule)-D capsule to (dim_capsule)-D capsule. Here, input shape = [None, input_num_capsule, input_dim_capsule] and
    output shape =[None, num_capsule, dim_capsule]
    
    """
    def __init__(self, num_capsule, dim_capsule, routings=3,**kwargs):
        super(DigiCap, self).__init__(**kwargs)
        self.num_capsule = num_capsule                         #no. of capsules in this layer
        self.dim_capsule = dim_capsule                         #dimension of the output vectors of the capsules in this layer
        self.routings = routings                               #number of iterations for the routing algorithm

    def build(self, input_shape):
        assert len(input_shape) >= 3,                      "The input Tensor should have shape=[None, input_num_capsule, input_dim_capsule]"
        initializer = tf.glorot_uniform_initializer()
        self.input_num_capsule = input_shape[1]
        self.input_dim_capsule = input_shape[2]

        # Transform matrix
        self.W = tf.Variable(initializer(shape=[self.num_capsule, self.input_num_capsule,self.dim_capsule, self.input_dim_capsule], dtype=tf.float32))

        self.built = True

    def call(self, inputs, training=None):
        # inputs.shape=[None, input_num_capsule, input_dim_capsule]
        # inputs_expand.shape=[None, 1, input_num_capsule, input_dim_capsule]
        inputs_expand = K.expand_dims(inputs, 1)

        # inputs_tiled.shape=[None, num_capsule, input_num_capsule, input_dim_capsule]
        inputs_tiled = K.tile(inputs_expand, [1, self.num_capsule, 1, 1])

        # inputs_hat.shape = [None, num_capsule, input_num_capsule, dim_capsule]
        inputs_hat = K.map_fn(lambda x: K.batch_dot(x, self.W, [2, 3]), elems=inputs_tiled)

        #  Routing algorithm --
        # b.shape = [None, self.num_capsule, self.input_num_capsule].
        b = tf.zeros(shape=[K.shape(inputs_hat)[0], self.num_capsule, self.input_num_capsule])
        #b is short lived. It is re-initialized  to 0 for every datapoint before the dynamic routing calculation

        assert self.routings > 0, 'The routings should be > 0.'
        for i in range(self.routings):
            # c.shape=[batch_size, num_capsule, input_num_capsule]
            c = tf.nn.softmax(b, axis=1)        #c is coupling coefficient

            # outputs.shape=[None, num_capsule, dim_capsule]
            outputs = squash(K.batch_dot(c, inputs_hat, [2, 2]))  # [None, 10, 16]

            if i < self.routings - 1:
                b += K.batch_dot(outputs, inputs_hat, [2, 3])

        return outputs
   
