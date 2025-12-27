import numpy as np
import time
import tensorflow as tf
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

p_file='P_10K.npz'
pm_file='powerModel_10K.npz'
P=np.load(p_file);
O=np.load(pm_file)
P=P['arr_0']
O=O['arr_0']

P=P.astype(np.float32)
O=O.astype(np.float32)

(n, t) = O.shape      # n traces of t samples
(n_bis, m) = P.shape  # n predictions for each of m candidates

num_iter=20;

tsta=time.time()

for iter in range(num_iter):
	DO = O - (np.einsum("nt->t", O, dtype=np.float32, optimize=True) / np.double(n)) # compute O - mean(O)
	DP = P - (np.einsum("nm->m", P, dtype=np.float32, optimize=True) / np.double(n)) # compute P - mean(P)
	
	numerator = np.einsum("nm,nt->mt", DP, DO, optimize=True)
	tmp1 = np.einsum("nm,nm->m", DP, DP, optimize=True)
	tmp2 = np.einsum("nt,nt->t", DO, DO, optimize=True)
	tmp = np.einsum("m,t->mt", tmp1, tmp2, optimize=True)
	denominator = np.sqrt(tmp)
	corr_index=numerator / denominator
tsto=time.time(); print('elapsed time - CPU: {}'.format((tsto-tsta)/num_iter)); tsta=time.time() 

sess=tf.InteractiveSession()

P_t=tf.Variable(P, dtype=np.float32, trainable=False); end_time=time.time();
O_t=tf.Variable(O, dtype=np.float32, trainable=False); end_time=time.time();

tsto=time.time(); print('elapsed time - tensor creation: {}'.format(tsto-tsta)); tsta=time.time() 

for iter in range(num_iter):
	#start_time=time.time(); A=tf.einsum("nt,nk->tk", P_t, O_t); end_time=time.time(); print('elapsed_time: '+str(end_time-start_time))
	DO_t = O_t - (tf.einsum("nt->t", O_t) / np.double(n)) # compute O - mean(O)
	DP_t = P_t - (tf.einsum("nm->m", P_t) / np.double(n)) # compute P - mean(P)
	
	numerator_t = tf.einsum("nm,nt->mt", DP_t, DO_t)
	tmp1_t = tf.einsum("nm,nm->m", DP_t, DP_t)
	tmp2_t = tf.einsum("nt,nt->t", DO_t, DO_t)
	tmp_t = tf.einsum("m,t->mt", tmp1_t, tmp2_t)
	denominator_t = tf.sqrt(tmp_t)
	corr_index_t=numerator_t / denominator_t
	
	init_op=tf.initialize_all_variables()
	sess.run(init_op)
tsto=time.time(); print('elapsed time - GPU: {}'.format((tsto-tsta)/num_iter)); tsta=time.time() 
print(sess.run(corr_index_t))


