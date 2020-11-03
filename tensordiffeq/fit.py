import tensorflow as tf
import numpy as np
from .networks import *
from .models import *
from .utils import *
import time



def fit(obj, tf_iter, newton_iter, batch_sz = None):
    obj.u_model = neural_net(obj.layer_sizes)
    #Can adjust batch size for collocation points, here we set it to N_f
    if batch_sz is not None:
        obj.batch_sz = batch_sz
    else:
        obj.batch_sz = len(obj.x_f)

    N_f = len(obj.x_f)
    n_batches =  N_f // obj.batch_sz

    start_time = time.time()
    tf_optimizer = tf.keras.optimizers.Adam(lr = 0.005, beta_1=.99)
    tf_optimizer_weights = tf.keras.optimizers.Adam(lr = 0.005, beta_1=.99)
    #tf_optimizer_u = tf.keras.optimizers.Adam(lr = 0.005, beta_1=.99)

    print("starting Adam training")

    for epoch in range(tf_iter):
        for i in range(n_batches):
            if obj.isAdaptive:
                loss_value, mse_0, mse_b, mse_f, grads, grads_col, grads_u = obj.adaptgrad()
                tf_optimizer.apply_gradients(zip(grads, obj.u_model.trainable_variables))
                tf_optimizer_weights.apply_gradients(zip([-grads_col, -grads_u], [obj.col_weights, obj.u_weights]))
            else:
                loss_value, mse_0, mse_b, mse_f, grads = obj.grad()
                tf_optimizer.apply_gradients(zip(grads, obj.u_model.trainable_variables))

        if epoch % 10 == 0:
            elapsed = time.time() - start_time
            print('It: %d, Time: %.2f' % (epoch, elapsed))
            tf.print(f"mse_0: {mse_0}  mse_b  {mse_b}  mse_f: {mse_f}   total loss: {loss_value}")
            start_time = time.time()

    #l-bfgs-b optimization
    print("Starting L-BFGS training")

    loss_and_flat_grad = obj.get_loss_and_flat_grad()

    lbfgs(loss_and_flat_grad,
      get_weights(obj.u_model),
      Struct(), maxIter=newton_iter, learningRate=0.8)



def fit_dist(obj, tf_iter, newton_iter, batch_sz = None):

    BUFFER_SIZE = len(obj.x_f)
    EPOCHS = tf_iter

    strategy = tf.distribute.MirroredStrategy()
    print("number of devices: {}".format(strategy.num_replicas_in_sync))

    if batch_sz is not None:
        obj.batch_sz = batch_sz
    else:
        obj.batch_sz = len(obj.x_f)

    N_f = len(obj.x_f)
    n_batches =  N_f // obj.batch_sz

    BATCH_SIZE_PER_REPLICA = obj.batch_sz
    GLOBAL_BATCH_SIZE = BATCH_SIZE_PER_REPLICA * strategy.num_replicas_in_sync

    train_dataset = tf.data.Dataset.from_tensor_slices((self.x_f, self.t_f))

    start_time = time.time()

    with strategy.scope():
        obj.u_model = neural_net(obj.layer_sizes)
        tf_optimizer = tf.keras.optimizers.Adam(lr = 0.005, beta_1=.99)
        tf_optimizer_weights = tf.keras.optimizers.Adam(lr = 0.005, beta_1=.99)
        #Can adjust batch size for collocation points, here we set it to N_f


    #tf_optimizer_u = tf.keras.optimizers.Adam(lr = 0.005, beta_1=.99)

    print("starting Adam training")

    for epoch in range(tf_iter):
        for i in range(n_batches):
            if obj.isAdaptive:
                loss_value, mse_0, mse_b, mse_f, grads, grads_col, grads_u = obj.adaptgrad()
                tf_optimizer.apply_gradients(zip(grads, obj.u_model.trainable_variables))
                tf_optimizer_weights.apply_gradients(zip([-grads_col, -grads_u], [obj.col_weights, obj.u_weights]))
            else:
                loss_value, mse_0, mse_b, mse_f, grads = obj.grad()
                tf_optimizer.apply_gradients(zip(grads, obj.u_model.trainable_variables))

        if epoch % 10 == 0:
            elapsed = time.time() - start_time
            print('It: %d, Time: %.2f' % (epoch, elapsed))
            tf.print(f"mse_0: {mse_0}  mse_b  {mse_b}  mse_f: {mse_f}   total loss: {loss_value}")
            start_time = time.time()

    #l-bfgs-b optimization
    print("Starting L-BFGS training")

    loss_and_flat_grad = obj.get_loss_and_flat_grad()

    lbfgs(loss_and_flat_grad,
      get_weights(obj.u_model),
      Struct(), maxIter=newton_iter, learningRate=0.8)

def train_step(inputs):
    x_f, t_f = inputs

def train_op_tf(obj):
    if obj.isAdaptive:
        loss_value, mse_0, mse_b, mse_f, grads, grads_col, grads_u = obj.adaptgrad()
        tf_optimizer.apply_gradients(zip(grads, obj.u_model.trainable_variables))
        tf_optimizer_weights.apply_gradients(zip([-grads_col, -grads_u], [obj.col_weights, obj.u_weights]))
    else:
        loss_value, mse_0, mse_b, mse_f, grads = obj.grad()
        tf_optimizer.apply_gradients(zip(grads, obj.u_model.trainable_variables))
