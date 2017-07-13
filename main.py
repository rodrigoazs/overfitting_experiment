# -*- coding: utf-8 -*-
"""
Created on Tue Jul 11 16:14:26 2017

@author: Rodrigo Azevedo
"""

from multiprocessing import Pool
import random
import numpy as np
import sys
import time
from ofexp import OverfittingExp

def display_time(seconds, granularity=2):
    result = []
    intervals = (
    ('semanas', 604800),  # 60 * 60 * 24 * 7
    ('dias', 86400),    # 60 * 60 * 24
    ('horas', 3600),    # 60 * 60
    ('minutos', 60),
    ('segundos', 1),
    )

    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append("{} {}".format(value, name))
    return ', '.join(result[:granularity])

def calculate_noise(i, j, rounds, N, Qf, sigma2):
    sum_g2_eout = 0.0
    sum_g10_eout = 0.0
    sum_sqrt_g2_eout = 0.0
    sum_sqrt_g10_eout = 0.0 
    
    for r in range(rounds):
        exp = OverfittingExp(Qf, N, sigma2)
        exp.run()
        sum_g2_eout += exp.g2_eout
        sum_g10_eout += exp.g10_eout
        sum_sqrt_g2_eout += np.sqrt(exp.g2_eout)
        sum_sqrt_g10_eout += np.sqrt(exp.g10_eout)
        
    return [i, j, sum_g2_eout/rounds, sum_g10_eout/rounds, sum_sqrt_g2_eout/rounds, sum_sqrt_g10_eout/rounds]

def do_task(args):
    return calculate_noise(*args)

def stochastic_noise(n_processes, N_bound, sigma2_bound, sigma2_samples, rounds, Qf):
    N_space = np.arange(N_bound[0], N_bound[1] + 1)
    sigma2_space = np.linspace(sigma2_bound[0], sigma2_bound[1], num=sigma2_samples)
    tasks = []
    
    for i in range(len(N_space)):
        for j in range(len(sigma2_space)):
            tasks.append((i, j, rounds, N_space[i], Qf, sigma2_space[j]))
            
    total_tasks = len(tasks)
    tasks_count = 0
    last_time = 0
    start_time = time.time()
            
    pool = Pool(n_processes)
    with open('stochastic_noise.txt', 'w') as file:
        for result in pool.imap_unordered(do_task, tasks):
        #for task in tasks:
            #result = do_task(task)
            tasks_count += 1
            last_time = time.time()
            file.write(str(result) + '\n')
            exec_time = last_time - start_time
            remaining_time = (total_tasks - tasks_count) * (exec_time) / tasks_count
            sys.stdout.write("\rCalculado ... %.2f%%. Tempo execução: %s. Tempo restante estimado: %s" % (((100.0 * tasks_count / total_tasks)), display_time(last_time - start_time), display_time(remaining_time)))
            sys.stdout.flush()

stochastic_noise(8, [1,130], [0.0, 2.5], 51, 1000, 20)

#a = calculate_noise(4, 1, 1,2)
#
#n_processes= 1
#N_bound=[1,11]
#sigma2_bound=[0,10]
#N_step=2
#sigma2_step=2
#rounds=10
#Qf=10
#
#N_space = np.linspace(N_bound[0], N_bound[1], num=((N_bound[1] - N_bound[0]) / (N_step*1.0) + 1.0))
#sigma2_space = np.linspace(sigma2_bound[0], sigma2_bound[1], num=((sigma2_bound[1] - sigma2_bound[0]) / (sigma2_step*1.0) + 1.0))
#tasks = []
#
#for N in N_space:
#    for sigma2 in sigma2_space:
#        tasks.append((rounds, N, Qf, sigma2))
#        
#total_tasks = len(tasks)
#tasks_count = 0
#
#pool = Pool(n_processes)
##with open('stochastic_noise.txt', 'wb') as file:
#    #file.write('aaa' + '\n')
#for result in pool.imap_unordered(do_task, tasks):
##for t in tasks:
#    result = do_task(t)
#    #print(t)
#    tasks_count += 1
#    #file.write(str(result) + '\n')
#    #print(result)
#    sys.stdout.write("\rCalculado ... %.2f%%" % ((100.0 * tasks_count / total_tasks)))
#    sys.stdout.flush()