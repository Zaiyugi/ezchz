#!/usr/bin/python

import os,sys,time
from dpapipetools import *
from DPACheesyQNotes import *
from DPACheesyQ import *
from DPACheesyQTasks import *
import re
import DPADataLibrary
import readline

import shutil
import glob

project_path = ".."
web_path = "../html"
done_web_path = project_path + "/total_done_tasks"
running_web_path = project_path + "/total_running_tasks"

# Snapshots taken in 30 second intervals
# 2880 -> 24 hrs worth of snapshots
# 20160 -> 1 week's worth
nbUsageSnapshots = 8640
nbDoneTaskSnapshots = 2880
ezchz_path = project_path + "/ezchz"

# Acquire sub-queues, add a Total sub-queue
queues = getCheesyQueuesList()
queues.append("Total")

# Create a data file for each sub-queue
usage_fos = []
for q in queues:
	q_usage_path = web_path + "/queue_data/" + str(q) + "_usage.csv"
	usage_fos.append( open(q_usage_path, "w") )

	ban = "step,waiting,running,done,machines,available"
	if q != "Total":
		ban += ",status"
	ban += ",timestamp"

	usage_fos[-1].write(ban + "\n")

# Create a list of all ezchz files by timestamp in reverse order
ezchz_reversed = project_path + "/ezchz_reversed"
os.system("ls -r " + ezchz_path + " > " + ezchz_reversed)
ezchz_rev_fo = open(ezchz_reversed, "r")

# Using "ezchz_reversed", compile list of necessary files
ezchz_usage_files = []
ezchz_tasks_files = []
u_cnt = 0
t_cnt = 0
for line in ezchz_rev_fo:
	if "usage" in line:
		if u_cnt < nbUsageSnapshots:
			ezchz_usage_files.append(line.rstrip('\r\n'))
			u_cnt += 1
	
	elif "tasks" in line:
		if t_cnt < nbDoneTaskSnapshots:
			ezchz_tasks_files.append(line.rstrip('\r\n'))
			t_cnt += 1
	
	if u_cnt >= nbUsageSnapshots and t_cnt >= nbDoneTaskSnapshots:
		break;

ezchz_rev_fo.close()

# Parse usage snapshots
cnt = 1
for f in ezchz_usage_files:
	ssfo = open(os.path.join(ezchz_path, f), "r")

	ssfo.readline()
	line = ssfo.readline()

	timestamp = int(line)	

	for line in ssfo:
		q_name, q_data = line.split(":")
		q_stats = q_data.split();

		output = str(cnt) 
		# q_stats: waiting running done machines available status
		output += "," + q_stats[0] 
		output += "," + q_stats[1] 
		output += "," + q_stats[2] 
		output += "," + q_stats[3] 
		output += "," + q_stats[4]

		# If not Total row, add sub-queue status
		if len(q_stats) > 5:
			if q_stats[5] == "running":
				output += ",1"
			else:
				output += ",0"

		output += "," + str(timestamp)
		output += "\n"

		ndx = queues.index(q_name)
		usage_fos[ndx].write(output)

	ssfo.close()
	cnt += 1

for qfo in usage_fos:
	qfo.close()

# Parse tasks snapshots; compile list of all done tasks
cnt = 1
total_done_fo = open(done_web_path, "w")
for f in ezchz_tasks_files:
	ssfo = open(os.path.join(ezchz_path, f), "r")
	ssfo.readline()
	ssfo.readline()

	for line in ssfo:
		task_data = line.split();

		task_info = ""
		q_name = ""
		if len(task_data) > 0:
			if task_data[0] == 'd':
				if len(task_data) == 6:
					q_name = task_data[4]
					# task_id startTime stopTime elapsed q_name snapshotTime
					task_info = task_data[1] + " null " + task_data[2] + " " + task_data[3] + " " + q_name + " " + task_data[5]
				else:
					q_name = task_data[5]
					# task_id startTime stopTime elapsed q_name snapshotTime
					task_info = task_data[1] + " " + task_data[2] + " " + task_data[3] + " " + task_data[4] + " " + q_name + " " + task_data[6]

				total_done_fo.write(task_info + "\n")

	ssfo.close()
	cnt += 1

total_done_fo.close()

# Get currently running tasks
total_running_fo = open(running_web_path, "w")
ssfo = open(os.path.join(ezchz_path, ezchz_tasks_files[0]), "r")
ssfo.readline()
ssfo.readline()

for line in ssfo:
	task_data = line.split();

	if len(task_data) > 0:
		if task_data[0] == 'r':
			if len(task_data) == 7:
				# task_id startTime elapsed q_name machine snapshotTime
				task_info = task_data[1] + " " + task_data[2] + " " + task_data[3] + " " + task_data[4] + " " + task_data[5] + " " + task_data[6]
				
				total_running_fo.write(task_info + "\n")

ssfo.close()
total_running_fo.close()

# Concatenate all queue_done files together
#q_done_path = project_path + "/task_lists/*_done"
#with open(done_web_path, "w") as outfile:
#	for filename in glob.glob(q_done_path):
#		with open(filename, "r") as infile:
#			shutil.copyfileobj(infile, outfile)

